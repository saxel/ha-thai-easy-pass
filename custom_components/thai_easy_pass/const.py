"""Constants for Thai Easy Pass integration."""
from logging import Logger, getLogger
from homeassistant.components.sensor import SensorDeviceClass

LOGGER: Logger = getLogger(__package__)

NAME = "Thai Easy Pass (member.exat.co.th)"
MANUFACTURER = "EXAT"
DOMAIN = "thai_easy_pass"
VERSION = "0.1.0"

# New EasyPass member portal (member-thaieasypass.exat.co.th).
BASE_URL = "https://member-thaieasypass.exat.co.th"
LOGIN_PAGE_URL = f"{BASE_URL}/"
SIGNIN_URL = f"{BASE_URL}/eservice/login"
EASY_PASS_URL = f"{BASE_URL}/eservice/easypasscardlist/get-all"
CARD_LIST_REFERER = f"{BASE_URL}/eservice/easypasscardlist"

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36"
)

# How often to poll for updates (in minutes)
UPDATE_INTERVAL = 30

KEY_SN = "serial_number"
KEY_OBU = "obu"
KEY_BALANCE = "balance"

# Legacy attribute labels (kept for backward-compat references in code).
ATTR_OBU = "หมายเลข OBU"
ATTR_SN = "เลขสมาร์ทการ์ด (S/N)"
ATTR_BALANCE = "จำนวนเงิน"

SENSORS = {
    ATTR_BALANCE: [
        "Balance",
        KEY_BALANCE,
        "mdi:currency-thb",
        SensorDeviceClass.MONETARY,
        "THB",
    ],
    ATTR_SN: ["Serial number", KEY_SN, "mdi:identifier", None, None],
    ATTR_OBU: ["OBU", KEY_OBU, "mdi:barcode", None, None],
}
