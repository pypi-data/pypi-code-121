from typing import (
    List,
)

from botoolkit.bo_postgres.entities import (
    WebBBDBImageBuild,
)


class WebBBDBImageBuildRepository:
    """
    Репозиторий для хранения сборок базовых образов баз данных
    """

    def __init__(self):
        self._entities: List[WebBBDBImageBuild] = []

    @property
    def entities(self) -> List[WebBBDBImageBuild]:
        return self._entities

    def add(
        self,
        entity: WebBBDBImageBuild,
    ):
        """
        Добавление сборки в репозиторий
        """
        self._entities.append(entity)
