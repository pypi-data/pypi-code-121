import sys

from cliff.app import (
    App,
)
from cliff.commandmanager import (
    CommandManager,
)

from botoolkit.bo_registry.settings import (
    NAMESPACE as BOREGISTRY_NAMESPACE,
)


class BORegistryApp(App):
    """
    Инструмент для работы с Registry
    """
    def __init__(self):
        super().__init__(
            description='BO Registry',
            version='0.0.3',
            command_manager=CommandManager(BOREGISTRY_NAMESPACE),
            deferred_help=True,
        )


def main(argv=sys.argv[1:]):
    bo_registry_app = BORegistryApp()
    return bo_registry_app.run(argv)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
