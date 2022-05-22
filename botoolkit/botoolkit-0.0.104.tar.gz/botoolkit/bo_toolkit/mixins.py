from pathlib import (
    Path,
)

from botoolkit.bo_toolkit.consts import (
    BEGIN_OPENSSH_PRIVATE_KEY,
    BEGIN_RSA_PRIVATE_KEY,
)
from botoolkit.bo_toolkit.helpers import (
    get_rsa_private_key_as_string,
)
from botoolkit.bo_toolkit.strings import (
    INCORRECT_PRIVATE_KEY_ERROR,
    RSA_PRIVATE_KEY_DOES_NOT_EXIST_ERROR,
)
from botoolkit.settings import (
    DEFAULT_RSA_PRIVATE_KEY_PATH,
)


class BOToolkitPrivateKeyArgumentMixin:
    """
        Добавляет параметры
            --toolkit_general_rsa_private_key
        """

    def patch_arguments_schema(self):
        super().patch_arguments_schema()

        self._arguments_schema.extend(
            (
                {
                    'section': 'toolkit_general',
                    'option': 'rsa_private_key',
                    'help': (
                        "RSA приватный ключ пользователя зарегистрированный в Bitbucket компании. Данный ключ "
                        "используется для сборки базового и финального образов приложения, клонирования других "
                        "репозиториев. Заполняется одной строкой, полученной при помощи команды "
                        "awk 1 ORS=' \\n' ~/.ssh/id_rsa && echo"
                    ),
                },
            )
        )

    def _validate_toolkit_general_rsa_private_key_path(self):
        """
        Валидация значения параметра toolkit_general_rsa_private_key_path
        """
        rsa_private_key = self._parsed_args.toolkit_general_rsa_private_key

        if (
            rsa_private_key and
            BEGIN_RSA_PRIVATE_KEY not in rsa_private_key and
            BEGIN_OPENSSH_PRIVATE_KEY not in rsa_private_key
        ):
            raise RuntimeError(
                INCORRECT_PRIVATE_KEY_ERROR
            )


class BOToolkitGeneralArgumentsMixin:
    """
    Добавляет параметры
        --toolkit_general_rsa_private_key_path
    """

    def patch_arguments_schema(self):
        super().patch_arguments_schema()

        self._arguments_schema.extend(
            (
                {
                    'section': 'toolkit_general',
                    'option': 'rsa_private_key_path',
                    'type': Path,
                    'default': str(DEFAULT_RSA_PRIVATE_KEY_PATH),
                    'help': (
                        f'Абсолютный путь до файла id_rsa содержащего приватный ключ пользователя. Значение по '
                        f'умолчанию {DEFAULT_RSA_PRIVATE_KEY_PATH}'
                    ),
                },
            )
        )

    def _validate_toolkit_general_rsa_private_key_path(self):
        """
        Валидация значения параметра toolkit_general_rsa_private_key_path
        """
        if not self._parsed_args.toolkit_general_rsa_private_key_path.exists():
            raise RuntimeError(
                RSA_PRIVATE_KEY_DOES_NOT_EXIST_ERROR
            )

        with open(str(self._parsed_args.toolkit_general_rsa_private_key_path), 'r') as rsa_private_key_file:  # noqa
            rsa_private_key = rsa_private_key_file.read()

        if (
            BEGIN_RSA_PRIVATE_KEY not in rsa_private_key and
            BEGIN_OPENSSH_PRIVATE_KEY not in rsa_private_key
        ):
            raise RuntimeError(
                INCORRECT_PRIVATE_KEY_ERROR
            )

    def _fill_toolkit_general_rsa_private_key_path(
        self,
        value: Path,
    ):
        """
        Заполнение значения параметра toolkit_general_rsa_private_key_path
        """
        self._config['toolkit_general']['rsa_private_key'].value = (
            get_rsa_private_key_as_string(
                rsa_private_key_path=value,
            )
        )


class DockerArgumentsMixin:
    """
    Добавляет параметры
        --docker_network
    """

    def patch_arguments_schema(self):
        super().patch_arguments_schema()

        self._arguments_schema.extend(
            (
                {
                    'section': 'docker',
                    'option': 'network',
                    'help': 'Наименование сети, используемой Docker-контейнерами.',
                },
                {
                    'section': 'docker',
                    'option': 'shm_size',
                    'help': 'Размер /dev/shm, например, 4g.',
                },
                {
                    'section': 'docker',
                    'option': 'cpu_max_count',
                    'help': 'Максимальное количество ядер, которые будут задействованы запускаемым контейнером.',
                },
            )
        )
