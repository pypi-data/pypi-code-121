import sys

from cliff.app import (
    App,
)
from cliff.commandmanager import (
    CommandManager,
)

from botoolkit.bo_telegram.settings import (
    NAMESPACE as BOTELEGRAM_NAMESPACE,
)


class BOTelegram(App):
    """
    Инструмент для работы с Telegram
    """
    def __init__(self):
        super().__init__(
            description='BO Telegram',
            version='0.0.1',
            command_manager=CommandManager(BOTELEGRAM_NAMESPACE),
            deferred_help=True,
        )


def main(argv=sys.argv[1:]):
    bo_telegram_app = BOTelegram()
    return bo_telegram_app.run(argv)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
