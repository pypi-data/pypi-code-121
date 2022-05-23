from typing import Optional

from testlodge.api.project import ProjectAPI
from testlodge.client.base import BaseClient
from testlodge.typing.project import ProjectJSON
from testlodge.typing.project import ProjectListJSON


class ProjectClient(BaseClient):
    def list_project_json(self, page: int = 1) -> ProjectListJSON:
        return getattr(self.api, ProjectAPI.name)._list(page)

    def show_project_json(self, *, project_id: int) -> ProjectJSON:
        return getattr(self.api, ProjectAPI.name)._show(project_id=project_id)

    def create_project_json(
        self,
        name: str,
        *,
        description: Optional[str] = None,
        issue_tracker_credential_id: Optional[int] = None,
        issue_tracker_project_id: Optional[str] = None,
    ) -> ProjectJSON:
        return getattr(self.api, ProjectAPI.name)._create(
            name=name,
            description=description,
            issue_tracker_credential_id=issue_tracker_credential_id,
            issue_tracker_project_id=issue_tracker_project_id,
        )

    def update_project_json(
        self,
        *,
        project_id: int,
        project: ProjectJSON,
    ) -> ProjectJSON:
        return getattr(self.api, ProjectAPI.name)._update(
            project_id=project_id,
            project=project,
        )

    def delete_project_json(
        self,
        *,
        project_id: int,
    ) -> ProjectJSON:
        return getattr(self.api, ProjectAPI.name)._delete(
            project_id=project_id,
        )
