import sys

from cliff.app import (
    App,
)
from cliff.commandmanager import (
    CommandManager,
)

from botoolkit.bo_ip.settings import (
    NAMESPACE as BOIP_NAMESPACE,
)


class BOIP(App):
    """
    Инструмент для работы с ip-адресами
    """
    def __init__(self):
        super().__init__(
            description='BO IP',
            version='0.0.1',
            command_manager=CommandManager(BOIP_NAMESPACE),
            deferred_help=True,
        )


def main(argv=sys.argv[1:]):
    bo_ip_app = BOIP()
    return bo_ip_app.run(argv)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
