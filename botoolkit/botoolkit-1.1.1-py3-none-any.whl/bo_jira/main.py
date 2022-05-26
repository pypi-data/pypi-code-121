import sys

from cliff.app import (
    App,
)
from cliff.commandmanager import (
    CommandManager,
)

from botoolkit.bo_jira.settings import (
    NAMESPACE as BOJIRA_NAMESPACE,
)


class BOJiraApp(App):
    """
    Инструмент для работы с проектами БО в Jira
    """
    def __init__(self):
        super().__init__(
            description='BO Jira',
            version='0.0.1',
            command_manager=CommandManager(BOJIRA_NAMESPACE),
            deferred_help=True,
        )


def main(argv=sys.argv[1:]):
    bo_jira_app = BOJiraApp()
    return bo_jira_app.run(argv)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
