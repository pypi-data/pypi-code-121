"""Helpers used by VSS CLI (vss-cli)."""
import contextlib
import csv
from http.client import HTTPConnection
import io
import json
import logging
import re
import shlex
import shutil
from typing import Any, Dict, Generator, List, Optional, Tuple, Union, cast

from pygments import highlight
from pygments.formatters import TerminalFormatter
from pygments.lexers import JsonLexer, YamlLexer
from ruamel.yaml import YAML
from tabulate import tabulate

import vss_cli.const as const
import vss_cli.yaml as yaml

_LOGGING = logging.getLogger(__name__)


def bytes_to_str(item: Optional[Union[str, bytes]]) -> str:
    """Convert bytes to string."""
    if isinstance(item, bytes):
        return item.decode('utf-8')
    if item is None:
        return ''
    return str(item)


def to_attributes(entry: str) -> Dict[str, str]:
    """Convert list of key=value pairs to dictionary."""
    if not entry:
        return {}

    lexer = shlex.shlex(entry, posix=True)
    lexer.whitespace_split = True
    lexer.whitespace = ','
    attributes_dict = {}  # type: Dict[str, str]
    attributes_dict = dict(
        pair.split('=', 1) for pair in lexer  # type: ignore
    )
    return attributes_dict


def to_tuples(entry: str) -> List[Tuple[str, str]]:
    """Convert list of key=value pairs to list of tuples."""
    if not entry:
        return []

    lexer = shlex.shlex(entry, posix=True)
    lexer.whitespace_split = True
    lexer.whitespace = ','
    attributes_list = []  # type: List[Tuple[str,str]]
    attributes_list = list(
        tuple(pair.split('=', 1)) for pair in lexer  # type: ignore
    )
    return attributes_list


def raw_format_output(
    output: str,
    data: List[Dict[str, Any]],
    yamlparser: YAML,
    columns: Optional[List] = None,
    columns_width: Optional[int] = -1,
    no_headers: bool = False,
    table_format: str = 'plain',
    sort_by: Optional[str] = None,
    single: Optional[str] = None,
    highlighted: bool = True,
) -> str:
    """Format the raw output."""
    if output == 'auto':
        _LOGGING.debug(
            "Output `auto` thus using %s", const.DEFAULT_DATA_OUTPUT
        )
        output = const.DEFAULT_DATA_OUTPUT

    if sort_by:
        _sort_table(data, sort_by)

    if output == 'json':
        try:
            if highlighted:
                return highlight(
                    json.dumps(data, indent=2, sort_keys=False),
                    JsonLexer(),
                    TerminalFormatter(),
                )
            else:
                return json.dumps(data, indent=2, sort_keys=False)
        except ValueError:
            return str(data)
    elif output == 'ndjson':
        try:
            return json.dumps(data)
        except ValueError:
            return str(data)
    elif output == 'yaml':
        try:
            if highlighted:
                return highlight(
                    cast(str, yaml.dump_yaml(yamlparser, data)),
                    YamlLexer(),
                    TerminalFormatter(),
                )
            else:
                return cast(str, yaml.dump_yaml(yamlparser, data))
        except ValueError:
            return str(data)
    elif output == 'table':
        from jsonpath_ng import parse

        if not columns:
            columns = const.COLUMNS_DEFAULT

        fmt = [(v[0], parse(v[1] if len(v) > 1 else v[0])) for v in columns]
        result = []
        if single:
            dat = data[0]
            for fmtpair in fmt:
                val = [match.value for match in fmtpair[1].find(dat)]
                val_str = ", ".join(map(str, val))
                line = const.COLUMNS_TWO_FMT.format(fmtpair[0], val_str)
                result.append(line)
            res = '\n'.join(result)
            return res
        else:
            if no_headers:
                headers = []  # type: List[str]
            else:
                headers = [v[0] for v in fmt]
            for item in data:
                row = []
                for fmtpair in fmt:
                    val = [match.value for match in fmtpair[1].find(item)]
                    row.append(", ".join(map(str, val)))

                result.append(row)

            if columns_width is None:
                columns_width = const.COLUMNS_WIDTH_DEFAULT

            # Truncates data
            if columns_width > -1 and result:
                if columns_width == 0:  # calculate size
                    terminal_size = shutil.get_terminal_size()
                    number_c = min([len(r) for r in result])
                    columns_width = int(terminal_size.columns / number_c)
                max_str = columns_width - len(const.COLUMNS_WIDTH_STR)
                result = [
                    [
                        (
                            c
                            if len(c) < columns_width
                            else c[:max_str] + const.COLUMNS_WIDTH_STR
                        )
                        for c in row
                    ]
                    for row in result
                ]
            if table_format == 'csv':
                output = io.StringIO()
                writer = csv.writer(output, quoting=csv.QUOTE_NONNUMERIC)
                writer.writerow(headers)
                for row in result:
                    writer.writerow(row)
                res = output.getvalue()  # type: str
            else:
                res = tabulate(
                    result, headers=headers, tablefmt=table_format
                )  # type: str
            return res
    else:
        raise ValueError(
            f"Output Format was {output}, "
            f"expected either 'json' or 'yaml' or 'table'"
        )


def _sort_table(result: List[Any], sort_by: str) -> List[Any]:
    """Sort table based on attribute."""
    from jsonpath_ng import parse

    expr = parse(sort_by)

    def _internal_sort(row: Dict[Any, str]) -> Any:
        val = next(iter([match.value for match in expr.find(row)]), None)
        return (val is None, val)

    result.sort(key=_internal_sort)
    return result


def format_output(
    ctx,
    data: List[Dict[str, Any]],
    columns: Optional[List] = None,
    single: Optional[bool] = False,
) -> str:
    """Format data to output based on settings in ctx/Context."""
    return raw_format_output(
        ctx.output,
        data,
        ctx.yaml(),
        columns,
        ctx.columns_width,
        ctx.no_headers,
        ctx.table_format,
        ctx.sort_by,
        single=single,
    )


def debug_requests_on() -> None:
    """Switch on logging of the requests module."""
    HTTPConnection.set_debuglevel(cast(HTTPConnection, HTTPConnection), 1)

    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger('requests.packages.urllib3')
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True


def debug_requests_off() -> None:
    """Switch off logging of the requests module.

    Might have some side-effects.
    """
    HTTPConnection.set_debuglevel(cast(HTTPConnection, HTTPConnection), 1)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.WARNING)
    root_logger.handlers = []
    requests_log = logging.getLogger('requests.packages.urllib3')
    requests_log.setLevel(logging.WARNING)
    requests_log.propagate = False


@contextlib.contextmanager
def debug_requests() -> Generator:
    """Yieldable way to turn on debugs for requests.

    with debug_requests(): <do things>
    """
    debug_requests_on()
    yield
    debug_requests_off()


def get_hostname_from_url(
    url: str, hostname_regex: str = const.DEFAULT_HOST_REGEX
) -> str:
    """Parse hostname from URL."""
    re_search = re.search(hostname_regex, url)
    _, _hostname = re_search.groups() if re_search else ('', '')
    _host = _hostname.split('.')[0] if _hostname.split('.') else ''
    return _host


def capitalize(value: str) -> str:
    """Capitalize string."""
    return re.sub(r"(\w)([A-Z])", r"\1 \2", value).title()


def str2bool(value: str) -> bool:
    """Convert string to boolean."""
    return value.lower() in ("yes", "true", "t", "1", "y")


def dump_object(obj: Any, _key: str = None, _list: List[str] = None) -> None:
    """Dump dictionary in kv format."""
    for key, value in obj.items():
        if isinstance(value, list):
            for i in value:
                if isinstance(i, dict):
                    dump_object(i, key, _list)
                else:
                    _list.append(const.COLUMNS_TWO_FMT.format(key, i))
        elif not isinstance(value, dict) and not isinstance(value, list):
            _k = _key + '.' + key
            _list.append(const.COLUMNS_TWO_FMT.format(_k, value))
        elif key not in ['_links']:
            dump_object(value, key, _list)


def process_sort(ctx, param, value: List[str]) -> List[str]:
    """Process sort parameters from input."""
    ops = ['asc', 'desc']
    processed_sorts = []
    sorts = [s.split('=') for s in value]
    _LOGGING.debug(f'trying to process sort options {sorts}')
    try:
        for sort in sorts:
            sort_by = list(sort)
            if len(sort) < 2:
                sort_by.insert(1, 'desc')
            op = sort_by[1]
            if op in ops:
                sort_by = ','.join(sort_by)
                processed_sorts.append(sort_by)
            else:
                _LOGGING.warning(f'ignoring sort option: {op}')
    except Exception as ex:
        _LOGGING.warning(
            f'an error occurred processing sort options: {ex}', exc_info=True
        )
    return processed_sorts


def process_filters(ctx, param, value: List[str]) -> List[str]:
    """Process filter parameter."""
    ops = ['gt', 'lt', 'le', 'like', 'in', 'ge', 'eq', 'ne']
    processed_filters = []
    wc = '%'
    filters = [f.split('=') for f in value]
    _LOGGING.debug(f'trying to process filters {filters}')
    try:
        for filtr in filters:
            f = filtr[1]
            has_wc = wc in f
            op_query = f.split(',')
            op_query_val_type = str
            # op_query contains (operator, value) if any
            filter_by = list(filtr)
            # filter_by contains (attribute, filter_str)
            if op_query:
                has_op = op_query[0] in ops
                check_index = 1 if has_op else 0
                # check for op_query_val_type
                try:
                    int(op_query[check_index])
                    op_query_val_type = int
                except ValueError:
                    pass
                if not has_op and op_query_val_type == str:
                    # if query does not have operator,
                    # use like by default
                    _LOGGING.debug('operator not found in query. using like')
                    filter_by.insert(1, 'like')
                if not has_op and op_query_val_type == int:
                    _LOGGING.debug('operator not found in query. using eq')
                    filter_by.insert(1, 'eq')
                if has_op and op_query_val_type == str:
                    _LOGGING.debug(
                        f'operator found in query. '
                        f'{op_query[0]} : {filter_by}'
                    )
                elif not has_wc and op_query_val_type == str:
                    _LOGGING.debug(f'{filter_by}')
                    filter_by[2] = f'%{filter_by[2]}%'
            filter_by = ','.join(filter_by)
            processed_filters.append(filter_by)
    except Exception as ex:
        _LOGGING.warning('ignoring invalid filters')
        _LOGGING.debug(f'exception while parsing filters: {ex}', exc_info=True)
    _LOGGING.debug(f'processed filters {processed_filters}')
    return processed_filters
