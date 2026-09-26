"""Sunways sensor entities."""

from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorEntityDescription, SensorStateClass
from homeassistant.const import (
    PERCENTAGE,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfFrequency,
    UnitOfPower,
    UnitOfTemperature,
    UnitOfTime,
)
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import SunwaysConfigEntry
from .const import DOMAIN, MANUFACTURER
from .coordinator import SunwaysDataUpdateCoordinator


@dataclass(frozen=True, kw_only=True)
class SunwaysSensorDescription(SensorEntityDescription):
    enabled: bool = True


DESCRIPTIONS = (
    SunwaysSensorDescription(
        key="solar_power",
        translation_key="solar_power",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SunwaysSensorDescription(
        key="installed_power",
        translation_key="installed_power",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
    SunwaysSensorDescription(
        key="efficiency",
        translation_key="efficiency",
        device_class=SensorDeviceClass.POWER_FACTOR,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SunwaysSensorDescription(
        key="load_power",
        translation_key="load_power",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SunwaysSensorDescription(
        key="grid_power",
        translation_key="grid_power",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SunwaysSensorDescription(
        key="grid_power_consumption",
        translation_key="grid_power_consumption",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SunwaysSensorDescription(
        key="grid_power_return",
        translation_key="grid_power_return",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SunwaysSensorDescription(
        key="battery_power",
        translation_key="battery_power",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SunwaysSensorDescription(
        key="battery_soc",
        translation_key="battery_soc",
        device_class=SensorDeviceClass.BATTERY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SunwaysSensorDescription(
        key="daily_generation",
        translation_key="daily_generation",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    SunwaysSensorDescription(
        key="monthly_generation",
        translation_key="monthly_generation",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    SunwaysSensorDescription(
        key="yearly_generation",
        translation_key="yearly_generation",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.MEGA_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    SunwaysSensorDescription(
        key="total_generation",
        translation_key="total_generation",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.MEGA_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    SunwaysSensorDescription(
        key="history_sample_time", translation_key="history_sample_time", device_class=SensorDeviceClass.TIMESTAMP
    ),
    SunwaysSensorDescription(
        key="history_sample_age",
        translation_key="history_sample_age",
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SunwaysSensorDescription(
        key="history_grid_power",
        translation_key="history_grid_power",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SunwaysSensorDescription(
        key="history_pv_power",
        translation_key="history_pv_power",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SunwaysSensorDescription(
        key="history_load_power",
        translation_key="history_load_power",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SunwaysSensorDescription(
        key="history_battery_power",
        translation_key="history_battery_power",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SunwaysSensorDescription(
        key="cloud_received_at",
        translation_key="cloud_received_at",
        device_class=SensorDeviceClass.TIMESTAMP,
        entity_registry_enabled_default=False,
    ),
    SunwaysSensorDescription(
        key="station_status_code", translation_key="station_status_code", entity_registry_enabled_default=False
    ),
)

DEVICE_DESCRIPTIONS = (
    SunwaysSensorDescription(key="device_last_update", translation_key="device_last_update"),
    SunwaysSensorDescription(
        key="device_total_hours",
        translation_key="device_total_hours",
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.HOURS,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    SunwaysSensorDescription(
        key="grid_frequency",
        translation_key="grid_frequency",
        device_class=SensorDeviceClass.FREQUENCY,
        native_unit_of_measurement=UnitOfFrequency.HERTZ,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    *(
        SunwaysSensorDescription(
            key=key,
            translation_key=key,
            device_class=SensorDeviceClass.TEMPERATURE,
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
        )
        for key in ("inverter_temperature", "battery_temperature")
    ),
    SunwaysSensorDescription(
        key="battery_soh",
        translation_key="battery_soh",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SunwaysSensorDescription(
        key="battery_voltage",
        translation_key="battery_voltage",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SunwaysSensorDescription(
        key="battery_current",
        translation_key="battery_current",
        device_class=SensorDeviceClass.CURRENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    *(
        SunwaysSensorDescription(
            key=key,
            translation_key=key,
            device_class=SensorDeviceClass.CURRENT,
            native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
            state_class=SensorStateClass.MEASUREMENT,
        )
        for key in ("battery_charge_current_limit", "battery_discharge_current_limit")
    ),
    SunwaysSensorDescription(
        key="parallel_power",
        translation_key="parallel_power",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    *(
        SunwaysSensorDescription(key=key, translation_key=key)
        for key in ("meter_connection_status", "battery_model", "working_mode")
    ),
    *(
        SunwaysSensorDescription(
            key=f"{prefix}{number}_{measure}",
            translation_key=f"{prefix}_{measure}",
            translation_placeholders={"number": str(number)},
            device_class={
                "voltage": SensorDeviceClass.VOLTAGE,
                "current": SensorDeviceClass.CURRENT,
                "power": SensorDeviceClass.POWER,
            }[measure],
            native_unit_of_measurement={
                "voltage": UnitOfElectricPotential.VOLT,
                "current": UnitOfElectricCurrent.AMPERE,
                "power": UnitOfPower.KILO_WATT,
            }[measure],
            state_class=SensorStateClass.MEASUREMENT,
            entity_registry_enabled_default=False,
        )
        for prefix, maximum in (("pv", 6), ("grid_l", 3), ("backup_l", 3))
        for number in range(1, maximum + 1)
        for measure in ("voltage", "current", "power")
    ),
    *(
        SunwaysSensorDescription(
            key=f"backup_l{number}_frequency",
            translation_key="backup_l_frequency",
            translation_placeholders={"number": str(number)},
            device_class=SensorDeviceClass.FREQUENCY,
            native_unit_of_measurement=UnitOfFrequency.HERTZ,
            state_class=SensorStateClass.MEASUREMENT,
            entity_registry_enabled_default=False,
        )
        for number in range(1, 4)
    ),
)


async def async_setup_entry(hass: Any, entry: SunwaysConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator = entry.runtime_data.coordinator
    station_entities = [SunwaysSensor(coordinator, entry, description) for description in DESCRIPTIONS]
    device_entities = [
        SunwaysDeviceSensor(coordinator, entry, device, description)
        for device in coordinator.data.get("devices", [])
        for description in DEVICE_DESCRIPTIONS
        if device["sensors"].get(description.key) is not None
    ]
    async_add_entities([*station_entities, *device_entities])


class SunwaysSensor(CoordinatorEntity[SunwaysDataUpdateCoordinator], SensorEntity):
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: SunwaysDataUpdateCoordinator,
        entry: SunwaysConfigEntry,
        description: SunwaysSensorDescription,
    ) -> None:
        super().__init__(coordinator, context=description.key)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.station_id}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.station_id)},
            manufacturer=MANUFACTURER,
            name=entry.title,
            configuration_url="https://www.sunways-portal.com",
        )

    @property
    def native_value(self) -> Any:
        return self.coordinator.data["sensors"].get(self.entity_description.key)


class SunwaysDeviceSensor(CoordinatorEntity[SunwaysDataUpdateCoordinator], SensorEntity):
    """A value belonging to one physical inverter in the station."""

    _attr_has_entity_name = True

    def __init__(self, coordinator, entry, device: dict[str, Any], description) -> None:
        super().__init__(coordinator, context=f"{device['id']}_{description.key}")
        self.entity_description = description
        self._device_id = device["id"]
        self._attr_unique_id = f"{coordinator.station_id}_{device['id']}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"{coordinator.station_id}_{device['id']}")},
            manufacturer=MANUFACTURER,
            name=device["name"],
            model=device.get("model"),
            sw_version=device.get("firmware"),
            serial_number=device.get("serial"),
            via_device=(DOMAIN, coordinator.station_id),
            configuration_url="https://www.sunways-portal.com",
        )

    @property
    def native_value(self) -> Any:
        for device in self.coordinator.data.get("devices", []):
            if device["id"] == self._device_id:
                return device["sensors"].get(self.entity_description.key)
        return None
