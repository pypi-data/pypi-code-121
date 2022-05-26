from ..utils import check_response
from ..models import LoginTokenGetModel, LoginUsersGetModel
from .basemodel import BaseModel


class LoginCategory(BaseModel):
    async def token_get(self, login: str, password: str, **kwargs) -> LoginTokenGetModel:
        method = "login.token.get"

        query = self.get_set_params(locals())
        status, response = await self._request("get", method, query)

        # logger.debug(f"Got response from {url}: {response}")
        result = await check_response(status, response, LoginTokenGetModel)
        return result

    async def users_get(self, token: str, **kwargs) -> LoginUsersGetModel:
        method = "login.users.get"

        query = self.get_set_params(locals())
        status, response = await self._request("get", method, query)

        # logger.debug(f"Got response from {url}: {response}")
        result = await check_response(status, response, LoginUsersGetModel)
        return result
