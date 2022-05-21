import abc
from strenum import StrEnum
from . import util
from .logger import logger


class TuyaDeviceType(StrEnum):
    LIGHT = "dj"
    CEILING_LIGHT = "xdd"
    AMBIANCE_LIGHT = "fwd"
    STRING_LIGHT = "dc"
    STRIP_LIGHT = "dd"
    MOTION_SENSOR_LIGHT = "gyd"
    CEILING_FAN_LIGHT = "fsd"
    SOLAR_LIGHT = "tyndj"
    DIMMER_LIGHT = "tgq"
    REMOTE_CONTROL_LIGHT = "ykq"
    SPOTLIGHT_LIGHT = "sxd"


class TuyaDeviceCategory(StrEnum):
    LIGHTING = "lighting"
    ELECTRICAL = "electrical"
    LARGE_HOME_APPLIANCE = "large home appliance"
    SMALL_HOME_APPLIANCE = "small home appliance"
    KITCHEN_APPLIANCE = "kitchen appliance"
    SECURITY_AND_VIDEO = "security and video"
    EXERCISE_AND_HEALTH = "exercise and health"
    GATEWAY_CONTROL = "gateway control"
    ENERGY = "energy"
    DIGITAL_ENTERTAINMENT = "digital entertainment"
    OUTDOOR_TRAVEL = "outdoor travel"


class TuyaDeviceTypeInterface(metaclass=abc.ABCMeta):
    @staticmethod
    @abc.abstractmethod
    def get_device_types() -> list[TuyaDeviceType]:
        raise NotImplementedError("User must define get_device_type to use this base class")

    @staticmethod
    @abc.abstractmethod
    def get_device_category() -> TuyaDeviceCategory:
        raise NotImplementedError("User must define get_device_category to use this base class")


class TuyaLightType(TuyaDeviceTypeInterface):
    @staticmethod
    def get_device_types() -> list[TuyaDeviceType]:
        return [TuyaDeviceType.LIGHT]

    @staticmethod
    def get_device_category() -> TuyaDeviceCategory:
        return TuyaDeviceCategory.LIGHTING


class TuyaDimmer(TuyaLightType):

    @staticmethod
    def get_device_types() -> list[TuyaDeviceType]:
        return [TuyaDeviceType.DIMMER_LIGHT]


class TuyaStringLight(TuyaLightType):

    @staticmethod
    def get_device_types() -> list[TuyaDeviceType]:
        return [TuyaDeviceType.STRING_LIGHT]


class TuyaStripLight(TuyaLightType):

    @staticmethod
    def get_device_types() -> list[TuyaDeviceType]:
        return [TuyaDeviceType.STRIP_LIGHT]


def category_code_to_type(category_code: str) -> TuyaDeviceTypeInterface:
    for cls in util.all_subclasses(TuyaDeviceTypeInterface):
        logger.debug("Now checking class: %s, with options: %s", cls, cls.get_device_types())
        if category_code in cls.get_device_types():
            logger.debug("Found! %s, %s", cls, cls())
            return cls()
