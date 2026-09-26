"""Strict conversion of Sunways cloud values without fake zeroes."""

import math
from typing import Any


def finite(value: Any, *, non_negative: bool = True) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        result = float(value)
    except (TypeError, ValueError, OverflowError):
        return None
    return result if math.isfinite(result) and (not non_negative or result >= 0) else None


def convert(value: Any, unit: Any, *, kind: str = "power", target: str = "kilo") -> float | None:
    number = finite(value)
    if number is None or not isinstance(unit, str):
        return None
    factors = {
        "power": {"W": 0.001, "kW": 1.0, "MW": 1000.0},
        "energy": {"Wh": 0.001, "kWh": 1.0, "MWh": 1000.0},
        "installed": {"Wp": 0.001, "kWp": 1.0, "MWp": 1000.0},
    }
    factor = factors[kind].get(unit.strip())
    if factor is None:
        return None
    result = number * factor / (1000 if target == "mega" else 1)
    return round(result, 6)


def split_grid(data: dict[str, Any]) -> tuple[float | None, float | None, float | None]:
    power = convert(data.get("pmeterTotal"), data.get("pmeterTotalUnit"))
    incoming, outgoing = data.get("arrowGridInverter"), data.get("arrowInverterGrid")
    if (
        power is None
        or not all(type(v) is int and v in (0, 1) for v in (incoming, outgoing))
        or incoming + outgoing > 1
    ):
        return None, None, None
    if incoming == outgoing == 0:
        return (0.0, 0.0, 0.0) if power == 0 else (None, None, None)
    return (power, 0.0, power) if incoming else (0.0, power, -power)


def normalize_overview(data: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    if not isinstance(data, dict):
        raise ValueError("Unexpected overview shape")
    grid_import, grid_export, grid_power = split_grid(data)
    battery = convert(data.get("batteryP"), data.get("batteryPUnit"))
    charge, discharge = data.get("arrowInverterBattery"), data.get("arrowBatteryInverter")
    battery_valid = all(type(v) is int and v in (0, 1) for v in (charge, discharge)) and charge + discharge <= 1
    signed_battery = (
        (-battery if charge else battery if discharge else 0.0 if battery == 0 else None)
        if battery is not None and battery_valid
        else None
    )
    soc = finite(data.get("soc"))
    soc = soc if soc is not None and 0 <= soc <= 100 else None
    sensors = {
        "solar_power": convert(data.get("pac"), data.get("pacUnit")),
        "installed_power": convert(data.get("instatlledPower"), data.get("instatlledPowerUnit"), kind="installed"),
        "efficiency": finite(data.get("powerRatio")),
        "load_power": convert(data.get("pLoad"), data.get("pLoadUnit")),
        "grid_power": grid_power,
        "grid_power_consumption": grid_import,
        "grid_power_return": grid_export,
        "battery_power": signed_battery,
        "battery_soc": soc,
        "daily_generation": convert(data.get("eDay"), data.get("eDayUnit"), kind="energy"),
        "monthly_generation": convert(data.get("eMonth"), data.get("eMonthUnit"), kind="energy"),
        "yearly_generation": convert(data.get("eYear"), data.get("eYearUnit"), kind="energy", target="mega"),
        "total_generation": convert(data.get("eTotal"), data.get("eTotalUnit"), kind="energy", target="mega"),
        "station_status_code": data.get("stationStatus") if type(data.get("stationStatus")) is int else None,
    }
    quality = {
        "grid_values_valid": grid_power is not None,
        "missing_values": [k for k, v in sensors.items() if v is None],
        "source_measurement_time": None,
        "meter_connected": None,
        "reason": "measurement_time_and_meter_status_not_exposed"
        if grid_power is not None
        else "grid_value_or_direction_invalid",
    }
    return sensors, quality
