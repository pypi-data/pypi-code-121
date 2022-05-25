from benchling_api_client.v2.beta.api.entities import bulk_upsert_entities
from benchling_api_client.v2.beta.models.entities_bulk_upsert_request import EntitiesBulkUpsertRequest

from benchling_sdk.helpers.client_helpers import v2_beta_client
from benchling_sdk.helpers.decorators import api_method
from benchling_sdk.helpers.response_helpers import model_from_detailed
from benchling_sdk.models import AsyncTaskLink
from benchling_sdk.services.base_service import BaseService


class EntityService(BaseService):
    """
    Entities.

    Entities include DNA and AA sequences, oligos, molecules, custom entities, and
    other biological objects in Benchling. Entities support schemas, tags, and aliases,
    and can be registered.

    See https://benchling.com/api/v2-alpha/reference#/Entities
    """

    @api_method
    def bulk_upsert(self, bulk_upsert: EntitiesBulkUpsertRequest) -> AsyncTaskLink:
        """
        Upsert many entities at once.

        All entities and their schemas must be within the same registry.

        This operation performs the following actions:

        1. Any existing objects are looked up in Benchling by the provided entity registry ID.
        2. Then, all objects are either created or updated accordingly, temporarily skipping any schema field links between objects.
        3. Schema field links between objects are populated according to the provided identifier. In the `value` field of the `Field` resource, the entity registry ID may be provided instead of the API ID if desired. You may link to objects being created in the same operation.
        4. Entities are registered, using the provided name and entity registry ID.

        If any action fails, the whole operation is canceled and no objects are created or updated.
        See https://benchling.com/api/v2-alpha/reference#/Entities/bulkUpsertEntities
        """
        beta_client = v2_beta_client(self.client)
        response = bulk_upsert_entities.sync_detailed(client=beta_client, json_body=bulk_upsert)
        return model_from_detailed(response)
