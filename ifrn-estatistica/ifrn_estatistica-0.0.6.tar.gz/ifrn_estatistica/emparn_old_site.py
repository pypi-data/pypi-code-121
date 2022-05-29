from asyncio import gather, run
from copy import deepcopy
from datetime import date
from os.path import isfile
from typing import Dict, List, Text, Tuple
from urllib.parse import urljoin

from httpx import AsyncClient
from lxml import html
from pandas import DataFrame
from parsel import Selector


async def download(url: Text) -> Text:
    """Função assíncona para download.

    :param url: para download.
    :return: text
    """
    async with AsyncClient() as client:
        response = await client.get(url, timeout=None)
        return response


async def get_dataset(urls: List) -> List:
    """Função assíncona para realizar vários downloads.

    :param urls: lista com urls para os downloads
    :return: list
    """
    return await gather(*[download(url) for url in urls])


class Emparn:
    """Scraping de dados do site da Emparn.

    example1: para coleta de links para dados brutos e acumulados do ano.

    from ifrn_estatistica.emparn import Emparn


    emparn = Emparn(cities=["NATAL", "MOSSORO"], starting_year=2019, keep=True)
    links_datasets, datasets = emparn.get_city_data()

    links_datasets
    {
        "NATAL": [
            "http://meteorologia.emparn.rn.gov.br:8181/monitoramento/2019/graficos/d8101.html",
            "http://meteorologia.emparn.rn.gov.br:8181/monitoramento/2020/graficos/d8101.html",
        ],
        "MOSSORO": [
            "http://meteorologia.emparn.rn.gov.br:8181/monitoramento/2019/graficos/d8007.html",
            "http://meteorologia.emparn.rn.gov.br:8181/monitoramento/2020/graficos/d8007.html",
        ],
    },

    datasets
    {
        "NATAL": {2019: "1729.6", 2020: "2161.2"},
        "MOSSORO": {2019: " 747.2", 2020: "1169.0"},
    },

    examplo2: coleta de dados brutos das cidades.
    from ifrn_estatistica.emparn import Emparn


    emparn = Emparn(cities=["NATAL", "MOSSORO"], starting_year=2019, keep=True)
    raw_datasets = emparn.raw_city_data()
    raw_datasets
    {
        "NATAL": {
            2019: [
                25.4,
                179.0,
                239.7,
                470.7,
                207.1,
                275.6,
                190.5,
                64.7,
                51.2,
                19.9,
                2.6,
                3.2,
            ],
            2020: [
                184.7,
                202.4,
                433.5,
                228.2,
                428.2,
                276.0,
                235.2,
                33.2,
                41.0,
                34.6,
                39.8,
                24.4,
            ],
        },
        "MOSSORO": {
            2019: [
                68.3,
                99.7,
                237.2,
                225.4,
                56.5,
                37.7,
                0.8,
                0.0,
                0.0,
                0.0,
                0.0,
                21.6,
            ],
            2020: [
                27.9,
                137.8,
                406.6,
                277.0,
                161.7,
                82.5,
                67.2,
                0.5,
                1.3,
                0.0,
                6.5,
                0.0,
            ],
        },
    }
    """

    def __init__(
        self,
        cities: List,
        starting_year=1992,
        final_year=int(date.today().year),
        keep=False,
    ):
        """Inicialização do obj.

        :param cities: list - lista de cidades
        :param starting_year: int - ano de inicio do scraping
        :param final_year: int - ano de termino do scraping
        :param keep: bool - para salvar o resultado em arquivo
        """
        self.cities = cities
        self.keep = keep
        self.starting_year = starting_year
        self.final_year = final_year

    def get_urls_accumulated(self) -> List:
        """Método para geração das URLs.

        :return: list
        """

        usrbase = "http://meteorologia.emparn.rn.gov.br:8181/monitoramento/{year}/acumulapr.htm"

        return [
            usrbase.replace("{year}", str(year))
            for year in range(self.starting_year, self.final_year)
        ]

    def _process_city_data(self, data: List, city: Text) -> List:
        """Método para tratamento dos dados acumulados.

        :param data: list - com os dados
        :param data: text - nome da cidade
        :return: list
        """

        selector = Selector(text=data)
        scraping_url = selector.xpath(
            "//body/p//td[contains(text(),"
            f"'{city.upper()}')]/following-sibling::td[5]/a/@href"
        ).get()
        scraping_accumulated = selector.xpath(
            f"//body/p//td[contains(text(),"
            f"'{city.upper()}')]/following-sibling::td[1]/text()"
        ).get()
        if isinstance(scraping_accumulated, list):
            for i in len(scraping_accumulated):
                if scraping_accumulated[i] != 0:
                    try:
                        accumulated = float(scraping_accumulated[i])
                    except TypeError:
                        accumulated = 0
                    return scraping_url[i], accumulated
        else:
            try:
                accumulated = float(scraping_accumulated)
            except TypeError:
                accumulated = 0
            return scraping_url, accumulated

    def get_city_data(self) -> Tuple:

        """Método para scriping de dados das cidades.

        :return: tuple tupla com dois dicts um com links
                para download de dados brutos e outro
                com o acumulado do ano.
        """

        urls = self.get_urls_accumulated()
        data = run(get_dataset(urls))
        city_dataset = {}
        dataset = []
        for i in range(len(self.cities)):
            year = self.starting_year
            for d in data:
                if year > 2011:
                    content = html.fromstring(d.content)
                    scraping_url = content.xpath(
                        "//td[text()>0]/../td[contains(text(),"
                        f"'{self.cities[i].upper()}')]/following-sibling::td/a/@href"
                    )[3]
                    resp = content.xpath(
                        "//td[text()>0]/../td[contains(text(),"
                        f"'{self.cities[i].upper()}')]/following-sibling::td/text()"
                    )
                    scraping_accumulated = sum([float(v) for v in resp]) / len(
                        resp
                    )
                else:
                    (
                        scraping_url,
                        scraping_accumulated,
                    ) = self._process_city_data(d.text, self.cities[i])
                dataset.append((scraping_url, scraping_accumulated))
                year += 1
            city_dataset[self.cities[i].upper()] = deepcopy(dataset)
            del dataset[:]

        links = {}
        links_tmp = []
        accumulated = {}
        accumulated_tmp = {}
        starting_year = self.starting_year
        for k in city_dataset.keys():
            for i in range((self.final_year - self.starting_year)):
                url_base = f"http://meteorologia.emparn.rn.gov.br:8181/monitoramento/{starting_year}/"
                links_tmp.append(urljoin(url_base, city_dataset[k][i][0]))
                accumulated_tmp[starting_year] = city_dataset[k][i][1]
                starting_year += 1
            starting_year = self.starting_year
            links[k] = deepcopy(links_tmp)
            del links_tmp[:]
            accumulated[k] = deepcopy(accumulated_tmp)

        if self.keep:
            if not isfile(f"{date.today()}_links_raw_data.csv"):
                df = DataFrame(links)
                df.to_csv(f"{date.today()}_links_raw_data.csv")

            if not isfile(f"{date.today()}_accumulated.csv"):
                df = DataFrame(accumulated)
                df.to_csv(f"{date.today()}_accumulated.csv")

        return links, accumulated

    def raw_city_data(self) -> Dict:

        """Método para scriping de dados brutos das cidades.

        :return: Dict - dicionário com os dados burtos das cidades.
        """

        links, _ = self.get_city_data()
        data = run(
            get_dataset(
                [
                    v[i]
                    for v in links.values()
                    for i in range((self.final_year - self.starting_year))
                ]
            )
        )
        count_data = 0
        dataset_city = {}
        dataset_years = {}
        dataset_months = []
        for city in self.cities:
            for year in range(self.starting_year, self.final_year):
                months = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
                if year % 4 == 0:
                    months = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
                content = html.fromstring(data[count_data].content)
                scraping = content.xpath("//td[text()>=0 or text()<0]/text()")
                month_counter = 0
                accumulated_month = 0
                for m in range(12):
                    for i in range(month_counter, months[m] + month_counter):
                        try:
                            if float(scraping[i]) < 0:
                                scraping[i] = 0
                            accumulated_month += float(scraping[i])
                        except IndexError:
                            break
                        except ValueError:
                            continue
                    month_counter += months[m]
                    dataset_months.append(round(accumulated_month, 3))
                    accumulated_month = 0
                dataset_years[year] = deepcopy(dataset_months)
                del dataset_months[:]
                count_data += 1
            dataset_city[city] = deepcopy(dataset_years)

        if self.keep:
            for k in dataset_city.keys():
                df = DataFrame(dataset_city[k])
                if not isfile(f"{date.today()}_raw_data_{k}.csv"):
                    df.to_csv(f"{date.today()}_raw_data_{k}.csv")
        return dataset_city

    def __repr__(self):
        return "Class Emparn"
