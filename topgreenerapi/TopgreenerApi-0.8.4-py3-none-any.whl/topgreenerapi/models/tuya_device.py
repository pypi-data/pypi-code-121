from datetime import datetime, timedelta
from typing import Any, Optional, Dict, Union, List, TypeVar, Type, cast, Callable
from enum import Enum

from topgreenerapi.models import device_schema

T = TypeVar("T")
EnumT = TypeVar("EnumT", bound=Enum)


def from_int(x: Any) -> int:
    assert isinstance(x, int) and not isinstance(x, bool)
    return x


def from_bool(x: Any) -> bool:
    assert isinstance(x, bool)
    return x


def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


def from_none(x: Any) -> Any:
    assert x is None
    return x


def from_union(fs, x):
    for f in fs:
        try:
            return f(x)
        except:
            pass
    assert False


def to_enum(c: Type[EnumT], x: Any) -> EnumT:
    assert isinstance(x, c)
    return x.value


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


def from_dict(f: Callable[[Any], T], x: Any) -> Dict[str, T]:
    assert isinstance(x, dict)
    return {k: f(v) for (k, v) in x.items()}


def from_list(f: Callable[[Any], T], x: Any) -> List[T]:
    assert isinstance(x, list)
    return [f(y) for y in x]


class DPName:
    pass

    def __init__(self, ) -> None:
        pass

    @staticmethod
    def from_dict(obj: Any) -> 'DPName':
        assert isinstance(obj, dict)
        return DPName()

    def to_dict(self) -> dict:
        result: dict = {}
        return result


class Cdv(Enum):
    EMPTY = ""
    THE_100 = "1.0.0"


class VerSw(Enum):
    THE_314 = "3.1.4"
    THE_433 = "4.3.3"


class Mcu:
    upgrade_status: int
    cdv: Cdv
    ver_sw: VerSw
    is_online: bool
    id: int
    cadv: str
    bv: Optional[str]
    pv: Optional[str]

    def __init__(self, upgrade_status: int, cdv: Cdv, ver_sw: VerSw, is_online: bool, id: int, cadv: str,
                 bv: Optional[str], pv: Optional[str]) -> None:
        self.upgrade_status = upgrade_status
        self.cdv = cdv
        self.ver_sw = ver_sw
        self.is_online = is_online
        self.id = id
        self.cadv = cadv
        self.bv = bv
        self.pv = pv

    @staticmethod
    def from_dict(obj: Any) -> 'Mcu':
        assert isinstance(obj, dict)
        upgrade_status = from_int(obj.get("upgradeStatus"))
        cdv = Cdv(obj.get("cdv"))
        ver_sw = VerSw(obj.get("verSw"))
        is_online = from_bool(obj.get("isOnline"))
        id = from_int(obj.get("id"))
        cadv = from_str(obj.get("cadv"))
        bv = from_union([from_str, from_none], obj.get("bv"))
        pv = from_union([from_str, from_none], obj.get("pv"))
        return Mcu(upgrade_status, cdv, ver_sw, is_online, id, cadv, bv, pv)

    def to_dict(self) -> dict:
        result: dict = {}
        result["upgradeStatus"] = from_int(self.upgrade_status)
        result["cdv"] = to_enum(Cdv, self.cdv)
        result["verSw"] = to_enum(VerSw, self.ver_sw)
        result["isOnline"] = from_bool(self.is_online)
        result["id"] = from_int(self.id)
        result["cadv"] = from_str(self.cadv)
        result["bv"] = from_union([from_str, from_none], self.bv)
        result["pv"] = from_union([from_str, from_none], self.pv)
        return result


class ModuleMap:
    wifi: Mcu
    mcu: Mcu

    def __init__(self, wifi: Mcu, mcu: Mcu) -> None:
        self.wifi = wifi
        self.mcu = mcu

    @staticmethod
    def from_dict(obj: Any) -> 'ModuleMap':
        assert isinstance(obj, dict)
        wifi = Mcu.from_dict(obj.get("wifi"))
        mcu = Mcu.from_dict(obj.get("mcu"))
        return ModuleMap(wifi, mcu)

    def to_dict(self) -> dict:
        result: dict = {}
        result["wifi"] = to_class(Mcu, self.wifi)
        result["mcu"] = to_class(Mcu, self.mcu)
        return result


class TuyaDevice:
    virtual: bool
    dp_name: DPName
    lon: str
    uuid: str
    mac: str
    icon_url: str
    runtime_env: str
    lat: str
    dev_id: str
    dev_key: str
    dp_max_time: int
    product_id: str
    dps: Dict[str, Union[bool, int]]
    assumed_dps: Dict[str, Union[bool, int, Any]]
    ip: str
    active_time: int
    category_code: str
    module_map: ModuleMap
    dev_attribute: int
    name: str
    timezone_id: str
    category: str
    local_key: str

    def __init__(self, virtual: bool, dp_name: DPName, lon: str, uuid: str, mac: str, icon_url: str, runtime_env: str,
                 lat: str, dev_id: str, dev_key: str, dp_max_time: int, product_id: str,
                 dps: Dict[str, Union[bool, int]], ip: str, active_time: int, category_code: str, module_map: ModuleMap,
                 dev_attribute: int, name: str, timezone_id: str, category: str, local_key: str) -> None:
        self.virtual = virtual
        self.dp_name = dp_name
        self.lon = lon
        self.uuid = uuid
        self.mac = mac
        self.icon_url = icon_url
        self.runtime_env = runtime_env
        self.lat = lat
        self.dev_id = dev_id
        self.dev_key = dev_key
        self.dp_max_time = dp_max_time
        self.product_id = product_id
        self.dps = dps
        self.ip = ip
        self.active_time = active_time
        self.category_code = category_code
        self.module_map = module_map
        self.dev_attribute = dev_attribute
        self.name = name
        self.timezone_id = timezone_id
        self.category = category
        self.local_key = local_key

        self.assumed_dps = {}
        for dp in dps:
            self.assumed_dps[dp] = {"value": dps[dp], "expiry": None}

    def setDp(self, ability: 'device_schema.DeviceSchema', value, assumed=False):
        if assumed:
            now = datetime.now()
            exp = now + timedelta(seconds=5)
            self.assumed_dps[str(ability.id)] = {"value": value, "expiry": exp}
        else:
            self.dps[str(ability.id)] = value
            val = self.assumed_dps[str(ability.id)]
            if "expiry" in val and not val["expiry"] is None:
                if val["expiry"] < datetime.now():
                    self.assumed_dps[str(ability.id)] = {"value": value, "expiry": None}

    def getDp(self, ability: 'device_schema.DeviceSchema', assumed=False) -> Any:
        if assumed:
            value = self.assumed_dps[str(ability.id)]
            if "value" in value:
                return value["value"]
            else:
                return value
        else:
            return self.dps[str(ability.id)]

    @staticmethod
    def from_dict(obj: Any) -> 'TuyaDevice':
        assert isinstance(obj, dict)
        virtual = from_bool(obj.get("virtual"))
        dp_name = DPName.from_dict(obj.get("dpName"))
        lon = from_str(obj.get("lon"))
        uuid = from_str(obj.get("uuid"))
        mac = from_str(obj.get("mac"))
        icon_url = from_str(obj.get("iconUrl"))
        runtime_env = from_str(obj.get("runtimeEnv"))
        lat = from_str(obj.get("lat"))
        dev_id = from_str(obj.get("devId"))
        dev_key = from_str(obj.get("devKey"))
        dp_max_time = from_int(obj.get("dpMaxTime"))
        product_id = from_str(obj.get("productId"))
        dps = from_dict(lambda x: from_union([from_int, from_bool], x), obj.get("dps"))
        ip = from_str(obj.get("ip"))
        active_time = from_int(obj.get("activeTime"))
        category_code = from_str(obj.get("categoryCode"))
        module_map = ModuleMap.from_dict(obj.get("moduleMap"))
        dev_attribute = from_int(obj.get("devAttribute"))
        name = from_str(obj.get("name"))
        timezone_id = from_str(obj.get("timezoneId"))
        category = from_str(obj.get("category"))
        local_key = from_str(obj.get("localKey"))
        return TuyaDevice(virtual, dp_name, lon, uuid, mac, icon_url, runtime_env, lat, dev_id, dev_key, dp_max_time,
                          product_id, dps, ip, active_time, category_code, module_map, dev_attribute, name, timezone_id,
                          category, local_key)

    @staticmethod
    def from_update_dict(obj: Any, model: 'TuyaDevice') -> 'TuyaDevice':
        assert isinstance(obj, dict)
        virtual = from_bool(obj.get("virtual"))
        lon = from_str(obj.get("lon"))
        uuid = from_str(obj.get("uuid"))
        mac = from_str(obj.get("mac"))
        icon_url = from_str(obj.get("iconUrl"))
        runtime_env = from_str(obj.get("runtimeEnv"))
        lat = from_str(obj.get("lat"))
        dev_id = from_str(obj.get("devId"))
        dev_key = from_str(obj.get("devKey"))
        dp_max_time = from_int(obj.get("dpMaxTime"))
        product_id = from_str(obj.get("productId"))
        dps = from_dict(lambda x: from_union([from_int, from_bool], x), obj.get("dps"))
        ip = from_str(obj.get("ip"))
        active_time = from_int(obj.get("activeTime"))
        module_map = ModuleMap.from_dict(obj.get("moduleMap"))
        dev_attribute = from_int(obj.get("devAttribute"))
        is_share = from_bool(obj.get("isShare"))
        name = from_str(obj.get("name"))
        timezone_id = from_str(obj.get("timezoneId"))
        local_key = from_str(obj.get("localKey"))
        model.virtual = virtual
        model.lon = lon
        model.uuid = uuid
        model.mac = mac
        model.icon_url = icon_url
        model.runtime_env = runtime_env
        model.lat = lat
        model.dev_id = dev_id
        model.dev_key = dev_key
        model.dp_max_time = dp_max_time
        model.product_id = product_id
        model.dps = dps
        model.ip = ip
        model.active_time = active_time
        model.module_map = module_map
        model.dev_attribute = dev_attribute
        model.name = name
        model.timezone_id = timezone_id
        model.local_key = local_key

        for asp in model.assumed_dps:
            val = model.assumed_dps[asp]
            if "expiry" in val and not val["expiry"] is None:
                if val["expiry"] < datetime.now():
                    # assumption expired
                    model.assumed_dps[asp] = {"value": dps[asp], "expiry": None}
            else:
                model.assumed_dps[asp] = {"value": dps[asp], "expiry": None}

        return model

    def to_dict(self) -> dict:
        result: dict = {}
        result["virtual"] = from_bool(self.virtual)
        result["dpName"] = to_class(DPName, self.dp_name)
        result["lon"] = from_str(self.lon)
        result["uuid"] = from_str(self.uuid)
        result["mac"] = from_str(self.mac)
        result["iconUrl"] = from_str(self.icon_url)
        result["runtimeEnv"] = from_str(self.runtime_env)
        result["lat"] = from_str(self.lat)
        result["devId"] = from_str(self.dev_id)
        result["devKey"] = from_str(self.dev_key)
        result["dpMaxTime"] = from_int(self.dp_max_time)
        result["productId"] = from_str(self.product_id)
        result["dps"] = from_dict(lambda x: from_union([from_int, from_bool], x), self.dps)
        result["ip"] = from_str(self.ip)
        result["activeTime"] = from_int(self.active_time)
        result["categoryCode"] = from_str(self.category_code)
        result["moduleMap"] = to_class(ModuleMap, self.module_map)
        result["devAttribute"] = from_int(self.dev_attribute)
        result["name"] = from_str(self.name)
        result["timezoneId"] = from_str(self.timezone_id)
        result["category"] = from_str(self.category)
        result["localKey"] = from_str(self.local_key)
        return result


def tuya_device_from_dict(s: Any) -> TuyaDevice:
    return TuyaDevice.from_dict(s)


def tuya_devices_from_dict(s: Any) -> List[TuyaDevice]:
    return from_list(TuyaDevice.from_dict, s)


def tuya_device_to_dict(x: List[TuyaDevice]) -> Any:
    return from_list(lambda x: to_class(TuyaDevice, x), x)
