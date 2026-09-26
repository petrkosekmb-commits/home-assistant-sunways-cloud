"""Constants for the Sunways integration."""

from datetime import timedelta
from typing import Final

DOMAIN: Final = "sunways"
MANUFACTURER: Final = "Sunways"
PLATFORMS: Final = ["sensor"]
CONF_STATION_ID: Final = "station_id"
CONF_INITIAL_TOKEN: Final = "initial_token"
CONF_SCAN_INTERVAL: Final = "scan_interval"
DEFAULT_SCAN_INTERVAL: Final = 60
MIN_SCAN_INTERVAL: Final = 30
MAX_SCAN_INTERVAL: Final = 3600
HISTORY_INTERVAL: Final = timedelta(minutes=5)
HISTORY_MAX_AGE_SECONDS: Final = 900
