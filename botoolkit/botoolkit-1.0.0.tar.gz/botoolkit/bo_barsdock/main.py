import sys

from cliff.app import (
    App,
)
from cliff.commandmanager import (
    CommandManager,
)

from botoolkit.bo_barsdock.settings import (
    NAMESPACE as BOBARSDOCK_NAMESPACE,
)


class BOBARSDockApp(App):
    """
    Инструмент для работы с bobarsdock
    """
    def __init__(self):
        super().__init__(
            description='BO BARS Dock',
            version='0.0.1',
            command_manager=CommandManager(BOBARSDOCK_NAMESPACE),
            deferred_help=True,
        )


def main(argv=sys.argv[1:]):
    bo_dock_app = BOBARSDockApp()
    return bo_dock_app.run(argv)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
