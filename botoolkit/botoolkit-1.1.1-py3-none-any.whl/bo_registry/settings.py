from pathlib import (
    Path,
)


TOOL_NAME = NAMESPACE = 'boregistry'

TEMPLATE_CONF_FILE_PATH = (
    Path(__file__).parent.absolute() / 'templates' / f'{TOOL_NAME}.conf'
)

CONSOLE_SCRIPTS = [
    f'{TOOL_NAME} = botoolkit.bo_registry.main:main',
]

NAMESPACES = {
    f'{NAMESPACE}': [
        'configure = botoolkit.bo_registry.commands:ConfigureBORegistryCommand',
        'show images = botoolkit.bo_registry.commands:BORegistryShowImagesCommand',  # noqa
        'remove images = botoolkit.bo_registry.commands:RemoveImagesBORegistryCommand',  # noqa
        'remove image = botoolkit.bo_registry.commands:BORegistryRemoveImageCommand',  # noqa
    ],
}
