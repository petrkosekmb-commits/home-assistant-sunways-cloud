"""Parse coherent timestamped station-history samples."""

from datetime import UTC, datetime
from typing import Any

from .const import HISTORY_MAX_AGE_SECONDS
from .quality import finite

FIELDS = {
    "pMeter": "history_grid_power",
    "power": "history_pv_power",
    "loadPower": "history_load_power",
    "battery": "history_battery_power",
}


def history_payload(station_id: str, station_type: Any, now: datetime) -> dict[str, Any]:
    if type(station_type) is not int:
        raise ValueError("Missing station type")
    offset = now.utcoffset()
    return {
        "id": station_id,
        "stationType": station_type,
        "durationType": 1,
        "curveType": "1000",
        "isReal": 1,
        "date": now.strftime("%Y-%m-%d"),
        "timeZoneOffset": int(offset.total_seconds() / 60) if offset else 0,
    }


def parse_history(response: Any, now: datetime) -> dict[str, Any]:
    result = {
        "history_sample_time": None,
        "history_sample_age": None,
        **{v: None for v in FIELDS.values()},
        "history_status": "missing_sample",
    }
    if not isinstance(response, dict) or not isinstance(response.get("curve"), list):
        result["history_status"] = "invalid_response"
        return result
    config = response.get("config")
    if not isinstance(config, list):
        result["history_status"] = "invalid_units"
        return result
    units = {r.get("key"): r.get("unit") for r in config if isinstance(r, dict)}
    candidates = []
    for row in response["curve"]:
        if not isinstance(row, dict) or not any(row.get(k) is not None for k in FIELDS):
            continue
        stamp = finite(row.get("dateStamp"))
        if stamp is None or not 1577836800000 <= stamp <= 4102444800000:
            result["history_status"] = "invalid_timestamp"
            return result
        if stamp <= now.timestamp() * 1000:
            candidates.append((stamp, row))
    if not candidates:
        result["history_status"] = "future_timestamp"
        return result
    stamp, row = max(candidates, key=lambda item: item[0])
    measured = datetime.fromtimestamp(stamp / 1000, UTC)
    age = max(0, round((now - measured).total_seconds()))
    result.update(history_sample_time=measured, history_sample_age=age)
    factors = {"W": 1.0, "kW": 1000.0, "MW": 1000000.0}
    for source, target in FIELDS.items():
        value, factor = finite(row.get(source), non_negative=source != "pMeter"), factors.get(units.get(source))
        if value is not None and factor is not None:
            result[target] = round((-value if source == "pMeter" else value) * factor, 3)
    result["history_status"] = (
        "record_available" if result["history_grid_power"] is not None else "missing_grid_or_unit"
    )
    if age > HISTORY_MAX_AGE_SECONDS:
        result["history_status"] = "stale"
        for target in FIELDS.values():
            result[target] = None
    return result
