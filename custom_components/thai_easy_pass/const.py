"""Constants for Thai Easy Pass integration."""
from logging import Logger, getLogger
from homeassistant.components.sensor import SensorDeviceClass

LOGGER: Logger = getLogger(__package__)

NAME = "Thai Easy Pass"
MANUFACTURER = "EXAT"
DOMAIN = "thai_easy_pass"
VERSION = "1.0.0"

SIGNIN_URL = "https://www.thaieasypass.com/th/member/signin"
EASY_PASS_URL = "https://www.thaieasypass.com/th/easypass/smartcard"

# How often to poll for updates (in minutes)
UPDATE_INTERVAL = 30

KEY_SN = "serial_number"
KEY_OBU = "obu"
KEY_BALANCE = "balance"

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
