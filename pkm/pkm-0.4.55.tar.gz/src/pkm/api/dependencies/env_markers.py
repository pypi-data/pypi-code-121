from typing import Callable, Optional, List, Sequence, TYPE_CHECKING

from pkm.api.versions.version import Version
from pkm.api.versions.version_specifiers import VersionSpecifier
from pkm.utils.parsers import SimpleParser

_EXTRAS_COLLECTION_T = List
_EXTRAS_T = _EXTRAS_COLLECTION_T[str]
_MARKER_PRED_T = Callable[["Environment", _EXTRAS_T], bool]
_MARKER_GET_T = Callable[["Environment", _EXTRAS_T], Sequence[str]]
_MARKER_OP_T = Callable[[Sequence[str], Sequence[str]], bool]

if TYPE_CHECKING:
    from pkm.api.environments.environment import Environment


class EnvironmentMarker:

    # noinspection PyShadowingBuiltins
    def __init__(self, expr: str, exec: _MARKER_PRED_T):
        self._expr = expr
        self._exec = exec

    def evaluate_on(self, env: "Environment", extras: _EXTRAS_T) -> bool:
        return self._exec(env, extras)

    def __str__(self) -> str:
        return self._expr

    @classmethod
    def parse_pep508(cls, text: str) -> "EnvironmentMarker":
        return PEP508EnvMarkerParser(text).read_marker()


_MARKER_STR_CHARS = set(
    ' \t0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIZKLMNOPQRSTUVWXYZ().{}-_*#:;,/?[]!`~@$%^&=+|<>')


class PEP508EnvMarkerParser(SimpleParser):

    def _read_identifier(self) -> str:
        if self.peek().isalpha():
            return self.until(lambda i, t: not t[i].isalnum() and t[i] not in '_-.')
        self.raise_err('expecting identifier')

    def _read_str(self) -> str:
        quote = self.match_any("'", "\"")
        oquote = "'" if quote == '"' else '"'

        content = self.until(lambda i, t: t[i] != oquote and t[i] not in _MARKER_STR_CHARS)
        self.match_or_err(quote, f'expecting closing quote: ({quote})')
        return content

    def _read_marker_var(self) -> _MARKER_GET_T:
        if self.peek() in '"\'':
            v_str = self._read_str()
            return lambda e, x: v_str
        else:
            v_ident = self._read_identifier()

            if v_ident == 'extra':
                return lambda e, x: x

            return lambda e, x: e.markers[v_ident]

    def _read_marker_op(self) -> _MARKER_OP_T:
        version_or_string_op = self.match_any("<=", "<", ">=", ">", "!=", "==", "===", "~=")
        if version_or_string_op:
            def _op(a: Sequence[str], b: Sequence[str]) -> bool:

                if version_or_string_op in ('==', '==='):
                    if isinstance(a, _EXTRAS_COLLECTION_T):
                        return b in a
                    elif isinstance(b, _EXTRAS_COLLECTION_T):
                        return a in b

                try:
                    a_ver = Version.parse(str(a))
                    spec = VersionSpecifier.parse(f"{version_or_string_op} {b}")
                    return spec.allows_version(a_ver)
                except ValueError:
                    if version_or_string_op == '~=':
                        raise
                    return eval(f"{repr(str(a))} {version_or_string_op} {repr(str(b))}")

            return _op

        string_op: str = self.match("in") or (self.match("not", "in") and "not in")
        if not string_op:
            self.raise_err("could not parse operator")

        def _op(a: Sequence[str], b: Sequence[str]) -> bool:
            return eval(f"{repr(str(a))} {string_op} {repr(str(b))}")

        return _op

    def _read_marker_expr(self) -> _MARKER_PRED_T:
        self.match_ws()

        if self.match("("):
            result = self._read_marker_compound_expr()
            self.match_or_err(")", "expecting closing paren")
            return result

        left = self._read_marker_var()
        self.match_ws()
        op = self._read_marker_op()
        self.match_ws()
        right = self._read_marker_var()

        return lambda e, x: op(left(e, x), right(e, x))

    def _read_marker_compound_expr(self) -> _MARKER_PRED_T:
        self.match_ws()

        expr: Optional[_MARKER_PRED_T] = None
        self.match_ws()

        ors: List[_MARKER_PRED_T] = []
        while self.is_not_empty() and self.peek() not in ';)':

            if expr:
                lop = self.match_any('and', 'or')
                if not lop:
                    self.raise_err('expecting logical operator: and/or')

                next_expr = self._read_marker_expr()

                if lop == 'and':
                    def expr(e, x, ex1=expr, ex2=next_expr):
                        return ex1(e, x) and ex2(e, x)

                else:
                    ors.append(expr)
                    expr = next_expr

            else:
                expr = self._read_marker_expr()

            self.match_ws()

        if ors:
            ors.append(expr)

            def expr(e, x):
                return any(expr_(e, x) for expr_ in ors)

        if expr is None:
            self.raise_err('expecting environment marker expression')

        return expr

    def read_marker(self) -> EnvironmentMarker:
        p = self.position
        exe = self._read_marker_compound_expr()
        return EnvironmentMarker(self.text[p:self.position], exe)
