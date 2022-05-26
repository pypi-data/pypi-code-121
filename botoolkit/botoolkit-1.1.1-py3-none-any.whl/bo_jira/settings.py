from pathlib import (
    Path,
)


TOOL_NAME = NAMESPACE = 'bojira'

TEMPLATE_CONF_FILE_PATH = (
    Path(__file__).parent.absolute() / 'templates' / f'{TOOL_NAME}.conf'
)

CONSOLE_SCRIPTS = [
    f'{TOOL_NAME} = botoolkit.bo_jira.main:main',
]

NAMESPACES = {
    f'{NAMESPACE}': [
        'configure = botoolkit.bo_jira.commands:ConfigureBOJiraCommand',
        'show databaser build errors issues = botoolkit.bo_jira.commands:BOJenkinsDatabaserBuildErrorsJiraIssuesLister',
    ],
}
