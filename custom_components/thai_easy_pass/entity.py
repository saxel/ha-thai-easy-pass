"""Thai Easy Pass Entity class."""
from __future__ import annotations

from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import ThaiEasyPassCoordinator


class ThaiEasyPassEntity(CoordinatorEntity):
    """ThaiEasyPassEntity class."""

    def __init__(self, coordinator: ThaiEasyPassCoordinator) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self._attr_unique_id = coordinator.config_entry.entry_id
