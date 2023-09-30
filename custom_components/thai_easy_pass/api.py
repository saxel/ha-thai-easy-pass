from __future__ import annotations

import asyncio
import socket

import aiohttp
import async_timeout

from bs4 import BeautifulSoup

from .const import (
    SIGNIN_URL,
    LOGGER,
    KEY_SN,
    KEY_OBU,
    KEY_BALANCE,
    ATTR_SN,
    ATTR_BALANCE,
    ATTR_OBU,
    EASY_PASS_URL,
)


class ThaiEasyPassApiClientError(Exception):
    """Exception to indicate a general API error."""


class ThaiEasyPassApiClientCommunicationError(ThaiEasyPassApiClientError):
    """Exception to indicate a communication error."""


class ThaiEasyPassApiClientAuthenticationError(ThaiEasyPassApiClientError):
    """Exception to indicate an authentication error."""


class ThaiEasyPassApiClient:
    """Thai Easy Pass API Client."""

    def __init__(
        self,
        username: str,
        password: str,
        session: aiohttp.ClientSession,
    ) -> None:
        self._username = username
        self._password = password
        self._session = session

    async def async_get_data(self, login=False) -> any:
        """Get data from the API."""
        data = await self._async_get_data(login)

        if not login and not data:
            data = await self._async_get_data(True)
        return data

    async def _async_get_data(self, login=False) -> any:
        """Get data from the API."""
        if login:
            await self.async_login()

        content = await self._api_wrapper(method="get", url=EASY_PASS_URL)

        soup = BeautifulSoup(content, "html.parser")
        table = soup.find("table")

        if not table:
            return []

        # Get table headers
        headers = []
        header_tr = table.find("tr", class_="head-table")
        for td in header_tr.find_all("td"):
            headers.append(td.text.strip())

        # Get devices from table
        devices = []
        for device_tr in header_tr.find_next_siblings("tr"):
            device = {}
            for i, td in enumerate(device_tr.find_all("td")):
                device[headers[i]] = td.text.strip()
            devices.append(device)

        return [
            {
                KEY_SN: device[ATTR_SN],
                KEY_OBU: device[ATTR_OBU],
                KEY_BALANCE: device[ATTR_BALANCE],
            }
            for device in devices
        ]

    async def async_login(self) -> any:
        """Login"""
        LOGGER.debug("Trying to login")
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = f"email={self._username}&password={self._password}"
        await self._session.post(SIGNIN_URL, data=data, headers=headers)

    async def _api_wrapper(
        self,
        method: str,
        url: str,
        data: dict | None = None,
        headers: dict | None = None,
    ) -> any:
        """Get information from the API."""
        try:
            async with async_timeout.timeout(10):
                response = await self._session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data,
                )
                if response.status in (401, 403):
                    raise ThaiEasyPassApiClientAuthenticationError(
                        "Invalid credentials",
                    )
                response.raise_for_status()
                return await response.text()

        except asyncio.TimeoutError as exception:
            raise ThaiEasyPassApiClientCommunicationError(
                "Timeout error fetching information"
            ) from exception
        except (aiohttp.ClientError, socket.gaierror) as exception:
            raise ThaiEasyPassApiClientCommunicationError(
                "Error fetching information"
            ) from exception
        except Exception as exception:
            raise ThaiEasyPassApiClientError(
                "Something really wrong happened!"
            ) from exception
