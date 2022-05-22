import copy
import datetime
from collections import namedtuple
from typing import List, Optional, Dict

import astral
import astral.sun
import attr

from worker_bunch.astral_times.astral_times_config import AstralTime, AstralTimesConfKey
from worker_bunch.service_config import ConfigException
from worker_bunch.utils.time_utils import TimeUtils


@attr.define
class AstralParsed:
    """Internal parse result. It's a little complicated to support individual "depression" values."""

    predefined: AstralTime = None

    is_dawn: Optional[bool] = None
    is_dusk: Optional[bool] = None
    depression: Optional[float] = None

    def is_valid(self) -> bool:
        mode_counter = 0
        if self.predefined:
            mode_counter += 1
        if self.is_dawn:
            mode_counter += 1
        if self.is_dusk:
            mode_counter += 1

        if mode_counter != 1:
            return False

        if self.predefined is not None:
            return True

        if self.is_dawn is True or self.is_dusk is True:
            if self.depression is None or 1 > self.depression < 18:
                return False

        return True


Location = namedtuple("Location", ["latitude", "longitude", "elevation"])


class AstralTimesManager:
    """
    Provides astral times for the configured location (latitude, longitude, altitude).

    API: https://astral.readthedocs.io/en/stable/index.html
    """

    def __init__(self, config):
        self._observer: Optional[astral.Observer] = None
        if config:
            latitude = config[AstralTimesConfKey.LATITUDE]
            longitude = config[AstralTimesConfKey.LONGITUDE]
            altitude = config[AstralTimesConfKey.ELEVATION]
            self._observer = astral.Observer(latitude=latitude, longitude=longitude, elevation=altitude)

        self._cache_time = TimeUtils.now()
        self._cached_values: Dict[str, datetime.datetime] = {}

        self._reset_cache(self._cache_time)

    def get_location(self) -> Optional[Location]:
        """Returns configured location"""
        if not self._observer:
            return None
        return Location(latitude=self._observer.latitude, longitude=self._observer.longitude, elevation=self._observer.elevation)

    def _reset_cache(self, cache_time):
        self._cached_values = {}
        self._cache_time = self.round_time_to_hour(cache_time)

    def _get_or_calc_astral_time(self, astral_key: str, pivot_time: datetime.datetime):
        if self._cache_time != self.round_time_to_hour(pivot_time):
            self._reset_cache(pivot_time)
        astral_time = self._cached_values.get(astral_key)
        if astral_time is None:
            if not self._observer:
                raise ConfigException("Astral times are not configured - missing location!")

            parsed = self.parse_astral_time_key(astral_key)
            astral_time = self.calc_astral_time(parsed, pivot_time, self._observer)
            self._cached_values[astral_key] = astral_time

        return astral_time

    def hits(self, astral_key: str, pivot_time: Optional[datetime.datetime] = None) -> List[str]:
        if pivot_time is None:
            pivot_time = TimeUtils.now()
        pivot_time = self.round_time_to_minute(pivot_time)

        astral_time = self._get_or_calc_astral_time(astral_key, pivot_time)
        return astral_time == pivot_time

    def get_astral_time(self, astral_key: str, pivot_time: Optional[datetime.datetime] = None) -> datetime.datetime:
        if pivot_time is None:
            pivot_time = TimeUtils.now()
        pivot_time = self.round_time_to_minute(pivot_time)

        astral_time = self._get_or_calc_astral_time(astral_key, pivot_time)
        return astral_time

    def get_astral_times(self, time: Optional[datetime.datetime] = None) -> Dict[str, any]:
        if time is None:
            time = TimeUtils.now()

        data = {"timestamp": time}

        for astral_time in AstralTime:
            recipe = AstralParsed(predefined=astral_time)
            try:
                data[astral_time.value] = self.calc_astral_time(recipe, time, self._observer)
            except ValueError:
                # ValueError: Sun never reaches 18 degrees below the horizon, at this location.
                data[astral_time.value] = None

        return data

    @classmethod
    def is_valid_astral_time_key(cls, value: str):
        try:
            parse_result = cls.parse_astral_time_key(value)
            return parse_result.is_valid()
        except ValueError:
            return False

    @classmethod
    def parse_astral_time_key(cls, value: str) -> AstralParsed:
        """The astral time syntax has to checked on worker level."""

        value = value.strip().lower()
        for astral_time in AstralTime:
            if astral_time.value == value:
                return AstralParsed(predefined=astral_time)

        is_dawn = value.startswith("dawn")
        is_dusk = value.startswith("dusk")
        try:
            depression = int(value[5:], 10)
        except ValueError:
            depression = None

        if depression and 1 <= depression <= 18:
            if is_dawn:
                return AstralParsed(is_dawn=True, depression=depression)
            if is_dusk:
                return AstralParsed(is_dusk=True, depression=depression)

        raise ValueError(f"no valid AstralParse value ({value})!")

    @classmethod
    def round_time_to_minute(cls, time: datetime.datetime) -> datetime.datetime:
        time = time + datetime.timedelta(seconds=30)
        time = time.replace(second=0)
        time = time.replace(microsecond=0)
        return time

    @classmethod
    def round_time_to_hour(cls, time: datetime.datetime) -> datetime.datetime:
        time = cls.round_time_to_minute(time)
        time = time.replace(minute=0)
        return time

    @classmethod
    def calc_astral_time(cls, parsed: AstralParsed, pivot_time: datetime.datetime, observer) -> datetime.datetime:
        if not parsed.is_valid():
            raise ValueError("invalid AstralParsed!")

        parsed = copy.deepcopy(parsed)

        date = pivot_time.date()
        astral_time = None

        if parsed.predefined == AstralTime.SUNRISE:
            astral_time = astral.sun.sunrise(observer, date, pivot_time.tzinfo)
        elif parsed.predefined == AstralTime.NOON:
            astral_time = astral.sun.noon(observer, date, pivot_time.tzinfo)
        elif parsed.predefined == AstralTime.SUNSET:
            astral_time = astral.sun.sunset(observer, date, pivot_time.tzinfo)
        elif parsed.predefined == AstralTime.MIDNIGHT:
            astral_time = astral.sun.midnight(observer, date, pivot_time.tzinfo)

        if astral_time is None and parsed.depression is None:
            if parsed.predefined in [AstralTime.DAWN_CIVIL, AstralTime.DUSK_CIVIL]:
                parsed.depression = 6
            elif parsed.predefined in [AstralTime.DAWN_ASTRO, AstralTime.DUSK_ASTRO]:
                parsed.depression = 12
            elif parsed.predefined in [AstralTime.DAWN_NAUTICAL, AstralTime.DUSK_NAUTICAL]:
                parsed.depression = 18

        if parsed.predefined in [AstralTime.DAWN_CIVIL, AstralTime.DAWN_ASTRO, AstralTime.DAWN_NAUTICAL]:
            parsed.is_dawn = True
        elif parsed.predefined in [AstralTime.DUSK_CIVIL, AstralTime.DUSK_ASTRO, AstralTime.DUSK_NAUTICAL]:
            parsed.is_dusk = True

        if astral_time is None and parsed.is_dawn and parsed.depression is not None:
            astral_time = astral.sun.dawn(observer, date, parsed.depression, pivot_time.tzinfo)

        if astral_time is None and parsed.is_dusk and parsed.depression is not None:
            astral_time = astral.sun.dusk(observer, date, parsed.depression, pivot_time.tzinfo)

        # if astral_time is None, then parsed.is_valid() has failed
        astral_time = cls.round_time_to_minute(astral_time)
        return astral_time
