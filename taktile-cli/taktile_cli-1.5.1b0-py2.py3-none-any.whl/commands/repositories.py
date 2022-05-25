from typing import List

from tktl.commands import BaseDeploymentApiCommand
from tktl.core.config import settings
from tktl.core.schemas.repository import Repository


class GetRepositories(BaseDeploymentApiCommand):
    def execute(self) -> List[Repository]:
        return self.client.call(
            verb="get", path=f"{settings.API_V1_STR}/models", model=Repository
        )
