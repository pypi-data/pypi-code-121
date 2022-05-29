from amino.lib.util import device
import hmac
import base64
from hashlib import sha1
from uuid import uuid4
import requests
from uuid import uuid4
import requests_random_user_agent
def user():
    return str(uuid4())
sid = None
def sigg(data):
        key='f8e7a61ac3f725941e3ac7cae2d688be97f30b93'
        mac = hmac.new(bytes.fromhex(key), data.encode("utf-8"), sha1)
        digest = bytes.fromhex("42") + mac.digest()
        return base64.b64encode(digest).decode("utf-8")

def random_user():
        s = requests.Session()
        return s.headers['User-Agent']

class Headers:
    def __init__(self, data = None, type = None, deviceId: str = None, sig: str = None):
        if deviceId:
            dev = device.DeviceGenerator(deviceId=deviceId)
        else:
            dev = device.DeviceGenerator()

        headers = {
            "NDCDEVICEID": dev.device_id,
            "AUID": user(),
            "SMDEVICEID": user(),
            "Accept-Language": "en-US",
            "Content-Type": "application/json",
            "User-Agent": random_user(),
            "Host": "service.narvii.com",
            "Accept-Encoding": "gzip",
            "Connection": "Keep-Alive"
        }

        if data:
            #print(data)
            headers["Content-Length"] = str(len(data))
            signature=None
            try: signature=sigg(data)
            except: pass
            headers["NDC-MSG-SIG"] = signature
        if sid: headers["NDCAUTH"] = f"sid={sid}"
        if type: headers["Content-Type"] = type
        #if sig: headers["NDC-MSG-SIG"] = sig
        self.headers = headers
 
 
