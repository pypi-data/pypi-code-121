from pathlib import (
    Path,
)


TOOL_NAME = NAMESPACE = 'bobarsdock'

TEMPLATE_CONF_FILE_PATH = (
    Path(__file__).parent.absolute() / 'templates' / f'{TOOL_NAME}.conf'
)

CONSOLE_SCRIPTS = [
    f'{TOOL_NAME} = botoolkit.bo_barsdock.main:main',
]

NAMESPACES = {
    f'{NAMESPACE}': [
        'configure = botoolkit.bo_barsdock.commands:ConfigureBOBARSDockCommand',
    ],
}
