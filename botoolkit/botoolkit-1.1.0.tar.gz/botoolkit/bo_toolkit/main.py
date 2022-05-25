import sys

from cliff.app import (
    App,
)
from cliff.commandmanager import (
    CommandManager,
)

from botoolkit.bo_toolkit.settings import (
    NAMESPACE as BOTOOLKIT_NAMESPACE,
)


class BOToolKitApp(App):
    """
    Инструмент для упрощения разработчиков проекта web_bb
    """
    def __init__(self):
        super().__init__(
            description='BO Toolkit',
            version='0.0.1',
            command_manager=CommandManager(BOTOOLKIT_NAMESPACE),
            deferred_help=True,
        )


def main(argv=sys.argv[1:]):
    bo_toolkit_app = BOToolKitApp()
    return bo_toolkit_app.run(argv)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
