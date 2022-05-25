from collections import (
    defaultdict,
    namedtuple,
)
from contextlib import (
    contextmanager,
)
from importlib import (
    import_module,
)
from inspect import (
    isclass,
)
from pathlib import (
    Path,
)
from re import (
    finditer,
)
from typing import (
    Dict,
    Iterable,
    List,
    Tuple,
    Type,
    Union,
)

from cliff.app import (
    App,
)
from configupdater import (
    ConfigUpdater,
)
from docker.errors import (
    BuildError,
)

from botoolkit import (
    settings,
)
from botoolkit.core.loggers import (
    logger,
)
from botoolkit.settings import (
    CONFIGURATION_DIRECTORY_PATH,
)


def fill_config_from_source(
    src_config: ConfigUpdater,
    dst_config: ConfigUpdater,
):
    """
    Заполнение целевого конфига существующими значениями исходного конфига
    """
    sections = set(dst_config.sections()).intersection(
        src_config.sections()
    )

    for section in sections:
        new_options = [
            option
            for option in dst_config[section]
        ]
        old_options = [
            option
            for option in src_config[section]
        ]

        options = set(new_options).intersection(old_options)

        for option in options:
            src_option = src_config.get(
                section=section,
                option=option,
            )

            src_option_value = src_option.value

            if src_option_value:
                if '%' in src_option_value:
                    src_option_value = src_option_value.replace('%', '%%')

                dst_config.set(
                    section=section,
                    option=option,
                    value=src_option_value,
                )


def raise_exception(
    exception_class: Type[Exception],
    message: str,
    is_silent: bool = False,
):
    """
    Функция генерации исключения с тихим режимом
    """
    if not is_silent:
        raise exception_class(message)


def get_tool_conf_file_path(
    tool_name: str,
) -> Path:
    """
    Получение пути конфигурационного инструмента
    """
    return CONFIGURATION_DIRECTORY_PATH / f'{tool_name}.conf'


def get_all_tool_names(
    settings_module,
    exclude: Tuple[str] = (),
) -> List[str]:
    """
    Получение списка зарегистрированных инструментов
    """
    tool_name_attr_names = filter(
        lambda attr_name: (
            attr_name == attr_name.upper() and
            attr_name.endswith('TOOL_NAME')
        ),
        dir(settings_module)
    )

    tool_names = list(
        filter(
            lambda tn: tn and tn not in exclude,
            (
                getattr(
                    settings_module,
                    attr_name,
                )
                for attr_name in tool_name_attr_names
            )
        )
    )

    return tool_names


def get_tool_template_conf_file_path(
    tool_name: str,
) -> Path:
    """
    Получение пути до шаблона конфигурационного файла инструмента
    """
    return getattr(
        settings,
        f'{tool_name.upper()}_TEMPLATE_CONF_FILE_PATH',
        None,
    )


Results = namedtuple('Results', ['sorted', 'cyclic'])


def topological_sort(
    dependency_pairs: Iterable[Union[str, Tuple[str, str]]],
):
    """
    Топологическая сортировка позволяет произвести сортировку элементов
    согласно зависимостям между ними

    print( topological_sort('aa'.split()) )
    print( topological_sort('ah bg cf ch di ed fb fg hd he ib'.split()) )

    Thanks for Raymond Hettinger
    """
    num_heads = defaultdict(int)  # num arrows pointing in
    tails = defaultdict(list)  # list of arrows going out
    heads = []  # unique list of heads in order first seen
    for h, t in dependency_pairs:
        num_heads[t] += 1
        if h in tails:
            tails[h].append(t)
        else:
            tails[h] = [t]
            heads.append(h)

    ordered = [h for h in heads if h not in num_heads]
    for h in ordered:
        for t in tails[h]:
            num_heads[t] -= 1
            if not num_heads[t]:
                ordered.append(t)
    cyclic = [n for n, heads in num_heads.items() if heads]

    return Results(ordered, cyclic)


def get_all_configured_tool_apps(
    exclude: Tuple[str] = None,
) -> Dict[str, Dict[str, Union[Type[App], bool, int]]]:
    """
    Получение приложений зарегистрированных инструментов

    Не удалось использовать, потому что при
    """
    from botoolkit.core.commands import (
        BaseBOConfigureCommand,
    )

    tool_name_app_map = {}
    dependency_pairs = set()
    all_tool_names = set()

    for tool_path in settings.ACTIVATED_TOOLS:
        settings_module = import_module(
            f'{tool_path}.settings',
        )

        tool_names = get_all_tool_names(
            settings_module=settings_module,
        )
        all_tool_names.update(tool_names)

        main_module = import_module(
            f'{tool_path}.main',
        )

        app_class = None
        for main_attr_name in dir(main_module):
            entity = getattr(
                main_module,
                main_attr_name,
                None,
            )

            if (
                isclass(entity) and
                issubclass(entity, App) and
                entity.__name__ != App.__name__
            ):
                app_class = entity
                break

        if app_class:
            for tool_name in tool_names:
                tool_name_app_map[tool_name] = {
                    'app_class': app_class,
                    'is_configured': False,
                    'index': 0,
                }

                commands_module = import_module(
                    f'{tool_path}.commands',
                )

                for attr_name in dir(commands_module):
                    entity = getattr(
                        commands_module,
                        attr_name,
                        None,
                    )

                    if (
                        isclass(entity) and
                        issubclass(entity, BaseBOConfigureCommand)
                    ):
                        e = entity(
                            app=None,
                            app_args=None,
                        )

                        if e.tool_name and e.is_force_configure:
                            tool_name_app_map[e.tool_name] = {
                                'app_class': app_class,
                                'is_configured': True,
                                'index': 0,
                            }

                            required_config_tool_names = getattr(
                                e,
                                'required_config_tool_names',
                                None,
                            )

                            if required_config_tool_names:
                                for required_tool_name in required_config_tool_names:
                                    if (
                                        required_tool_name not in exclude and
                                        tool_name != required_tool_name
                                    ):
                                        dependency_pairs.add(
                                            (
                                                tool_name,
                                                required_tool_name,
                                            )
                                        )
                                        all_tool_names.add(required_tool_name)

    sorted_result = topological_sort(
        dependency_pairs=dependency_pairs,
    )

    sorted_result_tool_names = (
        list(reversed(sorted_result.sorted)) + sorted_result.cyclic
    )
    without_dependencies = all_tool_names.difference(sorted_result_tool_names)
    sorted_tool_names = list(without_dependencies) + sorted_result_tool_names

    for index, tool_name in enumerate(sorted_tool_names):
        tool_name_app_map[tool_name]['index'] = index

    return tool_name_app_map


@contextmanager
def print_build_image_exception_log():
    """
    Контекстный менеджер для печати лога сборки образа при возникновении ошибок
    """
    try:
        yield
    except BuildError as e:
        for line in e.build_log:
            if 'stream' in line:
                logger.write(f'{line["stream"].strip()}\n')
        raise


def findfirst(regex, text, default=None):
    """
    Возвращает первое совпадение согласно регулярному выражению или default
    """
    try:
        result = next(finditer(regex, text))
    except StopIteration:
        result = default

    return result
