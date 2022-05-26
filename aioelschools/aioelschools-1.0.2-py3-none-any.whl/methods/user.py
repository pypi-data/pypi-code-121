from ..utils import check_response
from .basemodel import BaseModel
from ..models import (
    SystemPeriodGetModel, NewsGetModel, BillGetModel,
    MarkValueGetModel, DairyGetModel, CardGetModel,
    SkudGetModel, BillReplenishmentGetModel,
    FoodTransactionGetModel, PresenceGetModel,
    MarkExamGetModel, MarkResultGetModel,
    DepartmentGroupGetModel, DepartmentGetModel,
    TwoFactorCheckGetModel
)


class UserCategory(BaseModel):
    async def systemperiod_get(self, userid: int, token: str, **kwargs) -> SystemPeriodGetModel:
        method = "user.systemperiod.get"

        query = self.get_set_params(locals())
        status, response = await self._request("get", method, query)

        # logger.debug(f"Got response from {url}: {response}")
        return await check_response(status, response, SystemPeriodGetModel)

    async def news_get(self, childid: int, token: str, **kwargs) -> NewsGetModel:
        method = "user.news.get"

        query = self.get_set_params(locals())
        status, response = await self._request("get", method, query)

        # logger.debug(f"Got response from {url}: {response}")
        return await check_response(status, response, NewsGetModel)

    async def bill_get(self, userid: int, token: str, **kwargs) -> BillGetModel:
        method = "user.bill.get"

        query = self.get_set_params(locals())
        status, response = await self._request("get", method, query)

        # logger.debug(f"Got response from {url}: {response}")
        return await check_response(status, response, BillGetModel)

    async def markvalue_get(self, userid: int, systemperiodid: int, token: str, **kwargs) -> MarkValueGetModel:
        method = "user.markvalue.get"

        query = self.get_set_params(locals())
        status, response = await self._request("get", method, query)

        # logger.debug(f"Got response from {url}: {response}")
        return await check_response(status, response, MarkValueGetModel)

    async def dairy_get(self, userid: int, token: str, departmentid: int,
                        instituteid: int, year: int, week: int, **kwargs) -> DairyGetModel:
        method = "user.diary.get"

        query = self.get_set_params(locals())
        status, response = await self._request("get", method, query)

        # logger.debug(f"Got response from {url}: {response}")
        return await check_response(status, response, DairyGetModel)

    async def card_get(self, userid: int, token: str, **kwargs) -> CardGetModel:
        method = "user.card.get"

        query = self.get_set_params(locals())
        status, response = await self._request("get", method, query)

        # logger.debug(f"Got response from {url}: {response}")
        return await check_response(status, response, CardGetModel)

    async def skud_get(self, userid: int, token: str, **kwargs) -> SkudGetModel:
        method = "user.skud.get"

        query = self.get_set_params(locals())
        status, response = await self._request("get", method, query)

        # logger.debug(f"Got response from {url}: {response}")
        return await check_response(status, response, SkudGetModel)

    async def billreplenishment_get(self, userid: int, token: str, **kwargs) -> BillReplenishmentGetModel:
        method = "user.billreplenishment.get"

        query = self.get_set_params(locals())
        status, response = await self._request("get", method, query)

        # logger.debug(f"Got response from {url}: {response}")
        return await check_response(status, response, BillReplenishmentGetModel)

    async def foodtransaction_get(self, userid: int, token: str, **kwargs) -> FoodTransactionGetModel:
        method = "user.foodtransaction.get"

        query = self.get_set_params(locals())
        status, response = await self._request("get", method, query)

        # logger.debug(f"Got response from {url}: {response}")
        return await check_response(status, response, FoodTransactionGetModel)

    async def presence_get(self, userid: int, token: str, departmentid: int, **kwargs) -> PresenceGetModel:
        method = "user.presence.get"

        query = self.get_set_params(locals())
        status, response = await self._request("get", method, query)

        # logger.debug(f"Got response from {url}: {response}")
        return await check_response(status, response, PresenceGetModel)

    async def markexam_get(self, userid: int, token: str, **kwargs) -> MarkExamGetModel:
        method = "user.markexam.get"

        query = self.get_set_params(locals())
        status, response = await self._request("get", method, query)

        # logger.debug(f"Got response from {url}: {response}")
        return await check_response(status, response, MarkExamGetModel)

    async def markresult_get(self, userid: int, token: str, **kwargs) -> MarkResultGetModel:
        method = "user.markresult.get"

        query = self.get_set_params(locals())
        status, response = await self._request("get", method, query)

        # logger.debug(f"Got response from {url}: {response}")
        return await check_response(status, response, MarkResultGetModel)

    async def departmentgroup_get(self, userid: int, token: str, **kwargs) -> DepartmentGroupGetModel:
        method = "user.departmentgroup.get"

        query = self.get_set_params(locals())
        status, response = await self._request("get", method, query)

        # logger.debug(f"Got response from {url}: {response}")
        return await check_response(status, response, DepartmentGroupGetModel)

    async def department_get(self, userid: int, token: str, **kwargs) -> DepartmentGetModel:
        method = "user.department.get"

        query = self.get_set_params(locals())
        status, response = await self._request("get", method, query)

        # logger.debug(f"Got response from {url}: {response}")
        return await check_response(status, response, DepartmentGetModel)

    async def twofactorcheck_get(self, userid: int, token: str, **kwargs) -> TwoFactorCheckGetModel:
        method = "user.twofactorcheck.get"

        query = self.get_set_params(locals())
        status, response = await self._request("get", method, query)

        # logger.debug(f"Got response from {url}: {response}")
        return await check_response(status, response, TwoFactorCheckGetModel)