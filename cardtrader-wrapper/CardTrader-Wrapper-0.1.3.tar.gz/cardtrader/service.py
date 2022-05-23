import logging
import platform
from json import JSONDecodeError
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode

from ratelimit import limits, sleep_and_retry
from requests import get
from requests.exceptions import ConnectionError, HTTPError

from cardtrader import __version__
from cardtrader.exceptions import ServiceError
from cardtrader.schemas.blueprint import Blueprint
from cardtrader.schemas.category import Category
from cardtrader.schemas.expansion import Expansion
from cardtrader.schemas.game import Game
from cardtrader.schemas.info import Info
from cardtrader.schemas.product import Product
from cardtrader.sqlite_cache import SQLiteCache

LOGGER = logging.getLogger(__name__)
MINUTE = 60


class CardTrader:
    API_URL = "https://api.cardtrader.com/api/v2"

    def __init__(self, access_token: str, cache: Optional[SQLiteCache] = None):
        self.headers = {
            "Accept": "application/json",
            "User-Agent": f"CardTrader-Wrapper/{__version__}"
            f"/{platform.system()}: {platform.release()}",
            "Authorization": f"Bearer {access_token}",
        }
        self.cache = cache

    @sleep_and_retry
    @limits(calls=20, period=MINUTE)
    def _perform_get_request(self, url: str, params: Dict[str, str] = None) -> Dict[str, Any]:
        if params is None:
            params = {}

        try:
            response = get(url, params=params, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except ConnectionError as ce:
            raise ServiceError(f"Unable to connect to `{url}`: {ce.response.text}")
        except HTTPError as he:
            raise ServiceError(he.response.text)
        except JSONDecodeError as de:
            raise ServiceError(f"Invalid response from `{url}`: {de}")

    def _get_request(
        self,
        endpoint: str,
        params: Dict[str, str] = None,
        skip_cache: bool = False,
    ) -> Dict[str, Any]:
        cache_params = f"?{urlencode(params)}" if params else ""

        url = self.API_URL + endpoint
        cache_key = f"{url}{cache_params}"

        if self.cache and not skip_cache:
            if cached_response := self.cache.select(cache_key):
                return cached_response

        response = self._perform_get_request(url=url, params=params)
        if not response:
            return {}

        if self.cache and not skip_cache:
            self.cache.insert(cache_key, response)

        return response

    def info(self) -> Optional[Info]:
        response = self._get_request(endpoint="/info", skip_cache=True)
        if response:
            return Info.from_dict(response)
        return None

    def games(self) -> List[Game]:
        response = self._get_request(endpoint="/games")
        if response:
            return Game.schema().load(response["array"], many=True)
        return []

    def categories(self, game_id: Optional[int] = None) -> List[Category]:
        response = self._get_request(
            endpoint="/categories", params={"game_id": str(game_id)} if game_id else None
        )
        if response:
            return Category.schema().load(response, many=True)
        return []

    def expansions(self) -> List[Expansion]:
        response = self._get_request(endpoint="/expansions")
        if response:
            return Expansion.schema().load(response, many=True)
        return []

    def blueprints(self, expansion_id: int) -> List[Blueprint]:
        response = self._get_request(
            endpoint="/blueprints/export", params={"expansion_id": expansion_id}
        )
        if response:
            return Blueprint.schema().load(response, many=True)
        return []

    def products_by_expansion(self, expansion_id: int) -> List[Product]:
        response = self._get_request(
            endpoint="/marketplace/products", params={"expansion_id": expansion_id}
        )
        if response:
            return Product.schema().load(list(response.values())[0], many=True)
        return []

    def products_by_blueprint(self, blueprint_id: int) -> List[Product]:
        response = self._get_request(
            endpoint="/marketplace/products", params={"blueprint_id": blueprint_id}
        )
        if response:
            return Product.schema().load(list(response.values())[0], many=True)
        return []
