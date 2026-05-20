from __future__ import annotations

import asyncio
from typing import Any

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_COLOR_TEMP_KELVIN,
    ColorMode,
    LightEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import SkylightApiError, SkylightHyperspotApi
from .const import (
    CONF_NAME,
    DEFAULT_BRIGHTNESS,
    DEFAULT_KELVIN,
    DOMAIN,
    MAX_KELVIN,
    MIN_KELVIN,
)

SEND_DELAY = 0.25


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    api: SkylightHyperspotApi = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([SkylightHyperspotLight(api, entry)])


class SkylightHyperspotLight(LightEntity):
    """Skylight Hyperspot light entity."""

    _attr_has_entity_name = True
    _attr_name = None
    _attr_supported_color_modes = {ColorMode.COLOR_TEMP}
    _attr_color_mode = ColorMode.COLOR_TEMP
    _attr_min_color_temp_kelvin = MIN_KELVIN
    _attr_max_color_temp_kelvin = MAX_KELVIN

    def __init__(self, api: SkylightHyperspotApi, entry: ConfigEntry) -> None:
        self.api = api
        self.entry = entry
        name = entry.data[CONF_NAME]
        self._attr_unique_id = f"{entry.entry_id}_light"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": name,
            "manufacturer": "Skylight",
            "model": "Hyperspot",
        }
        self._attr_is_on = False
        self._attr_brightness = DEFAULT_BRIGHTNESS
        self._attr_color_temp_kelvin = DEFAULT_KELVIN
        self._send_task: asyncio.Task | None = None

    @property
    def available(self) -> bool:
        return True

    def _kelvin_to_mix(self, kelvin: int) -> int:
        """Map Kelvin to the app-like mix slider.

        0 = cold, 50 = both 100%, 100 = warm.
        Low Kelvin should be warm, high Kelvin should be cold.
        """
        kelvin = max(MIN_KELVIN, min(MAX_KELVIN, kelvin))
        # MIN_KELVIN -> 100 warm, MAX_KELVIN -> 0 cold
        return round((MAX_KELVIN - kelvin) / (MAX_KELVIN - MIN_KELVIN) * 100)

    def _calculate_values(self) -> tuple[int, int]:
        brightness = self._attr_brightness or 0
        intensity = brightness / 255
        mix = self._kelvin_to_mix(self._attr_color_temp_kelvin or DEFAULT_KELVIN)

        if mix <= 50:
            cold_percent = 100
            warm_percent = round((mix / 50) * 100)
        else:
            cold_percent = round(((100 - mix) / 50) * 100)
            warm_percent = 100

        cold = round(cold_percent / 100 * 10000 * intensity)
        warm = round(warm_percent / 100 * 10000 * intensity)
        return cold, warm

    async def _delayed_send(self) -> None:
        await asyncio.sleep(SEND_DELAY)
        cold, warm = self._calculate_values()
        try:
            await self.api.set_manual(cold, warm)
        except SkylightApiError:
            self._attr_available = False
        else:
            self._attr_available = True
        self.async_write_ha_state()

    def _schedule_send(self) -> None:
        if self._send_task and not self._send_task.done():
            self._send_task.cancel()
        self._send_task = asyncio.create_task(self._delayed_send())

    async def async_turn_on(self, **kwargs: Any) -> None:
        if ATTR_BRIGHTNESS in kwargs:
            self._attr_brightness = kwargs[ATTR_BRIGHTNESS]
        elif not self._attr_brightness:
            self._attr_brightness = DEFAULT_BRIGHTNESS

        if ATTR_COLOR_TEMP_KELVIN in kwargs:
            self._attr_color_temp_kelvin = kwargs[ATTR_COLOR_TEMP_KELVIN]

        self._attr_is_on = True
        self.async_write_ha_state()
        self._schedule_send()

    async def async_turn_off(self, **kwargs: Any) -> None:
        if self._send_task and not self._send_task.done():
            self._send_task.cancel()
        self._attr_is_on = False
        self.async_write_ha_state()
        try:
            await self.api.turn_off()
        except SkylightApiError:
            self._attr_available = False
        else:
            self._attr_available = True
        self.async_write_ha_state()
