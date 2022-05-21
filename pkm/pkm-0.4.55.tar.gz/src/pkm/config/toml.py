import re
from copy import copy
from dataclasses import dataclass
from numbers import Number
from pathlib import Path
from typing import Optional, Dict, Any, Mapping, List, Tuple, Union, MutableMapping, Callable

from pkm.utils.parsers import SimpleParser

_KEY_RX = re.compile(r'[a-zA-Z\d\-_]+')
KEY_T = Tuple
DUMPS_T = Callable[[Dict[str, Any]], str]


class TimeLiteral(str):
    pass


class Table(Dict[str, Any]):

    def __init__(self, *args, style: Optional[Dict[str, str]] = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.style: Dict[str, str] = style if style is not None else {'display': 'auto'}


class Array(List[Any]):
    def __init__(self, *args, style: Optional[Dict[str, str]] = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.style: Dict[str, str] = style if style is not None else {'display': 'auto'}


@dataclass
class _ValueStyle:
    prolog: str = ''
    epilog: str = ''
    content_trailing: str = ''

    value_str: Optional[str] = None
    value_sig: int = 0

    display: str = 'auto'


@dataclass
class _KeyStyle:
    prolog: str = ''
    epilog: str = ''
    key_str: Optional[str] = None
    display: str = 'auto'


_DEFAULT_VALUE_STYLE = _ValueStyle()
_DEFAULT_KEY_STYLE = _KeyStyle()


class _StyleSheet:
    def __init__(self):
        self.keys: Dict[KEY_T, _KeyStyle] = {}
        self.values: Dict[KEY_T, _ValueStyle] = {}

    def lastify(self, key: KEY_T) -> KEY_T:
        lk = len(key) + 1
        index = sum(len(k) == lk and k[:-1] == key for k in self.keys.keys())
        return *key, index

    def set_key_style(self, key: KEY_T, style: _KeyStyle):
        self.keys[key] = style

    def set_value_style(self, key: KEY_T, value: Any, style: _ValueStyle):
        if isinstance(value, (Mapping, List)):
            style.value_sig = type(value)
        else:
            style.value_sig = id(value)

        self.values[key] = style

    def update_value_auto_display(self, key: KEY_T, value: Any, display: str):
        if key not in self.values:
            self.set_value_style(key, value, _ValueStyle(display=display))
        else:
            vstyle = self.values[key]
            if vstyle.display == 'auto':
                vstyle.display = display

    def key_style(self, key: KEY_T, display: str = 'auto') -> _KeyStyle:
        result = self.keys.get(key) or _DEFAULT_KEY_STYLE

        if display != 'auto' and result.display != display:
            result = copy(result)
            result.display = display
            if display == 'assignment':
                result.epilog = ' '

        return result

    def value_style(self, key: KEY_T, value: Any, display: str = 'auto') -> _ValueStyle:
        predefined_style = self.values.get(key)
        if not predefined_style or \
                (predefined_style.value_sig is not type(value) and predefined_style.value_sig != id(value)):
            predefined_style = _DEFAULT_VALUE_STYLE

        if isinstance(value, (Table, Array)):
            predefined_style = _ValueStyle(**value.style)

        if predefined_style.display != 'auto' and (display == 'auto' or display == predefined_style.display):
            return predefined_style

        vstyle = copy(predefined_style)

        if display != 'auto':
            vstyle.display = display
        else:
            vstyle.display = 'inline'
            if isinstance(value, Mapping):
                is_root = not key
                is_first_level = len(key) == 1
                has_no_assignments = all(
                    isinstance(it, Mapping) or
                    (isinstance(it, List) and self.value_style((*key, k), it).display == 'table-array')
                    for k, it in value.items())
                contains_large_data = \
                    len(value) > 5 or \
                    any(isinstance(it, (Mapping, List)) or (isinstance(it, str) and len(it) > 40)
                        for it in value.values())

                if is_root:
                    vstyle.display = 'regular'
                elif has_no_assignments:
                    vstyle.display = 'hidden'
                elif contains_large_data or is_first_level:
                    vstyle.display = 'regular'

            elif isinstance(value, List):
                has_items = len(value) > 0
                has_no_assignments = all(isinstance(it, Mapping) for it in value)
                if has_items and has_no_assignments:
                    vstyle.display = 'table-array'

        # configure auto display
        if vstyle.display == 'inline':
            vstyle.prolog = ' '

        return vstyle


# noinspection PyMethodMayBeStatic
class _Writer:
    def __init__(self, style: Optional[_StyleSheet] = None):
        self.style = style or _StyleSheet()

    def write(self, data: Dict[str, Any]) -> str:
        key = ()
        return self._write_value(data, key, self.style.value_style(key, data)).rstrip()

    def _write_value(self, data: Any, key: KEY_T, vstyle: _ValueStyle) -> str:
        if isinstance(data, bool):
            return self._write_bool(data, vstyle)

        if isinstance(data, (Number, TimeLiteral)):
            return self._write_nummeric_like(data, vstyle)

        if isinstance(data, str):
            return self._write_str(data, vstyle)

        if isinstance(data, Mapping):
            return self._write_table(data, key, vstyle)

        if isinstance(data, List):
            return self._write_list(data, key, vstyle)

        raise ValueError(f"Unknown value type: {type(data)} for key {key}")

    def _write_nummeric_like(self, data: Any, style: _ValueStyle) -> str:
        v = style.value_str
        if v is None:
            v = str(data)

        return f"{style.prolog}{v}{style.epilog}"

    def _write_bool(self, data: Any, style: _ValueStyle) -> str:
        v = style.value_str
        if v is None:
            v = 'true' if data else 'false'

        return f"{style.prolog}{v}{style.epilog}"

    def _write_list(self, data: List[Any], key: KEY_T, vstyle: _ValueStyle) -> str:
        if vstyle.display == 'inline':  # TODO: support inline column and inline grid
            return self._write_inline_list(data, key, vstyle)
        return self._write_table_list(data, key, vstyle)

    def _write_inline_list(self, data: List[Any], key: KEY_T, vstyle: _ValueStyle) -> str:
        result = f"{vstyle.prolog}["

        def _write_value(v: Any, i: int) -> str:
            k = (*key, i)
            s = self.style.value_style(k, v, 'inline')
            return self._write_value(v, k, s)

        result += ', '.join(_write_value(v, i) for i, v in enumerate(data))
        result += f'{vstyle.content_trailing}]{vstyle.epilog}'
        return result

    def _write_table(self, data: Mapping[str, Any], key: KEY_T, vstyle: _ValueStyle) -> str:
        if vstyle.display == 'regular':
            return self._write_regular_table(data, key, vstyle)

        if vstyle.display == 'hidden':
            return self._write_hidden_table(data, key, vstyle)

        if vstyle.display == 'inline':
            return self._write_inline_table(data, key, vstyle)

        if vstyle.display == 'dotted':
            return self._write_dotted_table(data, key, vstyle)

        raise ValueError(f"unknown table display style: {vstyle.display}")

    def _write_str(self, data: str, vstyle: _ValueStyle) -> str:
        value_str = vstyle.value_str
        if value_str is None:
            escaped = data.translate({
                ord('\b'): '\\b',
                ord('\t'): '\\t',
                ord('\n'): '\\n',
                ord('\f'): '\\f',
                ord('\r'): '\\r',
                ord('"'): '\\"',
                ord('\\'): '\\\\',
            })

            value_str = f'"{escaped}"'

        return f'{vstyle.prolog}{value_str}{vstyle.epilog}'

    def _write_key(self, key: KEY_T, offset: int, display: str) -> str:

        if not key:
            return ''

        key_style = self.style.key_style(key, display)
        result = key_style.prolog

        key_str = key_style.key_str
        if not key_str:
            key_str = ''
            if display == 'table':
                key_str += '['
            elif display == 'table-array-item':
                key_str += '[['

            key_str += '.'.join(
                self._write_key_part(key[0:i])
                for i in range(offset + 1, len(key) + 1)
                if isinstance(key[i - 1], str))

            if display == 'table':
                key_str += ']'
            elif display == 'table-array-item':
                key_str += ']]'

        result += key_str
        result += key_style.epilog
        if display != 'assignment':
            result += '\n'

        return result

    def _write_key_part(self, part: KEY_T) -> str:
        if _KEY_RX.fullmatch(part[-1]):
            return part[-1]
        else:
            return self._write_str(part[-1], _DEFAULT_VALUE_STYLE)

    def _write_regular_table(
            self, data: Mapping[str, Any],
            key: KEY_T, vstyle: _ValueStyle) -> str:

        result = vstyle.prolog
        key_display = vstyle.display if vstyle.display == 'table-array-item' else 'table'
        result += self._write_key(key, 0, key_display)

        delayed_items: Dict[KEY_T, Any] = {}
        has_assignments = False

        for partial_key, item in data.items():
            item_key = (*key, partial_key)
            item_style = self.style.value_style(item_key, item)

            if item_style.display == 'inline':
                result += f"{self._write_key(item_key, len(key), 'assignment')}" \
                          f"={self._write_value(item, item_key, item_style)}\n"
                has_assignments = True
            else:
                if item_style.display == 'dotted':
                    result += self._write_value(item, item_key, self.style.value_style(item_key, item))
                    has_assignments = True
                else:
                    delayed_items[item_key] = item

        if has_assignments:
            result += '\n'

        for item_key, item in delayed_items.items():
            result += self._write_value(item, item_key, self.style.value_style(item_key, item))

        result += vstyle.epilog

        return result

    # noinspection PyUnusedLocal
    def _write_hidden_table(self, data: Mapping[str, Any], key: KEY_T, vstyle: _ValueStyle) -> str:
        result = ''

        for partial_key, item in data.items():
            item_key = (*key, partial_key)

            is_list = isinstance(item, List)
            is_table = isinstance(item, Mapping)

            inappropriate_item = not is_list and not is_table
            inappropriate_item = inappropriate_item or is_list and any(not isinstance(it, Mapping) for it in item)

            if inappropriate_item:
                return self._write_regular_table(data, key, self.style.value_style(key, data, 'regular'))

            item_style = self.style.value_style(item_key, item)
            if item_style.display == 'inline':
                item_style = self.style.value_style(item_key, item, 'regular')

            if is_list:
                result += self._write_table_list(item, item_key, item_style)
            elif item_style.display == 'hidden':
                result += self._write_hidden_table(item, item_key, item_style)
            else:
                result += self._write_regular_table(item, item_key, item_style)

        return result

    def _write_inline_table(self, data: Mapping[str, Any], key: KEY_T, vstyle: _ValueStyle) -> str:
        result = f"{vstyle.prolog}{{"

        def _write_assignment(partial_key: str, item: Any) -> str:
            item_key = (*key, partial_key)
            item_style = self.style.value_style(item_key, item, 'inline')

            return f"{self._write_key(item_key, len(key), 'assignment')}" \
                   f"={self._write_value(item, item_key, item_style)}"

        result += ', '.join(_write_assignment(k, v) for k, v in data.items())
        result += f"}}{vstyle.epilog}"
        return result

    def _write_dotted_table(self, data: Mapping[str, Any], key: KEY_T, vstyle: _ValueStyle) -> str:
        subkey = self._write_key_part(key)
        result = ""

        def _write_assignment(partial_key: str, item: Any) -> str:
            item_key = (*key, partial_key)
            key_style = self.style.key_style(item_key)
            key_str = self._write_key(item_key, len(key), 'assignment')
            if not key_style.key_str:
                key_str = f"{subkey}.{key_str}"
            item_style = self.style.value_style(item_key, item, 'inline')
            value_str = self._write_value(item, item_key, item_style)

            if isinstance(item, Mapping) and item_style.display == 'dotted':
                return value_str
            return f"{key_str}={value_str}"

        result += '\n'.join(_write_assignment(k, v) for k, v in data.items())
        result += '\n'
        result += vstyle.epilog
        return result

    def _write_table_list(self, data: List[Mapping[str, Any]], key: KEY_T, vstyle: _ValueStyle) -> str:
        def _write_table_item(table: Mapping[str, Any], index: int):
            table_key = (*key, index)
            table_style = self.style.value_style(table_key, table, 'table-array-item')
            return self._write_regular_table(table, table_key, table_style)

        items = ''.join(_write_table_item(it, i) for i, it in enumerate(data))
        return f"{vstyle.prolog}{items}{vstyle.epilog}"


class _TomlParser(SimpleParser):
    def __init__(self, text: str, file_name: Optional[str]):
        super().__init__(text, file_name)
        self.style = _StyleSheet()

    def read_non_data(self, allow_new_lines: bool = True) -> str:
        result = ''
        while self.is_not_empty():
            result += self.match_ws(allow_new_lines)
            n = self.peek()
            if n == '#':  # comment
                result += self.until_match('\n')
            else:
                break

        return result

    def read_multiline_basic_str(self) -> str:
        self.match_or_err('"""', 'multiline basic string expected')
        s = '"""' + self.until_match('"""')
        while s[-1] == '\\':
            s += self.next(3) + self.until_match('"""')

        s += '"""'
        self.match_or_err('"""', 'multiline basic string ending expected')

        return eval(s)

    def read_multiline_literal_str(self) -> str:
        self.match_or_err("'''", 'multiline literal string expected')
        string = self.until_match("'''")
        self.match_or_err("'''", "missing multiline literal string closing")
        return string

    def read_basic_str(self) -> str:
        self.match_or_err('"', 'basic string expected')
        s = '"' + self.until_match('"')
        while s[-1] == '\\':
            s += self.next() + self.until_match('"')

        s += '"'
        self.match_or_err('"', 'basic string ending expected')

        return eval(s)

    def read_literal_str(self) -> str:
        self.match_or_err("'", 'literal string expected')
        string = self.until_match("'")
        self.match_or_err("'", "missing literal string closing")
        return string

    def read_str(self) -> str:
        n = self.peek(3)
        value = ''

        if n == '"""':
            value = self.read_multiline_basic_str()
        elif n == "'''":
            value = self.read_multiline_literal_str()
        elif n[0] == '"':
            value = self.read_basic_str()
        elif n[0] == "'":
            value = self.read_literal_str()
        else:
            self.raise_err("string expected type")

        return value

    def read_bare_key(self) -> str:
        result = ''
        while self.is_not_empty():
            n = self.peek()
            if _KEY_RX.match(n):
                result += self.next()
            else:
                break

        return result

    def read_key(self, base_key: KEY_T = ()) -> KEY_T:
        prolog = self.read_non_data()
        p = self.position
        table_key = self.match('[')
        table_list_key = False

        if table_key:
            self.match_ws(False)
            table_list_key = self.match('[')

        parts = []
        while self.is_not_empty():
            self.match_ws(False)
            n = self.peek()
            if n in '"\'':
                parts.append(self.read_str())
            elif _KEY_RX.fullmatch(n):
                parts.append(self.read_bare_key())
            else:
                self.raise_err('non-key character')

            pp = self.position
            self.match_ws(False)
            if not self.match('.'):
                self.position = pp
                break

        key = tuple(parts)

        if table_key:
            self.match_or_err(']', 'expecting table key termination')

        if table_list_key:
            self.match_ws()
            self.match_or_err(']', 'expecting table list key termination')
            key = self.style.lastify(key)

        key_str = self.text[p:self.position]
        epilog = self.read_non_data(False)
        display = 'assignment'
        if table_key:
            display = 'table'
        if table_list_key:
            display = 'table-array-item'

        self.style.set_key_style((*base_key, *key),
                                 _KeyStyle(prolog=prolog, epilog=epilog, key_str=key_str, display=display))
        return key

    def _mark_internal_tables(self, table_key: KEY_T, key: KEY_T, display: str):
        for i in range(1, len(key) + 1):
            dtable_key = (*table_key, *key[0:i])
            self.style.update_value_auto_display(dtable_key, {}, display)

    def read_date(self) -> TimeLiteral:
        ts = self.until(lambda s, i: s[i].isnumeric() or s[i] in '-.: TZ')
        return TimeLiteral(ts)

    def read_number_or_date(self) -> Union[Number, TimeLiteral]:
        pos = self.position

        sign = (self.match('-') and '-') or (self.match('+') and '+') or ''
        nstr = sign + self.until(lambda i, s: not s[i].isnumeric() and s[i] not in '.e')

        n = self.peek()
        if n in '-:':
            self.position = pos
            return self.read_date()

        if not nstr:
            self.raise_err("number expected")

        return eval(nstr)

    def read_bool(self) -> bool:
        if self.match('true'):
            return True
        if self.match('false'):
            return False
        self.raise_err("boolean expected")

    def read_inline_list(self, key: KEY_T) -> List[Any]:
        prolog = self.read_non_data(False)
        self.match_or_err('[', 'expecting list start')
        result = []
        p = self.position
        content_trailing = None

        while self.is_not_empty():
            item_prolog = self.read_non_data()

            if self.match(']'):
                self.position -= 1
                content_trailing = self.text[p:self.position]
                break

            item_key = (*key, len(result))
            next_ = self.read_inline_value(item_key)
            item_style = self.style.value_style(item_key, next_)
            item_style.prolog = item_prolog
            item_style.epilog = self.read_non_data()
            result.append(next_)

            p = self.position
            if not self.match(', ') and not self.match(','):
                break

        content_trailing = content_trailing or self.read_non_data()
        self.match_or_err(']', 'expecting list end')
        epilog = self.read_non_data(False)
        self.style.set_value_style(key, result, _ValueStyle(prolog=prolog, epilog=epilog, display='inline',
                                                            content_trailing=content_trailing))
        return result

    def read_inline_table(self, key: KEY_T) -> Dict[str, Any]:
        prolog = self.read_non_data(False)
        self.match_or_err('{', 'expecting inline-table start')
        result = self.read_table_assignments(key, inline=True)
        self.match_or_err('}', 'expecting inline-table end')
        epilog = self.read_non_data(False)
        self.style.set_value_style(key, result, _ValueStyle(prolog=prolog, epilog=epilog, display='inline'))
        return result

    def read_inline_value(self, key: KEY_T) -> Any:
        prolog = self.read_non_data()
        value_str = None

        p = self.position
        n = self.peek()
        result = None
        if n in "+-" or n.isnumeric():
            result = self.read_number_or_date()
            value_str = self.text[p:self.position]
        elif n in '\'"':
            result = self.read_str()
            value_str = self.text[p:self.position]
        elif n in 'tf':
            result = self.read_bool()
            value_str = self.text[p:self.position]
        elif n == '[':
            result = self.read_inline_list(key)
        elif n == '{':
            result = self.read_inline_table(key)

        if result is None:
            self.raise_err("value expected")

        vstyle = self.style.value_style(key, result)
        vstyle.prolog = prolog
        vstyle.epilog = self.read_non_data(False)
        vstyle.value_str = value_str
        vstyle.display = 'inline'
        self.style.set_value_style(key, result, vstyle)

        return result

    def _enter(self, data: Any, key: KEY_T, value: Any):
        if not key:
            return data

        if isinstance(data, List):
            if len(key) == 1 and isinstance(key[0], Number):
                data.append(value)
                return

            return self._enter(data[-1], key, value)

        if isinstance(data, MutableMapping):
            if len(key) == 1:
                data[key[0]] = value
                return

            if key[0] not in data:
                if isinstance(key[1], Number):
                    data[key[0]] = []
                else:
                    data[key[0]] = {}

            return self._enter(data[key[0]], key[1:], value)

        raise ValueError(f"cannot enter {data}")

    def read_table_assignments(self, table_key: KEY_T, inline: bool = False) -> Dict[str, Any]:
        data = {}
        while self.is_not_empty():
            p = self.position
            self.read_non_data()
            key_start = self.peek()
            self.position = p
            if not key_start or key_start == '[':
                break

            k = self.read_key(base_key=table_key)
            self.match_or_err('=', 'expecting assignment')
            v = self.read_inline_value((*table_key, *k))
            self._enter(data, k, v)
            if len(k) > 1:
                self._mark_internal_tables(table_key, k[:-1], 'dotted')

            if inline and not self.match(', ') and not self.match(','):
                break
            if not inline and not self.match('\n'):
                break

        self.match('\n')  # drop last \n seperating assignments and next table - it is added implicitly
        return data

    def read_regular_table(self) -> Tuple[KEY_T, Dict[str, Any]]:
        prolog = self.read_non_data()
        key = self.read_key()
        self._mark_internal_tables((), key[:-1], 'hidden')

        if self.is_empty():
            data = {}
        else:
            self.match_or_err('\n', 'expecting newline after table key')
            data = self.read_table_assignments(key)

        if key[-1] == -1:
            key = (*key[:-1], id(data))
        self.style.set_value_style(key, data, _ValueStyle(prolog=prolog, display='regular'))
        return key, data

    def read(self) -> Dict[str, Any]:
        prolog = self.read_non_data()
        epilog = ''
        data = self.read_table_assignments(())

        while self.is_not_empty():
            p = self.position
            epilog = self.read_non_data()
            if self.is_not_empty():
                self.position = p
                epilog = ''
                key, value = self.read_regular_table()
                self._enter(data, key, value)
            else:
                break

        self.style.set_value_style((), data, _ValueStyle(prolog=prolog, epilog=epilog, display='regular'))
        return data


def key2path(key: str) -> KEY_T:
    return _TomlParser(key, None).read_key(())


def loads(data: str, file_name: Optional[str] = None) -> Tuple[Dict[str, Any], DUMPS_T]:
    reader = _TomlParser(data, file_name)
    data = reader.read()

    return data, lambda x: _Writer(reader.style).write(x)


def load(file: Union[Path, str]) -> Tuple[Dict[str, Any], DUMPS_T]:
    file = Path(file)
    return loads(file.read_text(), str(file.absolute()))


def dumps(data: Dict[str, Any]) -> str:
    return _Writer().write(data)
