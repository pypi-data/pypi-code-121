import sys

from cliff.app import (
    App,
)
from cliff.commandmanager import (
    CommandManager,
)

from botoolkit.bo_jenkins.settings import (
    NAMESPACE as BOJENKINS_NAMESPACE,
)


class BOJenkinsApp(App):
    """
    Инструмент для работы с проектом web_bb в Jenkins
    """
    def __init__(self):
        super().__init__(
            description='BO Jenkins',
            version='0.0.2',
            command_manager=CommandManager(BOJENKINS_NAMESPACE),
            deferred_help=True,
        )


def main(argv=sys.argv[1:]):
    bo_jenkins_app = BOJenkinsApp()
    return bo_jenkins_app.run(argv)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
