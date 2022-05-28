from datetime import datetime
from typing import List

from frenchbee import (
    FrenchBee,
    Flight,
    PassengerInfo,
    Trip,
    DateAndLocation,
    Location,
    FrenchBeeData,
)


def main() -> None:
    import argparse
    from pprint import pprint

    parser = argparse.ArgumentParser(description="Get French Bee airline prices.")
    subparsers = parser.add_subparsers(dest="command")

    data_parser = subparsers.add_parser("data", help="Get metadata about French Bee locations.")
    data_parser.add_argument(
        "--locations", action="store_true", help="Get all supported locations."
    )

    flight_parser = subparsers.add_parser("flight", help="Get flight information.")
    flight_parser.add_argument("origin", help="Origin airport.")
    flight_parser.add_argument("destination", help="Destination airport.")
    flight_parser.add_argument(
        "departure_date",
        type=lambda s: datetime.strptime(s, "%Y-%m-%d"),
        default=None,
        help="Departure date from origin airport. YYYY-mm-dd",
    )
    flight_parser.add_argument(
        "return_date",
        type=lambda s: datetime.strptime(s, "%Y-%m-%d"),
        default=None,
        help="Return date from destination airport. YYYY-mm-dd",
    )
    flight_parser.add_argument(
        "--passengers",
        type=int,
        default=1,
        help="Number of adult passengers. default=1",
    )
    flight_parser.add_argument(
        "--children", type=int, default=0, help="Number of child passengers. default=0"
    )

    args = parser.parse_args()

    if args.command == "data":
        data_client: FrenchBeeData = FrenchBeeData()
        data: List[Location] = list(data_client.get_locations())
        for location in data:
            print(location.json())
        exit()

    trip: Trip = Trip(
        origin_depart=DateAndLocation(
            date=args.departure_date, location=Location(args.origin)
        ),
        destination_return=DateAndLocation(
            date=args.return_date, location=Location(args.destination)
        ),
        passengers=PassengerInfo(Adults=args.passengers, Children=args.children),
    )

    client: FrenchBee = FrenchBee()
    departure_info: Flight = client.get_departure_info_for(trip)
    if departure_info:
        print(departure_info.json())
        return_info: Flight = client.get_return_info_for(trip)
        if return_info:
            print(return_info.json())
            print(
                f"Total price: ${departure_info.price + return_info.price} "
                + f"for {departure_info.day} to {return_info.day} "
                + f"from {departure_info.departure_airport} to {return_info.departure_airport}"
            )

            trip = client.get_flight_times(trip)
            pprint(trip.json())


if __name__ == "__main__":
    main()
