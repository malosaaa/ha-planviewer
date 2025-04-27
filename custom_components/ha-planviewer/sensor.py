"""Sensor platform for Planviewer integration."""

import logging
from datetime import datetime

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.typing import StateType

from .const import DOMAIN, CONF_INSTANCE_NAME
from .coordinator import PlanviewerDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Planviewer sensors from config entry."""
    coordinator: PlanviewerDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    instance_name = entry.data[CONF_INSTANCE_NAME]
    municipality_name = entry.data["municipality"].upper().replace(" ", "_") # Get municipality and format for ID
    sensors = []
    if coordinator.data:
        for index, announcement in enumerate(coordinator.data):
            sensors.append(PlanviewerAnnouncementSensor(coordinator, instance_name, municipality_name, announcement, index))

    # Add diagnostic sensors
    sensors.extend([
        PlanviewerDiagnosticSensor(coordinator, instance_name, municipality_name, "last_update_status", "Last Update Status"),
        PlanviewerDiagnosticSensor(coordinator, instance_name, municipality_name, "last_update_time", "Coordinator Last Update", SensorDeviceClass.TIMESTAMP),
        PlanviewerDiagnosticSensor(coordinator, instance_name, municipality_name, "consecutive_errors", "Consecutive Update Errors"),
    ])

    async_add_entities(sensors)

class PlanviewerAnnouncementSensor(CoordinatorEntity[PlanviewerDataUpdateCoordinator], SensorEntity):
    """Representation of a Planviewer announcement sensor."""

    _attr_has_entity_name = False # We will construct the name

    def __init__(self, coordinator: PlanviewerDataUpdateCoordinator, instance_name: str, municipality_name: str, announcement: dict, index: int) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._instance_name = instance_name
        self._municipality_name = municipality_name
        self._announcement = announcement
        self._index = index
        announcement_title_slug = self._announcement.get('vergunning', 'announcement').lower().replace(" ", "_")
        self._attr_unique_id = f"{DOMAIN}_{self._municipality_name}_{coordinator.config_entry.entry_id}_{index + 1}_{announcement_title_slug}"
        self._attr_name = f"{self._municipality_name} {index + 1}"

    @property
    def device_info(self) -> dict:
        """Return the device info."""
        return {
            "identifiers": {
                (DOMAIN, self._instance_name),
            },
            "name": f"Planviewer ({self._instance_name})",
            "manufacturer": "Planviewer",
            "model": "Announcement Sensor",
        }

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor."""
        return self._announcement.get("vergunning")

    @property
    def extra_state_attributes(self) -> dict[str, any]:
        """Return the state attributes of the sensor."""
        attributes = {}
        for key in self._announcement:
            if key not in ["vergunning"]:
                attributes[key] = self._announcement.get(key)
        return attributes

class PlanviewerDiagnosticSensor(CoordinatorEntity[PlanviewerDataUpdateCoordinator], SensorEntity):
    """Representation of a Planviewer Diagnostic Sensor."""
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_has_entity_name = False

    def __init__(
        self,
        coordinator: PlanviewerDataUpdateCoordinator,
        instance_name: str,
        municipality_name: str,
        data_key: str,
        name: str,
        device_class: SensorDeviceClass | None = None
    ) -> None:
        """Initialize the diagnostic sensor."""
        super().__init__(coordinator)
        self._instance_name = instance_name # Store instance_name
        self._municipality_name = municipality_name # Store municipality_name
        self._data_key = data_key
        self._attr_unique_id = f"{DOMAIN}_{self._municipality_name}_{coordinator.config_entry.entry_id}_diag_{data_key}"
        self._attr_name = f"{coordinator.config_entry.data[CONF_INSTANCE_NAME]} {name}"
        self._attr_device_class = device_class

    @property
    def device_info(self) -> dict:
        """Return the device info."""
        return {
            "identifiers": {
                (DOMAIN, self._instance_name),
            },
            "name": f"Planviewer ({self._instance_name})",
            "manufacturer": "Planviewer",
            "model": "Diagnostic Sensor",
        }

    @property
    def native_value(self) -> StateType:
        """Return the state of the diagnostic sensor."""
        if self._data_key == "last_update_status":
            return "OK" if not self.coordinator.last_update_error else "Error"
        elif self._data_key == "last_update_time":
            return self.coordinator.last_update_success_timestamp
        elif self._data_key == "consecutive_errors":
            return self.coordinator.error_count
        return None

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator is not None