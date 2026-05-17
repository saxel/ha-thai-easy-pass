"""Thai Easy Pass API Client (member-thaieasypass.exat.co.th)."""
from __future__ import annotations

import asyncio
import json
import socket
from urllib.parse import quote

import aiohttp
import async_timeout
from bs4 import BeautifulSoup

from .const import (
    BASE_URL,
    CARD_LIST_REFERER,
    EASY_PASS_URL,
    KEY_ACCOUNT_NUMBER,
    KEY_BALANCE,
    KEY_CAR_COLOR,
    KEY_CAR_MODEL,
    KEY_CARD_NAME,
    KEY_LICENSE_PLATE,
    KEY_MFLOW_STATUS,
    KEY_OBU,
    KEY_REWARD_POINT,
    KEY_SN,
    KEY_TAG_STATUS,
    LOGGER,
    LOGIN_PAGE_URL,
    SIGNIN_URL,
    USER_AGENT,
)


class ThaiEasyPassApiClientError(Exception):
    """Exception to indicate a general API error."""


class ThaiEasyPassApiClientCommunicationError(ThaiEasyPassApiClientError):
    """Exception to indicate a communication error."""


class ThaiEasyPassApiClientAuthenticationError(ThaiEasyPassApiClientError):
    """Exception to indicate an authentication error."""


class _SessionExpired(Exception):
    """Internal signal: server returned a login page instead of JSON."""


class ThaiEasyPassApiClient:
    """Thai Easy Pass API Client."""

    def __init__(
        self,
        username: str,
        password: str,
        session: aiohttp.ClientSession,
    ) -> None:
        """Initialize the API Client."""
        self._username = username
        self._password = password
        self._session = session
        self._csrf_token: str | None = None

    async def async_get_data(self, login: bool = False) -> list[dict]:
        """Fetch the card list, logging in first if needed."""
        if login or self._csrf_token is None:
            await self.async_login()

        try:
            data = await self._fetch_cards()
        except _SessionExpired:
            LOGGER.debug("Session expired, re-logging in")
            await self.async_login()
            try:
                data = await self._fetch_cards()
            except _SessionExpired as exc:
                raise ThaiEasyPassApiClientAuthenticationError(
                    "Session expired and re-login did not restore access"
                ) from exc

        LOGGER.debug("Received %d cards", len(data))
        return data

    async def async_login(self) -> None:
        """Log into the new member portal."""
        LOGGER.debug("Fetching CSRF token from login page")
        html = await self._api_wrapper(
            method="get",
            url=LOGIN_PAGE_URL,
            headers={
                "Accept": "text/html,application/xhtml+xml",
                "User-Agent": USER_AGENT,
            },
        )
        token = _extract_csrf_token(html)
        if not token:
            raise ThaiEasyPassApiClientError("CSRF token not found on login page")
        self._csrf_token = token

        LOGGER.debug("Submitting login")
        body = (
            f"_token={quote(token, safe='')}"
            f"&user_name={quote(self._username, safe='')}"
            f"&password={quote(self._password, safe='')}"
        )
        text = await self._api_wrapper(
            method="post",
            url=SIGNIN_URL,
            raw_body=body,
            headers={
                "Accept": "*/*",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "Origin": BASE_URL,
                "Referer": LOGIN_PAGE_URL,
                "User-Agent": USER_AGENT,
                "X-Requested-With": "XMLHttpRequest",
            },
        )

        try:
            payload = json.loads(text)
        except json.JSONDecodeError as exc:
            raise ThaiEasyPassApiClientError(
                f"Unexpected login response: {text[:200]}"
            ) from exc

        if (
            payload.get("status") != "success"
            or payload.get("status_code") != 200
        ):
            msg = payload.get("message") or payload.get("status") or "login failed"
            raise ThaiEasyPassApiClientAuthenticationError(str(msg))

        if payload.get("mfa_flag", 0) != 0:
            raise ThaiEasyPassApiClientError(
                "Account requires MFA, which is not supported"
            )

    async def _fetch_cards(self) -> list[dict]:
        """Fetch the card list JSON and shape it for the coordinator."""
        if not self._csrf_token:
            raise ThaiEasyPassApiClientError("No CSRF token; login required")

        url = (
            f"{EASY_PASS_URL}?_token={quote(self._csrf_token, safe='')}&page=1"
        )
        text = await self._api_wrapper(
            method="get",
            url=url,
            headers={
                "Accept": "*/*",
                "Referer": CARD_LIST_REFERER,
                "User-Agent": USER_AGENT,
                "X-Requested-With": "XMLHttpRequest",
            },
        )

        stripped = text.lstrip()
        if not stripped.startswith(("{", "[")):
            raise _SessionExpired()

        try:
            payload = json.loads(text)
        except json.JSONDecodeError as exc:
            raise ThaiEasyPassApiClientError(
                f"Invalid card list response: {text[:200]}"
            ) from exc

        raw_cards = (
            payload.get("easyPassCardsData", {}).get("data", []) or []
        )
        return [_map_card(card) for card in raw_cards]

    async def _api_wrapper(
        self,
        method: str,
        url: str,
        raw_body: str | None = None,
        headers: dict | None = None,
    ) -> str:
        """Perform an HTTP request and return the body text."""
        try:
            async with async_timeout.timeout(15):
                response = await self._session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    data=raw_body,
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
        except ThaiEasyPassApiClientError:
            raise
        except Exception as exception:  # noqa: BLE001
            raise ThaiEasyPassApiClientError(
                "Something really wrong happened!"
            ) from exception


def _extract_csrf_token(html: str) -> str | None:
    """Pull the Laravel CSRF token out of the login page HTML."""
    soup = BeautifulSoup(html, "html.parser")
    meta = soup.find("meta", attrs={"name": "csrf-token"})
    if meta and meta.get("content"):
        return meta["content"]
    hidden = soup.find("input", attrs={"name": "_token"})
    if hidden and hidden.get("value"):
        return hidden["value"]
    return None


def _map_card(card: dict) -> dict:
    """Map a card record from the new JSON shape to the coordinator's keys."""
    raw_balance = card.get("AC_Balance")
    try:
        balance = float(raw_balance) if raw_balance not in (None, "") else 0.0
    except (TypeError, ValueError):
        balance = 0.0

    raw_reward = card.get("Reward_Point")
    try:
        reward = int(raw_reward) if raw_reward not in (None, "") else 0
    except (TypeError, ValueError):
        reward = 0

    plate_no = (card.get("PlateNo") or "").strip()
    plate_province = (card.get("PlateProvince") or "").strip()
    if plate_no and plate_province:
        license_plate = f"{plate_no} {plate_province}"
    else:
        license_plate = plate_no or plate_province

    plus_data = card.get("easyPassPlusData") or {}

    return {
        KEY_SN: card.get("SmartcardID", ""),
        KEY_OBU: card.get("PAN_NUM", ""),
        KEY_BALANCE: balance,
        KEY_CARD_NAME: card.get("CardName") or "",
        KEY_CAR_MODEL: card.get("CarModel") or "",
        KEY_CAR_COLOR: card.get("CarColor") or "",
        KEY_LICENSE_PLATE: license_plate,
        KEY_REWARD_POINT: reward,
        KEY_TAG_STATUS: card.get("TagStatusText") or "",
        KEY_MFLOW_STATUS: plus_data.get("mflowStatus") or "",
        KEY_ACCOUNT_NUMBER: card.get("AccountNumber") or "",
    }
