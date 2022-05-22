import threading
from enum import Enum
from typing import List, Optional, Set


_astral_times_lock = threading.Lock()
_astral_extended_values: Optional[Set[str]] = None


class AstralTime(Enum):

    DAWN_ASTRO = "dawn_astro"
    DAWN_NAUTICAL = "dawn_nautical"
    DAWN_CIVIL = "dawn_civil"

    SUNRISE = "sunrise"
    NOON = "noon"
    SUNSET = "sunset"

    DUSK_CIVIL = "dusk_civil"
    DUSK_NAUTICAL = "dusk_nautical"
    DUSK_ASTRO = "dusk_astro"

    MIDNIGHT = "midnight"

    @classmethod
    def values(cls):
        return [astral_time.value for astral_time in AstralTime]

    @classmethod
    def extended_values(cls) -> List[str]:
        with _astral_times_lock:
            if not _astral_extended_values:
                cls._init_extended_values()
            return list(_astral_extended_values)

    @classmethod
    def extended_value_exists(cls, value: str) -> bool:
        if not value:
            return False
        with _astral_times_lock:
            global _astral_extended_values
            if not _astral_extended_values:
                cls._init_extended_values()
            return value in _astral_extended_values

    @classmethod
    def _init_extended_values(cls):
        global _astral_extended_values
        _astral_extended_values = set()
        for astral_time in AstralTime:
            _astral_extended_values.add(astral_time.value)
        for i in range(2, 19):
            _astral_extended_values.add(f"dawn_{i}")
            _astral_extended_values.add(f"dusk_{i}")


class AstralTimesConfKey:

    LATITUDE = "latitude"
    LONGITUDE = "longitude"
    ELEVATION = "elevation"


ASTRAL_TIMES_JSONSCHEMA = {
    "additionalProperties": False,
    "required": [AstralTimesConfKey.LATITUDE, AstralTimesConfKey.LONGITUDE, AstralTimesConfKey.ELEVATION],
    "type": "object",
    "properties": {
        AstralTimesConfKey.LATITUDE: {"type": "number", "minimum": -90, "maximum": 90},
        AstralTimesConfKey.LONGITUDE: {"type": "number", "minimum": -180, "maximum": 180},
        AstralTimesConfKey.ELEVATION: {
            "type": "number",
            "minimum": -1000,
            "maximum": 9000,
            "description": "in meters",
        },
    },
    "description": "A concrete location is necessary to use the astral time service. You don't need to configured it, "
                   "but this will lead to errors in case you use it.",
}
