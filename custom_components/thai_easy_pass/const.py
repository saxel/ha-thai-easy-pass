"""Constants for Thai Easy Pass integration."""
from logging import Logger, getLogger
from homeassistant.components.sensor import SensorDeviceClass

LOGGER: Logger = getLogger(__package__)

NAME = "Thai Easy Pass (member.exat.co.th)"
MANUFACTURER = "EXAT"
DOMAIN = "thai_easy_pass"
VERSION = "0.2.0"

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
KEY_CARD_NAME = "card_name"
KEY_CAR_MODEL = "car_model"
KEY_CAR_COLOR = "car_color"
KEY_LICENSE_PLATE = "license_plate"
KEY_REWARD_POINT = "reward_point"
KEY_TAG_STATUS = "tag_status"
KEY_MFLOW_STATUS = "mflow_status"
KEY_ACCOUNT_NUMBER = "account_number"

# Legacy attribute labels (kept for backward-compat references in code).
ATTR_OBU = "หมายเลข OBU"
ATTR_SN = "เลขสมาร์ทการ์ด (S/N)"
ATTR_BALANCE = "จำนวนเงิน"

# Sensor descriptors: [display_name, state_key, icon, device_class, unit,
#                     optional [(attribute_label, attribute_key), ...]]
SENSORS = {
    ATTR_BALANCE: [
        "Balance",
        KEY_BALANCE,
        "mdi:currency-thb",
        SensorDeviceClass.MONETARY,
        "THB",
        [("Account Number", KEY_ACCOUNT_NUMBER), ("Car Color", KEY_CAR_COLOR)],
    ],
    ATTR_SN: ["Serial number", KEY_SN, "mdi:identifier", None, None],
    ATTR_OBU: ["OBU", KEY_OBU, "mdi:barcode", None, None],
    "reward_point": [
        "Reward Point",
        KEY_REWARD_POINT,
        "mdi:gift",
        None,
        None,
    ],
    "license_plate": [
        "License Plate",
        KEY_LICENSE_PLATE,
        "mdi:car-info",
        None,
        None,
    ],
    "tag_status": [
        "Tag Status",
        KEY_TAG_STATUS,
        "mdi:card-account-details",
        None,
        None,
    ],
    "mflow_status": [
        "M-Flow Status",
        KEY_MFLOW_STATUS,
        "mdi:gate-arrow-right",
        None,
        None,
    ],
}
