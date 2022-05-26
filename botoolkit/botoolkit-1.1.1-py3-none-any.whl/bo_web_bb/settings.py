from pathlib import (
    Path,
)


TOOL_NAME = NAMESPACE = 'bowebbb'

TEMPLATE_CONF_FILE_PATH = (
    Path(__file__).parent.absolute() / 'templates' / f'{TOOL_NAME}.conf'
)

WEB_BB_IMAGES_DIR_PATH = (
    Path(__file__).parent.absolute().absolute() / 'images'
)
BASE_WEB_BB_APP_IMAGE_DIR_PATH = (
    WEB_BB_IMAGES_DIR_PATH / 'base_web_bb_app'
)
WEB_BB_APP_IMAGE_DIR_PATH = (
    WEB_BB_IMAGES_DIR_PATH / 'web_bb_app'
)

BASE_WEB_BB_APPLICATION_IMAGE_NAME = 'base-web-bb-application'
BASE_WEB_BB_APPLICATION_CONTAINER_NAME = 'base-web-bb-application-container'

WEB_BB_APPLICATION_IMAGE_NAME = 'web-bb-application'
WEB_BB_APPLICATION_CONTAINER_NAME = 'web-bb-application-container'

CONSOLE_SCRIPTS = [
    f'{TOOL_NAME} = botoolkit.bo_web_bb.main:main',
]

NAMESPACES = {
    f'{NAMESPACE}': [
        'configure = botoolkit.bo_web_bb.commands:ConfigureBOWebBBCommand',
        'build base = botoolkit.bo_web_bb.commands:BuildBaseWebBBApplicationImageCommand',
    ],
}
