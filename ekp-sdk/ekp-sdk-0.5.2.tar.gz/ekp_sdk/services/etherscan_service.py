from ekp_sdk.services.limiter import Limiter
from ekp_sdk.services.rest_client import RestClient
from ast import literal_eval

class EtherscanService:
    def __init__(
        self,
        api_key,
        base_url,
        rest_client: RestClient
    ):
        self.api_key = api_key
        self.base_url = base_url
        self.rest_client = rest_client
        self.limiter = Limiter(250, 10)

    async def get_latest_block_number(self):
        url = f"{self.base_url}?module=proxy&action=eth_blockNumber&apikey={self.api_key}"
        result = await self.rest_client.get(url, lambda data, text: literal_eval(data["result"]), self.limiter)

        return result
    
    async def get_contract_name(self, address):
        url = f"{self.base_url}?module=contract&action=getsourcecode&address={address}&apikey={self.api_key}"

        result = await self.rest_client.get(url, lambda data, text: data["result"][0]["ContractName"], self.limiter)

        return result

    async def get_abi(self, address):
        url = f"{self.base_url}?module=contract&action=getabi&address={address}&apikey={self.api_key}"

        result = await self.rest_client.get(url, lambda data, text: data["result"], self.limiter)

        return result

    async def get_transactions(self, address, start_block, offset):

        url = f'{self.base_url}?module=account&action=txlist&address={address}&startblock={start_block}&page=1&offset={offset}&sort=asc&apiKey={self.api_key}'

        def fn(data, text):
            trans = data["result"]
            
            if (trans is None) or not (isinstance(trans, list)):
                print(f"🚨 {text}")
                raise Exception("Received None data from url")

            return trans

        result = await self.rest_client.get(url, fn, self.limiter)

        return result

    async def get_logs(self, address, start_block):

        url = f'{self.base_url}?module=logs&action=getLogs&address={address}&fromBlock={start_block}&toBlock=latest&apiKey={self.api_key}'

        def fn(data, text):
            trans = data["result"]
            
            if (trans is None or not isinstance(trans, list)):
                print(f"🚨 {text}")
                raise Exception("Received None data from url")

            return trans

        result = await self.rest_client.get(url, fn, self.limiter)

        return result
