import sys

from cliff.app import (
    App,
)
from cliff.commandmanager import (
    CommandManager,
)

from botoolkit.bo_guide.settings import (
    NAMESPACE as BOGUIDE_NAMESPACE,
)


class BOGuide(App):
    """
    Инструмент для работы с ip-адресами
    """
    def __init__(self):
        super().__init__(
            description='BO Guide',
            version='0.0.1',
            command_manager=CommandManager(BOGUIDE_NAMESPACE),
            deferred_help=True,
        )


def main(argv=sys.argv[1:]):
    bo_guide_app = BOGuide()
    return bo_guide_app.run(argv)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
