from directory_api_client.base import AbstractAPIClient

url_country_data_by_country = 'dataservices/country-data/'
url_cia_world_factbook_data = 'dataservices/cia-factbook-data/'
url_society_data_by_country = 'dataservices/society-data-by-country/'
url_last_year_import_data_by_country = 'dataservices/lastyearimportdatabycountry/'
url_suggested_countries = '/dataservices/suggested-countries/'
url_trading_blocs_by_country = '/dataservices/trading-blocs/'
url_trade_barriers = '/dataservices/trade-barriers/'
url_market_trends = '/dataservices/uk-market-trends/'
url_trade_highlights = '/dataservices/uk-trade-highlights/'
url_commodity_exports_data_by_country = '/dataservices/commodity-exports-data-by-country/'
url_top_five_services = '/dataservices/top-five-services/'
url_top_five_goods = '/dataservices/top-five-goods/'


class DataServicesAPIClient(AbstractAPIClient):
    def get_country_data_by_country(self, countries, fields):
        return self.get(url=url_country_data_by_country, params={'countries': countries, 'fields': fields})

    def get_cia_world_factbook_data(self, country, data_key):
        return self.get(
            url=url_cia_world_factbook_data, params={'country': country, 'data_key': data_key}, use_fallback_cache=True
        )

    def get_society_data_by_country(self, countries: list):
        return self.get(url=url_society_data_by_country, params={'countries': countries}, use_fallback_cache=True)

    def get_last_year_import_data_by_country(self, commodity_code, countries: list):
        return self.get(
            url=url_last_year_import_data_by_country, params={'commodity_code': commodity_code, 'countries': countries}
        )

    def suggested_countries_by_hs_code(self, hs_code):
        return self.get(
            url=url_suggested_countries,
            params={
                'hs_code': hs_code,
            },
        )

    def trading_blocs_by_country(self, iso2):
        return self.get(
            url=url_trading_blocs_by_country,
            params={
                'iso2': iso2,
            },
        )

    def get_trade_barriers(self, sectors: list, countries: list):
        return self.get(url=url_trade_barriers, params={'sectors': sectors, 'countries': countries})

    def get_market_trends_by_country(self, iso2, from_year=None):
        params = {'iso2': iso2}
        if from_year:
            params['from_year'] = from_year

        return self.get(
            url=url_market_trends,
            params=params,
        )

    def get_trade_highlights_by_country(self, iso2):
        params = {'iso2': iso2}

        return self.get(
            url=url_trade_highlights,
            params=params,
        )

    def get_commodity_exports_data_by_country(self, iso2):
        return self.get(
            url=url_commodity_exports_data_by_country,
            params={'iso2': iso2},
        )

    def get_top_five_services_by_country(self, iso2):
        return self.get(url=url_top_five_services, params={'iso2': iso2})

    def get_top_five_goods_by_country(self, iso2):
        return self.get(url=url_top_five_goods, params={'iso2': iso2})
