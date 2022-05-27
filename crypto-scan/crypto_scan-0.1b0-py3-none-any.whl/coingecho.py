import requests
import pandas as pd

# https://www.coingecko.com/en/api/documentation


class CoinGecko:

    def __init__(self):
        self.url = "https://api.coingecko.com/api/v3"
        # default parameters
        self.default_parameters = {
        }

    def get_params(self, **kwargs):
        return {**self.default_parameters, **kwargs}

    def get_coins(self):
        url = f"{self.url}/coins/list"
        r = requests.get(url)
        return pd.DataFrame(r.json())

    def get_coin_history(self, coin_id, date):
        url = f"{self.url}/coins/{coin_id}/history"
        params = {
            "date": date
        }
        r = requests.get(url, params=self.get_params(**params))
        return r.json()
