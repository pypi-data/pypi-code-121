from testlodge.api.custom_field import CustomFieldAPI
from testlodge.client.base import BaseClient
from testlodge.typing.custom_field import CustomFieldJSON
from testlodge.typing.custom_field import CustomFieldListJSON


class CustomFieldClient(BaseClient):
    def list_custom_field_json(
        self,
        *,
        project_id: int,
    ) -> CustomFieldListJSON:
        return getattr(self.api, CustomFieldAPI.name)._list(project_id)

    def create_custom_field_json(self) -> CustomFieldJSON:
        raise NotImplementedError("This action is not supported.")
