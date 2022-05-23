from typing import List, Optional

from nwon_baseline.print_helper import print_color
from nwon_baseline.typings.terminal_colors import TerminalColors


def import_data_from_file(
    path: str, split_character: str, expected_column_names: List[str]
) -> Optional[List[List[str]]]:
    """
    Gets data from a file that is separated by some characters and arranged in one dataset per line.

    By defining the column names we now how much data you expect per line and can provide better error messages

    In the process some validation is done on the file
    """

    lines = __lines_from_import_file(path)

    if lines is None:
        return None

    return [
        line
        for index, line in enumerate(__separate_data_in_line(lines, split_character))
        if __validate_data_in_line(line, expected_column_names, split_character, index)
    ]


def __lines_from_import_file(path: str) -> Optional[List[str]]:
    try:
        with open(path, encoding="utf-8") as file:
            file_contents = file.read()
            return file_contents.splitlines()
    except FileNotFoundError as exc:
        print_color(exc.__str__(), TerminalColors.ERROR)
        return None


def __separate_data_in_line(lines: List[str], split_character: str) -> List[List[str]]:
    return [line.split(split_character) for line in lines if split_character in line]


def __validate_data_in_line(
    data_from_line: List[str],
    expected_values: List[str],
    split_character: str,
    index: int,
) -> Optional[List[str]]:
    if data_from_line.__len__() != expected_values.__len__():
        print_color(
            f"Error in Line {index+1}\n{split_character.join(data_from_line)}",
            TerminalColors.ERROR,
        )
        print_color(
            f"Each line should only contain the following {expected_values.__len__()} information separated by a '{split_character}': \n {split_character.join(expected_values)}",
            TerminalColors.WARNING,
        )
        return None

    return data_from_line
