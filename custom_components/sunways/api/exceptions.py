"""Exceptions that the library might throw."""


class SunwaysClientException(Exception):
    """Base for all exceptions raised by the library."""


class RequestFailed(SunwaysClientException):
    """Generic rejection of any command by the controller."""

    def __init__(self, error_code: int, msg: str):
        self._error_code = error_code
        self._msg = msg
        super().__init__(f"Sunways API responded '{msg}' ({error_code})")


class LoginFailed(RequestFailed):
    """Username/Password failure or token not valid any more."""


class ConnectionFailed(SunwaysClientException):
    """Connection to Sunways API failed at the network level."""


class InvalidDevice(SunwaysClientException):
    """Device type isn't valid for this operation."""
