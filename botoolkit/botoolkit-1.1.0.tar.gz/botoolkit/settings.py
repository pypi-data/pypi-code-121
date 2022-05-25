from pathlib import (
    Path,
)


# ==============================================================================
# General
# ==============================================================================

CONFIGURATION_DIRECTORY_NAME = '.botoolkit'

CONFIGURATION_DIRECTORY_PATH = Path.home() / CONFIGURATION_DIRECTORY_NAME

DEFAULT_RSA_PRIVATE_KEY_PATH = Path.home() / '.ssh' / 'id_rsa'

ACTIVATED_TOOLS = (
    'botoolkit.bo_conf',
    'botoolkit.bo_databaser',
    'botoolkit.bo_barsdock',
    'botoolkit.bo_git',
    'botoolkit.bo_guide',
    'botoolkit.bo_ip',
    'botoolkit.bo_jenkins',
    'botoolkit.bo_jira',
    'botoolkit.bo_postgres',
    'botoolkit.bo_registry',
    'botoolkit.bo_telegram',
    'botoolkit.bo_toolkit',
    'botoolkit.bo_web_bb',
)

ENTRY_POINTS = {
    'console_scripts': [],
}


def update_settings_from_tool_path(
    tool_path: str,
):
    """
    Обновляет словарь глобальной конфигурации данными
    из settings.py, указанного приложения.
    """

    module = __import__(
        f'{tool_path}.settings',
        globals(),
        locals(),
        fromlist=['*'],
    )

    tool_name = tool_path.split('.')[1].replace('_', '').upper()

    globals_ = globals()

    filtered_attr_names = filter(
        lambda attr_name: attr_name == attr_name.upper(),
        dir(module)
    )

    for attr_name in filtered_attr_names:
        attr_value = getattr(module, attr_name)

        if attr_name == 'CONSOLE_SCRIPTS':
            ENTRY_POINTS['console_scripts'].extend(
                attr_value
            )
        elif attr_name == 'NAMESPACES':
            ENTRY_POINTS.update(attr_value)
        else:
            globals_[f'{tool_name}_{attr_name}'] = attr_value


if ACTIVATED_TOOLS:
    for tool_path in ACTIVATED_TOOLS:
        update_settings_from_tool_path(
            tool_path=tool_path,
        )
