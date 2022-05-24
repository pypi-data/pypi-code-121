from pathlib import (
    Path,
)


TOOL_NAME = NAMESPACE = 'boconf'

GENERATOR_TOOL_NAME = 'boconf_generator'

TEMPLATE_CONF_FILE_PATH = (
    Path(__file__).parent.absolute() / 'templates' / f'{TOOL_NAME}.conf'
)

CONSOLE_SCRIPTS = [
    f'{TOOL_NAME} = botoolkit.bo_conf.main:main',
]

NAMESPACES = {
    f'{NAMESPACE}': [
        'configure = botoolkit.bo_conf.commands:ConfigureBOConfCommand',
        'check plugins = botoolkit.bo_conf.commands:CheckUnregisteredPluginsCommand',  # noqa
        'check options = botoolkit.bo_conf.commands:CheckUnregisteredOptionsCommand',  # noqa
        'check consistency = botoolkit.bo_conf.commands:CheckConfigurationConsistencyCommand',  # noqa
        'generator configure = botoolkit.bo_conf.commands:ConfigureBOConfGeneratorCommand',  # noqa
        'generator generate = botoolkit.bo_conf.commands:GenerateBOConfGeneratorCommand',  # noqa
    ],
}
