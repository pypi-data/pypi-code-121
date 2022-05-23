import dataclasses  # type: ignore
from dataclasses import InitVar
from typing import Any, Dict, Optional
import inspect
import requests
from requests.adapters import HTTPAdapter
# from requests.packages.urllib3.util.retry import Retry
from urllib3.util.retry import Retry
from logging import getLogger

from deeplabel.exceptions import InvalidAPIResponse
import deeplabel.projects as projects
import deeplabel.label.dl_models as dl_models
logger = getLogger(__name__)

@dataclasses.dataclass
class _MixinLogin:
    username: InitVar[str]
    password: InitVar[str]


@dataclasses.dataclass
class _MixinToken:
    token: str


@dataclasses.dataclass
class BaseClient:
    label_url: str = "https://deeplabel.app/videolabel"
    infer_url: str = "https://deeplabel.app/videolabel/infer"
    # session: Any = Field()
    project_id: Optional[str] = None
    restriction: str = "true"

    def __post_init__(self):
        session = requests.Session()
        retry = Retry(connect=5, backoff_factor=0.5)
        session.mount("http://", HTTPAdapter(max_retries=retry))
        session.mount("https://", HTTPAdapter(max_retries=retry))
        self.session = session

    @property
    def headers(self) -> Dict[str, str]:
        return {"Authorization": f"Bearer {self.token}"}  # type: ignore

    def post(self, url: str, json: Dict[str, Any]):
        if not url.startswith("http"):
            url = self._get_url_by_caller(url)
        if self.restriction in ["false",False]:
            json["restriction"] = "false"
        response = self.session.post(
            url, json=json, headers=self.headers)
        if response.status_code > 200:
            logger.error(f"{response.status_code}  {url} failed. {response.text} ; data:{json}")
            raise InvalidAPIResponse(f"{response.status_code}  {url} {response.text}")
        return response

    def _get_url_by_caller(self, suffix: str):
        """When client's get/post/put url is called, the passed suffix must me
        added to either label_url or infer_url. In order to determine which of
        these two should be the base url, use inspect.stack() to get the caller
        function's path and determine it.

        This func is generally called inside client's get/put/post methods which
        are called by the caller method in question. Hence callstack would be
        this_func -> get/post/put -> caller
        """
        caller_filename = inspect.stack()[2][1]  # 1 is for filename
        if "/infer/" in caller_filename:
            return self.infer_url + suffix
        elif "/label/" in caller_filename:
            return self.label_url + suffix
        else:
            called_func = inspect.stack()[1][3]  #  BaseClient.{get/put/post}
            logger.error(
                f"Called BaseClient.{called_func} without base url outside library"
            )
            raise InvalidAPIResponse(
                f"Suffix based url is only supported inside infer and label objects. "
                f"Please use full url to call BaseClient.{called_func}"
            )

    def get(
        self,
        url: str,
        params: Dict[str, Any],
        add_project_id: bool = False,
    ):
        """Get a deeplabel get api

        Args:
            url (str): url to get. can be a suffix like /graphs/nodes or full url
            params (Dict[str,Any]): query parameters
            add_project_id (bool, optional): Weather to add projectId to query
                params if available. Defaults to False.

        Raises:
            InvalidAPIResponse: If the response code is > 200

        Returns:
            Response: requests.Response object
        """
        if add_project_id and getattr(self, "project_id", None):
            params["projectId"] = self.project_id  # type: ignore
        if self.restriction in ["false",False]:
            params["restriction"] = "false"
        if not url.startswith("http"):
            url = self._get_url_by_caller(url)
        logger.debug(f"Fetching {url} params: {params}")
        response = self.session.get(
            url, params=params, headers=self.headers)
        logger.debug(f"Received Response {response.json()}")
        if response.status_code > 200:
            logger.error(f"{response.status_code}  {url} failed. {response.text}")
            raise InvalidAPIResponse(f"{response.status_code}  {url} {response.text}")
        return response

    def put(self, url: str, json: Dict[str, Any]):
        if not url.startswith("http"):
            url = self._get_url_by_caller(url)
        if self.restriction in ["false",False]:
            json["restriction"] = "false"
        response = self.session.put(url, json=json, headers=self.headers)
        if response.status_code > 200:
            logger.error(f"{response.status_code}  {url} failed. {response.text}")
            raise InvalidAPIResponse(f"{response.status_code}  {url} {response.text}")
        return response

    def project(self, project_id: str) -> "projects.Project":
        return projects.Project.from_project_id(project_id, client=self)

    def dl_model(self, dl_model_id: str) -> "dl_models.DlModel":
        return dl_models.DlModel.from_dl_model_id(dl_model_id, client=self)



@dataclasses.dataclass
class DeeplabelClient(BaseClient, _MixinToken):
    ...


@dataclasses.dataclass
class DeeplabelLoginClient(BaseClient, _MixinLogin):
    def __post_init__(self, email: str, password: str):  # type: ignore
        import deeplabel.auth as auth
        # Get Session
        super().__post_init__()
        # Get user and token
        user: auth.users.User = auth.users.User.from_login(email, password, self)
        assert user.root_secret_key, f"No root secret key found in user"
        token = auth.tokens.UserToken.from_root_secret_key(user.root_secret_key, self)
        self.token = token.hash
