from typing import List
from ekp_sdk.dto.moralis_nft_dto import MoralisNftDto
from ekp_sdk.services.limiter import Limiter
from ekp_sdk.services.rest_client import RestClient


class MoralisApiService:
    def __init__(
        self,
        api_key: str,
        rest_client: RestClient
    ):
        self.base_url = "https://deep-index.moralis.io/api/v2"
        self.api_key = api_key
        self.rest_client = rest_client
        self.limiter = Limiter(250, 10)
        
    # -----------------------------------------------------------------
    
    async def get_nfts_by_owner_and_token_address(
        self,
        owner_address: str,
        token_address: str,
        chain: str
    ) -> List[MoralisNftDto]:
        
        
        url = f"{self.base_url}/{owner_address}/nft/{token_address}?chain={chain}&format=decimal"

        result = await self.__get(url)
        
        

        return result
    
    # -----------------------------------------------------------------
    
    async def __get(self, url):
        try:
            await self.limiter.acquire()
            headers = {"X-API-Key": self.api_key}
            result = await self.rest_client.get(
                url, 
                lambda data, text: data["result"],
                headers=headers
            )
        finally:
            self.limiter.release()
        return result
