from pathlib import (
    Path,
)


TOOL_NAME = NAMESPACE = 'bogit'

TEMPLATE_CONF_FILE_PATH = (
    Path(__file__).parent.absolute() / 'templates' / f'{TOOL_NAME}.conf'
)

CONSOLE_SCRIPTS = [
    f'{TOOL_NAME} = botoolkit.bo_git.main:main',
]

NAMESPACES = {
    f'{NAMESPACE}': [
        'configure = botoolkit.bo_git.commands:ConfigureBOWebBBCommand',
        'show remote branches = botoolkit.bo_git.commands:ShowRemoteBranchesCommand',
        'check closed issues remote branches = botoolkit.bo_git.commands:CheckClosedIssueRemoteBranchCommand',
    ],
}
