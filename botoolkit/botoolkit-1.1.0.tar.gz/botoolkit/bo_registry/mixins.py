import validators

from botoolkit.bo_registry.helpers import (
    NexusAPIClient,
    RegistryAPIClient,
)
from botoolkit.core.strings import (
    WRONG_ARGUMENT_VALUE,
)


class RegistryURLArgumentsMixin:
    """
    Добавляет параметры
        --registry_url
    """

    def patch_arguments_schema(self):
        super().patch_arguments_schema()

        self._arguments_schema.extend(
            (
                {
                    'section': 'registry',
                    'option': 'url',
                    'help': 'URL используемого Registry или другого инструмента, используемого в его качестве.',
                },
            )
        )


class RegistryArgumentsMixin(RegistryURLArgumentsMixin):
    """
    Добавляет параметры
        --registry_container_name
        --registry_host_ip
        --registry_host_username
        --registry_url
        --registry_user
        --registry_password
    """

    def patch_arguments_schema(self):
        super().patch_arguments_schema()

        self._arguments_schema.extend(
            (
                {
                    'section': 'registry',
                    'option': 'container_name',
                    'help': 'Имя контейнера Registry запущенного на сервере.',
                },
                {
                    'section': 'registry',
                    'option': 'host_ip',
                    'help': 'IP-адрес сервера с запущенным Registry',
                },
                {
                    'section': 'registry',
                    'option': 'host_username',
                    'help': 'Имя пользователя на сервере, где запущен Registry.',
                },
                {
                    'section': 'registry',
                    'option': 'user',
                    'help': 'Имя пользователя в Registry.',
                },
                {
                    'section': 'registry',
                    'option': 'password',
                    'help': 'Пароль пользователя в Registry.',
                },
            )
        )

    def _validate_registry_host_ip(self):
        """
        Валидация параметра registry_host_ip
        """
        if (
            self._parsed_args.registry_host_ip and
            not validators.ipv4(self._parsed_args.registry_host_ip)
        ):
            raise RuntimeError(
                WRONG_ARGUMENT_VALUE.format(
                    argument_name='registry_host_ip',
                )
            )


class RegistryClientArgumentMixin:
    """
    Добавляет параметры
        --registry_client
    """

    def patch_arguments_schema(self):
        super().patch_arguments_schema()

        self._arguments_schema.extend(
            (
                {
                    'section': 'registry',
                    'option': 'client',
                    'help': (
                        'Указывается используемый клиент Registry. Допустимые значения: registry, nexus. Значение по '
                        'умолчанию - nexus.'
                    ),
                    'default': 'nexus',
                },
            )
        )

    def _validate_registry_client(self):
        """
        Валидация параметра registry_client
        """
        registry_clients = {
            'registry': RegistryAPIClient,
            'nexus': NexusAPIClient,
        }

        if (
            self._parsed_args.registry_client
            and self._parsed_args.registry_client in registry_clients
        ):
            self._parsed_args.registry_client = registry_clients[self._parsed_args.registry_client]
        else:
            raise RuntimeError(
                WRONG_ARGUMENT_VALUE.format(
                    argument_name='registry_client',
                )
            )