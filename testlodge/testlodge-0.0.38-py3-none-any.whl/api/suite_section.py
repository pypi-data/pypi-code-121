from furl import Path as UrlPath
from furl.furl import furl as Url
from requests.models import Response
from testlodge.api.base import BaseAPI
from testlodge.typing.suite_section import SuiteSectionJSON
from testlodge.typing.suite_section import SuiteSectionListJSON


class SuiteSectionAPI(BaseAPI):
    """API for suite sections.


    Endpoints
    ---------
    * List
    * Show
    * Create
    * Update
    * Delete
    """

    name: str = 'suite_section'

    def _list(
        self, *, project_id: int, suite_id: int, page: int = 1
    ) -> SuiteSectionListJSON:
        """Paginated list of all suite sections inside a suite.

        Parameters
        ----------
        project_id: Identifier
            The ID of the project.
        suite_id: Identifier
            The ID of the suite.
        page: int, default=1
            Default: 1
            The number of the page to return.
        """

        method = 'GET'
        url: Url = self.client.base_url / UrlPath(
            f'/projects/{project_id}'
            f'/suites/{suite_id}'
            '/suite_sections.json'
        )
        if page != 1:
            params = {'page': page}
        else:
            params = {}

        response: Response = self.client._request(
            method=method, url=url, params=params
        )
        data: SuiteSectionListJSON = response.json()

        return data

    def _show(
        self,
        *,
        project_id: int,
        suite_id: int,
        suite_section_id: int,
    ) -> SuiteSectionJSON:
        """Get the details for a _suite section_.

        Parameters
        ----------
        project_id: Identifier
            The ID of the project.
        suite_id: Identifier
            The ID of the suite.
        suite_section_id: Identifier
            The ID of the suite section.
        """

        method = 'GET'
        url: Url = self.client.base_url / UrlPath(
            f'/projects/{project_id}'
            f'/suites/{suite_id}'
            f'/suite_sections/'
            f'{suite_section_id}.json'
        )

        response: Response = self.client._request(method=method, url=url)
        data: SuiteSectionJSON = response.json()

        return data

    def _create(
        self,
        *,
        project_id: int,
        suite_id: int,
        suite_section: SuiteSectionJSON,
    ) -> SuiteSectionJSON:
        """Create a new _suite section_.

        Parameters
        ----------
        project_id: Identifier
            The ID of the project.
        suite_id: Identifier
            The ID of the suite.
        suite_section: SuiteSectionJSON
            The suite section.
            Example:
                {
                    'title': 'Section 1'
                }
        """

        method = 'POST'
        url: Url = self.client.base_url / UrlPath(
            f'/projects/{project_id}'
            f'/suites/{suite_id}'
            f'/suite_sections.json'
        )

        response: Response = self.client._request(
            method=method, url=url, json=suite_section
        )
        new_suite_section: SuiteSectionJSON = response.json()

        return new_suite_section

    def _update(
        self,
        *,
        project_id: int,
        suite_id: int,
        suite_section_id: int,
        suite_section: SuiteSectionJSON,
    ) -> SuiteSectionJSON:
        """Update a _suite section_.

        Parameters
        ----------
        project_id: Identifier
            The ID of the project.
        suite_id: Identifier
            The ID of the suite.
        suite_section_id: Identifier
            The ID of the suite section.
        suite_section: SuiteSectionJSON
            The suite section.
            Example:
                {
                    'title': 'Section 1'
                }
        """

        method = 'PATCH'
        url: Url = self.client.base_url / UrlPath(
            f'/projects/{project_id}'
            f'/suites/{suite_id}'
            f'/suite_sections/{suite_section_id}.json'
        )

        response: Response = self.client._request(
            method=method, url=url, json=suite_section
        )
        updated_suite_section: SuiteSectionJSON = response.json()

        return updated_suite_section

    def _delete(
        self,
        *,
        project_id: int,
        suite_id: int,
        suite_section_id: int,
    ) -> None:
        """Delete a _suite section_.

        Parameters
        ----------
        project_id: Identifier
            The ID of the project.
        suite_id: Identifier
            The ID of the suite.
        suite_section_id: Identifier
            The ID of the suite section.
        """

        method = 'DELETE'
        url: Url = self.client.base_url / UrlPath(
            f'/projects/{project_id}'
            f'/suites/{suite_id}'
            f'/suite_sections/{suite_section_id}.json'
        )

        response: Response = self.client._request(method=method, url=url)
        status_code: int = response.status_code
        if status_code != 204:
            print(f'Unexpected response code: {status_code}')

        return None
