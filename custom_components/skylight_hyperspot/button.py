from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import SkylightApiError, SkylightHyperspotApi
from .const import CONF_NAME, DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    api: SkylightHyperspotApi = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([SkylightHyperspotAutoButton(api, entry)])


class SkylightHyperspotAutoButton(ButtonEntity):
    """Button to send the currently known auto/resume command."""

    _attr_has_entity_name = True
    _attr_name = "Auto / Zeitplan"

    def __init__(self, api: SkylightHyperspotApi, entry: ConfigEntry) -> None:
        self.api = api
        self.entry = entry
        name = entry.data[CONF_NAME]
        self._attr_unique_id = f"{entry.entry_id}_auto_button"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": name,
            "manufacturer": "Skylight",
            "model": "Hyperspot",
        }
        self._attr_available = True

    async def async_press(self) -> None:
        try:
            await self.api.auto()
        except SkylightApiError:
            self._attr_available = False
        else:
            self._attr_available = True
        self.async_write_ha_state()
