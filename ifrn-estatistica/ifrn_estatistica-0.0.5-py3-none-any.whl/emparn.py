from datetime import datetime
from typing import Dict, List, NewType, Text

from httpx import Client

Datetime = NewType("Datetime", datetime)


STATIONS = "http://186.209.104.157/api/relatorios/precipitacao/filtro-estacoes"
DAILY_RAINFALL = "http://186.209.104.157/api/relatorios/precipitacao/diaria"
ANNUAL_RAINFALL = "http://186.209.104.157/api/relatorios/precipitacao/anual"
ACCUMULATED_RAINFALL = (
    "http://186.209.104.157/api/relatorios/precipitacao/acumulada"
)
HISTORICAL_MEDIA_RAINFALL = (
    "http://186.209.104.157/api/relatorios/precipitacao/media-historica"
)
RESUME_STATE_RAINFALL = "http://186.209.104.157/api/relatorios/precipitacao/resumo-pluviometrico-estado"


def get(url: Text) -> Dict:
    """Função para requisições GET.

    :param url: TEXT - url de alvo.
    :return: Dict
    """
    with Client() as client:
        response = client.get(url)
    return response.json()


def post(url: Text, data: Dict) -> Dict:
    """Função para execução de requisições POST.

    :param url: TEXT - url de alvo.
    :param data: dict - payload da requisição
    :return: Dict
    """
    with Client() as client:
        response = client.post(url, json=data)
    return response.json()


def accumulated_annual_rainfall(
    places: List[int], start_day: Datetime, final_day: Datetime
):

    """Função para retorno do acumulado das estações."""
    data = {"postosIds": places, "diaInicio": start_day, "diaFim": final_day}
    response = post(url=ANNUAL_RAINFALL, data=data)
    return [
        a["precipitacaoAcumuladaAno"]
        for a in response["relatoriosAnuais"][0]["dadosPrecipitacao"]
    ]


def get_city_stations() -> Dict:

    """Função para geração de dicionários com as estações das cidades.

    :return: Dict
    """

    data = get(STATIONS)
    cities = data["municipios"]
    stations = data["estacoes"]

    city_stations = {}

    for city in cities:
        for station in stations:
            if city["id"] == station["municipio"]:
                if city["nome"] in city_stations:
                    city_stations[city["nome"]].append(station["id"])
                else:
                    city_stations[city["nome"]] = [station["id"]]
    return city_stations
