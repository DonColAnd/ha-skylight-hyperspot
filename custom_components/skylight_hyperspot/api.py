from __future__ import annotations

import asyncio
from dataclasses import dataclass

from aiohttp import ClientError, ClientSession

from .const import AUTO_COMMAND, DEFAULT_TIMEOUT


class SkylightApiError(Exception):
    """Raised when the Skylight Hyperspot cannot be reached."""


@dataclass
class SkylightHyperspotApi:
    """Small local HTTP API client for Skylight Hyperspot."""

    host: str
    session: ClientSession
    timeout: int = DEFAULT_TIMEOUT

    @property
    def base_url(self) -> str:
        return f"http://{self.host}"

    async def _get(self, params: str) -> str:
        url = f"{self.base_url}/scheduleSettings"
        try:
            async with asyncio.timeout(self.timeout):
                response = await self.session.get(url, params={"params": params})
                text = await response.text()
                response.raise_for_status()
                return text
        except (TimeoutError, ClientError) as err:
            raise SkylightApiError(str(err)) from err

    async def set_manual(self, cold: int, warm: int) -> str:
        cold = max(0, min(10000, int(cold)))
        warm = max(0, min(10000, int(warm)))
        return await self._get(f"h_2_{cold}_{warm}:")

    async def turn_off(self) -> str:
        return await self.set_manual(0, 0)

    async def auto(self) -> str:
        # Known command from reverse engineering: returns "Lamp is turned on."
        return await self._get(AUTO_COMMAND)

    async def firmware(self) -> str:
        return await self._get("n")

    async def model(self) -> str:
        return await self._get("o")
