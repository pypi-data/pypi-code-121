from typing import Any, Callable, Final, Sequence, Tuple, TypeVar

import colorama
from prettytable import PrettyTable

import beni.color as bprint

_T = TypeVar('_T')


def get(
    data_list: Sequence[_T],
    *,
    title: str | None = None,
    fields: Sequence[Tuple[str, Callable[[_T], Any]]],
    rowcolor: Callable[[list[Any]], Any] | None = None,
    extend: list[list[Any]] | None = None,
):
    header_color: Final = colorama.Fore.YELLOW
    table = PrettyTable()
    if title:
        table.title = bprint.getStr(title, header_color)
    field_funclist: list[Callable[[_T], Any]] = []
    field_namelist: list[str] = []
    align_dict: dict[str, str] = {}
    for i in range(len(fields)):
        item = fields[i]
        field_funclist.append(item[1])
        field_name = item[0]
        if field_name.endswith('>'):
            field_name = field_name[:-1]
            align_dict[field_name] = 'r'
        elif field_name.endswith('<'):
            field_name = field_name[:-1]
            align_dict[field_name] = 'l'
        field_namelist.append(field_name)
    table.field_names = [bprint.getStr(x, header_color) for x in field_namelist]
    for k, v in align_dict.items():
        table.align[bprint.getStr(k, header_color)] = v
    row_list: list[list[Any]] = []
    for data in data_list:
        row = [func(data) for func in field_funclist]
        row_list.append(row)
    if extend:
        row_list.extend(extend)
    if rowcolor:
        for row in row_list:
            color = rowcolor(row)
            if color:
                for i in range(len(row)):
                    row[i] = bprint.getStr(row[i], color)
    table.add_rows(row_list)
    return str(table.get_string())
