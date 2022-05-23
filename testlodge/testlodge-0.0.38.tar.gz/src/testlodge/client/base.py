from types import SimpleNamespace
from typing import List
from typing import Type

import requests
from furl import furl
from furl.furl import furl as Url
from requests import Response
from testlodge.api.base import BaseAPI as API
from testlodge.api.case import CaseAPI
from testlodge.api.custom_field import CustomFieldAPI
from testlodge.api.plan import PlanAPI
from testlodge.api.project import ProjectAPI
from testlodge.api.requirement import RequirementAPI
from testlodge.api.requirement_document import RequirementDocumentAPI
from testlodge.api.run import RunAPI
from testlodge.api.suite import SuiteAPI
from testlodge.api.suite_section import SuiteSectionAPI
from testlodge.api.user import UserAPI


class BaseClient:
    """Represents a client accessing the TestLodge API."""

    def __init__(
        self,
        email: str,
        api_key: str,
        account_id: int,
        apis: List[Type[API]] = None,
    ):

        if apis is None:
            apis = [
                UserAPI,
                CustomFieldAPI,
                ProjectAPI,
                SuiteSectionAPI,
                SuiteAPI,
                CaseAPI,
                PlanAPI,
                RunAPI,
                RequirementAPI,
                RequirementDocumentAPI,
            ]

        self.email: str = email
        self.api_key: str = api_key
        self.account_id: int = account_id

        self.history: List[Response] = []

        # Initialize the APIs
        self.api = SimpleNamespace()
        for api in apis:
            api_instance = api(client=self)
            setattr(self.api, api.name, api_instance)

    @property
    def base_url(self) -> Url:

        return furl(f'https://api.testlodge.com/v1/account/{self.account_id}')

    def _request(self, method: str, url: str, *args, **kwargs) -> Response:
        """Wrap requests.request to add handlers for response,
        logging, etc."""

        response = requests.request(
            method=method,
            url=url,
            auth=(self.email, self.api_key),
            *args,  # type: ignore
            **kwargs,  # type: ignore
        )

        self.history.append(response)

        return response
