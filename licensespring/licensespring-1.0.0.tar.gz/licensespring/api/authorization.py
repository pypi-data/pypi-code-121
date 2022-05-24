import base64
import hashlib
import hmac
import time
from wsgiref.handlers import format_date_time


def date_header_value():
    return format_date_time(time.time())


def autorization_headers(api_key, shared_key):
    date_header = date_header_value()

    msg = "licenseSpring\ndate: {}".format(date_header)
    hashed = hmac.new(
        bytes(shared_key, "utf-8"), msg.encode("utf-8"), hashlib.sha256
    ).digest()
    signature = base64.b64encode(hashed).decode()
    auth = [
        'algorithm="hmac-sha256"',
        'headers="date"',
        'signature="{}"'.format(signature),
        'apiKey="{}"'.format(api_key),
    ]
    authorization = ",".join(auth)

    return {"Date": date_header, "Authorization": authorization}


def offline_signature(
    api_key, shared_key, hardware_id, license_key=None, username=None
):
    date_header = date_header_value()
    msg = "licenseSpring\ndate: {}\n{}\n{}\n{}".format(
        date_header, license_key if license_key else username, hardware_id, api_key
    )
    hashed = hmac.new(
        bytes(shared_key, "utf-8"), msg.encode("utf-8"), hashlib.sha256
    ).digest()
    signature = base64.b64encode(hashed).decode()
    return signature
