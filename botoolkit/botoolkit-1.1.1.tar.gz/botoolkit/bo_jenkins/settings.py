from pathlib import (
    Path,
)


TOOL_NAME = NAMESPACE = 'bojenkins'

TEMPLATE_CONF_FILE_PATH = (
    Path(__file__).parent.absolute() / 'templates' / f'{TOOL_NAME}.conf'
)

CONSOLE_SCRIPTS = [
    f'{TOOL_NAME} = botoolkit.bo_jenkins.main:main',
]

NAMESPACES = {
    f'{NAMESPACE}': [
        'configure = botoolkit.bo_jenkins.commands:ConfigureBOJenkinsCommand',
        'stands = botoolkit.bo_jenkins.commands:BOJenkinsStandsLister',
        'generate databaser interface = botoolkit.bo_jenkins.commands:BOJenkinsGenerateDatabaserInterfaceCommand',
        'run databaser = botoolkit.bo_jenkins.commands:BOJenkinsRunDatabaserCommand',
        'check databaser = botoolkit.bo_jenkins.commands:BOJenkinsCheckDatabaserCommand',
    ],
}
