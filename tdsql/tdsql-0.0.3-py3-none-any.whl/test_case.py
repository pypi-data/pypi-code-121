from pathlib import Path
from typing import ClassVar
import re

import pandas as pd

from tdsql.exception import InvalidInputError
from tdsql import util


class TdsqlTestCase:
    cnt: ClassVar[int] = 0

    def __init__(
        self,
        sqlpath: Path,
        replace: dict[str, str],
        expected: str,
    ):
        self.sqlpath = sqlpath
        self.actual_sql = _replace_sql(sqlpath, replace)
        self.expected_sql = expected
        self.actual_sql_result: pd.DataFrame | Exception | None = None
        self.expected_sql_result: pd.DataFrame | Exception | None = None
        self.__class__.cnt += 1
        self.id: int = self.__class__.cnt


oneline_pattern = re.compile(r"^.*--\s*tdsql-line:\s*(\S+)\s*$")
start_pattern = re.compile(r"^.*--\s*tdsql-start:\s*(\S+)\s*$")
end_pattern = re.compile(r"^.*--\s*tdsql-end:\s*(\S+)\s*$")


def _replace_sql(sqlpath: Path, replace: dict[str, str]) -> str:
    original_sql = util.read(sqlpath)
    original_sql_lines = original_sql.splitlines()

    # check where to replace
    position: dict[str, tuple[int, int]] = {}
    for i, l in enumerate(original_sql_lines):
        match_ = oneline_pattern.match(l)
        if match_ is not None:
            ident = match_.group(1)
            if position.get(ident) is not None:
                raise InvalidInputError(
                    f"{sqlpath}: `{ident}` appear twice at line {i+1}"
                )
            position[ident] = (i, i)
            continue

        match_ = start_pattern.match(l)
        if match_ is not None:
            ident = match_.group(1)
            if position.get(ident) is not None:
                raise InvalidInputError(
                    f"{sqlpath}: `{ident}` appear twice at line {i+1}"
                )
            position[ident] = (i, -1)
            continue

        match_ = end_pattern.match(l)
        if match_ is not None:
            ident = match_.group(1)
            if position.get(ident) is None:
                raise InvalidInputError(
                    f"{sqlpath}: `{ident}` has not started but ends at line {i+1}"
                )
            position[ident] = (position[ident][0], i)
            continue

    for k, v in position.items():
        if v[1] == -1:
            raise InvalidInputError(
                f"{sqlpath}: `{k}` started at line {v[0]+1} but it does not end"
            )

    # exec replacement
    replaced_sql_lines: list[str | None] = original_sql_lines.copy()  # type: ignore
    collision_check: set[int] = set()

    for ident, text in replace.items():
        if ident not in position.keys():
            raise InvalidInputError(f"{sqlpath}: `{ident}` does not appear")

        for i in range(position[ident][0], position[ident][1] + 1):
            if i in collision_check:
                raise InvalidInputError(f"{sqlpath}: cannot replace line {i+1} twice")
            else:
                collision_check.add(i)

        text_lines = text.splitlines()
        for i, l in enumerate(text_lines):
            match_ = oneline_pattern.match(l)
            if match_ is None:
                continue
            if match_.group(1) == "this":
                f, t = position[ident]
                text = "\n".join(
                    text_lines[:i] + original_sql_lines[f : t + 1] + text_lines[i + 1 :]
                )
            else:
                raise InvalidInputError(
                    f"only `-- tdsql-line: this` is allowed but got `{ident}`"
                )

        start, end = position[ident]
        replaced_sql_lines[start] = text
        for i in range(start, end):
            replaced_sql_lines[i + 1] = None

    return "\n".join([line for line in replaced_sql_lines if line is not None])
