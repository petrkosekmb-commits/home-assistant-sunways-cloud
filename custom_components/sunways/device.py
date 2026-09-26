"""Normalize per-inverter values exposed by Sunways Portal."""

from __future__ import annotations

from typing import Any

from .quality import finite


def _find(data: Any, key: str) -> Any:
    """Find a key in the shallow/nested response formats used by the portal."""
    if isinstance(data, dict):
        if key in data:
            return data[key]
        for value in data.values():
            if isinstance(value, dict):
                found = _find(value, key)
                if found is not None:
                    return found
    return None


def _number(data: Any, key: str, *, signed: bool = False) -> float | None:
    return finite(_find(data, key), non_negative=not signed)


def _series(data: Any, key: str) -> list[float | None]:
    value = _find(data, key)
    if isinstance(value, str):
        values = value.split("/")
    elif isinstance(value, list):
        values = value
    else:
        return []
    return [finite(item) for item in values]


def normalize_device(device: dict[str, Any], detail: dict[str, Any]) -> dict[str, Any]:
    """Return identity and optional sensor values for one inverter."""
    device_id = str(device.get("id") or _find(detail, "id") or "")
    serial = device.get("deviceSn") or _find(detail, "deviceSn")
    result: dict[str, Any] = {
        "id": device_id,
        "name": device.get("deviceName") or _find(detail, "deviceName") or serial or device_id,
        "serial": str(serial) if serial is not None else None,
        "model": device.get("modeltype") or _find(detail, "modeltype"),
        "firmware": _find(detail, "firmwareVersion"),
        "sensors": {
            "device_last_update": _find(detail, "workStatus"),
            "device_total_hours": _number(detail, "timeTotal"),
            "grid_frequency": _number(detail, "fgrid"),
            "inverter_temperature": _number(detail, "temperature1", signed=True),
            "battery_temperature": _number(detail, "bmsPackTemperature", signed=True),
            "battery_soh": _number(detail, "soh"),
            "battery_voltage": _number(detail, "batteryV"),
            "battery_current": _number(detail, "batteryI", signed=True),
            "battery_charge_current_limit": _number(detail, "iChargingLimit"),
            "battery_discharge_current_limit": _number(detail, "iDischargeLimit"),
            "parallel_power": _number(detail, "couplingPower", signed=True),
            "meter_connection_status": _find(detail, "runStatus"),
            "battery_model": _find(detail, "batteryTypeCodeStr"),
            "working_mode": _find(detail, "hybirdWorkMode"),
        },
    }
    groups = (
        ("pv", "vpv", "ipv", "powerPv", 6),
        ("grid_l", "vgridPhase", "igridPhase", "powerPhase", 3),
        ("backup_l", "backupV", "backupI", "backupP", 3),
    )
    for prefix, voltage_key, current_key, power_key, maximum in groups:
        voltage, current, power = (_series(detail, key) for key in (voltage_key, current_key, power_key))
        for index in range(maximum):
            suffix = index + 1
            result["sensors"].update(
                {
                    f"{prefix}{suffix}_voltage": voltage[index] if index < len(voltage) else None,
                    f"{prefix}{suffix}_current": current[index] if index < len(current) else None,
                    f"{prefix}{suffix}_power": power[index] if index < len(power) else None,
                }
            )
    backup_frequency = _series(detail, "backupF")
    for index in range(3):
        result["sensors"][f"backup_l{index + 1}_frequency"] = (
            backup_frequency[index] if index < len(backup_frequency) else None
        )
    return result
