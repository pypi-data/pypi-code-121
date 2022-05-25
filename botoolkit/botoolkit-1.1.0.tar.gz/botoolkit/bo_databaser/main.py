import sys

from cliff.app import (
    App,
)
from cliff.commandmanager import (
    CommandManager,
)

from botoolkit.bo_databaser.settings import (
    NAMESPACE as BODATABASER_NAMESPACE,
)


class BODatabaserApp(App):
    """
    Инструмент для работы с Databaser
    """
    def __init__(self):
        super().__init__(
            description='BO Databaser',
            version='0.0.6',
            command_manager=CommandManager(BODATABASER_NAMESPACE),
            deferred_help=True,
        )


def main(argv=sys.argv[1:]):
    bo_databaser_app = BODatabaserApp()
    return bo_databaser_app.run(argv)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
