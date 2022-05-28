from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List


def minimize_dict(maximized: Dict[Any, Any]) -> Dict[Any, Any]:
    return {
        key: value
        for key, value in maximized.items()
        if value is not None and value != ""
    }


def serialize_datetimes(dic: Dict[str, Any]) -> Dict[str, Any]:
    output: Dict[str, Any] = {}
    for key, value in dic.items():
        if not isinstance(value, datetime):
            output[key] = value
        elif value.hour != 0 or value.minute != 0 or value.second != 0:
            output[key] = value.strftime("%Y-%m-%d %H:%M:%S")
        else:
            output[key] = value.strftime("%Y-%m-%d")
    return output


@dataclass
class PassengerInfo:
    Adults: int
    Children: int = 0
    Infants: int = 0

    def json(self) -> Dict[str, Any]:
        return minimize_dict(self.__dict__)


@dataclass
class Location:
    code: str
    name: str = None
    terminal: str = None
    transport: str = None

    def json(self) -> Dict[str, Any]:
        return minimize_dict(self.__dict__)


@dataclass
class Flight:
    arrival_airport: str
    currency: str
    day: datetime
    departure_airport: str
    is_offer: bool
    price: float
    tax: float

    def json(self) -> Dict[str, Any]:
        return serialize_datetimes(minimize_dict(self.__dict__))


@dataclass
class DateAndLocation:
    date: datetime
    location: Location

    def json(self) -> Dict[str, Any]:
        value: Dict[str, Any] = dict(self.__dict__)
        value["location"] = self.location.json()
        return serialize_datetimes(minimize_dict(value))


@dataclass
class Segment:
    airline_code: str
    airline_name: str
    flight_num: str
    duration: int
    start: DateAndLocation
    end: DateAndLocation

    def json(self) -> Dict[str, Any]:
        value: Dict[str, Any] = dict(self.__dict__)
        value["start"] = self.start.json()
        value["end"] = self.end.json()
        return minimize_dict(value)


@dataclass
class Trip:
    origin_depart: DateAndLocation
    destination_return: DateAndLocation
    passengers: PassengerInfo

    origin_segments: List[List[Segment]] = None
    destination_segments: List[List[Segment]] = None

    def json(self) -> Dict[str, Any]:
        value: Dict[str, Any] = dict(self.__dict__)
        value["origin_depart"] = self.origin_depart.json()
        value["destination_return"] = self.destination_return.json()
        value["passengers"] = self.passengers.json()
        if self.origin_segments:
            value["origin_segments"] = [
                [k.json() for k in j] for j in self.origin_segments
            ]
        if self.destination_segments:
            value["destination_segments"] = [
                [k.json() for k in j] for j in self.destination_segments
            ]
        return minimize_dict(value)
