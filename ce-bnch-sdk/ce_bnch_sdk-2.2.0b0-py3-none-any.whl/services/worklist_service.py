from typing import Iterable, List, Optional

from benchling_api_client.types import Response
from benchling_api_client.v2.beta.api.worklists import (
    create_worklist,
    create_worklist_item,
    delete_worklist,
    get_worklist,
    list_worklists,
    update_worklist,
)
from benchling_api_client.v2.beta.models.list_worklists_sort import ListWorklistsSort
from benchling_api_client.v2.beta.models.worklist import Worklist
from benchling_api_client.v2.beta.models.worklist_create import WorklistCreate
from benchling_api_client.v2.beta.models.worklist_item import WorklistItem
from benchling_api_client.v2.beta.models.worklist_item_create import WorklistItemCreate
from benchling_api_client.v2.beta.models.worklist_type import WorklistType
from benchling_api_client.v2.beta.models.worklist_update import WorklistUpdate
from benchling_api_client.v2.beta.models.worklists_paginated_list import WorklistsPaginatedList

from benchling_sdk.errors import raise_for_status
from benchling_sdk.helpers.decorators import api_method
from benchling_sdk.helpers.pagination_helpers import NextToken, PageIterator
from benchling_sdk.helpers.response_helpers import model_from_detailed
from benchling_sdk.helpers.serialization_helpers import none_as_unset, optional_array_query_param
from benchling_sdk.services.base_service import BaseService


class WorklistService(BaseService):
    """
    Worklists.

    Worklists are a convenient way to organize items for bulk actions, and are complementary to folders and projects.

    See https://benchling.com/api/v2-beta/reference#/Worklists
    """

    @api_method
    def _worklists_page(
        self,
        *,
        sort: Optional[ListWorklistsSort] = None,
        modified_at: Optional[str] = None,
        ids: Optional[Iterable[str]] = None,
        worklist_type: Optional[WorklistType] = None,
        next_token: Optional[str] = None,
        page_size: Optional[int] = 50,
    ) -> Response[WorklistsPaginatedList]:
        return list_worklists.sync_detailed(  # type: ignore
            client=self.client,
            sort=none_as_unset(sort),
            modified_at=none_as_unset(modified_at),
            ids=none_as_unset(optional_array_query_param(ids)),
            worklist_type=none_as_unset(worklist_type),
            next_token=none_as_unset(next_token),
            page_size=none_as_unset(page_size),
        )

    def list(
        self,
        *,
        sort: Optional[ListWorklistsSort] = None,
        modified_at: Optional[str] = None,
        ids: Optional[Iterable[str]] = None,
        worklist_type: Optional[WorklistType] = None,
        page_size: Optional[int] = 50,
    ) -> PageIterator[Worklist]:
        """
        List worklists.

        Individual items within a worklist are summarized.

        See https://benchling.com/api/v2-beta/reference#/Worklists/listWorklists
        """

        def api_call(next_token: NextToken) -> Response[WorklistsPaginatedList]:
            return self._worklists_page(
                sort=sort,
                modified_at=modified_at,
                ids=ids,
                worklist_type=worklist_type,
                next_token=next_token,
                page_size=page_size,
            )

        def results_extractor(body: WorklistsPaginatedList) -> Optional[List[Worklist]]:
            return body.worklists

        return PageIterator(api_call, results_extractor)

    @api_method
    def create(self, worklist: WorklistCreate) -> Worklist:
        """
        Create a worklist.

        See https://benchling.com/api/v2-beta/reference#/Worklists/createWorklist
        """
        response = create_worklist.sync_detailed(client=self.client, json_body=worklist)
        return model_from_detailed(response)

    @api_method
    def delete(self, worklist_id: str) -> None:
        """
        Permanently deletes a worklist.

        See https://benchling.com/api/v2-beta/reference#/Worklists/deleteWorklist
        """
        response = delete_worklist.sync_detailed(client=self.client, worklist_id=worklist_id)
        raise_for_status(response)

    @api_method
    def get_by_id(self, worklist_id: str) -> Worklist:
        """
        Get a worklist by ID.

        See https://benchling.com/api/v2-beta/reference#/Worklists/getWorklist
        """
        response = get_worklist.sync_detailed(client=self.client, worklist_id=worklist_id)
        return model_from_detailed(response)

    @api_method
    def update(self, worklist_id: str, worklist_update: WorklistUpdate) -> Worklist:
        """
        Update a worklist.

        See https://benchling.com/api/v2-beta/reference#/Worklists/updateWorklist
        """
        response = update_worklist.sync_detailed(
            client=self.client, worklist_id=worklist_id, json_body=worklist_update
        )
        return model_from_detailed(response)

    @api_method
    def append_item(self, worklist_id, worklist_item_create: WorklistItemCreate) -> WorklistItem:
        """
        Append an item to the end of a worklist if the item is not already present in the worklist.

        See https://benchling.com/api/v2-beta/reference#/Worklists/createWorklistItem
        """
        response = create_worklist_item.sync_detailed(
            client=self.client, worklist_id=worklist_id, json_body=worklist_item_create
        )
        return model_from_detailed(response)
