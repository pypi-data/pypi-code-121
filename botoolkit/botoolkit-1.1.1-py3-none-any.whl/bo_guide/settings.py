from pathlib import (
    Path,
)


TOOL_NAME = NAMESPACE = 'boguide'

TEMPLATE_CONF_FILE_PATH = (
    Path(__file__).parent.absolute() / 'templates' / f'{TOOL_NAME}.conf'
)

CONSOLE_SCRIPTS = [
    f'{TOOL_NAME} = botoolkit.bo_guide.main:main',
]

NAMESPACES = {
    f'{NAMESPACE}': [
        'configure = botoolkit.bo_guide.commands:BOGuideConfigureCommand',
        'python check updates = botoolkit.bo_guide.commands:BOGuidePythonCheckUpdatesCommand',
    ],
}
