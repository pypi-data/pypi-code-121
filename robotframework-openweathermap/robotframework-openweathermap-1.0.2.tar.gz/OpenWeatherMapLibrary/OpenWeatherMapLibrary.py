#!/usr/local/bin/python3
#
# Robot Framework Keyword library wrapper for the
# OpenWeatherMap API (https://openweathermap.org/api)
# Author: Joerg Schultze-Lutter, 2022
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
import requests.cookies
from robot.api.deco import library, keyword, not_keyword
from enum import Enum
import re
import logging

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s %(module)s -%(levelname)s- %(message)s"
)
logger = logging.getLogger(__name__)

__version__ = "1.0.2"
__author__ = "Joerg Schultze-Lutter"

#
# Various API types which are supported by the OpenWeatherMap API
# Enum value is used for the construction of the future URL
#
class OpenWeatherMapApiType(Enum):
    API = "api"
    PRO = "pro"
    HISTORY = "history"
    BULK = "bulk"


#
# Robot Framework Keyword Library for the OpenWeatherMap API
#
@library(scope="GLOBAL", auto_keywords=False)
class OpenWeatherMapLibrary:
    # Default parameter settings
    DEFAULT_LATITUDE = None
    DEFAULT_LONGITUDE = None
    DEFAULT_APIKEY = None
    DEFAULT_OUTPUT_FORMAT = None
    DEFAULT_UNIT_FORMAT = None
    DEFAULT_LANGUAGE = None
    DEFAULT_EXCLUDE = None
    DEFAULT_NUMBER_OF_RESULTS = None
    DEFAULT_DT_START = None
    DEFAULT_DT_END = None
    DEFAULT_DT = None

    # Class-internal parameters
    __owm_latitude = None
    __owm_longitude = None
    __owm_apikey = None
    __owm_output_format = None
    __owm_unit_format = None
    __owm_language = None
    __owm_exclude = None
    __owm_number = None
    __owm_dt_start = None
    __owm_dt_end = None
    __owm_dt = None

    # constructor
    def __init__(
        self,
        owm_latitude: float = DEFAULT_LATITUDE,
        owm_longitude: float = DEFAULT_LONGITUDE,
        owm_apikey: str = DEFAULT_APIKEY,
        own_output_format: str = DEFAULT_OUTPUT_FORMAT,
        owm_unit_format: str = DEFAULT_UNIT_FORMAT,
        owm_language: str = DEFAULT_LANGUAGE,
        owm_exclude: str = DEFAULT_EXCLUDE,
        owm_number: int = DEFAULT_NUMBER_OF_RESULTS,
        owm_dt_start: int = DEFAULT_DT_START,
        owm_dt_end: int = DEFAULT_DT_END,
        owm_dt: int = DEFAULT_DT,
    ):
        self.__owm_latitude = owm_latitude
        self.__owm_longitude = owm_longitude
        self.__owm_apikey = owm_apikey
        self.__owm_number = owm_number
        self.__owm_language = owm_language
        self.__owm_exclude = owm_exclude
        self.__owm_output_format = own_output_format
        self.__owm_unit_format = owm_unit_format
        self.__owm_dt_start = owm_dt_start
        self.__owm_dt_end = owm_dt_end
        self.__owm_dt = owm_dt

    # Python "Getter" methods
    #
    # Note that adding a Robot decorator (@keyword) will not
    # cause an error but the keyword will not be recognized later on
    # Therefore, Robot-specific "getter" keywords are required
    @property
    def owm_latitude(self):
        return self.__owm_latitude

    @property
    def owm_longitude(self):
        return self.__owm_longitude

    @property
    def owm_apikey(self):
        return self.__owm_apikey

    @property
    def owm_number(self):
        return self.__owm_number

    @property
    def owm_language(self):
        return self.__owm_language

    @property
    def owm_exclude(self):
        return self.__owm_exclude

    @property
    def owm_output_format(self):
        return self.__owm_output_format

    @property
    def owm_unit_format(self):
        return self.__owm_unit_format

    @property
    def owm_dt_start(self):
        return self.__owm_dt_start

    @property
    def owm_dt_end(self):
        return self.__owm_dt_end

    @property
    def owm_dt(self):
        return self.__owm_dt

    # Python "Setter" methods
    #
    # Note that adding a Robot decorator (@keyword) will not
    # cause an error but the keyword will not be recognized later on
    # Therefore, Robot-specific "setter" keywords are required

    @owm_latitude.setter
    def owm_latitude(self, owm_latitude: float):
        if not owm_latitude:
            raise ValueError("No latitude value has been specified")
        self.__owm_latitude = owm_latitude

    @owm_longitude.setter
    def owm_longitude(self, owm_longitude: float):
        if not owm_longitude:
            raise ValueError("No longitude value has been specified")
        self.__owm_longitude = owm_longitude

    @owm_apikey.setter
    def owm_apikey(self, owm_apikey: str):
        if not owm_apikey:
            raise ValueError("No API-Key value has been specified")
        self.__owm_apikey = owm_apikey

    @owm_number.setter
    def owm_number(self, owm_number: int):
        if not owm_number:
            raise ValueError("No Number of Results value has been specified")
        if owm_number < 1:
            raise ValueError("Number of Results value needs to be greater than zero")
        self.__owm_number = owm_number

    @owm_language.setter
    def owm_language(self, owm_language: str):
        self.__owm_language = self.__owm_language_check(owm_language=owm_language)

    @owm_exclude.setter
    def owm_exclude(self, owm_exclude: str):
        self.__owm_exclude = self.__owm_exclude_check(owm_exclude=owm_exclude)

    @owm_output_format.setter
    def owm_output_format(self, owm_output_format: str):
        self.__owm_output_format = self.__owm_output_format_check(
            owm_output_format=owm_output_format
        )

    @owm_unit_format.setter
    def owm_unit_format(self, owm_unit_format: str):
        self.__owm_unit_format = self.__owm_unit_format_check(
            owm_unit_format=owm_unit_format
        )

    @owm_dt_start.setter
    def owm_dt_start(self, owm_dt_start: str):
        if not owm_dt_start:
            raise ValueError("No dt-start value has been specified")
        self.__owm_dt_start = owm_dt_start

    @owm_dt_end.setter
    def owm_dt_end(self, owm_dt_end: str):
        if not owm_dt_end:
            raise ValueError("No dt-end value has been specified")
        self.__owm_dt_end = owm_dt_end

    @owm_dt.setter
    def owm_dt(self, owm_dt: str):
        if not owm_dt:
            raise ValueError("No dt value has been specified")
        self.__owm_dt = owm_dt

    # Python class validation methods
    @not_keyword
    def __owm_unit_format_check(self, owm_unit_format: str):
        valid_units = ["standard", "metric", "imperial"]
        if owm_unit_format:
            owm_unit_format = owm_unit_format.lower()
            if owm_unit_format not in valid_units:
                raise ValueError(
                    f"Invalid unit format specified; valid values: {valid_units}"
                )
        return owm_unit_format

    @not_keyword
    def __owm_output_format_check(self, owm_output_format: str):
        valid_formats = ["xml", "html", "json"]
        if owm_output_format:
            owm_output_format = owm_output_format.lower()
            if owm_output_format not in valid_formats:
                raise ValueError(
                    f"Invalid output format specified; valid values: {valid_formats}"
                )
        return owm_output_format

    @not_keyword
    def __owm_exclude_check(self, owm_exclude):
        # 'excludes' value can contain 1..n comma-separated values
        # have a look at each one of them and check if we have
        # received something that looks valid
        valid_excludes = ["current", "minutely", "hourly", "daily", "alerts"]
        if owm_exclude:
            # lowercase our value and remove any potential spaces
            owm_exclude = owm_exclude.lower().replace(" ", "")

            # Split it up with comma separator
            excludes = owm_exclude.split(",")

            # Iterate through that list
            for exclude in excludes:
                if exclude not in valid_excludes:
                    raise ValueError(
                        f"Invalid output format specified; valid values: {valid_excludes}"
                    )
        return owm_exclude

    @not_keyword
    def __owm_language_check(self, owm_language: str):
        # fmt: off
        valid_languages = [
            "af", "al", "ar", "az",
            "bg", "ca", "cz", "da",
            "de", "el", "en", "eu",
            "fa", "fi", "fr", "gl",
            "he", "hi", "hr", "hu",
            "id", "it", "ja", "kr",
            "la", "lt", "mk", "no",
            "nl", "pl", "pt", "ro",
            "ru", "sv", "se", "sk",
            "sl", "sp", "es", "sr",
            "th", "tr", "ua", "uk",
            "vi", "cn", "tw", "zu",
        ]
        # fmt: on

        if owm_language:
            owm_language = owm_language.lower()
            if owm_language not in valid_languages:
                raise ValueError(
                    f"Invalid language code specified; valid values: {valid_languages}"
                )

            # Language code convenience mapping
            if owm_language == "cn":
                owm_language = "zh_cn"
            if owm_language == "tw":
                owm_language = "zh_tw"

        return owm_language

    #
    # Robot-specific "getter" keywords
    #
    @keyword("Get OpenWeatherMap Latitude")
    def get_owm_latitude(self):
        return self.owm_latitude

    @keyword("Get OpenWeatherMap Longitude")
    def get_owm_longitude(self):
        return self.owm_longitude

    @keyword("Get OpenWeatherMap API Key")
    def get_owm_apikey(self):
        return self.owm_apikey

    @keyword("Get OpenWeatherMap Number Of Results")
    def get_owm_number(self):
        return self.owm_number

    @keyword("Get OpenWeatherMap Language")
    def get_owm_language(self):
        return self.owm_language

    @keyword("Get OpenWeatherMap Excludes")
    def get_owm_exclude(self):
        return self.owm_exclude

    @keyword("Get OpenWeatherMap Output Format")
    def get_owm_output_format(self):
        return self.owm_output_format

    @keyword("Get OpenWeatherMap Unit Format")
    def get_owm_unit_format(self):
        return self.owm_unit_format

    @keyword("Get OpenWeatherMap Datetime Start")
    def get_owm_dt_start(self):
        return self.owm_dt_start

    @keyword("Get OpenWeatherMap Datetime End")
    def get_owm_dt_end(self):
        return self.owm_dt_end

    @keyword("Get OpenWeatherMap Datetime")
    def get_owm_dt(self):
        return self.owm_dt

    #
    # Robot-specific "setter" keywords
    #
    @keyword("Set OpenWeatherMap Latitude")
    def set_owm_latitude(self, latitude: float = None):
        logger.debug(msg="Setting OWM Latitude")
        self.owm_latitude = latitude

    @keyword("Set OpenWeatherMap Longitude")
    def set_owm_longitude(self, longitude: float = None):
        logger.debug(msg="Setting OWM Longitude")
        self.owm_longitude = longitude

    @keyword("Set OpenWeatherMap API Key")
    def set_owm_apikey(self, apikey: str = None):
        logger.debug(msg="Setting OWM API Key")
        self.owm_apikey = apikey

    @keyword("Set OpenWeatherMap Number Of Results")
    def set_owm_number(self, number: int = None):
        logger.debug(msg="Setting OWM Number Of Results")
        self.owm_number = number

    @keyword("Set OpenWeatherMap Language")
    def set_owm_language(self, language: str = None):
        logger.debug(msg="Setting OWM Language")
        self.owm_language = language

    @keyword("Set OpenWeatherMap Excludes")
    def set_owm_excludes(self, exclude: str = None):
        logger.debug(msg="Setting OWM Excludes")
        self.owm_exclude = exclude

    @keyword("Set OpenWeatherMap Output Format")
    def set_owm_output_format(self, output_format: str = None):
        logger.debug(msg="Setting OWM Output Format")
        self.owm_output_format = output_format

    @keyword("Set OpenWeatherMap Unit Format")
    def set_owm_unit_format(self, unit_format: str = None):
        logger.debug(msg="Setting OWM Unit Format")
        self.owm_unit_format = unit_format

    @keyword("Set OpenWeatherMap Datetime Start")
    def set_owm_dt_start(self, dt_start: int = None):
        logger.debug(msg="Setting OWM Datetime Start")
        self.owm_dt_start = dt_start

    @keyword("Set OpenWeatherMap Datetime End")
    def set_owm_dt_end(self, dt_end: int = None):
        logger.debug(msg="Setting OWM Datetime End")
        self.owm_dt_end = dt_end

    @keyword("Set OpenWeatherMap Datetime")
    def set_owm_dt(self, dt: int = None):
        logger.debug(msg="Setting OWM Datetime")
        self.owm_dt = dt

    #
    # Robot Framework Action Keywords for OpenWeatherMap
    #
    @keyword("Get Current Weather")
    #
    # API Call:https://openweathermap.org/current
    #
    def get_current_weather(
        self,
        latitude: float = None,
        longitude: float = None,
        apikey: str = None,
        output_format: str = None,
        unit_format: str = None,
        language: str = None,
    ):
        # perform pre-sanity checks for the optional parameters
        output_format = self.__owm_output_format_check(owm_output_format=output_format)
        unit_format = self.__owm_unit_format_check(owm_unit_format=unit_format)
        language = self.__owm_language_check(owm_language=language)

        __url_path = "/2.5/weather"
        url = self.__get_base_api(api_type=OpenWeatherMapApiType.API) + __url_path

        # Add mandatory / optional fields whereas present
        # parameter payload dictionary
        payload = {}

        # fmt: off
        payload = self.__add_parameter(name="lat", param1=self.get_owm_latitude(), param2=latitude, optional=False, payload=payload)
        payload = self.__add_parameter(name="lon", param1=self.get_owm_longitude(), param2=longitude, optional=False, payload=payload)
        payload = self.__add_parameter(name="appid", param1=self.get_owm_apikey(), param2=apikey, optional=False, payload=payload)
        payload = self.__add_parameter(name="mode", param1=self.get_owm_output_format(), param2=output_format, optional=True, payload=payload)
        payload = self.__add_parameter(name="units", param1=self.get_owm_unit_format(), param2=unit_format, optional=True, payload=payload)
        payload = self.__add_parameter(name="lang", param1=self.get_owm_language(), param2=language, optional=True, payload=payload)
        # fmt: on

        return self.__make_request(url=url, payload=payload)

    @keyword("Get Hourly Forecast 4 Days")
    #
    # API Call:https://openweathermap.org/api/hourly-forecast
    #
    def get_hourly_forecast_four_days(
        self,
        latitude: float = None,
        longitude: float = None,
        apikey: str = None,
        output_format: str = None,
        language: str = None,
        number: int = None,
    ):
        # perform pre-sanity checks for the optional parameters
        output_format = self.__owm_output_format_check(owm_output_format=output_format)
        language = self.__owm_language_check(owm_language=language)

        # API does not support html output; fail the keyword in case
        # we are suppose to return html content
        if output_format == "html":
            raise ValueError("This API call does not support the HTML output format")

        __url_path = "/2.5/forecast/hourly"
        url = self.__get_base_api(api_type=OpenWeatherMapApiType.PRO) + __url_path

        # Add mandatory / optional fields whereas present
        # parameter payload dictionary
        payload = {}

        # fmt: off
        payload = self.__add_parameter(name="lat", param1=self.get_owm_latitude(), param2=latitude, optional=False, payload=payload)
        payload = self.__add_parameter(name="lon", param1=self.get_owm_longitude(), param2=longitude, optional=False, payload=payload)
        payload = self.__add_parameter(name="appid", param1=self.get_owm_apikey(), param2=apikey, optional=False, payload=payload)
        payload = self.__add_parameter(name="mode", param1=self.get_owm_output_format(), param2=output_format, optional=True, payload=payload)
        payload = self.__add_parameter(name="cnt", param1=self.get_owm_number(), param2=number, optional=True, payload=payload)
        payload = self.__add_parameter(name="lang", param1=self.get_owm_language(), param2=language, optional=True, payload=payload)
        # fmt: on

        return self.__make_request(url=url, payload=payload)

    @keyword("Get OneCall Forecast")
    #
    # API Call:https://openweathermap.org/api/one-call-api
    #
    def get_onecall_forecast(
        self,
        latitude: float = None,
        longitude: float = None,
        apikey: str = None,
        exclude: str = None,
        unit_format: str = None,
        language: str = None,
    ):
        # perform pre-sanity checks for the optional parameters
        exclude = self.__owm_exclude_check(owm_exclude=exclude)
        unit_format = self.__owm_unit_format_check(owm_unit_format=unit_format)
        language = self.__owm_language_check(owm_language=language)

        __url_path = "/2.5/onecall"
        url = self.__get_base_api(api_type=OpenWeatherMapApiType.API) + __url_path

        # Add mandatory / optional fields whereas present
        # parameter payload dictionary
        payload = {}

        # fmt: off
        payload = self.__add_parameter(name="lat", param1=self.get_owm_latitude(), param2=latitude, optional=False, payload=payload)
        payload = self.__add_parameter(name="lon", param1=self.get_owm_longitude(), param2=longitude, optional=False, payload=payload)
        payload = self.__add_parameter(name="appid", param1=self.get_owm_apikey(), param2=apikey, optional=False, payload=payload)
        payload = self.__add_parameter(name="exclude", param1=self.get_owm_exclude(), param2=exclude, optional=True, payload=payload)
        payload = self.__add_parameter(name="units", param1=self.get_owm_unit_format(), param2=unit_format, optional=True, payload=payload)
        payload = self.__add_parameter(name="lang", param1=self.get_owm_language(), param2=language, optional=True, payload=payload)
        # fmt: on

        return self.__make_request(url=url, payload=payload)

    @keyword("Get Daily Forecasts 16 Days")
    #
    # API Call:https://openweathermap.org/forecast16
    #
    def get_daily_forecasts_16_days(
        self,
        latitude: float = None,
        longitude: float = None,
        apikey: str = None,
        number: int = None,
        output_format: str = None,
        unit_format: str = None,
        language: str = None,
    ):
        # perform pre-sanity checks for the optional parameters
        output_format = self.__owm_output_format_check(owm_output_format=output_format)
        unit_format = self.__owm_unit_format_check(owm_unit_format=unit_format)
        language = self.__owm_language_check(owm_language=language)

        # API does not support html output; fail the keyword in case
        # we are suppose to return html content
        if output_format == "html":
            raise ValueError("This API call does not support the HTML output format")

        __url_path = "/2.5/forecast/daily"
        url = self.__get_base_api(api_type=OpenWeatherMapApiType.API) + __url_path

        # Add mandatory / optional fields whereas present
        # parameter payload dictionary
        payload = {}

        # fmt: off
        payload = self.__add_parameter(name="lat", param1=self.get_owm_latitude(), param2=latitude, optional=False, payload=payload)
        payload = self.__add_parameter(name="lon", param1=self.get_owm_longitude(), param2=longitude, optional=False, payload=payload)
        payload = self.__add_parameter(name="appid", param1=self.get_owm_apikey(), param2=apikey, optional=False, payload=payload)
        payload = self.__add_parameter(name="mode", param1=self.get_owm_output_format(), param2=output_format, optional=True, payload=payload)
        payload = self.__add_parameter(name="cnt", param1=self.get_owm_number(), param2=number, optional=True, payload=payload)
        payload = self.__add_parameter(name="lang", param1=self.get_owm_language(), param2=language, optional=True, payload=payload)
        payload = self.__add_parameter(name="units", param1=self.get_owm_unit_format(), param2=unit_format, optional=True, payload=payload)
        # fmt: on

        return self.__make_request(url=url, payload=payload)

    @keyword("Get Climatic Forecast 30 Days")
    #
    # API Call:https://openweathermap.org/forecast30
    #
    def get_climatic_forecast_30_days(
        self,
        latitude: float = None,
        longitude: float = None,
        apikey: str = None,
        number: int = None,
        output_format: str = None,
        unit_format: str = None,
        language: str = None,
    ):
        # perform pre-sanity checks for the optional parameters
        output_format = self.__owm_output_format_check(owm_output_format=output_format)
        unit_format = self.__owm_unit_format_check(owm_unit_format=unit_format)
        language = self.__owm_language_check(owm_language=language)

        # API does not support html output; fail the keyword in case
        # we are suppose to return html content
        if output_format == "html":
            raise ValueError("This API call does not support the HTML output format")

        __url_path = "/2.5/forecast/climate"
        url = self.__get_base_api(api_type=OpenWeatherMapApiType.PRO) + __url_path

        # Add mandatory / optional fields whereas present
        # parameter payload dictionary
        payload = {}

        # fmt: off
        payload = self.__add_parameter(name="lat", param1=self.get_owm_latitude(), param2=latitude, optional=False, payload=payload)
        payload = self.__add_parameter(name="lon", param1=self.get_owm_longitude(), param2=longitude, optional=False, payload=payload)
        payload = self.__add_parameter(name="appid", param1=self.get_owm_apikey(), param2=apikey, optional=False, payload=payload)
        payload = self.__add_parameter(name="mode", param1=self.get_owm_output_format(), param2=output_format, optional=True, payload=payload)
        payload = self.__add_parameter(name="cnt", param1=self.get_owm_number(), param2=number, optional=True, payload=payload)
        payload = self.__add_parameter(name="lang", param1=self.get_owm_language(), param2=language, optional=True, payload=payload)
        payload = self.__add_parameter(name="units", param1=self.get_owm_unit_format(), param2=unit_format, optional=True, payload=payload)
        # fmt: on

        return self.__make_request(url=url, payload=payload)

    @keyword("Get Current Solar Radiation")
    #
    # API Call:https://openweathermap.org/api/solar-radiation
    #
    def get_current_solar_radiation(
        self, latitude: float = None, longitude: float = None, apikey: str = None
    ):
        __url_path = "/2.5/solar_radiation"
        url = self.__get_base_api(api_type=OpenWeatherMapApiType.API) + __url_path

        # Add mandatory / optional fields whereas present
        # parameter payload dictionary
        payload = {}

        # fmt: off
        payload = self.__add_parameter(name="lat", param1=self.get_owm_latitude(), param2=latitude, optional=False, payload=payload)
        payload = self.__add_parameter(name="lon", param1=self.get_owm_longitude(), param2=longitude, optional=False, payload=payload)
        payload = self.__add_parameter(name="appid", param1=self.get_owm_apikey(), param2=apikey, optional=False, payload=payload)
        # fmt: on

        return self.__make_request(url=url, payload=payload)

    @keyword("Get Solar Radiation Forecast")
    #
    # API Call:https://openweathermap.org/api/solar-radiation
    #
    def get_solar_radiation_forecast(
        self, latitude: float = None, longitude: float = None, apikey: str = None
    ):
        __url_path = "/2.5/solar_radiation/forecast"
        url = self.__get_base_api(api_type=OpenWeatherMapApiType.API) + __url_path

        # Add mandatory / optional fields whereas present
        # parameter payload dictionary
        payload = {}

        # fmt: off
        payload = self.__add_parameter(name="lat", param1=self.get_owm_latitude(), param2=latitude, optional=False, payload=payload)
        payload = self.__add_parameter(name="lon", param1=self.get_owm_longitude(), param2=longitude, optional=False, payload=payload)
        payload = self.__add_parameter(name="appid", param1=self.get_owm_apikey(), param2=apikey, optional=False, payload=payload)
        # fmt: on

        return self.__make_request(url=url, payload=payload)

    @keyword("Get Solar Radiation History")
    #
    # API Call:https://openweathermap.org/api/solar-radiation
    #
    def get_solar_radiation_history(
        self,
        latitude: float = None,
        longitude: float = None,
        apikey: str = None,
        dt_start: int = None,
        dt_end: int = None,
    ):
        __url_path = "/2.5/solar_radiation/history"
        url = self.__get_base_api(api_type=OpenWeatherMapApiType.API) + __url_path

        # Add mandatory / optional fields whereas present
        # parameter payload dictionary
        payload = {}

        # fmt: off
        payload = self.__add_parameter(name="lat", param1=self.get_owm_latitude(), param2=latitude, optional=False, payload=payload)
        payload = self.__add_parameter(name="lon", param1=self.get_owm_longitude(), param2=longitude, optional=False, payload=payload)
        payload = self.__add_parameter(name="appid", param1=self.get_owm_apikey(), param2=apikey, optional=False, payload=payload)
        payload = self.__add_parameter(name="start", param1=self.get_owm_dt_start(), param2=dt_start, optional=False, payload=payload)
        payload = self.__add_parameter(name="end", param1=self.get_owm_dt_end(), param2=dt_end, optional=False, payload=payload)
        # fmt: on

        return self.__make_request(url=url, payload=payload)

    @keyword("Get 5 Day 3 Hour Forecast")
    #
    # API Call:https://openweathermap.org/forecast5
    #
    def get_5_day_3_hour_forecast(
        self,
        latitude: float = None,
        longitude: float = None,
        apikey: str = None,
        number: int = None,
        output_format: str = None,
        unit_format: str = None,
        language: str = None,
    ):
        # perform pre-sanity checks for the optional parameters
        output_format = self.__owm_output_format_check(owm_output_format=output_format)
        unit_format = self.__owm_unit_format_check(owm_unit_format=unit_format)
        language = self.__owm_language_check(owm_language=language)

        # API does not support html output; fail the keyword in case
        # we are suppose to return html content
        if output_format == "html":
            raise ValueError("This API call does not support the HTML output format")

        __url_path = "/2.5/forecast"
        url = self.__get_base_api(api_type=OpenWeatherMapApiType.API)

        # Add mandatory / optional fields whereas present
        # parameter payload dictionary
        payload = {}

        # fmt: off
        payload = self.__add_parameter(name="lat", param1=self.get_owm_latitude(), param2=latitude, optional=False, payload=payload)
        payload = self.__add_parameter(name="lon", param1=self.get_owm_longitude(), param2=longitude, optional=False, payload=payload)
        payload = self.__add_parameter(name="appid", param1=self.get_owm_apikey(), param2=apikey, optional=False, payload=payload)
        payload = self.__add_parameter(name="mode", param1=self.get_owm_output_format(), param2=output_format, optional=True, payload=payload)
        payload = self.__add_parameter(name="cnt", param1=self.get_owm_number(), param2=number, optional=True, payload=payload)
        payload = self.__add_parameter(name="lang", param1=self.get_owm_language(), param2=language, optional=True, payload=payload)
        payload = self.__add_parameter(name="units", param1=self.get_owm_unit_format(), param2=unit_format, optional=True, payload=payload)
        # fmt: on

        return self.__make_request(url=url, payload=payload)

    @keyword("Get Current Air Pollution Data")
    #
    # API Call:https://openweathermap.org/api/air-pollution
    #
    def get_current_air_pollution_data(
        self, latitude: float = None, longitude: float = None, apikey: str = None
    ):
        __url_path = "/2.5/air_pollution/forecast"
        url = self.__get_base_api(api_type=OpenWeatherMapApiType.API)

        # Add mandatory / optional fields whereas present
        # parameter payload dictionary
        payload = {}

        # fmt: off
        payload = self.__add_parameter(name="lat", param1=self.get_owm_latitude(), param2=latitude, optional=False, payload=payload)
        payload = self.__add_parameter(name="lon", param1=self.get_owm_longitude(), param2=longitude, optional=False, payload=payload)
        payload = self.__add_parameter(name="appid", param1=self.get_owm_apikey(), param2=apikey, optional=False, payload=payload)
        # fmt: on

        return self.__make_request(url=url, payload=payload)

    @keyword("Get Air Pollution Data Forecast")
    #
    # API Call:https://openweathermap.org/api/air-pollution
    #
    def get_air_pollution_data_forecast(
        self,
        latitude: float = None,
        longitude: float = None,
        apikey: str = None,
    ):
        __url_path = "/2.5/air_pollution/forecast"
        url = self.__get_base_api(api_type=OpenWeatherMapApiType.API)

        # Add mandatory / optional fields whereas present
        # parameter payload dictionary
        payload = {}

        # fmt: off
        payload = self.__add_parameter(name="lat", param1=self.get_owm_latitude(), param2=latitude, optional=False, payload=payload)
        payload = self.__add_parameter(name="lon", param1=self.get_owm_longitude(), param2=longitude, optional=False, payload=payload)
        payload = self.__add_parameter(name="appid", param1=self.get_owm_apikey(), param2=apikey, optional=False, payload=payload)
        # fmt: on

        return self.__make_request(url=url, payload=payload)

    @keyword("Get Air Pollution Data History")
    #
    # API Call:https://openweathermap.org/api/air-pollution
    #
    def get_air_pollution_data_history(
        self,
        latitude: float = None,
        longitude: float = None,
        apikey: str = None,
        dt_start: int = None,
        dt_end: int = None,
    ):
        __url_path = "/2.5/air_pollution/history"
        url = self.__get_base_api(api_type=OpenWeatherMapApiType.API)

        # Add mandatory / optional fields whereas present
        # parameter payload dictionary
        payload = {}

        # fmt: off
        payload = self.__add_parameter(name="lat", param1=self.get_owm_latitude(), param2=latitude, optional=False, payload=payload)
        payload = self.__add_parameter(name="lon", param1=self.get_owm_longitude(), param2=longitude, optional=False, payload=payload)
        payload = self.__add_parameter(name="appid", param1=self.get_owm_apikey(), param2=apikey, optional=False, payload=payload)
        payload = self.__add_parameter(name="start", param1=self.get_owm_dt_start(), param2=dt_start, optional=False, payload=payload)
        payload = self.__add_parameter(name="end", param1=self.get_owm_dt_end(), param2=dt_end, optional=False, payload=payload)
        # fmt: on

        return self.__make_request(url=url, payload=payload)

    @keyword("Get Road Risk Data")
    #
    # API Call:https://openweathermap.org/api/road-risk
    #
    def get_road_risk_data(
        self,
        latitude: float = None,
        longitude: float = None,
        apikey: str = None,
        dt: int = None,
    ):

        __url_path = "/2.5/roadrisk"
        url = self.__get_base_api(api_type=OpenWeatherMapApiType.API)

        # Add mandatory / optional fields whereas present
        # parameter payload dictionary
        payload = {}
        # fmt: off
        payload = self.__add_parameter(name="lat", param1=self.get_owm_latitude(), param2=latitude, optional=False, payload=payload)
        payload = self.__add_parameter(name="lon", param1=self.get_owm_longitude(), param2=longitude, optional=False, payload=payload)
        payload = self.__add_parameter(name="appid", param1=self.get_owm_apikey(), param2=apikey, optional=False, payload=payload)
        payload = self.__add_parameter(name="dt", param1=self.get_owm_dt(), param2=dt, optional=False, payload=payload)
        # fmt: on

        # Unlike the other OWM APIs, this API call expects to receive its data via request body
        # So let's extract the values from the original payload and then pop the values from the payload
        #
        # Build the request body and remove the original entries from the payload element
        body_data = {
            "track": [
                {
                    "lat": payload.pop("lat"),
                    "lon": payload.pop("lon"),
                    "dt": payload.pop("dt"),
                }
            ]
        }

        # Finally, send this request with a request body to the API
        return self.__make_request(url=url, payload=payload, data=body_data)

    @not_keyword
    def __get_base_api(self, api_type: Enum):
        """
        Construct the base URL based on the ENUM value that is associated
        with each API call

        Parameters
        ==========
        api_type : 'Enum'
            API type, defined in class OpenWeatherMapApiType

        Returns
        =======
        url: 'str'
            OpenWeatherMap base URL
        """
        url = ""
        valid_values = [
            OpenWeatherMapApiType.API,
            OpenWeatherMapApiType.PRO,
            OpenWeatherMapApiType.HISTORY,
            OpenWeatherMapApiType.BULK,
        ]
        if api_type not in valid_values:
            raise ValueError("Received invalid enum value for base URL")
        url = "https://" + api_type.value + ".openweathermap.org/data"
        return url

    @not_keyword
    def __add_parameter(
        self, name: str, param1: object, param2: object, optional: bool, payload: dict
    ):
        """
        Receives a set of two values (value 2 has priority over value 1) and a
        variable name. Adds name/value setting to dict if present. When
        'optional' flag is set to False, throw an exception if neither
        value 1 nor value 2 are provided

        Parameters
        ==========
        name : 'str'
            Variable name
        param1: 'object'
            Value of any data type. By default, this variable's value is the
            one that the user has potentially set via the "Set ... " keywords
        param2: 'object'
            Value of any data type. By default, this variable's value is the
            one that the user has passed along as part of the actual keyword
            (which will then have priority over the ones set by the "Set ..."
            keywords
        optional: 'bool'
            True = Do not throw an exception if neither param1 nor param2 are
                   provided
        payload: 'dict'
            Payload key/value dictionary for our HTTP GET request

        Returns
        =======
        payload: 'dict'
            Payload key/value dictionary for our HTTP GET request
        """
        if not optional and not param1 and not param2:
            raise ValueError(
                f"Value for '{name}' neither set nor provided via parameter"
            )

        value = param2 if param2 else param1
        response = ""
        if value:
            payload[name] = value
        else:
            if not optional:
                raise ValueError(
                    f"Value for {name} neither set nor provided via parameter"
                )

        return payload

    @not_keyword
    def __make_request(self, url: str, payload: dict, data: dict = None):
        """
        Issues a HTTP GET and returns the response code / body
        Parameters
        ==========
        url : 'str'
            Our URL that we want to run the GET for
        payload: 'dict'
            URL parameters
        Returns
        =======
        status_code: 'int'
            numeric HTTP status code
        text: 'str'
            HTTP response body
        """
        if data:
            resp = requests.get(url=url, params=payload, data=data)
        else:
            resp = requests.get(url=url, params=payload)
        return resp.status_code, resp.text


if __name__ == "__main__":
    pass
