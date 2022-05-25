"""
WeatherAPI types.
"""

import json
import pickle
from datetime import datetime as dt

from . import raw

__all__ = [
    'Location',
    'HourlyPoint',
    'DayPoint',
    'AstroPoint',
    'DailyPoint',
    'IpPoint',
    'SportsPoint'
]

class BasePoint:
    """Abstract class representing a single data point."""
    @classmethod
    def from_raw(cls, data):
        """Return new instance of child from json converted `weatherapi` response."""
        # Unpacking uses the dict's keys as keyword arguments
        return cls(**data)

    @classmethod
    def from_json(cls, data):
        """Return new instance of child from raw `weatherapi` response."""
        return cls(**json.loads(data))

    def to_bytes(self):
        """Return a bytes-like object."""
        return pickle.dumps(self)

class BasePointLoc:
    """``BasePoint`` with extra location parameter."""
    @classmethod
    def from_raw(cls, location, data):
        """Return new instance of child from json converted `weatherapi` response."""
        return cls(location, **data) # Unpacking uses the dict's keys are keyword arguments

    @classmethod
    def from_json(cls, location, data):
        """Return new instance of child from raw `weatherapi` response."""
        return cls(location, **json.loads(data))

    def to_bytes(self):
        """Return a bytes-like object."""
        return pickle.dumps(self)

# Inheritance only to implement `from_raw` and `from_json` automatically for all subclasses

class Location(BasePoint):
    """
    Represents location data such as coordinates, time zone, region, at a particular time.

    :var lat: :class:`float`
    :var lon: :class:`float`
    :var name: :class:`str`
    :var region: :class:`str`
    :var tz_id: :class:`str`
    :var localtime: :class:`datetime.datetime`
    """
    def __init__(self,
        lat, lon, name, region=None, country=None, tz_id=None, localtime=None,
        **kwargs
    ):
        self.lat = lat
        self.lon = lon
        self.name = name
        self.region = region
        self.country = country
        self.tz_id = tz_id
        self.localtime = dt.strptime(localtime, "%Y-%m-%d %H:%M") if localtime else None

class HourlyPoint(BasePointLoc):
    """
    Represents weather data at a particular time in some location.

    :var location: :class:`Location`
    :var time: :class:`datetime.datetime`
    :var temp_c: :class:`types.Cel`
    :var feelslike_c: :class:`types.Cel`
    :var windchill_c: :class:`types.Cel`
    :var heatindex_c: :class:`types.Cel`
    :var dewpoint_c: :class:`types.Cel`
    :var condition: :class:`dict`
    :var wind_kph: :class:`types.Km`
    :var gust_kph: :class:`types.Km`
    :var wind_degree: :class:`int`
    :var wind_dir: :class:`str`
    :var pressure_mb: :class:`types.Mb`
    :var precip_mm: :class:`types.Mm`
    :var will_it_rain: :class:`int`
    :var will_it_snow: :class:`int`
    :var chance_of_rain: :class:`str`
    :var chance_of_snow: :class:`str`
    :var humidity: :class:`int`
    :var cloud: :class:`int`
    :var is_day: :class:`bool`
    :var uv: :class:`float`
    :var vis_km: :class:`types.Km`
    """
    def __init__(
        self, location,
        temp_c, feelslike_c,
        condition,
        wind_kph, wind_degree, wind_dir, gust_kph,
        pressure_mb, precip_mm, humidity,
        cloud, is_day, uv,
        last_updated=None, time=None,
        windchill_c=None, heatindex_c=None, dewpoint_c=None,
        will_it_rain=None, will_it_snow=None,
        chance_of_rain=None, chance_of_snow=None,
        vis_km=None,
        **kwargs
    ):
        if isinstance(location, Location):
            self.location = location
        else:
            self.location = Location.from_raw(location)

        self.time = dt.strptime(last_updated if not time else time, "%Y-%m-%d %H:%M") \
                    if (last_updated or time) else None

        self.temp_c = raw.Cel(temp_c)
        self.feelslike_c = raw.Cel(feelslike_c)

        self.windchill_c = raw.Cel(windchill_c)
        self.heatindex_c = raw.Cel(heatindex_c)
        self.dewpoint_c = raw.Cel(dewpoint_c)

        self.condition = condition

        self.wind_kph = raw.Km(wind_kph)
        self.gust_kph = raw.Km(gust_kph)

        self.wind_degree = wind_degree
        self.wind_dir = wind_dir

        self.pressure_mb = raw.Mb(pressure_mb)
        self.precip_mm = raw.Mm(precip_mm)

        self.will_it_rain = will_it_rain
        self.will_it_snow = will_it_snow
        self.chance_of_rain = chance_of_rain
        self.chance_of_snow = chance_of_snow

        self.humidity = humidity
        self.cloud = cloud

        self.is_day = bool(is_day)

        self.uv = uv
        self.vis_km = raw.Km(vis_km)

class DayPoint(BasePointLoc):
    """
    The total conditions per day.

    :var location: :class:`Location`
    :var maxtemp_c: :class:`types.Cel`
    :var mintemp_c: :class:`types.Cel`
    :var avgtemp_c: :class:`types.Cel`
    :var condition: :class:`dict`
    :var maxwind_kph: :class:`types.Km`
    :var totalprecip_mm: :class:`types.Mm`
    :var avgvis_km: :class:`types.Km`
    :var avghumidity: :class:`int`
    :var uv: :class:`float`
    """
    def __init__(
        self, location,
        maxtemp_c, mintemp_c, avgtemp_c, maxwind_kph,
        totalprecip_mm, avgvis_km, avghumidity, condition, uv,
        **kwargs
    ):
        if isinstance(location, Location):
            self.location = location
        else:
            self.location = Location.from_raw(location)

        self.maxtemp_c = raw.Cel(maxtemp_c)
        self.mintemp_c = raw.Cel(mintemp_c)
        self.avgtemp_c = raw.Cel(avgtemp_c)

        self.condition = condition

        self.maxwind_kph = raw.Km(maxwind_kph)

        self.totalprecip_mm = raw.Mm(totalprecip_mm)
        self.avgvis_km = raw.Km(avgvis_km)
        self.avghumidity = avghumidity

        self.uv = uv

class AstroPoint(BasePointLoc):
    """
    Astronomy information.

    :var location: :class:`Location`
    :var sunrise: :class:`str`
    :var sunset: :class:`str`
    :var moonrise: :class:`str`
    :var moonset: :class:`str`
    :var moon_phase: :class:`str`
    """
    def __init__(self, location, sunrise, sunset, moonrise, moonset, moon_phase, **kwargs):
        if isinstance(location, Location):
            self.location = location
        else:
            self.location = Location.from_raw(location)

        self.sunrise = sunrise
        self.sunset = sunset

        self.moonrise = moonrise
        self.moonset = moonset

        self.moon_phase = moon_phase

class DailyPoint(BasePointLoc):
    """
    All information per day, inlcuding hourly info.

    :var location: :class:`Location`
    :var day: :class:`DayPoint`
    :var astro: :class:`AstroPoint`
    :var hour: list[:class:`HourlyPoint`]
    """
    def __init__(self, location, day, astro, hour):
        self.location = location if isinstance(location, Location) else Location.from_raw(location)

        self.day = day if isinstance(day, DayPoint) else DayPoint.from_raw(location, day)

        self.astro = astro

        self.hour = [
            i if isinstance(i, HourlyPoint) else HourlyPoint.from_raw(location, i)
            for i in hour
        ]

class IpPoint(BasePoint):
    """
    IP Address information.

    :var location: :class:`Location`
    :var ip: :class:`str`
    :var type: :class:`str`
    """
    def __init__(self,
        ip, type,
        country_name,
        city, region,
        lat, lon, tz_id,
        **kwargs
    ):
        self.location = Location(lat, lon, city, region=region, country=country_name, tz_id=tz_id)
        self.ip = ip
        self.type = type

class SportsPoint(BasePoint):
    """
    Information about a sports event, such as stadium, region, start time, etc.

    :var stadium: :class:`str`
    :var country: :class:`str`
    :var region: :class:`str`
    :var tournament: :class:`str`
    :var start: :class:`datetime.datetime`
    :var match: :class:`str`
    """
    def __init__(self, stadium, country, region, tournament, start, match):
        self.stadium = stadium
        self.country = country # / Might wrap in a `Location` object
        self.region = region   # /
        self.tournament = tournament
        self.start = dt.strptime(start, "%Y-%m-%d %H:%M") if start else None
        self.match = match
