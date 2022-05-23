from enum import auto
from enum import IntEnum
from typing import List
from typing import Optional

from furl import Path as UrlPath
from furl.furl import furl as Url
from requests.models import Response
from testlodge.api.base import BaseAPI
from testlodge.typing.requirement_document import RequirementDocumentJSON
from testlodge.typing.requirement_document import RequirementDocumentListJSON


class SortRequirementDocumentOrder(IntEnum):
    """Method to sort requirement documents by."""

    CREATED_AT = auto()
    UPDATED_AT = auto()
    TITLE = auto()


class RequirementDocumentAPI(BaseAPI):
    """API for requirement documents.

    Endpoints
    ---------
    * List
    * Show
    * Create
    * Update
    * Delete
    """

    name: str = 'requirement_document'

    def _list(
        self,
        *,
        project_id: int,
        page: int = 1,
        order: SortRequirementDocumentOrder = SortRequirementDocumentOrder.CREATED_AT,
    ) -> RequirementDocumentListJSON:
        """Paginated list of all requirement documents in a project.

        Parameters
        ----------
        project_id: int
            The ID of the project.
        page: int, default=1
            Default: 1
            The number of the page to return.
        order: SortRequirementDocumentOrder, default=SortRequirementDocumentOrder.CREATED_AT
            Default: SortOrder.CREATED_AT
            Method to sort the list of requirement documents.
        """

        method = 'GET'
        url: Url = self.client.base_url / UrlPath(
            f'/projects/{project_id}/requirement_documents.json'
        )
        params: dict = {}
        if page != 1:
            params['page'] = page
        if order != SortRequirementDocumentOrder.CREATED_AT:
            params['order'] = int(order)

        response: Response = self.client._request(
            method=method, url=url, params=params
        )
        requirement_documents_list: RequirementDocumentListJSON = (
            response.json()
        )

        return requirement_documents_list

    def _show(
        self,
        *,
        project_id: int,
        requirement_document_id: int,
    ) -> RequirementDocumentJSON:
        """Get the details for a requirement documents.

        Parameters
        ----------
        project_id: int
            The ID of the project.
        requirement_document_id: int
            The ID of the requirement document.
        """

        method = 'GET'
        url: Url = self.client.base_url / UrlPath(
            f'/projects/{project_id}/requirement_documents/{requirement_document_id}.json'
        )

        response: Response = self.client._request(
            method=method,
            url=url,
        )
        requirement_document_json: RequirementDocumentJSON = response.json()

        return requirement_document_json

    def _create(
        self,
        *,
        project_id: int,
        requirement_document: RequirementDocumentJSON,
    ) -> RequirementDocumentJSON:
        """Create a requirement document.

        Parameters
        ----------
        project_id: int
            The ID of the project.
        requirement_document: RequirementDocumentJSON

            title: str
                Title of the requirement.
            should_version: bool, default=False
                Default: False
                Should content be versioned when changed.
        """

        method = 'POST'
        url: Url = self.client.base_url / UrlPath(
            f'/projects/{project_id}/requirement_documents.json.'
        )

        data = dict(requirement_document=requirement_document)

        response: Response = self.client._request(
            method=method, url=url, json=data
        )
        requirement_json: RequirementDocumentJSON = response.json()

        return requirement_json

    def _update(
        self,
        *,
        project_id: int,
        requirement_document_id: int,
        requirement_document: RequirementDocumentJSON,
    ) -> RequirementDocumentJSON:
        """Update a requirement.

        Parameters
        ----------
        project_id: int
            The ID of the project.
        requirement_document_id: int
            The ID of the requirement document.
        requirement_document: RequirementDocumentJSON

            title: str
                Title of the requirement.
            should_version: bool, default=False
                Default: False
                Should content be versioned when changed.
        """

        method = 'PATCH'
        url: Url = self.client.base_url / UrlPath(
            f'/projects/{project_id}/requirement_documents/{requirement_document_id}.json'
        )
        data = dict(requirement_document=requirement_document)

        response: Response = self.client._request(
            method=method,
            url=url,
            json=data,
        )
        requirement_json: RequirementDocumentJSON = response.json()

        return requirement_json

    def _delete(
        self,
        *,
        project_id: int,
        requirement_document_id: int,
    ) -> None:
        """Delete a requirement document.

        Parameters
        ----------
        project_id: int
            The ID of the project.
        requirement_document_id: int
            The ID of the requirement document.
        """

        method = 'DELETE'
        url: Url = self.client.base_url / UrlPath(
            f'/projects/{project_id}/requirement_documents/{requirement_document_id}.json'
        )

        response: Response = self.client._request(method=method, url=url)

        status_code: int = response.status_code
        if status_code != 204:
            print(f'Unexpected response code: {status_code}')

        return None
