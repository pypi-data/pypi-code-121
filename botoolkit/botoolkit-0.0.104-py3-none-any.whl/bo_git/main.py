import sys

from cliff.app import (
    App,
)
from cliff.commandmanager import (
    CommandManager,
)

from botoolkit.bo_git.settings import (
    NAMESPACE as BOGIT_NAMESPACE,
)


class BOGitApp(App):
    """
    Инструмент для работы с Git
    """
    def __init__(self):
        super().__init__(
            description='BO Git',
            version='0.0.1',
            command_manager=CommandManager(BOGIT_NAMESPACE),
            deferred_help=True,
        )


def main(argv=sys.argv[1:]):
    bo_git_app = BOGitApp()
    return bo_git_app.run(argv)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
