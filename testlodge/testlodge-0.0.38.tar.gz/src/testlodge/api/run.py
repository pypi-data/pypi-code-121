from enum import auto
from enum import IntEnum
from typing import Optional

from furl import Path as UrlPath
from furl.furl import furl as Url
from requests.models import Response
from testlodge.api.base import BaseAPI
from testlodge.typing.run import RunJSON
from testlodge.typing.run import RunListJSON


class SortRunOrder(IntEnum):
    """Method to sort runs by."""

    CREATED_AT = auto()
    NAME = auto()


class Status(IntEnum):
    """Run Status"""

    NOT_STARTED = auto()
    IN_PROGRESS = auto()
    COMPLETE = auto()


class RunAPI(BaseAPI):
    """API for test runs.

    Endpoints
    ---------
    * List
    * Show
    * Create
    * Update
    * Delete
    """

    name: str = 'run'

    def _list(
        self,
        *,
        project_id: int,
        page: int = 1,
        user_id: int = None,
        status: Optional[Status] = None,
        order: SortRunOrder = SortRunOrder.CREATED_AT,
    ) -> RunListJSON:
        """Paginated list of all runs in a project.

        Parameters
        ----------
        project_id: int
            The ID of the project.
        page: int, default=1
            Default: 1
            The number of the page to return.
        user_id: int, optional
            Filter by user.
        status: Status, optional, default=None
            Default: None
            Status of the run.
        order: SortRunOrder, default=SortRunOrder.CREATED_AT
            Default: SortRunOrder.CREATED_AT
            Method to sort the list of runs.
        """

        method = 'GET'
        url: Url = self.client.base_url / UrlPath(
            f'/projects/{project_id}/runs.json'
        )
        params: dict = {}
        if page != 1:
            params['page'] = page
        if order != SortRunOrder.CREATED_AT:
            params['order'] = int(order)
        if status is not None:
            params['status'] = int(status)
        if user_id is not None:
            params['user_id'] = user_id

        response: Response = self.client._request(
            method=method, url=url, params=params
        )
        run_list: RunListJSON = response.json()

        return run_list

    def _show(
        self,
        *,
        project_id: int,
        run_id: int,
    ) -> RunJSON:
        """Get the details for a run.

        Parameters
        ----------
        project_id: int
            The ID of the project.
        run_id: int
            The ID of the run.
        """

        method = 'GET'
        url: Url = self.client.base_url / UrlPath(
            f'/projects/{project_id}' f'/runs/{run_id}.json'
        )

        response: Response = self.client._request(
            method=method,
            url=url,
        )
        run_json: RunJSON = response.json()

        return run_json

    def _create(
        self,
        *,
        project_id: int,
        run: RunJSON,
    ) -> RunJSON:
        """Create a run.

        Parameters
        ----------
        project_id: int
            The ID of the project.
        run: RunJSON

            name: str
                Run name.
            step_ids: list[int]
                Either step_ids or suite_ids is required.
                Associated case IDs.
            suite_ids: list[int]
                Either step_ids or suite_ids is required.
                Associated suite IDs.
            plan_id: int, optional
                Associated test plan.
            user_id: int, optional
                Associated user.
        """

        method = 'POST'
        url: Url = self.client.base_url / UrlPath(
            f'/projects/{project_id}' '/runs.json'
        )

        data = dict(run=run)

        response: Response = self.client._request(
            method=method, url=url, json=data
        )
        run_json: RunJSON = response.json()

        return run_json

    def _update(
        self,
        *,
        project_id: int,
        run_id: int,
        run: RunJSON,
    ) -> RunJSON:
        """Update a run.

        Parameters
        ----------
        project_id: int
            The ID of the project.
        run_id: int
            The ID of the run.
        run: RunJSON

            name: str
                Name of the run.
            plan_id: int
                Associated test plan.
            user_id: int
                Associated user.
        """

        method = 'PATCH'
        url: Url = self.client.base_url / UrlPath(
            f'/projects/{project_id}/runs/{run_id}.json'
        )
        data = dict(run=run)

        response: Response = self.client._request(
            method=method,
            url=url,
            json=data,
        )
        run_json: RunJSON = response.json()

        return run_json

    def _delete(
        self,
        *,
        project_id: int,
        run_id: int,
    ) -> None:
        """Delete a run.

        Parameters
        ----------
        project_id: int
            The ID of the project.
        run_id: int
            The ID of the run.
        """

        method = 'DELETE'
        url: Url = self.client.base_url / UrlPath(
            f'/projects/{project_id}/runs/{run_id}.json'
        )

        response: Response = self.client._request(method=method, url=url)

        status_code: int = response.status_code
        if status_code != 204:
            print(f'Unexpected response code: {status_code}')

        return None
