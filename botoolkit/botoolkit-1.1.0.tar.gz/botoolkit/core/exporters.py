from abc import (
    ABCMeta,
    abstractmethod,
)
from pathlib import (
    Path,
)
from typing import (
    Tuple,
)

from configupdater import (
    ConfigUpdater,
)


class ConfigurationExporter(metaclass=ABCMeta):
    """
    Базовый класс экспортера конфига
    """

    ALLOWED_SECTIONS: Tuple[str] = ()

    def __init__(
        self,
        tool_name: str,
        config: ConfigUpdater,
        configuration_dir_path: Path,
    ):
        self._tool_name = tool_name
        self._config = config
        self._configuration_dir_path = configuration_dir_path

    @abstractmethod
    def export(self) -> Path:
        """
        Осуществление экспорта конфига по указанному пути
        """
        pass


class ConfExporter(ConfigurationExporter):
    """
    Экспорт конфига в файл с форматом conf
    """

    def export(self) -> Path:
        configuration_file_path = (
            self._configuration_dir_path / f'{self._tool_name}.conf'
        )

        with open(str(configuration_file_path), 'w') as configuration_file:
            self._config.write(
                fp=configuration_file,
            )

        configuration_file_path.chmod(
            mode=0o700,
        )

        return configuration_file_path


class EnvExporter(ConfigurationExporter):
    """
    Экспорт конфига в файл с форматом env, содержащем переменные окружения
    """

    def export(self) -> Path:
        variables = []

        configuration_file_path = (
            self._configuration_dir_path / f'{self._tool_name}.env'
        )

        for section in self._config.sections():
            if self.ALLOWED_SECTIONS and section not in self.ALLOWED_SECTIONS:
                continue

            for option in self._config[section]:
                value = self._config[section][option].value.strip().replace(', ', ',')

                variables.append(
                    (
                        f'{section}_{option}'.upper(),
                        value,
                    )
                )

        result = '\n'.join(
            [
                f'{name}="{value}"'
                for name, value in variables
            ]
        )

        with open(str(configuration_file_path), 'w') as configuration_file:
            configuration_file.write(result)

        configuration_file_path.chmod(
            mode=0o700,
        )

        return configuration_file_path
