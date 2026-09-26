"""Internal Sunways client."""

import base64
import hashlib
import time
from dataclasses import asdict, dataclass
from typing import Any
from urllib.parse import urljoin

from aiohttp import CookieJar, Payload, client_exceptions
from aiohttp.client import ClientSession

from .exceptions import (
    ConnectionFailed,
    LoginFailed,
    RequestFailed,
)

_API_HOST = "https://api.sunways-portal.com"
_API_LOGIN = "/monitor/auth/login"
_API_AUTH_INFO = "/monitor/auth/info?useFor=1"

API_STATION_LIST = "/monitor/core/power/station/monitoring/getPage"
API_STATION_OVERVIEW = "/monitor/core/power/station/overview/getSingleStationOverview"
API_DEVICE_LIST = "/monitor/core/device/getListByStation/"
API_DEVICE_INFO = "/monitor/core/device/getSingleDeviceInfo"


ASSUMED_TOKEN_LIFETIME = 60 * 60


@dataclass
class TokenJar:
    token: str | None = None
    issued: float | None = 0.0

    dict = asdict


class SunwaysApiConnection:
    """Low level Sunways API client."""

    _token_ttl: float
    _token_jar: TokenJar | None
    _own_session: bool
    _station_id: str
    _default_headers: dict

    def __init__(self, email: str, password: str, websession: ClientSession, token_jar: TokenJar | None = None):
        self._url = _API_HOST
        self._email = email
        self._password = password
        self._session = websession
        self._own_session = websession is None
        self._default_headers = {"ver": "pc"}
        self._verify_ssl = True
        self._token_jar = token_jar
        self._token_ttl = ASSUMED_TOKEN_LIFETIME

    async def _get_session(self) -> ClientSession:
        if self._session is None:
            self._own_session = True
            jar = CookieJar(unsafe=True)
            self._session = ClientSession(cookie_jar=jar)
        return self._session

    async def __aenter__(self):
        try:
            await self.login()
            return self
        except Exception as error:
            if self._own_session:
                await self.close()
            raise error

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> bool:
        """Call when the client is disposed."""
        # Close the web session, if we created it (i.e. it was not passed in)
        if self._own_session:
            await self.close()
        return False

    async def close(self):
        """Close the current web session."""
        if self._session:
            await self._session.close()
            self._session = None

    async def login(self):
        """Call to login and store token."""

        encoded_password = self._encode_password(self._password)
        auth = {"email": self._email, "password": encoded_password, "channel": 1}
        await self._do_request("post", _API_LOGIN, json=auth)

    async def _check_login(self) -> bool:
        """Check token validity."""
        if self._token_jar is None:
            return False

        current_lifetime = time.time() - self._token_jar.issued

        if current_lifetime < self._token_ttl:
            # Assume TTL good for a login to remain active
            return True

        try:
            response = await self._do_request("get", _API_AUTH_INFO)
            if response["userInfo"]:
                # Extend token ttl
                self._token_ttl += ASSUMED_TOKEN_LIFETIME
                return True
        except (ConnectionFailed, LoginFailed, RequestFailed, KeyError, TypeError):
            pass

        # Reduce token ttl
        self._token_ttl -= ASSUMED_TOKEN_LIFETIME
        return False

    async def request(self, method: str, end_point: str, params=None, json=None, data: Payload | None = None) -> Any:
        """Perform a request to the API, with authentication"""

        if not await self._check_login():
            await self.login()

        return await self._do_request(method, end_point, params=params, json=json, data=data)

    async def _do_request(
        self, method: str, end_point: str, params=None, json=None, data: Payload | None = None
    ) -> Any:
        """Perform a request to the API, and unpack the response."""

        url = urljoin(self._url, end_point)
        session = await self._get_session()

        # Note: We need to push back the token in the 'Cookie' and the 'token' header
        headers = self._default_headers.copy()
        if end_point != _API_LOGIN and self._token_jar:
            headers["token"] = self._token_jar.token
            # todo make session.cookie_jar.update_cookies work
            headers["Cookie"] = f"token={self._token_jar.token}"

        try:
            async with session.request(
                method,
                url,
                params=params,
                headers=headers,
                json=json,
                data=data,
                ssl=self._verify_ssl,
            ) as response:
                if response.status != 200:
                    if response.content_type == "application/json":
                        content = await response.json(encoding="utf-8")
                        self._check_application_errors(content)

                    raise RequestFailed(response.status, "HTTP Request Error")

                # If something goes wrong with the login session, HTTP 200 is returned :/
                if response.content_type != "application/json":
                    raise RequestFailed(0, "Invalid response body")

                content = await response.json(encoding="utf-8")
                self._check_application_errors(content)

                # The JWT token is returned in the header in login response
                if "token" in response.headers:
                    response_token = response.headers["token"]
                    self._token_jar = TokenJar(response_token, time.time())

                # Unpack response data
                if "data" in content:
                    return content["data"]
                return content

        except client_exceptions.ClientConnectionError as err:
            raise ConnectionFailed(err) from err
        except client_exceptions.ClientError as err:
            raise RequestFailed(0, f"Unexpected error: {err}") from None

    def _check_application_errors(self, response):
        if not isinstance(response, dict):
            return
        if "code" not in response:
            raise RequestFailed(-1, "Unexpected response: " + str(response))
        if response["code"] == "1000000":
            return
        if response["code"].lower().startswith("auth_"):
            raise LoginFailed(response["code"], response["msg"])
        raise RequestFailed(response["code"], response["msg"])

    def _encode_password(self, password: str) -> str:
        # The portal protocol requires MD5 before Base64; used only for protocol compatibility.
        md5_hash = hashlib.md5(password.encode(), usedforsecurity=False).hexdigest()
        return base64.b64encode(md5_hash.encode()).decode()
