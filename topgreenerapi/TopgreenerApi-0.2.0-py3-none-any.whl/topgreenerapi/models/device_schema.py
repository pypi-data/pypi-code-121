from typing import Optional, Any, List, TypeVar, Type, cast, Callable

from topgreenerapi.capability import Capability

T = TypeVar("T")


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


def from_int(x: Any) -> int:
    assert isinstance(x, int) and not isinstance(x, bool)
    return x


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


def from_list(f: Callable[[Any], T], x: Any) -> List[T]:
    assert isinstance(x, list)
    return [f(y) for y in x]


class Property:
    type: str
    unit: Optional[str]
    min: Optional[int]
    max: Optional[int]
    scale: Optional[int]
    step: Optional[int]

    def __init__(self, type: str, unit: Optional[str], min: Optional[int], max: Optional[int], scale: Optional[int], step: Optional[int]) -> None:
        self.type = type
        self.unit = unit
        self.min = min
        self.max = max
        self.scale = scale
        self.step = step

    @staticmethod
    def from_dict(obj: Any) -> 'Property':
        assert isinstance(obj, dict)
        type = from_str(obj.get("type"))
        unit = from_union([from_str, from_none], obj.get("unit"))
        min = from_union([from_int, from_none], obj.get("min"))
        max = from_union([from_int, from_none], obj.get("max"))
        scale = from_union([from_int, from_none], obj.get("scale"))
        step = from_union([from_int, from_none], obj.get("step"))
        return Property(type, unit, min, max, scale, step)

    def to_dict(self) -> dict:
        result: dict = {}
        result["type"] = from_str(self.type)
        result["unit"] = from_union([from_str, from_none], self.unit)
        result["min"] = from_union([from_int, from_none], self.min)
        result["max"] = from_union([from_int, from_none], self.max)
        result["scale"] = from_union([from_int, from_none], self.scale)
        result["step"] = from_union([from_int, from_none], self.step)
        return result


class DeviceSchema:
    mode: str
    code: str
    name: str
    property: Property
    id: int
    type: str
    desc: str
    iconname: Optional[str]

    def __init__(self, mode: str, code: str, name: str, property: Property, id: int, type: str, desc: str, iconname: Optional[str]) -> None:
        self.mode = mode
        self.code = code
        self.name = name
        self.property = property
        self.id = id
        self.type = type
        self.desc = desc
        self.iconname = iconname

    @staticmethod
    def from_dict(obj: Any) -> 'DeviceSchema':
        assert isinstance(obj, dict)
        mode = from_str(obj.get("mode"))
        code = from_str(obj.get("code"))
        name = from_str(obj.get("name"))
        property = Property.from_dict(obj.get("property"))
        id = from_int(obj.get("id"))
        type = from_str(obj.get("type"))
        desc = from_str(obj.get("desc"))
        iconname = from_union([from_str, from_none], obj.get("iconname"))
        return DeviceSchema(mode, code, name, property, id, type, desc, iconname)

    def to_dict(self) -> dict:
        result: dict = {}
        result["mode"] = from_str(self.mode)
        result["code"] = from_str(self.code)
        result["name"] = from_str(self.name)
        result["property"] = to_class(Property, self.property)
        result["id"] = from_int(self.id)
        result["type"] = from_str(self.type)
        result["desc"] = from_str(self.desc)
        result["iconname"] = from_union([from_str, from_none], self.iconname)
        return result

    def get_capability(self) -> Capability:
        ability = Capability(self.code)
        return ability


def deviceschema_from_dict(s: Any) -> DeviceSchema:
    return DeviceSchema.from_dict(s)


def deviceschemas_from_dict(s: Any) -> List[DeviceSchema]:
    return from_list(DeviceSchema.from_dict, s)


def deviceschema_to_dict(x: List[DeviceSchema]) -> Any:
    return from_list(lambda x: to_class(DeviceSchema, x), x)