"""Utils used by the CodeGrade API.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""
import datetime
import io
import json
import math
import re
import sys
import typing as t
import uuid
import warnings
from dataclasses import dataclass

import cg_maybe
import cg_request_args as rqa
import structlog

from . import parsers

if t.TYPE_CHECKING:
    from httpx import Response
    from httpx._types import FileContent

if sys.version_info >= (3, 8):
    from typing import Final, Literal, Protocol, TypedDict
else:  # pragma: no cover
    from typing_extensions import Final, Literal, Protocol, TypedDict

logger = structlog.get_logger()

T = t.TypeVar("T")


def response_code_matches(code: int, expected: t.Union[str, int]) -> bool:
    if expected == "default":
        return True
    elif isinstance(expected, int) and code == expected:
        return True
    return (
        isinstance(expected, str)
        and code > 100
        and code / 100 == int(expected[0])
    )


def to_multipart(
    dct: t.Dict[str, t.Any],
) -> t.Mapping[str, t.Tuple[str, "FileContent"]]:
    res: t.Dict[str, t.Tuple[str, "FileContent"]] = {}
    for key, value in dct.items():
        if isinstance(value, list):
            for idx, subval in enumerate(value):
                assert isinstance(subval, tuple)
                res[f"{key}_{idx}"] = subval  # type: ignore
        elif isinstance(value, tuple):
            res[key] = value  # type: ignore
        else:
            res[key] = (key, io.BytesIO(json.dumps(value).encode("utf-8")))

    return res


def to_dict(obj: t.Any) -> t.Any:
    if obj is None:
        return None
    elif isinstance(obj, (str, bool, int, float)):
        return obj
    elif isinstance(obj, uuid.UUID):
        return str(obj)
    elif isinstance(obj, dict):
        # Store locally for faster lookup
        _to_dict = to_dict
        return {k: _to_dict(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        # Store locally for faster lookup
        _to_dict = to_dict
        return [_to_dict(sub) for sub in obj]
    elif isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    elif isinstance(obj, datetime.timedelta):
        return obj.total_seconds()

    from .models.types import File

    if isinstance(obj, File):
        return obj.to_tuple()
    elif hasattr(obj, "to_dict"):
        return obj.to_dict()

    import decimal

    if isinstance(obj, decimal.Decimal):
        return str(obj)

    raise AssertionError("Don't know how to serialize {!r}".format(obj))


def unpack_union(typ: t.Any) -> t.Tuple[t.Type, ...]:
    if getattr(typ, "__origin__", None) == t.Union:
        subs = typ.__args__
        if any(hasattr(el, "__origin__") for el in subs):
            return tuple(s for sub in subs for s in unpack_union(sub))
        return subs
    return (typ,)


def get_error(
    response: "Response",
    code_errors: t.Sequence[
        t.Tuple[t.Sequence[t.Union[str, int]], t.Sequence[t.Any]]
    ],
) -> Exception:
    found_code = response.status_code
    for codes, make_errors in code_errors:
        if not any(response_code_matches(found_code, code) for code in codes):
            continue
        json_data = response.json()
        for idx, make_error in enumerate(make_errors):
            last = idx + 1 == len(make_errors)
            try:
                return make_error.from_dict(json_data, response=response)
            except rqa.ParseError:
                if last:
                    raise
                continue

    from .errors import ApiResponseError

    return ApiResponseError(response=response)


_WARNING_SUB = re.compile(r"\\(.)")


@dataclass
class HttpWarning:
    __slots__ = ("code", "agent", "text")
    code: int
    agent: str
    text: str

    @classmethod
    def parse(cls, *, warning: str) -> "HttpWarning":
        code, agent, text = warning.split(" ", maxsplit=2)
        text = text.strip()
        if text[0] != '"' or text[-1] != '"':
            raise ValueError("Warning string is malformed")
        text = _WARNING_SUB.sub(r"\1", text[1:-1])
        return cls(
            code=int(code),
            agent=agent,
            text=text,
        )


def log_warnings(response: "Response") -> None:
    headers = response.headers

    # Work around for different httpx versions
    get = getattr(headers, "get_list", None)
    if get is None:
        get = getattr(headers, "getlist")

    for warn_str in get("Warning"):
        try:
            warning = HttpWarning.parse(warning=warn_str)
        except ValueError:
            logger.warn(
                "Cannot parse warning",
                warning=warn_str,
                exc_info=True,
            )
        else:
            warnings.warn(
                "Got a API warning from {}: {}".format(
                    warning.agent, warning.text
                )
            )


def maybe_input(prompt: str, dflt: str = "") -> cg_maybe.Maybe[str]:
    """Queries the user for an input.

    :param prompt: The question to ask the user.
    :param dflt: Default return value.

    :returns: A Just of the user's answer or default, or Nothing in case of
              error.
    """
    try:
        res = input(
            "{}{}: ".format(
                prompt,
                " [default: {}]".format(dflt) if dflt else "",
            )
        )
    except EOFError:
        return cg_maybe.Nothing
    else:
        return cg_maybe.Just(res or dflt)


def select_from_list(
    prompt: str, lst: t.Iterable[T], make_label: t.Callable[[T], str]
) -> cg_maybe.Maybe[T]:
    """Queries the user to select one of the values from a list.

    :param prompt: The question to ask the user.
    :param lst: The list from which to select.
    :param make_label: A function that generates a label for each value in the
        list.

    :returns: A Just of the value selected by the user, or Nothing if the
              selection is invalid

    :rtype: Maybe[T]
    """
    lst = list(lst)
    max_width = math.ceil(math.log10(len(lst) + 1))
    for idx, item in enumerate(lst):
        print(
            "[{0: >{1}}] {2}".format(idx + 1, max_width, make_label(item)),
            file=sys.stderr,
        )

    while True:
        inp = maybe_input(prompt)
        if inp.is_nothing:
            return cg_maybe.Nothing

        try:
            res = lst[int(inp.value) - 1]
            print("Selecting", make_label(res), file=sys.stderr)
            return cg_maybe.Just(res)
        except ValueError:
            continue


def value_or_exit(
    maybe_value: cg_maybe.Maybe[T], err_message: str = "Value was undefined"
) -> T:
    """Get the value from a Maybe or exit the program with an error message.

    :param maybe_value: The value to extract.
    :param err_message: THe error message if there is nothing to extract.

    :returns: The contained value.
    """

    def _make_exception() -> Exception:
        print(err_message)
        return sys.exit(1)

    return maybe_value.try_extract(_make_exception)
