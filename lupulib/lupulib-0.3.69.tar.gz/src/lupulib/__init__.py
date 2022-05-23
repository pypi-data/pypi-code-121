# SYS imports
import os
import sys
from trace import Trace

# Append subdirectories to sys.path
ppath = os.path.abspath(os.path.join(os.path.dirname(__file__),os.pardir))
print(ppath)
qpath = os.path.dirname(__file__)
print(qpath)
fpath = os.path.join(os.path.dirname(__file__), 'devices')
sys.path.append(qpath)
sys.path.append(fpath)
print(sys.path)

# Old imports for API Calls
# import requests
# from requests.exceptions import HTTPError

# General Imports
import pickle
import time
import logging
import json
# import yaml
from pathlib import Path

# New imports to optimize API-Calls
from typing import Dict
import asyncio
import aiohttp
import urllib.error
import urllib.parse
import urllib.request

# Import from lupulib
import lupulib
import lupulib.devices
from lupulib.devices.binary_sensor import LupusecBinarySensor
from lupulib.devices.sensor import LupusecSensor
from lupulib.devices.switch import LupusecSwitch
from lupulib.devices.thermal_switch import LupusecThemalSwitch
from lupulib.devices.updown_switch import LupusecUpDownSwitch
import lupulib.constants as CONST
import lupulib.exceptions
# from lupulib.exceptions import LupusecParseError, LupusecRequestError, LupusecResponseError
# from lupulib.devices.binary_sensor import LupusecBinarySensor
# from lupulib.devices.switch import LupusecSwitch


_LOGGER = logging.getLogger(__name__)
home = str(Path.home())
# print(home)


class LupusecAPI:
    """Interface to Lupusec Webservices."""

    def __init__(self, username, password, ip_address) -> None:
        """LupusecAPI constructor to interface Lupusec Alarm System XT2Plus."""
        self._username = username
        self._password = password
        self._ip_address = ip_address
        _LOGGER.debug("LupusecAPI: ip-address=%s, username=%s, pwd=%s", 
            self._ip_address, self._username, self._password)
        self._url = "http://{}/action/".format(ip_address)
        self._model = "unknown"
        self._auth = None
        if self._username != None and self._password != None:
            self._auth = aiohttp.BasicAuth(login=self._username, password=self._password, encoding='utf-8')
            _LOGGER.debug("...auth.encode: %s", self._auth.encode())  
            _LOGGER.debug("...set aiohttp.BasicAuth")
        self._system = None
        self._token = None

        # Try to access local cache file
        _LOGGER.debug(f"Check for Cache-File: {home}/{CONST.HISTORY_CACHE_NAME}")
        try:
            self._history_cache = pickle.load(
                open(home + "/" + CONST.HISTORY_CACHE_NAME, "rb")
            )
            _LOGGER.debug("...file exists.")
        # If local cache file does not exist -> create one    
        except Exception as e:
            _LOGGER.debug(e)
            self._history_cache = []
            pickle.dump(
                self._history_cache, open(home + "/" + CONST.HISTORY_CACHE_NAME, "wb")
            )
            _LOGGER.debug("...file created.")       

        # Set cache timestamps
        _LOGGER.debug(f"Cache current timestamp: {time.time()}")       
        self._cacheStampS = time.time()
        self._cacheStampP = time.time()
        #self._panel = self.get_panel()

        # Set device caches to none
        self._cacheBinarySensors = None
        self._cacheSensors = None
        self._cacheSwitches = None
        self._devices = None
        self._apiDevices = None


    # ToDo: should renamed to: _async_api_get()
    async def _async_api_call(ip, session, action_url) -> Dict:
        """Generic sync method to call the Lupusec API"""
        # Generate complete URL from Constants.py
        url = f'{CONST.URL_HTTP}{ip}{CONST.URL_PORT}{CONST.URL_ACTION}{action_url}'
        _LOGGER.debug("_async_api_call() called: URL=%s", url)
        start_time = time.time()
        _LOGGER.debug(f"Starttime: {start_time}")

        try:
            async with session.get(url, ssl=False) as resp:
                _LOGGER.debug("Response_Status=%s", resp.status)

                # check for Response Status other than 200
                if resp.status != 200:
                    _LOGGER.error(f"ERROR: Response status = {resp.status}")
                    return {}

                # check for non-JSON Response Headers   
                if not resp.headers["content-type"].strip().startswith("application/json"):
                    _LOGGER.error(f"ERROR: Content Type is not JSON = {resp.headers['content-type']}")
                    return {}

                # Get Response Body
                # content = await resp.json()
                content = await resp.text()

                # ToDo: check for empty body, size = 0
                content = content.replace(chr(245), "")
                content = content.replace("\t", "")
                clean_content = json.loads(content)
                _LOGGER.debug("Data Type of Response: =%s", type(clean_content))
                end_time = time.time()
                _LOGGER.debug(f"Endtime: {end_time}")   
                _LOGGER.debug(f"Duration: {end_time - start_time} seconds") 
                _LOGGER.debug("API-Call finished.")  
                #print(clean_content)            
                return clean_content

        except aiohttp.client_exceptions.ClientConnectorError:
            _LOGGER.error("Cannot connect to: ", url)
            return {}

        except aiohttp.ContentTypeError:
            _LOGGER.error("JSON decode failed")
            return {}


    async def _async_api_post(ip, session, action_url, headers, params) -> Dict:
        """Generic sync method to call the Lupusec API"""
        # Generate complete URL from Constants.py
        url = f'{CONST.URL_HTTP}{ip}{CONST.URL_PORT}{CONST.URL_ACTION}{action_url}'
        _LOGGER.debug("_async_api_post() called: URL=%s", url)
        start_time = time.time()
        _LOGGER.debug(f"Starttime: {start_time}")
        if (headers == None):
            headers = {}
        print("_async_api_post() called...")
        print("headers:")
        print(headers)
        print("params:")
        print(params)

        try:
            async with session.post(url, headers=headers, data=params, ssl=False) as resp:
                # check for Response Status other than 200
                _LOGGER.debug("Response_Status=%s", resp.status)
                if resp.status != 200:
                    _LOGGER.error(f"ERROR: Response status = {resp.status}")
                    return {}

                # check for non-JSON Response Headers   
                _LOGGER.debug("Content_Type=%s", resp.headers["content-type"])              
                if not resp.headers["content-type"].strip().startswith("application/json"):
                    _LOGGER.error(f"ERROR: Content Type is not JSON = {resp.headers['content-type']}")
                    content = await resp.text()
                    print(content)
                    return {}

                # Get Response Body
                content = await resp.text()

                # ToDo: check for empty body, size = 0
                content = content.replace(chr(245), "")
                content = content.replace("\t", "")
                print(content)
                clean_content = json.loads(content)
                _LOGGER.debug("Data Type of Response: =%s", type(clean_content))
                end_time = time.time()
                _LOGGER.debug(f"Endtime: {end_time}")   
                _LOGGER.debug(f"Duration: {end_time - start_time} seconds") 
                _LOGGER.debug("API-Call finished.")              
                return clean_content

        except aiohttp.client_exceptions.ClientConnectorError:
            _LOGGER.error("Cannot connect to: ", url)
            return {}

        except aiohttp.ContentTypeError:
            _LOGGER.error("JSON decode failed")
            return {}



    async def async_get_token(self, session) -> int:
        """Async method to get the a session token from Lupusec System."""
        _LOGGER.debug("__init__.py.async_get_token() called: ")

         # Get Session Token
        _LOGGER.debug("await response...")
        token_response =  await LupusecAPI._async_api_call(self._ip_address, session, CONST.TOKEN_REQUEST)
        _LOGGER.debug("done. check content in response_list...")
        _LOGGER.debug("response.getsizeof(): %s", sys.getsizeof(token_response)) 
        print(token_response)
        if (sys.getsizeof(token_response) > 0):
            _LOGGER.debug("RESULT_RESPONSE: %s", token_response[CONST.RESPONSE_RESULT]) 
            if (token_response[CONST.RESPONSE_RESULT] == 1):
                _LOGGER.debug("RESPONSE_MESSAGE: %s", token_response[CONST.RESPONSE_MESSAGE]) 
                if (len(token_response[CONST.RESPONSE_MESSAGE]) != 0):
                    self._token = token_response[CONST.RESPONSE_MESSAGE]
                    _LOGGER.debug("Token: %s", self._token) 
                    _LOGGER.debug("__init__.py.async_get_token() finished.")    
                    return token_response[CONST.RESPONSE_RESULT]
            return 0
        return 0
 

    async def async_get_system(self) -> None:
        """Async method to get the system info."""
        _LOGGER.debug("__init__.py.async_get_system() called: ")

         # Get System Info
        async with aiohttp.ClientSession(auth=self._auth) as session:
            tasks = []

            # INFO_REQUEST
            _LOGGER.debug("__init__.py.async_get_system(): REQUEST=%s", CONST.INFO_REQUEST)
            tasks.append(asyncio.ensure_future(LupusecAPI._async_api_call(self._ip_address, session, CONST.INFO_REQUEST)))

            # Print response list
            _LOGGER.debug("await asyncio.gather(*tasks)...")
            response_list = await asyncio.gather(*tasks)
            _LOGGER.debug("done. check content in response_list...")
            for content in response_list:
                print(content)
                if CONST.INFO_HEADER in content:
                    self._system = content[CONST.INFO_HEADER]
                    _LOGGER.debug("System Info: %s", self._system)                    
                    print("  Hardware-Version: ", self._system[CONST.SYS_HW_VERSION])
                    print("  Firmware-Version: ", self._system[CONST.SYS_SW_VERSION])                    

            # return devices.system.LupusecSystem(content)

        _LOGGER.debug("__init__.py.async_get_system() finished.")            


    async def async_set_mode(self, mode) -> None:
        """Async method to set alarm mode."""
        _LOGGER.debug("__init__.py.async_set_mode() called: ")
        _LOGGER.info("...set mode: %s", mode)

        params = {"mode": mode, "area": 1}

         # Set Alarm Mode
        async with aiohttp.ClientSession(auth=self._auth) as session:
            _LOGGER.debug("auth.encode: %s", self._auth.encode())            
            tasks = []

            # Get Session Token
            _LOGGER.debug("__init__.py.async_set_mode(): REQUEST=%s", CONST.TOKEN_REQUEST)
            token_response = await LupusecAPI.async_get_token(self, session)
            _LOGGER.debug("async_get_token(): done. check response...")
            print(token_response)
            if (token_response != 0):
                _LOGGER.debug("Token: %s", self._token)
                # SET_ALARM_REQUEST
                _LOGGER.debug("__init__.py.async_set_mode(): REQUEST=%s", CONST.SET_ALARM_REQUEST)
                # Print response list
                _LOGGER.debug("await asyncio.gather(*tasks)...")
                set_alarm_response = await LupusecAPI._async_api_post(self._ip_address, session, 
                    CONST.SET_ALARM_REQUEST, params)
                _LOGGER.debug("_async_api_post(): done. check response...")
                for content in set_alarm_response:
                    print(content)  
            else :    
                _LOGGER.debug("ERROR: no session Token available.")
            
        _LOGGER.debug("__init__.py.async_set_mode() finished.")


    async def async_set_switch(self, switch, mode) -> None:
        """Async method to set switches."""
        _LOGGER.debug("__init__.py.async_set_switch() called: ")
        _LOGGER.info("...for switch: %s, set mode: %s", switch, mode)
        execution = "a=1&z=" + str(switch) + "&sw=" + mode + "&pd="
        # example: exec: a=1&z=20&sw=on&pd=
        _LOGGER.debug("{ exec: %s}", execution)        
        params = {"exec": execution}
        print(params)

         # Control Switch
        async with aiohttp.ClientSession(auth=self._auth) as session:
            _LOGGER.debug("auth.encode: %s", self._auth.encode())            

            # Get Session Token
            _LOGGER.debug("__init__.py.async_set_switch(): REQUEST=%s", CONST.TOKEN_REQUEST)
            token_response = await LupusecAPI.async_get_token(self, session)
            _LOGGER.debug("async_get_token(): done. check response...")
            print(token_response)
            if (token_response != 0):
                _LOGGER.debug("Token: %s", self._token)
                headers = {"X-Token": self._token}
                print(headers)

                # SET_SWITCH
                _LOGGER.debug("__init__.py.async_set_switch(): REQUEST=%s", CONST.EXECUTE_REQUEST)
                set_switch_response = await LupusecAPI._async_api_post(self._ip_address, session, 
                    CONST.EXECUTE_REQUEST, headers, params)
                _LOGGER.debug("_async_api_post(): done. check response...")

                if (sys.getsizeof(set_switch_response) > 0):
                    _LOGGER.debug("RESULT_RESPONSE: %s", set_switch_response[CONST.RESPONSE_RESULT]) 
                    if (token_response[CONST.RESPONSE_RESULT] == 1):
                        _LOGGER.debug("RESPONSE_MESSAGE: %s", set_switch_response[CONST.RESPONSE_MESSAGE]) 
                        if (len(set_switch_response[CONST.RESPONSE_MESSAGE]) != 0):
                            _LOGGER.info("...switch: %s, set to mode: %s", switch, mode)
                    else :
                        _LOGGER.info("ERROR: RESULT_RESPONSE: %s", set_switch_response[CONST.RESPONSE_RESULT])
                        _LOGGER.info("RESPONSE_MESSAGE: %s", set_switch_response[CONST.RESPONSE_MESSAGE])  
            else :    
                _LOGGER.info("ERROR: no session Token available.")
            
        _LOGGER.debug("__init__.py.async_set_switch() finished.")


    async def get_switches(self) -> Dict:
        """Async method to get switches."""
        _LOGGER.debug("__init__.py.get_switches() called: ")
        timeNow = time.time()
        
        # Get switches from cache or update from Lupusec System
        # ToDo: update frequency shall not be hard-coded -> transfer to constant
        if self._cacheSwitches is None or timeNow - self._cacheStampP > 2.0:
            _LOGGER.debug("...switches need update from Lupusec System.")
            self._cacheStamp_p = timeNow

            async with aiohttp.ClientSession(auth=self._auth) as session:
                _LOGGER.debug("auth.encode: %s", self._auth.encode())  

                # Get all devices and filter for switches
                _LOGGER.debug("__init__.py.async_get_devices(): REQUEST=%s", CONST.DEVICE_LIST_REQUEST)
                get_switches_response = await LupusecAPI._async_api_call(self._ip_address, session, CONST.DEVICE_LIST_REQUEST)
                _LOGGER.debug("_async_api_call(): done. check response...")
                # Retreive Device Liste from Response
                if CONST.DEVICE_LIST_HEADER in get_switches_response:
                    device_content = get_switches_response[CONST.DEVICE_LIST_HEADER]
                    print("Number of devices=", len(device_content))    
                    if (len(device_content) != 0):             
                        switches = []
                        for device in device_content:
                            print("sid: ", device["sid"], ", name: ", device["name"], 
                                ", type: ", device["type"], ", status: ", device["status"])
                            if (device["type"] in CONST.TYPES_SWITCH):    
                                switches.append(device)
                                _LOGGER.debug("device is switch...added.")
                            else :
                                _LOGGER.debug("device is no switch...skipping.")
                        self._cacheSwitches = switches
                    else : 
                        _LOGGER.info("ERROR: get_switches(): no switches found.")
                else :
                    _LOGGER.info("ERROR: get_switches(): no switches found.")

        _LOGGER.debug("__init__.py.get_switches() finished.") 

        if (len(self._cacheSwitches) != 0):
            print("Number of switches=", len(self._cacheSwitches))            
            for switch in self._cacheSwitches:
                print("sid: ", switch["sid"], 
                    ", name: ", switch["name"], 
                    ", type: ", switch["type"], 
                    ", area: ", switch["area"],
                    ", zone: ", switch["zone"],                     
                    ", status: ", switch["status_ex"])
        return self._cacheSwitches

    async def get_binary_sensors(self) -> Dict:
        """Async method to get BinarySensors."""
        _LOGGER.debug("__init__.py.get_binary_sensors() called: ")
        timeNow = time.time()
        
        # Get switches from cache or update from Lupusec System
        # ToDo: update frequency shall not be hard-coded -> transfer to constant
        if self._cacheBinarySensors is None or timeNow - self._cacheStampP > 2.0:
            _LOGGER.debug("...BinarySensors need update from Lupusec System.")
            self._cacheStampP = timeNow

            async with aiohttp.ClientSession(auth=self._auth) as session:
                _LOGGER.debug("auth.encode: %s", self._auth.encode())  

                # Get all devices and filter for switches
                _LOGGER.debug("__init__.py.async_get_devices(): REQUEST=%s", CONST.DEVICE_LIST_REQUEST)
                get_bin_sensors_response = await LupusecAPI._async_api_call(self._ip_address, session, CONST.DEVICE_LIST_REQUEST)
                _LOGGER.debug("_async_api_call(): done. check response...")
                # Retreive Device Liste from Response
                if CONST.DEVICE_LIST_HEADER in get_bin_sensors_response:
                    device_content = get_bin_sensors_response[CONST.DEVICE_LIST_HEADER]
                    print("Number of devices=", len(device_content))    
                    if (len(device_content) != 0):             
                        binary_sensors = []
                        for device in device_content:
                            print("sid: ", device["sid"], ", name: ", device["name"], 
                                ", type: ", device["type"], ", status: ", device["status"])
                            if (device["type"] in CONST.TYPES_BIN_SENSOR):    
                                binary_sensors.append(device)
                                _LOGGER.debug("device is BinarySensor...added.")
                            else :
                                _LOGGER.debug("device is no BinarySensor...skipping.")
                        self._cacheBinarySensors = binary_sensors
                    else : 
                        _LOGGER.info("ERROR: get_binary_sensors(): no BinarySensors found.")
                else :
                    _LOGGER.info("ERROR: get_binary_sensors(): no BinarySensors found.")

        _LOGGER.debug("__init__.py.get_binary_sensors() finished.") 

        if (len(self._cacheBinarySensors) != 0):
            print("Number of switches=", len(self._cacheBinarySensors))            
            for sensor in self._cacheBinarySensors:
                print("sid: ", sensor["sid"], 
                    ", name: ", sensor["name"], 
                    ", type: ", sensor["type"], 
                    ", area: ", sensor["area"],
                    ", zone: ", sensor["zone"],                     
                    ", status: ", sensor["status_ex"])
        return self._cacheBinarySensors



    async def get_device_async(self, device_id) -> Dict:
        """Async method to get a single device."""
        _LOGGER.debug("__init__.py.get_device_async() called for device_id=%s", device_id)
        timeNow = time.time()
        
        # Get device from cache or update from Lupusec System
        # ToDo: update frequency shall not be hard-coded -> transfer to constant
        if self._cacheBinarySensors is None or timeNow - self._cacheStampP > 2.0:
            _LOGGER.debug("...Devices need update from Lupusec System.")
            self._cacheStampP = timeNow

            async with aiohttp.ClientSession(auth=self._auth) as session:
                _LOGGER.debug("auth.encode: %s", self._auth.encode())  

                # Get all devices from LupusecAPI
                _LOGGER.debug("__init__.py.async_get_devices(): REQUEST=%s", CONST.DEVICE_LIST_REQUEST)
                get_bin_sensors_response = await LupusecAPI._async_api_call(self._ip_address, session, CONST.DEVICE_LIST_REQUEST)
                _LOGGER.debug("_async_api_call(): done. check response...")
                # Retreive Device Liste from Response
                if CONST.DEVICE_LIST_HEADER in get_bin_sensors_response:
                    device_content = get_bin_sensors_response[CONST.DEVICE_LIST_HEADER]
                    print("Number of devices=", len(device_content))    
                    if (len(device_content) != 0):             
                        binary_sensors = []
                        for device in device_content:
                            if (device["type"] in CONST.TYPES_BIN_SENSOR):    
                                binary_sensors.append(device)
                                _LOGGER.debug("device is BinarySensor...added.")
                            else :
                                _LOGGER.debug("device is no BinarySensor...skipping.")
                        self._cacheBinarySensors = binary_sensors
                    else : 
                        _LOGGER.info("ERROR: get_device_async(): no BinarySensors found.")
                else :
                    _LOGGER.info("ERROR: get_device_async(): no BinarySensors found.")
            _LOGGER.debug("update from LupusecAPI finished.") 

        if (len(self._cacheBinarySensors) != 0):         
            for sensor in self._cacheBinarySensors:
                if (sensor["sid"] == device_id):
                    _LOGGER.debug("device with sid=%s found: status=%s", sensor["sid"], sensor["status_ex"])
                    return sensor    
                else :
                    _LOGGER.debug("no device found with sid=%s", device_id)
                    return {}
        else :
            return {}


    def get_sensors(self):
        _LOGGER.debug("get_sensors() called:")
        stamp_now = time.time()
        if self._cacheSensors is None or stamp_now - self._cacheStampS > 2.0:
            self._cacheStampS = stamp_now
            response = self._request_get(self.api_sensors)
            response = self.clean_json(response.text)["senrows"]
            sensors = []
            for device in response:
                device["status"] = device["cond"]
                device["device_id"] = device[self.api_device_id]
                device.pop("cond")
                device.pop(self.api_device_id)
                if not device["status"]:
                    device["status"] = "Geschlossen"
                else:
                    device["status"] = None
                sensors.append(device)
            self._cacheSensors = sensors

        return self._cacheSensors


    async def api_get_devices(self) -> Dict:
        """Async method to get the device list from Lupusec System."""
        _LOGGER.debug("__init__.py.async_get_devices() called: ")
        # Get System Info
        async with aiohttp.ClientSession(auth=self._auth) as session:
            tasks = []

            # Device List REQUEST
            _LOGGER.debug("__init__.py.async_get_devices(): REQUEST=%s", CONST.DEVICE_LIST_REQUEST)
            tasks.append(asyncio.ensure_future(LupusecAPI._async_api_call(self._ip_address, session, CONST.DEVICE_LIST_REQUEST)))

            # Print response list
            _LOGGER.debug("await asyncio.gather(*tasks)...")
            response_list = await asyncio.gather(*tasks)
            _LOGGER.debug("done. check content in response_list...")
            for content in response_list:
                # Retreive Device Liste from Response
                if CONST.DEVICE_LIST_HEADER in content:
                    device_content = content[CONST.DEVICE_LIST_HEADER]
                    print("Number of devices=", len(device_content))                    
                    api_devices = []
                    for device in device_content:
                        #if "openClose" in device:
                        #        device["status"] = device["openClose"]
                        #        device.pop("openClose")
                        #device["device_id"] = device[self.api_device_id]
                        #device.pop("cond")
                        #device.pop(self.api_device_id)
                        #if device["status"] == "{WEB_MSG_DC_OPEN}":
                        #    print("yes is open " + device["name"])
                        #    device["status"] = 1
                        #if device["status"] == "{WEB_MSG_DC_CLOSE}" or device["status"] == "0":
                        #    device["status"] = "Geschlossen"
                        print("sid: ", device["sid"], ", name: ", device["name"], 
                            ", type: ", device["type"], ", status: ", device["status"])
                        api_devices.append(device)
                self._apiDevices = api_devices

        _LOGGER.debug("__init__.py.async_get_devices() finished.")            
        return self._apiDevices


    def get_panel(self):
        _LOGGER.debug("get_panel() called:")
	    # we are trimming the json from Lupusec heavily, since its bullcrap
        response = self._request_get("panelCondGet")
        if response.status_code != 200:
            raise Exception("Unable to get panel " + response.status_code)
        panel = self.clean_json(response.text)["updates"]
        panel["mode"] = panel[self.api_mode]
        panel.pop(self.api_mode)

        if self.model == 2:
            panel["mode"] = CONST.XT2_MODES_TO_TEXT[panel["mode"]]
        panel["device_id"] = CONST.ALARM_DEVICE_ID
        panel["type"] = CONST.ALARM_TYPE
        panel["name"] = CONST.ALARM_NAME

        history = self.get_history()

        if self.model == 1:
            for histrow in history:
                if histrow not in self._history_cache:
                    if (
                        CONST.MODE_ALARM_TRIGGERED
                        in histrow[CONST.HISTORY_ALARM_COLUMN]
                    ):
                        panel["mode"] = CONST.STATE_ALARM_TRIGGERED
                    self._history_cache.append(histrow)
                    pickle.dump(
                        self._history_cache,
                        open(home + "/" + CONST.HISTORY_CACHE_NAME, "wb"),
                    )
        elif self.model == 2:
            _LOGGER.debug("Alarm on XT2 not implemented")
        return panel

 
    def get_history(self):
        _LOGGER.debug("get_history() called: ")
        response = self._request_get(CONST.HISTORY_REQUEST)
        return self.clean_json(response.text)[CONST.HISTORY_HEADER]


    def refresh(self):
        _LOGGER.debug("refresh() called: ")
        """Do a full refresh of all devices and automations."""
        self.get_devices(refresh=True)


    async def get_devices(self, refresh=True) -> Dict:
        """Get all devices from Lupusec."""
        _LOGGER.debug("get_devices() called: ")
        # Make API-call only, if device list is empty or needs refresh
        if refresh or self._devices is None:
            _LOGGER.debug("...refreshing all devices...")
            if self._devices is None:
                self._devices = {}

            # timestamp_now = time.time()
            # if self._cacheSensors is None or timestamp_now - self._cacheStampS > CONST.UPDATE_FREQ:
            # Call api_get_devices()

            _LOGGER.debug("...starting API-Call api_get_devices()...")
            responseObject = await LupusecAPI.api_get_devices(self)
            #if responseObject and not isinstance(responseObject, (tuple, list)):
            #    responseObject = responseObject
            _LOGGER.debug("...API-Call: response received...")
            _LOGGER.debug("...iterate over all devices in responseObject:")
            for deviceJson in responseObject:
                print("sid: ", deviceJson["sid"], ", name: ", deviceJson["name"], 
                            ", type: ", deviceJson["type"], ", status: ", deviceJson["status"])
                # Attempt to reuse an existing device
                device = self._devices.get(deviceJson["name"])
                _LOGGER.debug("...device: " + deviceJson["name"])
                # No existing device, create a new one
                if device:
                    _LOGGER.debug("...update existing device: " + deviceJson["name"])
                    device.update(deviceJson)
                else:
                    _LOGGER.debug("...newDevice found: " + deviceJson["name"])
                    device = newDevice(deviceJson, self)

                    if not device:
                        _LOGGER.info("Device is unknown")
                        continue

                    self._devices[device.device_id] = device

            # We will be treating the Lupusec panel itself as an armable device.
            #panelJson = self.get_panel()
            #_LOGGER.debug("Get the panel in get_devices: %s", panelJson)
            #self._panel.update(panelJson)

            # alarmDevice = self._devices.get("0")
            #if alarmDevice:
            #    alarmDevice.update(panelJson)
            #else:
            #    alarmDevice = devices.LupusecAlarm.create_alarm(panelJson, self)
            #    self._devices["0"] = alarmDevice

        return list(self._devices.values())


    def get_device(self, device_id, refresh=False):
        """Get a single device."""
        _LOGGER.debug("get_device() called for single device: ")
        if self._devices is None:
            self.get_devices()
            refresh = False

        device = self._devices.get(device_id)

        if device and refresh:
            device.refresh()

        return device


    def get_alarm(self, area="1", refresh=False):
        """Shortcut method to get the alarm device."""
        _LOGGER.debug("get_alarm() called: ")
        if self._devices is None:
            self.get_devices()
            refresh = False

        return self.get_device(CONST.ALARM_DEVICE_ID, refresh)


    def clean_json(textdata):
            # textdata = textdata.replace(chr(245), "")
        return textdata


def newDevice(deviceJson, lupusec):
    """Create new device object for the given type."""
    type_tag = deviceJson.get("type")

    if not type_tag:
        _LOGGER.info("Device has no type")

    if type_tag in CONST.TYPES_BIN_SENSOR:
        _LOGGER.debug("newDevice(): name: " + deviceJson["name"] + "; type: " + str(type_tag) + " = BIN_SENSOR")
        return LupusecBinarySensor(deviceJson, lupusec)
    elif type_tag in CONST.TYPES_SENSOR:
        _LOGGER.debug("newDevice(): name=" + deviceJson["name"] + "; type=" + str(type_tag) + " = SENSOR")        
        return LupusecSensor(deviceJson, lupusec)
    elif type_tag in CONST.TYPES_SWITCH:
        _LOGGER.debug("newDevice(): name=" + deviceJson["name"] + "; type=" + str(type_tag) + "= SWITCH")        
        return LupusecSwitch(deviceJson, lupusec)
    elif type_tag in CONST.TYPES_UPDOWN_SWITCH:
        _LOGGER.debug("newDevice(): name=" + deviceJson["name"] + "; type=" + str(type_tag) + "= UPDOWN_SWITCH")        
        return LupusecThemalSwitch(deviceJson, lupusec)
    elif type_tag in CONST.TYPES_THERMAL_SWITCH:
        _LOGGER.debug("newDevice(): name=" + deviceJson["name"] + "; type=" + str(type_tag) + "= THERMAL_SWITCH")        
        return LupusecUpDownSwitch(deviceJson, lupusec)                
    else:
        _LOGGER.info("Device is not known")
    return None
