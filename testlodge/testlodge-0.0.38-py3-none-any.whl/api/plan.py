from enum import auto
from enum import IntEnum

from furl import Path as UrlPath
from furl.furl import furl as Url
from requests.models import Response
from testlodge.api.base import BaseAPI
from testlodge.typing.plan import PlanJSON
from testlodge.typing.plan import PlanListJSON


class SortPlanOrder(IntEnum):
    """Method to sort by."""

    CREATED_AT = auto()
    UPDATED_AT = auto()
    NAME = auto()


class PlanAPI(BaseAPI):
    """API for test plans.

    Endpoints
    ---------
    * List
    * Show
    * Create
    * Update
    * Delete
    """

    name: str = 'plan'

    def _list(
        self,
        *,
        project_id: int,
        page: int = 1,
        order: SortPlanOrder = SortPlanOrder.CREATED_AT,
    ) -> PlanListJSON:
        """Paginated list of all plans in a project.

        Parameters
        ----------
        project_id: int
            The ID of the project.
        page: int, default=1
            Default: 1
            The number of the page to return.
        order: SortPlanOrder, default=SortPlanOrder.CREATED_AT
            Default: SortPlanOrder.CREATED_AT
            Method to sort the list.
        """

        method = 'GET'
        url: Url = self.client.base_url / UrlPath(
            f'/projects/{project_id}' 'plans.json'
        )
        params: dict = {}
        if page != 1:
            params['page'] = page
        if order != SortPlanOrder.CREATED_AT:
            params['order'] = int(order)

        response: Response = self.client._request(
            method=method, url=url, params=params
        )
        plan_list: PlanListJSON = response.json()

        return plan_list

    def _show(
        self,
        *,
        project_id: int,
        plan_id: int,
    ) -> PlanJSON:
        """Get the details for a plan.

        Parameters
        ----------
        project_id: int
            The ID of the project.
        plan_id: int
            The ID of the plan.
        """

        method = 'GET'
        url: Url = self.client.base_url / UrlPath(
            f'/projects/{project_id}' f'/plans/{plan_id}.json'
        )

        response: Response = self.client._request(
            method=method,
            url=url,
        )
        plan_json: PlanJSON = response.json()

        return plan_json

    def _create(
        self,
        *,
        project_id: int,
        plan: PlanJSON,
    ) -> PlanJSON:
        """Create a plan.

        Parameters
        ----------
        project_id: int
            The ID of the project.
        plan: PlanJSON

            name: str
                Name of the plan
        """

        method = 'POST'
        url: Url = self.client.base_url / UrlPath(
            f'/projects/{project_id}' 'plans.json'
        )

        data = dict(plan=plan)

        response: Response = self.client._request(
            method=method, url=url, json=data
        )
        plan_json: PlanJSON = response.json()

        return plan_json

    def _update(
        self,
        *,
        project_id: int,
        plan_id: int,
        plan: PlanJSON,
    ) -> PlanJSON:
        """Update a plan.

        Parameters
        ----------
        project_id: int
            The ID of the project.
        plan_id: int
            The ID of the plan.
        plan: PlanJSON

            name: str
                Name of the plan
        """

        method = 'PATCH'
        url: Url = self.client.base_url / UrlPath(
            f'/projects/{project_id}' f'/plans/{plan_id}.json'
        )

        data = dict(plan=plan)

        response: Response = self.client._request(
            method=method,
            url=url,
            json=data,
        )
        plan_json: PlanJSON = response.json()

        return plan_json

    def _delete(self, *, project_id: int, plan_id: int) -> None:
        """Delete a plan.

        Parameters
        ----------
        project_id: int
            The ID of the project.
        plan_id: int
            The ID of the plan.
        """

        method = 'DELETE'
        url: Url = self.client.base_url / UrlPath(
            f'/projects/{project_id}' f'/plans/{plan_id}.json'
        )

        response: Response = self.client._request(method=method, url=url)

        status_code: int = response.status_code
        if status_code != 204:
            print(f'Unexpected response code: {status_code}')

        return None
