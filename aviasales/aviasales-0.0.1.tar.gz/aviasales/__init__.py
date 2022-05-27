import logging
from typing import Optional

import aiohttp
import faker

from .schemas import TicketSearchSchema, CityIATACodeSchema


class AviaSalesAPI:
    """
    Класс для работы с апишкой
    """

    def __init__(self):
        self.__api_start_url: str = "https://delta.aviasales.ru/search/v2/start"
        self.__fake = faker.Faker()
        self.__headers = {
            "user-agent": self.__fake.chrome(),
            "x-origin-cookie": "language=ru; auid=rBMutmKLi8Q6ngAgCiD7Ag==; _sp_ses.dc27=*; currency=RUB; nuid=85cced0b-3b78-4a00-9566-040ea742ca24; _awt=33a13b6-6ab3e7064373689424566366e634637a9633513a23d23f40a304a2dc13613136a3439c346; marker=direct; currency=rub; uncheck_hotel_cookie=true; last_search=MOW0806IST1; search_init_stamp=1653312534355; _sp_id.dc27=1e0d2afe-477c-4ed6-bf99-0011fa3b9d71.1653312457.1.1653312535.1653312457.09168b9c-8926-4e99-9fa4-eee2537caf26",
        }

    async def start(
        self, origin: str, destination: str, departure_at: str
    ) -> Optional[str]:
        """
        Функция для получения uuid поиска
        :param origin: IATA код вылета
        :param destination: IATA посадки
        :param departure_at: время в формате ГГГГ-ММ-ДД // 2022-06-15
        :return:
        """

        body = {
            "search_params": {
                "directions": [
                    {"origin": origin, "destination": destination, "date": departure_at}
                ],
                "passengers": {"adults": 1, "children": 0, "infants": 0},
                "trip_class": "Y",
            },
            "client_features": {
                "direct_flights": True,
                "brand_ticket": True,
                "top_filters": True,
                "badges": True,
                "tour_tickets": True,
                "assisted": True,
            },
            "marker": "15468.ydof13322170818",
            "market_code": "ru",
            "citizenship": "ru",
            "currency_code": "rub",
            "languages": {"ru": 1},
            "debug": {
                "experiment_groups": {
                    "serp-exp-virtualInterline": "on",
                    "serp-exp-pinFlight": "on",
                    "serp-exp-fares": "on",
                    "serp-exp-baggageUpsale": "on",
                    "asb-exp-footerButton": "off",
                    "asb-exp-ticketsVersion": "v2",
                    "asb-exp-insurance": "separate",
                    "avs-exp-downgradedGates": "on",
                    "asb-exp-feedback": "form",
                    "avs-exp-comparisonWidget": "on",
                    "avs-exp-aa": "on",
                    "ex-exp-autosearchWidget": "on",
                    "serp-exp-travelRestrictions": "on",
                    "avs-exp-checkbox": "tvil",
                    "guides-exp-travelMapBanner": "treatment-labels",
                    "guides-exp-feed": "off",
                    "serp-exp-marketingOperatingCarrier": "on",
                    "prem-exp-webFloatingElement": "more",
                    "b2b-exp-signin": "on",
                    "avs-exp-newAutocomplete": "on",
                    "serp-exp-softFilters": "on",
                    "serp-exp-scoring": "off",
                }
            },
            "brand": "AS",
        }
        for attempt in range(3):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        self.__api_start_url, json=body, headers=self.__headers
                    ) as resp:
                        if resp.status != 200:
                            logging.warning(f"Iter error in [start]")
                            continue
                        result = await resp.json()
                        return result["search_id"]
            except Exception as e:
                logging.error(e)

    async def get_flight_legs(self, search_uuid: str) -> Optional[TicketSearchSchema]:
        """
        Получаем пересадки при помощи uuid поиска
        :param search_uuid: uuid поиска
        :return:
        """
        url = "https://delta.ams.aviasales.ru/search/v3/results"
        body = {
            "search_id": search_uuid,
            "rnd": "3pax5",
            "last_update_timestamp": 1653309255,
            "order": "best",
            "limit": 10,
            "brand_ticket_agent_ids": [180],
            "filters": {"without_short_layover": False},
        }

        for attempt in range(3):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        url=url, json=body, headers=self.__headers
                    ) as resp:
                        if resp.status == 200:
                            result = await resp.json()
                            if len(result) == 0:
                                logging.warning(
                                    f"Iter error in [get_flight_legs] for uuid [{search_uuid}]"
                                )
                                continue
                            return TicketSearchSchema(
                                **result[0] if len(result) == 1 else result[1]
                            )
            except Exception as e:
                logging.error(e)

    async def get_term_code(self, term) -> Optional[CityIATACodeSchema]:
        """
        Функция для трансляции IATA кода в названия города и наоборот
        :param term: IATA код аэропорта или названия города
        :return:
        """
        url = f"https://suggest.aviasales.ru/v2/places.json?locale=ru_RU&max=7&term={term}&types[]=airport&types[]"
        for attempt in range(3):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as resp:
                        if resp.status != 200:
                            continue
                        result = await resp.json()
                        if len(result) == 0:
                            logging.warning(
                                f"Iter error in [get_term_code] for term [{term}]"
                            )
                            continue
                        return CityIATACodeSchema(**result[0])
            except Exception as e:
                logging.error(e)

