"""
WeatherAPI client implementation.
Use this to make requests to weatherapi.com.
"""

import os
import json

from datetime import datetime as dt

import requests

from . import cache
from . import errors
from . import types

__all__ = ['Client']

# some constants
_TYPE_CACHE = 'c'
_TYPE_JSON = 'r'

class Client:
    """
    Represents a connection to weatherapi.com.
    Use this class to interact with the weatherapi API.

    :var session: A `requests.Session` object. Requests are made with this (``session.get``).
    """

    BASE = "https://api.weatherapi.com/v1"

    def __init__(self, token, use_cache=False, cache_file=False, cache_path='.cache'):
        self._token = token
        self.session = requests.Session()

        if use_cache:
            if cache_file:
                self.cache = cache.FileCacheManager(cache_path)
            else:
                self.cache = cache.BufferedCacheManager(cache_path)
        else:
            self.cache = cache.CacheManager(cache_path)

        # This looks for the cities list file
        with open(
            os.path.join(os.path.dirname(__file__), 'etc/cities/cities_p.json'),
            'r', encoding='utf-8'
        ) as f:
            self.cities = json.loads(f.read())

    # Utils ----------------------

    @staticmethod
    def __is_error_code(response):
        """
        Convert weatherapi.com provided error code to Error Type.

        :param response: The raw weatherapi.com response.
        """

        if "error" in response:
            code = response['error']['code']
            message = response['error']['message']

            # These are hardcoded
            if code == 1002:
                return errors.NoApiKey(message, code)
            elif code == 1003:
                return errors.QueryNotProvided(message, code)
            elif code == 1005:
                return errors.InvalidRequestUrl(message, code)
            elif code == 1006:
                return errors.InvalidLocation(message, code)
            elif code == 1008:
                return errors.ApiKeyDisabled(message, code)
            elif code == 2006:
                return errors.InvalidApiKey(message, code)
            elif code == 2007:
                return errors.QuotaExceeded(message, code)
            elif code == 2008:
                return errors.ApiKeyDisabled(message, code)
            elif code == 9999:
                return errors.InternalError(message, code)
            else:
                return errors.WeatherApiError(message, code)

        return

    def __make_request(self, endpoint, parameters):
        """Private method to make a request to ``weatherapi.com``."""

        try:
            # Does the actual request
            return self.session.get(f"{self.BASE}/{endpoint}{parameters}",
                                    timeout=(4, 4)).json()
        except Exception as e:
            raise errors.InternalError(f"Unable to fetch data at this time: {e}", 9999)

    def __generic_request(self, loc, mode, endpoint, parameters, *args, **kwargs):
        """
        Generic request method, covering any endpoint and parameters.

        :returns: ``(str, response)``. Response can be a `types` object, or a raw
            weatherapi response. The first element of the tuple is either
            ``_TYPE_CACHE`` or ``_TYPE_JSON``.
        """

        if loc == '':
            raise errors.QueryNotProvided('Location cannot be empty.', 0)

        n = self.cache.read(mode)
        if n:
            return (_TYPE_CACHE, n)

        response = self.__make_request(endpoint, parameters)

        e = Client.__is_error_code(response)
        if e:
            raise e

        return (_TYPE_JSON, response)

    # All implementations should follow the same naming pattern.
    # `{type}-{location}-now-{time-identifier}`
    # Old cache will be cleaned up disregarding `time-identifier`.
    # So, any cache starting with `{type}-{location}` will be deleted
    # if a new cache starting with `{type}-{location}` is dumped.

    def __cache_dump(self, data, mode):
        """Dump response cache with name ``mode``."""
        self.cache.cleanup(mode.split('-now-')[0] + '-now-*') # Discard any old cache
        self.cache.dump(mode, data) # Writes cache

    # ----------------------------

    def find_city(self, loc):
        """
        Try to find a city with a match from a known list of locations.
        This method is highly unlikely to be used frequently, since weatherAPI tries
        to interpret location names even if incorrect, but is provided anyway.
        """
        if loc == '':
            raise errors.QueryNotProvided('Location cannot be empty.', 0)

        return [  # Generates a list of city names containing the string `loc`
            i for i in self.cities if loc.lower() in i['name'].lower()
        ]

    # The cache implementation keeps track of data
    # with their ``name``s. We use ``location``+``ident``
    # (``ident`` is some identifier - usually time) as the
    # name to decide whether the cache is outdated or not.
    # If ``ident`` is some time, then its generalized to a range
    # (say if current time is ``2021-04-01 19:20:30``
    # -> ``2021-04-01 19``), so anything else within that range
    # get matched.'
    # ``2021-04-01 19:05:51`` -> ``2021-04-01 19``
    # ``2021-04-01 19:45:21`` -> ``2021-04-01 19``

    def current(self, loc):
        """
        Get current weather conditions in a location.

        :param loc: Query location to find data for. It could be following:\n
             - **Latitude and Longitude (Decimal degree)**. *e.g:'48.8567,2.3508'*,\n
             - **city name** *e.g: 'Paris'*,\n
             - **US zip** *e.g: '10001'*,\n
             - **UK postcode** *e.g: 'SW1'*,\n
             - **Canada postal code** *e.g: 'G2J'*,\n
             - **metar:<metar code>** *e.g: 'metar:EGLL'*,\n
             - **iata:<3 digit airport code>** *e.g: 'iata:DXB'*,\n
             - **auto:ip IP lookup** *e.g: 'auto:ip'*,\n
             - **IP address (IPv4 and IPv6 supported)** *e.g: '100.0.0.1*'

        :rtype: :class:`types.HourlyPoint`
        """

        # https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
        mode = f"current-{loc.lower()}-now-{dt.now().strftime('%Y-%m-%d-%H-%M')[:-1]}"

        _type, response = self.__generic_request(loc, mode, 'current.json', f'?key={self._token}&q={loc}')

        if _type == _TYPE_CACHE:
            return response

        # Creates the `HourlyPoint` object
        data = types.HourlyPoint.from_raw(response["location"], response["current"])

        self.__cache_dump(data, mode)

        return data

        # The same pattern is followed for all other API methods implemented.

    def forecast(self, loc, days=3):
        """
        Get weather forecast for a location.

        :param loc: See docs on method ``current``.
        :param days: Number of days to restrict the forecast for.
            WeatherAPI allows up to 10 days, but it in practice the maximum is 3.

        :returns: A tuple with the current weather, and a list of forecasted days.
        :rtype: ``(types.HourlyPoint, list[types.DailyPoint])``
        """

        mode = f"forecast-{loc.lower()}-now-{dt.now().strftime('%Y-%m-%d-%H-%M')[:-1]}"

        _type, response = self.__generic_request(loc, mode, 'forecast.json', f'?key={self._token}&q={loc}&days={min(days, 10)}')

        if _type == _TYPE_CACHE:
            return response

        # `data` here is a tuple of the current weather (`HourlyPoint`)
        # and a list of forecasted days (`DailyPoint`s).
        data = (
            types.HourlyPoint.from_raw(response["location"], response["current"]),
            [
                types.DailyPoint(response["location"], i["day"], i["astro"], i["hour"])
                for i in response["forecast"]["forecastday"]
            ]
        )

        self.__cache_dump(data, mode)

        return data

    def astronomy(self, loc):
        """
        Get astronomy information for a location.

        :param loc: See docs on method ``current``.

        :rtype: :class:`types.AstroPoint`
        """

        mode = f"astro-{loc.lower()}-now-{dt.now().strftime('%Y-%m-%d')}"

        _type, response = self.__generic_request(loc, mode, 'astronomy.json', f'?key={self._token}&q={loc}')

        if _type == _TYPE_CACHE:
            return response

        data = types.AstroPoint.from_raw(response["location"], response["astronomy"]["astro"])

        self.__cache_dump(data, mode)

        return data

    def ip_lookup(self, ip):
        """
        Get information for an IP address.

        :param ip: IPv6 or IPv4 string.

        :rtype: :class:`IpPoint`
        """

        mode = f"iplookup-{ip}"

        _type, response = self.__generic_request(ip, mode, 'ip.json', f'?key={self._token}&q={ip}')

        if _type == _TYPE_CACHE:
            return response

        data = types.IpPoint.from_raw(response)

        self.cache.dump(mode, data)
        # cleanup not required here

        return data

    def search(self, loc):
        """
        Get a list of location objects based on query parameter.

        :param loc: See docs on method ``current``.

        :rtype: ``list[types.Location]``
        """

        mode = f"search-{loc.lower()}"

        _type, response = self.__generic_request(loc, mode, 'search.json', f'?key={self._token}&q={loc}')

        if _type == _TYPE_CACHE:
            return response

        data = [
            types.Location.from_raw(i)
            for i in response
        ]

        self.cache.dump(mode, data)

        return data

    def timezone_info(self, loc):
        """
        Get timezone and associated information for a location.

        :param loc: See docs on method ``current``.

        :rtype: :class:`types.Location`
        """

        if loc == '':
            raise errors.QueryNotProvided('Location cannot be empty.', 0)

        # No cache
        # since localtime is a returned parameter.

        response = self.__make_request('timezone.json', f'?key={self._token}&q={loc}')

        e = Client.__is_error_code(response)
        if e:
            raise e

        return types.Location.from_raw(response["location"])

    def sports_lookup(self, loc):
        """
        Get listing of all upcoming sports events for football,
        cricket and golf. From the behaviour of the WeatherAPI Sports API,
        parameter `loc` doesn't actually matter but is required anyway.

        :param loc: See docs on method ``current``.

        :rtype: ``dict{str: list[SportsPoint]}``
        """
        mode = f"sports-{loc.lower()}-now-{dt.now().strftime('%Y-%m-%d')}"

        _type, response = self.__generic_request(loc, mode, 'sports.json', f'?key={self._token}&q={loc}')

        if _type == _TYPE_CACHE:
            return response

        # `SportsPoint` contains data per sports event. It's not specific
        # to any type of sport, nor is it a collection. We use a dictionary
        # with the type of sport as a key, and list of `SportsPoints` as its value.
        data = {
            j: [types.SportsPoint.from_raw(i) for i in response[j]]
            for j in ['football', 'cricket', 'golf']
        }


        self.__cache_dump(data, mode)

        return data

    def history(self, loc, days):
        """
        Get weather history for a location. This hasn't been tested
        since it requires a paid weatherapi.com plan, but should work.

        :param loc: See docs on method ``current``.
        :param dt: Datetime string in the format `YYY-MM-DD`.
            Data starting from this date will be returned.

        :returns: A tuple with the current weather, and a list of historical
                  weather per day.
        :rtype: ``(types.HourlyPoint, list[types.DailyPoint])``
        """
        # weatherapi returns history data as an `Forecast` object as per their API.
        # https://www.weatherapi.com/docs/#apis-history

        mode = f"history-{loc.lower()}-now-{dt.now().strftime('%Y-%m-%d-%H-%M')[:-1]}"

        _type, response = self.__generic_request(loc, mode, 'history.json', f'?key={self._token}&q={loc}&days={min(days, 10)}')

        if _type == _TYPE_CACHE:
            return response

        # `data` here is a tuple of the current weather (`HourlyPoint`)
        # and a list of forecasted days (`DailyPoint`s).
        data = (
            types.HourlyPoint.from_raw(response["location"], response["current"]),
            [
                types.DailyPoint(response["location"], i["day"], i["astro"], i["hour"])
                for i in response["forecast"]["forecastday"]
            ]
        )

        self.__cache_dump(data, mode)

        return data

    # Aliases ---------------------------------------

    def astro(self, *args, **kwargs):
        """Alias for ``astronomy``."""
        return self.astronomy(*args, **kwargs)

    def ip(self, *args, **kwargs):
        """Alias for ``ip_lookup``."""
        return self.ip_lookup(*args, **kwargs)

    def tz(self, *args, **kwargs):
        """Alias for ``timezone_info``."""
        return self.timezone_info(*args, **kwargs)

    def sports(self, *args, **kwargs):
        """Alias for ``sports_lookup``."""
        return self.sports_lookup(*args, **kwargs)
