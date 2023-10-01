"""Sensor platform for Thai Easy Pass."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
)
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN, KEY_SN, SENSORS, NAME, MANUFACTURER
from .coordinator import ThaiEasyPassCoordinator
from .entity import ThaiEasyPassEntity


async def async_setup_entry(hass, entry, async_add_devices):
    """Set up the sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    sensors = []

    for card in coordinator.data:
        serial_number = card.get(KEY_SN)
        device_info = DeviceInfo(
            identifiers={(DOMAIN, serial_number)},
            manufacturer=MANUFACTURER,
            model=NAME,
            name=NAME,
        )

        for sensor_info in SENSORS.values():
            sensors.append(
                ThaiEasyPassSensor(
                    coordinator=coordinator,
                    device_info=device_info,
                    name=sensor_info[0],
                    key=sensor_info[1],
                    icon=sensor_info[2],
                    device_class=sensor_info[3],
                    native_unit_of_measurement=sensor_info[4],
                    serial_number=serial_number,
                )
            )
    async_add_devices(sensors)


class ThaiEasyPassSensor(ThaiEasyPassEntity, SensorEntity):
    """Sensor implementation."""

    def __init__(
        self,
        coordinator: ThaiEasyPassCoordinator,
        device_info: DeviceInfo,
        key: str,
        name: str,
        icon: str,
        device_class: SensorDeviceClass,
        native_unit_of_measurement,
        serial_number: str,
    ) -> None:
        """Initialize the sensor."""
        self._device_info = device_info
        self._key = key
        self._name = name
        self._icon = icon
        self._serial_number = serial_number
        self._device_class = device_class
        self._native_unit_of_measurement = native_unit_of_measurement
        super().__init__(coordinator)

    @property
    def unique_id(self) -> str:
        """Unique Id."""
        return f"thai_easy_pass_{self._key}_{self._serial_number}"

    @property
    def native_value(self) -> int:
        """Value."""
        return self.get_card().get(self._key)

    @property
    def native_unit_of_measurement(self) -> str:
        """Unit."""
        return self._native_unit_of_measurement

    @property
    def device_class(self) -> str:
        """Device class."""
        return self._device_class

    @property
    def name(self) -> str:
        """Name."""
        return self._name

    @property
    def icon(self) -> str | None:
        """Icon."""
        return self._icon

    @property
    def available(self) -> bool:
        """Available."""
        return True

    @property
    def device_info(self) -> DeviceInfo | None:
        """Device Info."""
        return self._device_info

    def get_card(self) -> {}:
        """Get the card."""
        for card in self.coordinator.data:
            if card.get(KEY_SN) == self._serial_number:
                return card
        return None
