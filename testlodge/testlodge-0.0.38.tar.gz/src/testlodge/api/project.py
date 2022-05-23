from typing import Dict
from typing import Optional

from furl import Path as UrlPath
from furl.furl import furl as Url
from requests.models import Response
from testlodge.api.base import BaseAPI
from testlodge.typing.project import ProjectJSON
from testlodge.typing.project import ProjectListJSON


class ProjectAPI(BaseAPI):
    """API for projects.

    Endpoints
    ---------
    * List
    * Show
    * Create
    * Update
    * Delete
    """

    name: str = 'project'

    def _list(
        self,
        page: int = 1,
    ) -> ProjectListJSON:
        """Paginated list of all projects for a user.

        Parameters
        ----------
        page: int, default=1
            Default: 1
            Page to return.
        """

        method: str = 'GET'
        url: Url = self.client.base_url / UrlPath('/projects.json')
        if page != 1:
            params = {'page': page}
        else:
            params = {}

        response: Response = self.client._request(
            method=method, url=url, params=params
        )
        project_list: ProjectListJSON = response.json()

        return project_list

    def _show(
        self,
        *,
        project_id: int,
    ) -> ProjectJSON:
        """Get the details for a project.

        Parameters
        ----------
        project_id: Identifier
            The ID of the project.
        """

        method = 'GET'
        url: Url = self.client.base_url / UrlPath(
            f'/projects/{project_id}.json'
        )

        response: Response = self.client._request(
            method=method,
            url=url,
        )
        project_json: ProjectJSON = response.json()

        return project_json

    def _create(
        self,
        name: str,
        *,
        description: Optional[str] = None,
        issue_tracker_credential_id: Optional[int] = None,
        issue_tracker_project_id: Optional[str] = None,
    ) -> ProjectJSON:
        """Create a project.

        Parameters
        ----------
        name: str
            Name of the project.
        description: str, optional
            Project description.
        issue_tracker_credential_id: int, optional
            ID for an integrated issue tracker.
        issue_tracker_project_id: str, optional
            Project ID associated with integrated issue tracker.
        """

        method = 'POST'
        url: Url = self.client.base_url / UrlPath('/projects.json')

        data: Dict = dict(name=name)
        if description is not None:
            data['description'] = description
        if issue_tracker_credential_id is not None:
            data['issue_tracker_credential_id'] = str(
                issue_tracker_credential_id
            )
        if issue_tracker_project_id is not None:
            data['issue_tracker_project_id'] = issue_tracker_project_id

        response: Response = self.client._request(
            method=method, url=url, json=data
        )
        project_json: ProjectJSON = response.json()

        return project_json

    def _update(
        self,
        *,
        project_id: int,
        project: ProjectJSON,
    ) -> ProjectJSON:
        """Update a project.

        Parameters
        ----------
        project_id: int
            The ID of the project.
        project: ProjectJSON
            name: str
                Name of the project.
            description: str
                Project description.
            issue_tracker_credential_id: int
                ID for an integrated issue tracker.
            issue_tracker_project_id: str
                Project ID associated with integrated issue tracker.
        """

        method = 'PATCH'
        url: Url = self.client.base_url / UrlPath(
            f'/projects/{project_id}.json'
        )

        response: Response = self.client._request(
            method=method,
            url=url,
            json=project,
        )
        project_json: ProjectJSON = response.json()

        return project_json

    def _delete(
        self,
        *,
        project_id: int,
    ) -> None:
        """Delete a project.

        Parameters
        ----------
        project_id: int
            The ID of the project.
        """

        method = 'DELETE'
        url: Url = self.client.base_url / UrlPath(
            f'/projects/{project_id}.json'
        )

        response: Response = self.client._request(method=method, url=url)

        status_code: int = response.status_code
        if status_code != 204:
            print(f'Unexpected response code: {status_code}')

        return None
