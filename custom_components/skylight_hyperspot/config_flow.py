from __future__ import annotations

from homeassistant import config_entries
import voluptuous as vol

from .api import SkylightApiError, SkylightHyperspotApi
from .const import CONF_HOST, CONF_NAME, DOMAIN


class SkylightConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Skylight Hyperspot."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            host = user_input[CONF_HOST].strip()
            name = user_input[CONF_NAME].strip() or "Skylight Hyperspot"

            api = SkylightHyperspotApi(host, self.hass.helpers.aiohttp_client.async_get_clientsession(self.hass))
            try:
                await api.model()
            except SkylightApiError:
                errors["base"] = "cannot_connect"
            else:
                await self.async_set_unique_id(host)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=name,
                    data={CONF_HOST: host, CONF_NAME: name},
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST): str,
                    vol.Required(CONF_NAME, default="Skylight Hyperspot"): str,
                }
            ),
            errors=errors,
        )
