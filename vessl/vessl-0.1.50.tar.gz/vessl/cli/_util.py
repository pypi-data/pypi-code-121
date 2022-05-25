from datetime import datetime
from typing import Any, Callable, Dict, List, Union

import click
import inquirer
from terminaltables import AsciiTable

from openapi_client.models import StorageFile
from vessl.util.constant import WEB_HOST

TAB_SIZE = 2
UNDEFINED = click.style("undefined", fg="red")


class Endpoint:
    dataset = WEB_HOST + "/{}/datasets/{}"  # Organization name, dataset name
    experiment = (
        WEB_HOST + "/{}/{}/experiments/{}"
    )  # Organization name, project name, experiment number
    experiment_logs = (
        WEB_HOST + "/{}/{}/experiments/{}/logs"
    )  # Organization name, project name, experiment number
    model_repository = WEB_HOST + "/{}/models/{}"  # Organization name, repository name
    model = WEB_HOST + "/{}/models/{}/{}"  # Organization name, repository name, number
    organization = WEB_HOST + "/{}"  # Organization name
    project = WEB_HOST + "/{}/{}"  # Organization name, project name
    sweep = WEB_HOST + "/{}/{}/sweeps/{}"  # Organization name, project name, sweep name
    sweep_logs = (
        WEB_HOST + "/{}/{}/sweeps/{}/logs"
    )  # Organization name, project name, sweep name
    workspace = WEB_HOST + "/{}/workspaces/{}"  # Organization name, workspace id


def format_key(key: str) -> str:
    return click.style(key, fg="green")


def print_table(
    objects: List[Any], keys: List[str], data_func: Callable, **kwargs
) -> None:
    table_data = [[format_key(x) for x in keys]]
    table_data.extend(data_func(x) for x in objects)

    table = AsciiTable(table_data)
    table.inner_column_border = kwargs.get("inner_column_border", False)
    table.inner_heading_row_border = kwargs.get("inner_heading_row_border", False)
    table.inner_footing_row_border = kwargs.get("inner_footing_row_border", False)
    table.outer_border = kwargs.get("outer_border", False)

    print(table.table)


def format_data(data: Any, depth: int) -> List[str]:
    indent = " " * (TAB_SIZE * depth + 1)

    if not isinstance(data, dict):
        # `data` is primitive type
        return [f"{indent}{data}"]

    lines = []
    for key, value in data.items():
        if isinstance(value, dict):
            lines.append(f"{indent}{format_key(key)}")
            lines.extend(format_data(value, depth + 1))
        elif isinstance(value, list):
            lines.append(f"{indent}{format_key(key)}")
            for x in value:
                # TODO: find a more elegant way. Perhaps yaml library?
                additional_lines = format_data(x, depth + 1)
                additional_lines[0] = additional_lines[0].lstrip()
                additional_lines[0] = f"{indent}- {additional_lines[0]}"
                lines.extend(additional_lines)
        else:
            lines.append(f"{indent}{format_key(key)} {value}")
    return lines


def print_data(data: Dict[str, Any]) -> None:
    lines = format_data(data, 0)
    print("\n".join(lines))


def print_logs(logs: List[Any]):
    timezone = datetime.now().astimezone().tzinfo
    for log in logs:
        ts = datetime.fromtimestamp(log.timestamp, tz=timezone).strftime("%H:%M:%S.%f")
        message = log.message.replace("\\r", "\n").replace("\\n", "\n")
        for x in message.split("\n"):
            print(f"[{ts}] {x}")


def truncate_datetime(value: datetime) -> Union[str, datetime]:
    if not value:
        return UNDEFINED
    return value.replace(microsecond=0)


def format_size(value: int, suffix="B") -> str:
    if value == 0:
        return "0 B"

    for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
        if abs(value) < 1024.0:
            return f"{value:.1f} {unit}{suffix}"
        value /= 1024.0
    return f"{value:.1f} Yi{suffix}"


def format_bool(value: bool, true_value: str = "Y", false_value: str = "N") -> str:
    return true_value if value else false_value


def format_string(value: str, null_value: str = "None", empty_value: str = "-") -> str:
    if value is None:
        return null_value
    if not value:
        return empty_value
    return value


def format_url(url: str) -> str:
    """Prints in url format

    Replace whitespaces with %20. More url rules could be added.
    """
    return url.replace(" ", "%20")


def print_volume_files(
    files: List[StorageFile],
    keys: List[str] = None,
    data_func: Callable = None,
    **kwargs,
) -> None:
    """Print volume files

    Separately defined as a util function because it is used often across many files.
    TODO: Support recursive. Add Sort? Parse paths?
    """

    if keys is None:
        keys = ["Path", "Dir", "Size"]

    if data_func is None:
        data_func = lambda x: [
            x.path,
            format_bool(x.is_dir),
            format_size(x.size) if not x.is_dir else "-",
        ]

    print_table(files, keys, data_func)


def prompt_choices(text: str, choices: List[Any], default: Any = None) -> Any:
    """Prompt choices

    Args:
        choices (list): A list of choices to display, or a list of 2-tuples where
                        the first element is the choice to display and the second
                        element is return value.
    """
    key = "question"
    inquiry = inquirer.List(key, message=text, default=default, choices=choices)
    return inquirer.prompt([inquiry], raise_keyboard_interrupt=True).get(key)


def prompt_checkbox(text: str, choices: List[Any], default: Any = None) -> Any:
    key = "question"
    inquiry = inquirer.Checkbox(key, message=text, default=default, choices=choices)
    return inquirer.prompt([inquiry], raise_keyboard_interrupt=True).get(key)


def generic_prompter(
    text: str, type: click.ParamType = click.STRING, default=None
) -> Callable:
    def prompter(ctx: click.Context, param: click.Parameter, value: str):
        return click.prompt(text, type=type, default=default)

    return prompter


def choices_prompter(text: str, choices: List[Any], default: Any = None) -> Callable:
    def prompter(ctx: click.Context, param: click.Parameter, value: str):
        return prompt_choices(text, choices, default)

    return prompter


def sizeof_fmt(num, suffix="B"):
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"