from typing import Any, List

from pydantic import BaseModel


class FlightLegsOperatingCarrierDesignator(BaseModel):
    carrier: str
    airline_id: str
    number: str


class FlightLegsEquipment(BaseModel):
    code: str
    type: str
    name: str


class FlightLegsItem(BaseModel):
    origin: str
    destination: str
    local_departure_date_time: str
    local_arrival_date_time: str
    departure_unix_timestamp: int
    arrival_unix_timestamp: int
    operating_carrier_designator: FlightLegsOperatingCarrierDesignator
    equipment: FlightLegsEquipment
    technical_stops: List
    signature: str
    tags: Any


class TicketSegmentsSchema(BaseModel):
    # ...
    flights: List[int]


class TicketSchema(BaseModel):
    # ...
    segments: List[TicketSegmentsSchema]


class TicketSearchSchema(BaseModel):
    # ...
    flight_legs: List[FlightLegsItem]
    tickets: List[TicketSchema]


class CityIATACodeSchema(BaseModel):
    code: str
    name: str
    country_code: str
    country_name: str
    city_code: str
    city_name: str
    state_code: Any
    index_strings: List[str]
    weight: int
    cases: Any
