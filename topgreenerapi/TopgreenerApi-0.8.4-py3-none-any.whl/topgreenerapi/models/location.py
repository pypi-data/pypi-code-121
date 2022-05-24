from typing import List, Any, TypeVar, Callable, Type, cast


T = TypeVar("T")


def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


def from_list(f: Callable[[Any], T], x: Any) -> List[T]:
    assert isinstance(x, list)
    return [f(y) for y in x]


def from_int(x: Any) -> int:
    assert isinstance(x, int) and not isinstance(x, bool)
    return x


def from_float(x: Any) -> float:
    assert isinstance(x, (float, int)) and not isinstance(x, bool)
    return float(x)


def from_bool(x: Any) -> bool:
    assert isinstance(x, bool)
    return x


def to_float(x: Any) -> float:
    assert isinstance(x, float)
    return x


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


class Location:
    geo_name: str
    rooms: List[Any]
    gmt_modified: int
    group_id: int
    lon: float
    gmt_create: int
    owner_id: int
    uid: str
    background: str
    name: str
    id: int
    lat: float
    status: bool

    def __init__(self, geo_name: str, rooms: List[Any], gmt_modified: int, group_id: int, lon: float, gmt_create: int, owner_id: int, uid: str, background: str, name: str, id: int, lat: float, status: bool) -> None:
        self.geo_name = geo_name
        self.rooms = rooms
        self.gmt_modified = gmt_modified
        self.group_id = group_id
        self.lon = lon
        self.gmt_create = gmt_create
        self.owner_id = owner_id
        self.uid = uid
        self.background = background
        self.name = name
        self.id = id
        self.lat = lat
        self.status = status

    @staticmethod
    def from_dict(obj: Any) -> 'Location':
        assert isinstance(obj, dict)
        geo_name = from_str(obj.get("geoName"))
        rooms = from_list(lambda x: x, obj.get("rooms"))
        gmt_modified = from_int(obj.get("gmtModified"))
        group_id = from_int(obj.get("groupId"))
        lon = from_float(obj.get("lon"))
        gmt_create = from_int(obj.get("gmtCreate"))
        owner_id = int(from_str(obj.get("ownerId")))
        uid = from_str(obj.get("uid"))
        background = from_str(obj.get("background"))
        name = from_str(obj.get("name"))
        id = from_int(obj.get("id"))
        lat = from_float(obj.get("lat"))
        status = from_bool(obj.get("status"))
        return Location(geo_name, rooms, gmt_modified, group_id, lon, gmt_create, owner_id, uid, background, name, id, lat, status)

    def to_dict(self) -> dict:
        result: dict = {}
        result["geoName"] = from_str(self.geo_name)
        result["rooms"] = from_list(lambda x: x, self.rooms)
        result["gmtModified"] = from_int(self.gmt_modified)
        result["groupId"] = from_int(self.group_id)
        result["lon"] = to_float(self.lon)
        result["gmtCreate"] = from_int(self.gmt_create)
        result["ownerId"] = from_str(str(self.owner_id))
        result["uid"] = from_str(self.uid)
        result["background"] = from_str(self.background)
        result["name"] = from_str(self.name)
        result["id"] = from_int(self.id)
        result["lat"] = to_float(self.lat)
        result["status"] = from_bool(self.status)
        return result

    def __repr__(self):
        return str(self.__dict__)


def location_from_dict(s: Any) -> Location:
    return Location.from_dict(s)


def location_to_dict(x: Location) -> Any:
    return to_class(Location, x)
