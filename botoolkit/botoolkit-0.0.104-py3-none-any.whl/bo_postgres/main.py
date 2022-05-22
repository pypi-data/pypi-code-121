import sys

from cliff.app import (
    App,
)
from cliff.commandmanager import (
    CommandManager,
)

from botoolkit.bo_postgres.settings import (
    NAMESPACE as BOPOSTGRES_NAMESPACE,
)


class BOPostgresApp(App):
    """
    Инструмент для работы с Postgres
    """
    def __init__(self):
        super().__init__(
            description='BO Postgres',
            version='0.0.3',
            command_manager=CommandManager(BOPOSTGRES_NAMESPACE),
            deferred_help=True,
        )


def main(argv=sys.argv[1:]):
    bo_postgres_app = BOPostgresApp()
    return bo_postgres_app.run(argv)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
