from pathlib import (
    Path,
)
from typing import (
    List,
    Tuple,
)

from configupdater import (
    ConfigUpdater,
)

from botoolkit.bo_git.helpers import (
    clone_or_pull_repository,
)
from botoolkit.settings import (
    CONFIGURATION_DIRECTORY_PATH,
)


def get_configurations_path() -> Path:
    """
    Получения пути до директории со склонированным репозиторием с
    конфигурациями тестовых стендов
    """
    return CONFIGURATION_DIRECTORY_PATH / 'configurations'


def get_web_bb_test_stands_configurations_dir_path(
    configurations_path: Path,
) -> Path:
    """
    Получение пути до директории с конфигурационными файлами тестовых стендов
    """
    return configurations_path / 'web_bb' / 'test'


def get_stands_configs(
    configurations_git_repository_url: str,
    configurations_path: Path,
) -> List[Tuple[str, ConfigUpdater]]:
    """
    Функция получения распарсенных конфигурационных файлов тестовых стендов
    """
    test_stands_configs_dir_path = (
        get_web_bb_test_stands_configurations_dir_path(
            configurations_path=configurations_path,
        )
    )

    clone_or_pull_repository(
        path=configurations_path,
        url=configurations_git_repository_url,
    )

    config_paths = test_stands_configs_dir_path.glob('*.conf')

    test_stand_configs: List[Tuple[str, ConfigUpdater]] = []

    for config_path in config_paths:
        config = ConfigUpdater()
        config_path_str = str(config_path)
        config.read(config_path_str)

        test_stand_configs.append(
            (
                config_path_str,
                config,
            )
        )

    return test_stand_configs
