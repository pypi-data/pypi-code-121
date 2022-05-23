from typing import Dict
from typing import Optional

from furl import Path as UrlPath
from furl.furl import furl as Url
from requests.models import Response
from testlodge.api.base import BaseAPI
from testlodge.typing.case import CaseJSON
from testlodge.typing.case import CaseListJSON


class CaseAPI(BaseAPI):
    """API for test cases.

    Endpoints
    ---------
    * List
    * Show
    * Create
    * Update
    * Delete
    """

    name: str = 'case'

    def _list(
        self,
        *,
        project_id: int,
        suite_id: int,
        suite_section_id: int,
        page: int = 1,
    ) -> CaseListJSON:
        """Paginated list of all cases inside a suite section.

        Parameters
        ----------
        project_id: int
            The ID of the project.
        suite_id: int
            The ID of the suite.
        suite_section_id: int
            The ID of the suite section.
        page: int, default=1
            Default: 1
            The number of the page to return.
        """

        method = 'GET'
        url: Url = self.client.base_url / UrlPath(
            f'/projects/{project_id}'
            f'/suites/{suite_id}'
            f'/suite_sections/{suite_section_id}/steps.json'
        )
        if page != 1:
            params = {'page': page}
        else:
            params = {}

        response: Response = self.client._request(
            method=method, url=url, params=params
        )
        case_list: CaseListJSON = response.json()

        return case_list

    def _show(
        self,
        *,
        project_id: int,
        suite_id: int,
        case_id: int,
        include: Optional[Dict[str, str]] = None,
    ) -> CaseJSON:
        """Get the details for a _case_.

        Parameters
        ----------
        project_id: int
            The ID of the project.
        suite_id: int
            The ID of the suite.
        case_id: int
            The ID of the test case.
        include: dict[str], optional
            An array of strings, representing the additional options to include
            in the response.

            steps_uploads: str
                Any file that has been uploaded and associated with the test
                (urls in the response will only be available for ~30 seconds).
            requirements: list[RequirementJSON]
                Any requirements that have been associated to the case.
        """

        method = 'GET'
        url: Url = self.client.base_url / UrlPath(
            f'/projects/{project_id}'
            f'/suites/{suite_id}'
            f'/steps/{case_id}.json'
        )

        if include is not None:
            raise NotImplementedError('Not implemented yet.')
        else:
            include = {}

        response: Response = self.client._request(
            method=method, url=url, params=include
        )
        case_json: CaseJSON = response.json()

        return case_json

    def _create(
        self,
        *,
        project_id: int,
        suite_id: int,
        step: CaseJSON,
        suite_section_id: Optional[int] = None,
    ) -> CaseJSON:
        """Create a test case.

        Parameters
        ----------
        project_id: int
            The ID of the project.
        suite_id: int
            The ID of the suite.
        step: dict[CaseJSON]

            title: str
            description: str, optional
            test_steps: str, optional
            expected_result: str, optional
            custom_fields: list[CustomField], optional
                Custom fields of the test case.

        suite_section_id: int, optional
            Default: The top suite section in the test suite, or creates one if
            none exists.
            The ID of the suite section.
        """

        method = 'POST'
        url: Url = self.client.base_url / UrlPath(
            f'/projects/{project_id}' f'/suites/{suite_id}/steps.json'
        )

        if suite_section_id is not None:
            data = {'suite_section_id': suite_section_id, 'step': step}
        else:
            data = {'step': step}

        response: Response = self.client._request(
            method=method, url=url, json=data
        )
        case_json: CaseJSON = response.json()

        return case_json

    def _update(
        self,
        *,
        project_id: int,
        suite_id: int,
        case_id: int,
        step: CaseJSON,
    ) -> CaseJSON:
        """Update a test case.

        Parameters
        ----------
        project_id: int
            The ID of the project.
        suite_id: int
            The ID of the suite.
        case_id: int
            The ID of the test case.
        step: CaseJSON

            title: str
            description: str, optional
            test_steps: str, optional
            expected_result: str, optional
            custom_fields: list[CustomField], optional
                Custom fields of the test case.
        """

        method = 'PATCH'
        url: Url = self.client.base_url / UrlPath(
            f'/projects/{project_id}/suites/{suite_id}/steps/{case_id}.json'
        )

        response: Response = self.client._request(
            method=method, url=url, json=step
        )
        case_json: CaseJSON = response.json()

        return case_json

    def _delete(self, *, project_id: int, suite_id: int, case_id: int) -> None:
        """Delete a test case.

        Parameters
        ----------
        project_id: int
            The ID of the project.
        suite_id: int
            The ID of the suite.
        case_id: int
            The ID of the test case.
        """

        method = 'DELETE'
        url: Url = self.client.base_url / UrlPath(
            f'/projects/{project_id}'
            f'/suites/{suite_id}'
            f'/steps/{case_id}.json'
        )

        response: Response = self.client._request(method=method, url=url)

        status_code: int = response.status_code
        if status_code != 204:
            print(f'Unexpected response code: {status_code}')

        return None
