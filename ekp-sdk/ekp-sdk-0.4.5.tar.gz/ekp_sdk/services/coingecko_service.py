import json

from ekp_sdk.services.rest_client import RestClient


class CoingeckoService:
    def __init__(
        self,
        rest_client: RestClient
    ):
        self.base_url = "https://api.coingecko.com/api/v3"
        self.rest_client = rest_client

    async def get_coin_id_map(self, platform_id):

        url = f"{self.base_url}/coins/list?include_platform=true"

        response = await self.rest_client.get(url)

        map = {}

        for coin in response:
            if (platform_id not in coin["platforms"]):
                continue

            map[coin["platforms"][platform_id]] = coin["id"]

        return map

    async def get_historic_price(self, coin_id, date_str, fiat_id):

        url = f"{self.base_url}/coins/{coin_id}/history?date={date_str}"

        result = await self.rest_client.get(url, lambda data, text: data['market_data']['current_price'][fiat_id])

        return result

    async def get_latest_price(self, coin_id, fiat_id):

        url = f"{self.base_url}/simple/price?ids={coin_id}&vs_currencies={fiat_id}"

        result = await self.rest_client.get(url, lambda data, text: data[coin_id][fiat_id])

        return result
