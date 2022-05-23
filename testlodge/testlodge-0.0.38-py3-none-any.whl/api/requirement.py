from typing import Dict
from typing import List
from typing import Optional

from furl import Path as UrlPath
from furl.furl import furl as Url
from requests.models import Response
from testlodge.api.base import BaseAPI
from testlodge.typing.requirement import RequirementJSON
from testlodge.typing.requirement import RequirementListJSON


class RequirementAPI(BaseAPI):
    """API for requirements.

    Endpoints
    ---------
    * List
    * Show
    * Create
    * Update
    * Delete
    """

    name: str = 'requirement'

    def _list(
        self,
        *,
        project_id: int,
        requirement_document_id: int,
        page: int = 1,
    ) -> RequirementListJSON:
        """Paginated list of all requirements in a requirement document.

        Parameters
        ----------
        project_id: int
            The ID of the project.
        requirement_document_id: int
            The ID of the requirement document.
        page: int, default=1
            Default: 1
            The number of the page to return.
        """

        method = 'GET'
        url: Url = self.client.base_url / UrlPath(
            f'/projects/{project_id}'
            f'/requirement_documents/{requirement_document_id}'
            '/requirements.json'
        )
        params: dict = {}
        if page != 1:
            params['page'] = page

        response: Response = self.client._request(
            method=method, url=url, params=params
        )
        requirement_list: RequirementListJSON = response.json()

        return requirement_list

    def _show(
        self,
        *,
        project_id: int,
        requirement_document_id: int,
        requirement_id: int,
        include: Optional[List[str]] = None,
    ) -> RequirementJSON:
        """Get the details for a requirement.

        Parameters
        ----------
        project_id: int
            The ID of the project.
        requirement_document_id: int
            The ID of the requirement document.
        requirement_id: int
            The ID of the requirement.

        include: dict[str], optional
            An array of strings, representing the additional options to include
            in the response.

            requirement_uploads: str
                Any file that has been uploaded and associated with the
                requirement (urls in the response will only be valid
                for ~30 seconds).
            steps: list[str]
                Any steps that have been associated to the case.
        """

        method = 'GET'
        url: Url = self.client.base_url / UrlPath(
            f'/projects/{project_id}'
            f'/requirement_documents/{requirement_document_id}'
            f'/requirements/{requirement_id}.json'
        )

        params: Dict[str, str] = {}
        if include is not None:
            raise NotImplementedError('Not implemented yet.')
        else:
            ...

        response: Response = self.client._request(
            method=method,
            url=url,
            params=params,
        )
        suite_json: RequirementJSON = response.json()

        return suite_json

    def _create(
        self,
        *,
        project_id: int,
        requirement_document_id: int,
        requirement: RequirementJSON,
    ) -> RequirementJSON:
        """Create a requirement.

        Parameters
        ----------
        project_id: int
            The ID of the project.
        requirement_document_id: int
            The ID of the requirement document.
        requirement: RequirementJSON

            title: str
                Title of the requirement.
            description: str
                Description of the requirement.
            custom_fields: List[CustomFieldJSON]
        """

        method = 'POST'
        url: Url = self.client.base_url / UrlPath(
            f'/projects/{project_id}'
            f'/requirement_documents/{requirement_document_id}'
            '/requirements.json'
        )

        data = dict(requirement=requirement)

        response: Response = self.client._request(
            method=method, url=url, json=data
        )
        requirement_json: RequirementJSON = response.json()

        return requirement_json

    def _update(
        self,
        *,
        project_id: int,
        requirement_document_id: int,
        requirement_id: int,
        requirement: RequirementJSON,
    ) -> RequirementJSON:
        """Update a requirement.

        Parameters
        ----------
        project_id: int
            The ID of the project.
        requirement_document_id: int
            The ID of the requirement document.
        requirement_id: int
            The ID of the requirement.
        requirement: RequirementJSON

            title: str
                Title of the requirement.
            description: str
                Description of the requirement.
            custom_fields: List[CustomFieldJSON]
        """

        method = 'PATCH'
        url: Url = self.client.base_url / UrlPath(
            f'/projects/{project_id}'
            f'/requirement_documents/{requirement_document_id}'
            f'/requirements/{requirement_id}.json'
        )
        data = dict(requirement=requirement)

        response: Response = self.client._request(
            method=method,
            url=url,
            json=data,
        )
        requirement_json: RequirementJSON = response.json()

        return requirement_json

    def _delete(
        self,
        *,
        project_id: int,
        requirement_document_id: int,
        requirement_id: int,
    ) -> None:
        """Delete a requirement.

        Parameters
        ----------
        project_id: int
            The ID of the project.
        requirement_document_id: int
            The ID of the requirement document.
        requirement_id: int
            The ID of the requirement.
        """

        method = 'DELETE'
        url: Url = self.client.base_url / UrlPath(
            f'/projects/{project_id}'
            f'/requirement_documents/{requirement_document_id}'
            f'/requirements/{requirement_id}.json'
        )

        response: Response = self.client._request(method=method, url=url)

        status_code: int = response.status_code
        if status_code != 204:
            print(f'Unexpected response code: {status_code}')

        return None
