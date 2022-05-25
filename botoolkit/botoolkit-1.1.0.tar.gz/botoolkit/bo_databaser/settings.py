from pathlib import (
    Path,
)


TOOL_NAME = NAMESPACE = 'bodatabaser'

BUILD_TOOL_NAME = 'bodatabaser_build'

TEMPLATE_CONF_FILE_PATH = (
    Path(__file__).parent.absolute() / 'templates' / f'{TOOL_NAME}.conf'
)
BUILD_TEMPLATE_CONF_FILE_PATH = (
    Path(__file__).parent.absolute() / 'templates' / f'{TOOL_NAME}_build.conf'
)

CONSOLE_SCRIPTS = [
    f'{TOOL_NAME} = botoolkit.bo_databaser.main:main',
]

NAMESPACES = {
    f'{NAMESPACE}': [
        'configure = botoolkit.bo_databaser.commands:ConfigureBODatabaserCommand',  # noqa
        'build configure = botoolkit.bo_databaser.commands:ConfigureBuildDatabaserCommand',  # noqa
        'run = botoolkit.bo_databaser.commands:RunDatabaserCommand',
        'stop = botoolkit.bo_databaser.commands:StopDatabaserCommand',
    ],
}