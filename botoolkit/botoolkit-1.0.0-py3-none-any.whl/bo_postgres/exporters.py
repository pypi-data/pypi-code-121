from pathlib import (
    Path,
)

import yaml

from botoolkit.bo_postgres.repositories import (
    WebBBDBImageBuildRepository,
)
from botoolkit.bo_postgres.settings import (
    BASE_DB_IMAGE_SCHEMA_TEMPLATE_PATH,
)
from botoolkit.settings import (
    CONFIGURATION_DIRECTORY_PATH,
)


class WebBBDBImageConfigurationExporter:
    """
    Экспортер конфигураций для сборок базовых образов баз данных
    """

    def __init__(
        self,
        repository: WebBBDBImageBuildRepository,
    ):
        self._repository = repository

    def to_yaml(
        self,
        file_path: Path = None,
        clear: bool = True,
    ):
        """
        Экспорт параметров базовых образов БД в yaml-файл
        """
        local_base_db_image_schema_path = (
            CONFIGURATION_DIRECTORY_PATH / BASE_DB_IMAGE_SCHEMA_TEMPLATE_PATH.name
        ) if not file_path else str(file_path)

        base_db_image_schema_map = {
            (schema.image_repository, schema.image_tag): schema.as_dict()
            for schema in self._repository.entities
        }

        if (
            local_base_db_image_schema_path.exists() and
            not clear
        ):
            with open(str(local_base_db_image_schema_path), 'r') as f:
                old_base_db_image_schema = yaml.load(
                    stream=f.read(),
                    Loader=yaml.FullLoader,
                )

                old_base_db_image_schema_map = {
                    (schema['image_repository'], schema['image_tag']): schema
                    for schema in old_base_db_image_schema
                }

            for (image_repository, image_tag), old_schema in old_base_db_image_schema_map.items():
                if (image_repository, image_tag) in base_db_image_schema_map:
                    base_db_image_schema_map[(image_repository, image_tag)].update(
                        old_schema
                    )
                else:
                    base_db_image_schema_map[(image_repository, image_tag)] = old_schema

        with open(str(local_base_db_image_schema_path), 'w') as f:
            f.write(yaml.dump(list(base_db_image_schema_map.values())))

        local_base_db_image_schema_path.chmod(
            mode=0o700,
        )
