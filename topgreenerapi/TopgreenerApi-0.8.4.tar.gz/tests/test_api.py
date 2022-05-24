import os
import unittest
from topgreenerapi import logger
from topgreenerapi import api


class TestApi(unittest.IsolatedAsyncioTestCase):

    def test_message_sign(self):
        key = os.environ["TOPGREENER_key"]
        app_secret = os.environ["TOPGREENER_appsecret"]
        super_secret = os.environ["TOPGREENER_secretkey"]
        app_certhash = os.environ["TOPGREENER_certhash"]
        expectedKey = app_certhash + '_' + super_secret + '_' + app_secret
        api1 = api.TopgreenerCloud(key, app_secret, super_secret, app_certhash)
        toSign = "a=tuya.m.my.group.device.sort.list||appVersion=1.1.1||clientId=uadkfvsv7tpgch9nes7w||deviceId" \
                 "=897757a2214f073ad418da57de36ec408c0b590c8eaa||et=3||lang=en_US||os=Android||postData" \
                 "=d8f5ef5c4e93bfd57fd181e3aa42619f||requestId=46f37579-5bf0-4984-a459-b2d99d50086d||sid" \
                 "=az163879O484027533sYsru32747f67adfaf786dbfb55a2c2541410b||time=1652816648||ttid" \
                 "=sdk_tuya_international@uadkfvsv7tpgch9nes7w||v=1.0"
        expectedSig = "c777ed075a5dd77ccb5645ec445434a3f4d78ec0886034128601de89dda607c7"
        result = api1.signMessage(expectedKey, toSign)
        self.assertEqual(expectedSig, result, 'Signatures did not match expected!')

        toSign = "a=tuya.m.device.product.ref.list||appVersion=1.1.1||clientId=uadkfvsv7tpgch9nes7w||deviceId" \
                 "=897757a2214f073ad418da57de36ec408c0b590c8eaa||et=3||lang=en_US||os=Android||postData" \
                 "=a24b99ff264fca06eca28c2fe0cca478||requestId=4b502814-7d21-42c1-abf8-4a14155872b8||sid" \
                 "=az163879O484027533sYsru32747f67adfaf786dbfb55a2c2541410b||time=1652816648||ttid" \
                 "=sdk_tuya_international@uadkfvsv7tpgch9nes7w||v=1.0"
        expectedSig = "73c690d4074559dc067c45ead09e7e0bb2569a61b88c023ac87fda7358593e68"
        result = api1.signMessage(expectedKey, toSign)
        self.assertEqual(expectedSig, result, 'Signatures did not match expected!')

    async def test_login(self):
        SLEEP_DURATION = 5
        key = os.environ["TOPGREENER_key"]
        app_secret = os.environ["TOPGREENER_appsecret"]
        super_secret = os.environ["TOPGREENER_secretkey"]
        app_certhash = os.environ["TOPGREENER_certhash"]
        api1 = api.TopgreenerCloud(key, app_secret, super_secret, app_certhash)
        sid = await api1.login(os.environ["TOPGREENER_username"], os.environ["TOPGREENER_password"])
        groups = await api1.sendRequest('tuya.m.location.list')
        for group in groups:
            logger.debug("group: %s", group)
            schema = await api1.sendRequest('tuya.m.device.ref.info.my.list', gid=group["groupId"])
            logger.debug("schema!!!!: %s", schema)
            deviceArr = await api1.sendRequest('tuya.m.my.group.device.list', gid=group["groupId"])
            logger.debug("devices: %s", deviceArr)
            for device in deviceArr:
                logger.debug("device data: %s", device)
                logger.debug("group %s device %s devId %s", group["name"], device["name"], device["devId"])

        await api1.close()

    async def test_api_get_dev(self):
        key = os.environ["TOPGREENER_key"]
        app_secret = os.environ["TOPGREENER_appsecret"]
        super_secret = os.environ["TOPGREENER_secretkey"]
        app_certhash = os.environ["TOPGREENER_certhash"]
        api1 = api.TopgreenerCloud(key, app_secret, super_secret, app_certhash)
        sid = await api1.login(os.environ["TOPGREENER_username"], os.environ["TOPGREENER_password"])

        logger.debug("Now fetching locations..")
        locations = await api1.get_locations()
        logger.debug("Locations are %s", locations)

        for location in locations:
            logger.debug("Now fetching devices..")
            devices = await api1.get_devices(location.group_id)
            logger.debug("Devices are: %s", devices)

            for device in devices:
                logger.debug("Device %s capabilities: %s", device.name, device.get_capabilities())

        await api1.close()

    async def test_api_dev_type(self):
        key = os.environ["TOPGREENER_key"]
        app_secret = os.environ["TOPGREENER_appsecret"]
        super_secret = os.environ["TOPGREENER_secretkey"]
        app_certhash = os.environ["TOPGREENER_certhash"]
        api1 = api.TopgreenerCloud(key, app_secret, super_secret, app_certhash)
        sid = await api1.login(os.environ["TOPGREENER_username"], os.environ["TOPGREENER_password"])

        logger.debug("Now fetching locations..")
        locations = await api1.get_locations()
        logger.debug("Locations are %s", locations)

        for location in locations:
            logger.debug("Now fetching devices..")
            devices = await api1.get_devices(location.group_id)
            logger.debug("Devices are: %s", devices)

            for device in devices:
                logger.debug("Device %s capabilities: %s", device.name, device.get_capabilities())
                logger.debug("Device %s is of type: %s", device.name, device.dev_type.get_device_types())
                logger.debug("Reloading device... %s", device.name)

                if device.name == 'Loft':
                    await device.set_power_state(True)
                    self.assertEqual(device.get_power_state(), True, "Power state should be assumed true")

                    await device.update_device_status()
                    self.assertEqual(device.get_power_state(), True, "Power state should be assumed true")

        await api1.close()


if __name__ == '__main__':
    unittest.main()
