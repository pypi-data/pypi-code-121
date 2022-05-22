import sys

from cliff.app import (
    App,
)
from cliff.commandmanager import (
    CommandManager,
)

from botoolkit.bo_conf.settings import (
    NAMESPACE as BOCONF_NAMESPACE,
)


class BOConfiguratorApp(App):
    """
    Инструмент для работы с конфигурационными файлами приложения web_bb
    """
    def __init__(self):
        super().__init__(
            description=(
                'boconf - инструмент, предназначен для работы с конфигурационными файлами проекта web_bb. Основной '
                'задачей является создание конфигурационных файлов.'
            ),
            version='0.0.2',
            command_manager=CommandManager(BOCONF_NAMESPACE),
            deferred_help=True,
        )


def main(argv=sys.argv[1:]):
    bo_configurator_app = BOConfiguratorApp()
    return bo_configurator_app.run(argv)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
