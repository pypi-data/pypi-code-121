from multichain_explorer.src.services.fetch_service import FetchService

class CoinMarketCapService():
    """
    This class is used to fetch data from the CoinMarketCap API 
    """
    API_URL: str = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
    API_KEY: str = ''

    def __init__(self):
        self.currency = "USD"
        self.fetchService = FetchService()

    def fetchData(self, symbol: str) -> dict:
        """
        Fetch data from the CoinMarketCap API

        Args:
            symbol: the symbol of the cryptocurrency

        Returns:
            The data as a dict
        """
        try:
            params = self.get_params(symbol)
            headers = self.get_headers()

            #TODO - Use class member service
            # data = self.fetchService.fetch_json(self.API_URL, params, headers)
            data = FetchService().fetch_json(
                                        self.API_URL,
                                        params,
                                        headers
                                    )
            return data
        except Exception as e:
            print(e)
            raise


    def get_params(self, symbol: str) -> dict:
        """
        Get the parameters for the API call

        Args:
            symbol: the symbol of the cryptocurrency

        Returns:
            The parameters as a dict
        """
        parameters = {
            'symbol': symbol,
            'convert': self.currency
        }
        return parameters


    def get_headers(self) -> dict:
        """
        Get the headers for the API call

        Returns:
            The headers as a dict
        """
        headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': self.API_KEY
        }
        return headers

