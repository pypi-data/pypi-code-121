import sys

from cliff.app import (
    App,
)
from cliff.commandmanager import (
    CommandManager,
)

from botoolkit.bo_web_bb.settings import (
    NAMESPACE as BOWEBBB_NAMESPACE,
)


class BOWebBBApp(App):
    """
    Инструмент для работы с проектом web_bb
    """
    def __init__(self):
        super().__init__(
            description='BO WebBB',
            version='0.0.1',
            command_manager=CommandManager(BOWEBBB_NAMESPACE),
            deferred_help=True,
        )


def main(argv=sys.argv[1:]):
    bo_web_bb_app = BOWebBBApp()
    return bo_web_bb_app.run(argv)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
