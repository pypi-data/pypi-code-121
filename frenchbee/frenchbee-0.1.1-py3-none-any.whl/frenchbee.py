from dataclasses import dataclass
from datetime import datetime
import json
from requests import Session, Response
from typing import Any, Iterable, List, Tuple, Union, Dict
import re
import html
import jsonpath_ng as jsonpath

from .reese84 import FrenchBeeReese84
from .models import Location, PassengerInfo, Flight, DateAndLocation, Segment, Trip


@dataclass
class FrenchBeeResponse:
    command: str
    selector: str
    method: str
    args: List[
        Union[str, dict]
    ]  # dict(departure => [year => { month => { day => { data... }} }])
    data: str


class FrenchBee:
    def __init__(self) -> None:
        self.session = Session()
        self.session.headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        }
        self.session.cookies["base_host"] = "frenchbee.com"
        self.session.cookies["market_lang"] = "en"
        self.session.cookies["site_origin"] = "us.frenchbee.com"

    def _make_search_request(
        self,
        source: str,
        destination: str,
        passengers: PassengerInfo,
        departure: datetime,
        returns: datetime,
        module: str,
    ) -> List[FrenchBeeResponse]:
        url: str = "https://us.frenchbee.com/en?ajax_form=1"
        departure_date: str = f"{departure:%Y-%m-%d}" if departure else ""
        return_date: str = f"{returns:%Y-%m-%d}" if returns else ""
        payload: Dict[str, Any] = {
            "visible_newsearch_flights_travel_type": "R",
            "visible_newsearch_flights_from": source,
            "visible_newsearch_flights_to": destination,
            "newsearch_flights_travel_type": "R",
            "newsearch_flights_from": source,
            "newsearch_flights_to": destination,
            "newsearch_flights_departure_date": departure_date,
            "newsearch_flights_return_date": return_date,
            "adults-count": passengers.Adults,
            "children-count": passengers.Children,
            "infants-count": passengers.Infants,
            "um_youth-count": 0,
            "form_id": "frenchbee-amadeus-search-flights-form",
            "_triggering_element_name": module,
        }
        response: Response = self.session.post(url, data=payload)
        return [
            FrenchBeeResponse(
                command=resp.get("command"),
                method=resp.get("method"),
                selector=resp.get("selector"),
                args=resp.get("args") or [],
                data=resp.get("data"),
            )
            for resp in response.json()
        ]

    def _normalize_response(self, response: Dict[str, Any]) -> Dict[datetime, Flight]:
        if not response:
            return None
        normalize: Dict[datetime, Flight] = {}
        for (
            key_year,
            months,
        ) in (
            response.items()
        ):  # key_year: str, months: Dict[str, Dict[str, Dict[str, Any]]]
            year: int = int(key_year)
            for (
                key_month,
                days,
            ) in months.items():  # key_month: str, days: Dict[str, Dict[str, Any]]
                month: int = int(key_month)
                for (
                    key_day,
                    flight,
                ) in days.items():  # key_day: str, flight: Dict[str, Any]
                    day: int = int(key_day)
                    normalize[datetime(year, month, day)] = Flight(
                        arrival_airport=flight.get("arrival_airport"),
                        currency=flight.get("currency"),
                        day=datetime.strptime(flight.get("day"), "%Y-%m-%d"),
                        departure_airport=flight.get("departure_airport"),
                        is_offer=flight.get("is_offer"),
                        price=float(flight.get("price")),
                        tax=float(flight.get("tax")),
                    )
        return normalize

    def get_departure_availability(self, trip: Trip) -> Dict[datetime, Flight]:
        payload: List[FrenchBeeResponse] = self._make_search_request(
            source=trip.origin_depart.location.code,
            destination=trip.destination_return.location.code,
            passengers=trip.passengers,
            departure=None,
            returns=None,
            module="visible_newsearch_flights_to",
        )
        info: FrenchBeeResponse = next(
            filter(lambda r: r.args[0] == "departureCalendarPriceIsReady", payload),
            None,
        )
        return (
            self._normalize_response(info.args[1].get("departure"))
            if len(info.args) >= 2 and info.args[1]
            else None
        )

    def get_return_availability(self, trip: Trip) -> Dict[datetime, Flight]:
        payload: List[FrenchBeeResponse] = self._make_search_request(
            source=trip.origin_depart.location.code,
            destination=trip.destination_return.location.code,
            passengers=trip.passengers,
            departure=trip.origin_depart.date,
            returns=None,
            module="visible_newsearch_flights_departure_date",
        )
        info: FrenchBeeResponse = next(
            filter(lambda i: i.args[0] == "returnCalendarPriceIsReady", payload), None
        )
        return (
            self._normalize_response(info.args[1].get("return"))
            if len(info.args) >= 2 and info.args[1]
            else None
        )

    def get_departure_info_for(self, trip: Trip) -> Flight:
        info: Dict[datetime, Flight] = self.get_departure_availability(trip)
        return info.get(trip.origin_depart.date) if info else None

    def get_return_info_for(self, trip: Trip) -> Flight:
        info: Dict[datetime, Flight] = self.get_return_availability(trip)
        return info.get(trip.destination_return.date) if info else None

    def get_flight_times(self, trip: Trip) -> Trip:
        form_url, form_inputs = self._get_flight_times_form_parameters(trip)

        token: str = FrenchBeeReese84().token()
        self.session.cookies.set("reese84", token, domain="vols.frenchbee.com")
        response: Response = self.session.post(form_url, data=form_inputs)

        html_body: str = response.text
        script: Dict[str, Any] = self._get_flight_times_script(html_body)
        with open("s.json", "w") as f:
            f.write(json.dumps(script, indent=4, sort_keys=True))

        bounds: List[Dict[str, Any]] = self._get_json_path(
            script,
            "$.pageDefinitionConfig.pageData.business.Availability.proposedBounds",
        )
        departure_options: List[Dict[str, Any]] = bounds[0].get(
            "proposedFlightsGroup", []
        )
        return_options: List[Dict[str, Any]] = bounds[1].get("proposedFlightsGroup", [])

        trip.origin_segments = list(self._get_segment_options(departure_options))
        trip.destination_segments = list(self._get_segment_options(return_options))

        return trip

    def _get_flight_times_form_parameters(
        self, trip: Trip
    ) -> Tuple[str, Dict[str, str]]:
        payload: List[FrenchBeeResponse] = self._make_search_request(
            source=trip.origin_depart.location.code,
            destination=trip.destination_return.location.code,
            passengers=trip.passengers,
            departure=trip.origin_depart.date,
            returns=trip.destination_return.date,
            module="op",
        )
        resp: FrenchBeeResponse = next(
            filter(lambda i: i.command == "insert", payload), None
        )

        form_match: re.Match = re.search(
            '\<form[^\>]*action="([^"]+)"[^\>]*>', resp.data
        )
        if not form_match:
            return
        form_url: str = form_match.group(1)

        input_match: List[Tuple[str, str]] = re.findall(
            '\<input[^\>]*name="([^"]+)"[^\>]*value="([^"]+)"[^\>]*>', resp.data
        )
        form_inputs: Dict[str, str] = {key: value for key, value in input_match}
        if "EXTERNAL_ID" in form_inputs:
            form_inputs["EXTERNAL_ID"] = html.unescape(form_inputs["EXTERNAL_ID"])

        return (form_url, form_inputs)

    def _get_flight_times_script(self, html_body: str) -> Dict[str, Any]:
        script_start: str = "PlnextPageProvider.init("
        idx_start: int = html_body.index(script_start) + len(script_start)
        idx_start = html_body.index(
            "config", idx_start
        )  # outer layer is not valid JSON
        idx_start = html_body.index("{", idx_start)

        script_end: str = "pageEngine"
        idx_end: int = html_body.index(script_end, idx_start)
        idx_end = (
            html_body.rindex("}", idx_start, idx_end) + 1
        )  # walk backwards to find the end

        script: str = html_body[idx_start:idx_end]
        return json.loads(script)

    def _get_segment_options(
        self, options: List[Dict[str, Any]]
    ) -> Iterable[List[Segment]]:
        for option in options:
            segments_for_option: List[Segment] = option.get("segments", [])
            segments: List[Segment] = []
            for segment_option in segments_for_option:
                segment: Segment = Segment(
                    airline_code=segment_option.get("airline", {}).get("code"),
                    airline_name=segment_option.get("airline", {}).get("name"),
                    flight_num=segment_option.get("flightNumber"),
                    duration=int(segment_option.get("segmentTime") or "0"),
                    start=DateAndLocation(
                        date=self._get_datetime_gmt(segment_option.get("beginDateGMT")),
                        location=Location(
                            code=segment_option.get("beginLocation", {}).get(
                                "locationCode"
                            ),
                            name=segment_option.get("beginLocation", {}).get(
                                "locationName"
                            ),
                            terminal=segment_option.get("beginTerminal"),
                            transport=segment_option.get("equipment", {}).get("name"),
                        ),
                    ),
                    end=DateAndLocation(
                        date=self._get_datetime_gmt(segment_option.get("endDateGMT")),
                        location=Location(
                            code=segment_option.get("endLocation", {}).get(
                                "locationCode"
                            ),
                            name=segment_option.get("endLocation", {}).get(
                                "locationName"
                            ),
                            terminal=segment_option.get("endTerminal"),
                        ),
                    ),
                )
                segments.append(segment)
            yield segments

    def _get_json_path(self, json_object: Any, path: str, default: Any = None) -> Any:
        extractor = jsonpath.parse(path)  # no type given
        matches = extractor.find(json_object)
        if matches:
            if len(matches) == 1:
                return matches[0].value
            return [match.value for match in matches]
        return default

    def _get_datetime_gmt(self, value: str, default: Any = None) -> datetime:
        if value:
            return datetime.strptime(value, "%b %d, %Y %I:%M:%S %p")
        return default
