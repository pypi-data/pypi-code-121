"""Lupusec Alarm System"""

# Generic imports
import json
import logging

# Imports from lupulib
import lupulib.constants as CONST


class LupusecSystem(object):
    """Class to represent a Lupusec System"""

    def __init__(self, json_obj):
        """Set up Lupusec System."""
        self._json_state = json_obj
        self._hw_version = json_obj[CONST.SYS_HW_VERSION]
        self._sw_version = json_obj[CONST.SYS_SW_VERSION]
        self._gsm_version = json_obj[CONST.SYS_GSM_VERSION]
        self._ip_address = json_obj[CONST.SYS_IP_ADDRESS]
        self._mac_address = json_obj[CONST.SYS_MAC_ADDRESS]       


    def get_value(self, name):
        """Get a value from the json object."""
        return self._json_state.get(name)

    @property
    def hw_version(self):
        """Shortcut to get the hardware version of the system."""
        return self.get_value(CONST.SYS_HW_VERSION)

    @property
    def sw_version(self):
        """Shortcut to get the software version of the system."""
        return self.get_value(CONST.SYS_SW_VERSION)    

    @property
    def gsm_version(self):
        """Shortcut to get the GSM version of the system."""
        return self.get_value(CONST.SYS_GSM_VERSION)

    @property
    def ip_address(self):
        """Shortcut to get the ip-address of the system."""
        return self.get_value(CONST.SYS_IP_ADDRESS)        

    @property
    def mac_address(self):
        """Shortcut to get the mac-address of the system."""
        return self.get_value(CONST.SYS_MAC_ADDRESS)        

