from furl import Path as UrlPath
from furl.furl import furl as Url
from requests.models import Response
from testlodge.api.base import BaseAPI
from testlodge.typing.user import UserListJSON


class UserAPI(BaseAPI):
    """API for users.

    Endpoints
    ---------
    * List
    """

    name: str = 'user'

    def _list(
        self,
        page: int = 1,
    ) -> UserListJSON:
        """Paginated list of all users in an account.

        Parameters
        ----------
        page: int, default=1
            Default: 1
            Page to return.
        """

        method = 'GET'
        url: Url = self.client.base_url / UrlPath('/users.json')
        if page != 1:
            params = {'page': page}
        else:
            params = {}

        response: Response = self.client._request(
            method=method, url=url, params=params
        )
        user_list: UserListJSON = response.json()

        return user_list
