import json
import random
import string
from .util import c, s, uu

uid = None
sid = None
deviceId = None
lang = None


class Headers:
    def __init__(self, data=None):
        if deviceId: self.deviceId = deviceId
        else: self.deviceId = c()

        self.headers = {
            "NDCDEVICEID": self.deviceId,
            "AUID": uu(),
            "SMDEVICEID": uu(),
            "Content-Type": "application/json; charset=utf-8",
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 7.1.2; SM-N975F Build/samsung-user 7.1.2 2; com.narvii.amino.master/3.4.33602)",
            "Host": "service.narvii.com",
            "Accept-Encoding": "gzip",
            "Connection": "Upgrade"
        }
        self.web_headers = {
            "accept": "*/*",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "ar,en-US;q=0.9,en;q=0.8",
            "content-type": "application/json",
            "sec-ch-ua": '"Google Chrome";v="93", " Not;A Brand";v="99", "Chromium";v="93"',
            "x-requested-with": "xmlhttprequest"
        }

        if sid:
            self.headers["NDCAUTH"] = sid
            self.web_headers["cookie"] = sid

        if uid:
            self.uid = uid

        if data:
            self.headers["Content-Length"] = str(len(data))
            if type(data) is not str: data = json.dumps(data)
            self.headers["NDC-MSG-SIG"] = s(data)

        if lang:
            self.headers.update({"NDCLANG": lang[:lang.index("-")], "Accept-Language": lang})


class AdHeaders:
    def __init__(self, userId: str = None):
        self.data = {
            "reward": {
                "ad_unit_id": "t00_tapjoy_android_master_checkinwallet_rewardedvideo_322",
                "credentials_type": "publisher",
                "custom_json": {
                    "hashed_user_id": userId
                },
                "demand_type": "sdk_bidding",
                "event_id": uu(),
                "network": "tapjoy",
                "placement_tag": "default",
                "reward_name": "Amino Coin",
                "reward_valid": True,
                "reward_value": 2,
                "shared_id": "6d6ee5da-da10-43b0-9883-8d3dd5bea928",
                "version_id": "1563565882",
                "waterfall_id": "6d6ee5da-da10-43b0-9883-8d3dd5bea928"
            },
            "app": {
                "bundle_id": "com.narvii.amino.master",
                "current_orientation": "portrait",
                "release_version": "3.4.33602",
                "user_agent": "Dalvik/2.1.0 (Linux; U; Android 7.1.2; SM-N975F Build/samsung-user 7.1.2 2; com.narvii.amino.master/3.4.33602)"
            },
            "device_user": {
                "country": "TR",
                "device": {
                    "architecture": "i686",
                    "carrier": {
                        "country_code": 286,
                        "name": "Vodafone-Telsim",
                        "network_code": 0
                    },
                    "is_phone": True,
                    "model": "SM-N975F",
                    "model_type": "Samsung",
                    "operating_system": "android",
                    "operating_system_version": "25",
                    "screen_size": {
                        "height": 1280,
                        "resolution": 1.5,
                        "width": 720
                    }
                },
                "do_not_track": False,
                "idfa": "0dee8541-fc6b-474b-970e-54e341f04719",
                "ip_address": "",
                "locale": "ar",
                "timezone": {
                    "location": "Asia\/Turkey",
                    "offset": "GMT+03:00"
                },
                "volume_enabled": True
            },
            "session_id": "6ee4373f-ecc9-4d05-b1fe-8c73ee8d3a9d",
            "date_created": 1633283996
        }
        self.headers = {
            "authorization": "Basic NWJiNTM0OWUxYzlkNDQwMDA2NzUwNjgwOmM0ZDJmYmIxLTVlYjItNDM5MC05MDk3LTkxZjlmMjQ5NDI4OA==",
            "X-Tapdaq-SDK-Version": "android-sdk_7.1.1",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 7.1.2; SM-N975F Build/samsung-user 7.1.2 2; com.narvii.amino.master/3.4.33602)",
            "Host": "ads.tapdaq.com"
        }
