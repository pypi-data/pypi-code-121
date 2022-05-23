import asyncio
import codecs
import hashlib
import hmac
import json
import math
import secrets
import time
import uuid

import aiohttp
from aiohttp import ClientSession, TCPConnector

import topgreenerapi.device
from . import util
from .models import location, tuya_device, meta_schema
from .exceptions import TuyaException
from topgreenerapi.models.location import Location
from .logger import logger
from .models.meta_schema import MetaSchema


class TopgreenerCloud:
    API_VERSION = "0.0.1"
    APP_VERSION = "3.8.5"

    def __init__(self, client_id, app_secret, super_secret, app_certhash, device_id=None, region='AZ'):
        self.client_id = client_id
        self.app_secret = app_secret
        self.super_secret = super_secret
        self.app_certhash = app_certhash
        self.sid = None
        self.session = ClientSession(connector=TCPConnector())

        self.keyHmac = self.app_certhash + '_' + self.super_secret + '_' + self.app_secret

        if device_id is None:
            self.device_id = secrets.token_hex(44)
        else:
            self.device_id = device_id

        if region == 'AZ':
            self.region = 'AZ'
            self.endpoint = 'https://a1.tuyaus.com/api.json'
        elif region == 'AY':
            self.region = 'AY'
            self.endpoint = 'https://a1.tuyacn.com/api.json'
        elif region == 'EU':
            self.region = 'EU'
            self.endpoint = 'https://a1.tuyaeu.com/api.json'
        else:
            raise ValueError('Bad region identifier')

    def mobileHash(self, data):
        preHash = hashlib.md5(data.encode('utf-8')).hexdigest()

        return preHash[8:16] + preHash[0:8] + preHash[24:32] + preHash[16:24]

    def signMessage(self, key, strToSign):
        return hmac.new(codecs.encode(key), msg=codecs.encode(strToSign),
                        digestmod=hashlib.sha256).hexdigest()

    async def sendRequest(self, action, data=None, gid=None, requiresSID=True, version="1.0"):

        if self.sid is None and requiresSID:
            raise ValueError('You must call login() first!')

        d = str(int(time.time()))
        params = {
            "a": action,
            "deviceId": self.device_id,
            "os": 'Linux',
            "lang": 'en',
            "v": version,
            "clientId": self.client_id,
            "requestId": str(uuid.uuid4()),
            "time": d
        }

        if data is not None:
            logger.debug('Data is %s', data)
            params["postData"] = json.dumps(data)

        if gid is not None:
            params["gid"] = gid

        params["et"] = self.API_VERSION
        params["ttid"] = 'tuya'
        params["appVersion"] = self.APP_VERSION

        if requiresSID:
            params["sid"] = self.sid

        valuesToSign = ['a', 'v', 'lat', 'lon', 'lang', 'deviceId', 'imei',
                        'imsi', 'appVersion', 'ttid', 'isH5', 'h5Token', 'os',
                        'clientId', 'postData', 'time', 'requestId', 'n4h5', 'sid',
                        'sp', 'et']

        sortedPairs = util.order_dict(params)

        strToSign = ''

        for key in sortedPairs:
            if key not in valuesToSign or not params[key]:
                continue
            elif key == 'postData':
                if strToSign:
                    strToSign += '||'
                strToSign += key
                strToSign += '='
                strToSign += self.mobileHash(params[key])
            else:
                if strToSign:
                    strToSign += '||'
                strToSign += key
                strToSign += '='
                strToSign += params[key]

        params["sign"] = self.signMessage(self.keyHmac, strToSign)

        try:
            logger.debug("Sending parameters: %s", params)

            async with self.session.post(self.endpoint, data=params) as resp:
                data = await resp.json()
                logger.debug("Received response: %s", data)

                if "success" not in data or data["success"] is False:
                    raise TuyaException("Request unsuccessful! Params: " + data["errorCode"] + " " + data["errorMsg"])

                return data["result"]

        except aiohttp.ClientError as e:
            logger.error("Error occured! %s", e)
            raise e

    async def get_locations(self) -> list[Location]:
        locations = []
        groups = await self.sendRequest('tuya.m.location.list')
        for group in groups:
            result = location.location_from_dict(group)
            locations.append(result)

        return locations

    async def get_devices(self, locationId) -> list[topgreenerapi.device.Device]:
        devschemas: dict[str, MetaSchema] = {}
        schem = await self.sendRequest('tuya.m.device.ref.info.my.list', gid=locationId)
        schemas = meta_schema.meta_schema_from_dict(schem)
        for dev in schemas:
            devschemas[dev.id] = dev
        deviceArr = await self.sendRequest('tuya.m.my.group.device.list', gid=locationId)

        devices: list[topgreenerapi.device.Device] = []
        for devi in deviceArr:
            tuyaDevice = tuya_device.tuya_device_from_dict(devi)
            device = topgreenerapi.device.Device(tuyaDevice.name, tuyaDevice.dev_id, locationId, tuyaDevice, self)
            device.set_schema(devschemas[tuyaDevice.product_id])
            devices.append(device)

        return devices

    async def register(self, email, password):
        try:
            apiResult = await self.sendRequest('tuya.m.user.email.register',
                                               data={
                                                   "countryCode": self.region,
                                                   "email": email,
                                                   "passwd": hashlib.md5(password).hexdigest()
                                               }, requiresSID=False)
            self.sid = apiResult["sid"]
            return self.sid
        except TuyaException as e:
            if e.errorCode == 'USER_NAME_IS_EXIST':
                return self.login(email, password)

            raise e

    async def login(self, email, password):
        try:
            token = await self.sendRequest('tuya.m.user.email.token.create',
                                           data={
                                               "countryCode": self.region,
                                               "email": email
                                           }, requiresSID=False)

            input = str.encode(hashlib.md5(password.encode('utf-8')).hexdigest())
            e = int(token["exponent"])
            n = int(token["publicKey"])

            keylength = math.ceil(n.bit_length() / 8)
            input_nr = int.from_bytes(input, byteorder='big')
            crypted_nr = pow(input_nr, e, n)
            crypted_data = crypted_nr.to_bytes(keylength, byteorder='big').hex()

            apiResult = await self.sendRequest('tuya.m.user.email.password.login',
                                               data={
                                                   "countryCode": self.region,
                                                   "email": email,
                                                   "passwd": crypted_data,
                                                   "ifencrypt": 1,
                                                   "options": {"group": 1},
                                                   "token": token["token"]
                                               }, requiresSID=False)

            if apiResult["domain"] and apiResult["domain"]["mobileApiUrl"] and not self.endpoint.startswith(
                    apiResult["domain"]["mobileApiUrl"]):
                logger.debug("Changing endpoints after logging: %s -> %s/api.json",
                             self.endpoint, apiResult["domain"]["mobileApiUrl"])

                self.endpoint = apiResult["domain"]["mobileApiUrl"] + '/api.json'
                self.region = apiResult["domain"]["regionCode"]

            self.sid = apiResult["sid"]
            return self.sid
        except Exception as e:
            logger.error("Error while logging in! Trace: %s", e)
            raise e

    async def close(self):
        if self.session:
            await self.session.close()

    async def waitForToken(self, token, devices=1):
        SLEEP_DURATION = 200e-3
        for x in range(200):
            try:
                tokenResult = await self.sendRequest('tuya.m.device.list.token',
                                                     data={
                                                         "token": token
                                                     })

                if tokenResult.length >= devices:
                    return tokenResult

                # wait 200ms and check again
                await asyncio.sleep(SLEEP_DURATION)
            except Exception as e:
                logger.error("Error while waiting for device registration! Stack: %s", e)
                raise e

        raise ValueError("Timed out waiting for device(s) to connect to cloud")
