from pathlib import (
    Path,
)


TOOL_NAME = NAMESPACE = 'botoolkit'

TEMPLATE_CONF_FILE_PATH = (
    Path(__file__).parent.absolute() / 'templates' / f'{TOOL_NAME}.conf'
)

CONSOLE_SCRIPTS = [
    f'{TOOL_NAME} = botoolkit.bo_toolkit.main:main',
]

NAMESPACES = {
    f'{NAMESPACE}': [
        'configure = botoolkit.bo_toolkit.commands:ConfigureBOToolKitCommand',
        'work on = botoolkit.bo_toolkit.commands:BOToolkitWorkOnCommand',
        'work off = botoolkit.bo_toolkit.commands:BOToolkitWorkOffCommand',
    ],
}
