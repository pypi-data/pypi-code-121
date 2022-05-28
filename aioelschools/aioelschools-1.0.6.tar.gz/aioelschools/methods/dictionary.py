from ..utils import check_response
from .basemodel import BaseModel
from ..models import (
    DictionaryTypeGetModel, MarkKindGetModel, SystemPeriodGetModel,
    PayAgentGetModel, FoodTransactionTypeGetModel, MarkTypeValueGetModel
)


class DictionaryCategory(BaseModel):
    async def daytype_get(self, **kwargs) -> DictionaryTypeGetModel:
        method = "dictionary.daytype.get"

        query = self.get_set_params(locals())
        status, response = await self._request("get", method, query)

        # logger.debug(f"Got response from {url}: {response}")
        return await check_response(status, response, DictionaryTypeGetModel)

    async def markkind_get(self, **kwargs) -> MarkKindGetModel:
        method = "dictionary.markkind.get"

        query = self.get_set_params(locals())
        status, response = await self._request("get", method, query)

        # logger.debug(f"Got response from {url}: {response}")
        return await check_response(status, response, MarkKindGetModel)

    async def systemperiod_get(self, **kwargs) -> SystemPeriodGetModel:
        method = "dictionary.systemperiod.get"

        query = self.get_set_params(locals())
        status, response = await self._request("get", method, query)

        # logger.debug(f"Got response from {url}: {response}")
        return await check_response(status, response, SystemPeriodGetModel)

    async def billtype_get(self, **kwargs) -> DictionaryTypeGetModel:
        method = "dictionary.billtype.get"

        query = self.get_set_params(locals())
        status, response = await self._request("get", method, query)

        # logger.debug(f"Got response from {url}: {response}")
        return await check_response(status, response, DictionaryTypeGetModel)

    async def payagent_get(self, **kwargs) -> PayAgentGetModel:
        method = "dictionary.payagent.get"

        query = self.get_set_params(locals())
        status, response = await self._request("get", method, query)

        # logger.debug(f"Got response from {url}: {response}")
        return await check_response(status, response, PayAgentGetModel)

    async def foodtransaction_get(self, **kwargs) -> FoodTransactionTypeGetModel:
        method = "dictionary.foodtransactiontype.get"

        query = self.get_set_params(locals())
        status, response = await self._request("get", method, query)

        # logger.debug(f"Got response from {url}: {response}")
        return await check_response(status, response, FoodTransactionTypeGetModel)

    async def examtype_get(self, **kwargs) -> DictionaryTypeGetModel:
        method = "dictionary.examtype.get"

        query = self.get_set_params(locals())
        status, response = await self._request("get", method, query)

        # logger.debug(f"Got response from {url}: {response}")
        return await check_response(status, response, DictionaryTypeGetModel)

    async def markresulttype_get(self, **kwargs) -> DictionaryTypeGetModel:
        method = "dictionary.markresulttype.get"

        query = self.get_set_params(locals())
        status, response = await self._request("get", method, query)

        # logger.debug(f"Got response from {url}: {response}")
        return await check_response(status, response, DictionaryTypeGetModel)

    async def marktypevalue_get(self, **kwargs) -> MarkTypeValueGetModel:
        method = "dictionary.marktypevalue.get"

        query = self.get_set_params(locals())
        status, response = await self._request("get", method, query)

        # logger.debug(f"Got response from {url}: {response}")
        return await check_response(status, response, MarkTypeValueGetModel)