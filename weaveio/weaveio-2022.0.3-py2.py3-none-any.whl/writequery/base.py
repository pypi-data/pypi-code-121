from collections import defaultdict
from functools import reduce
from operator import xor
from textwrap import dedent
from typing import List, Callable, Union

import re
from warnings import warn

from ..context import ContextMeta


def camelcase(x):
    if x[0] != x[0].upper():
        raise ValueError(f"Labels must be camelcase")
    return x


class CypherQuery(metaclass=ContextMeta):
    def __init__(self, collision_manager='track&flag'):
        self.data = []
        self.statements = [TimeStamp()]  # type: List[BaseStatement]
        self.timestamp = self.statements[0].output_variables[0]
        self.open_contexts = [[self.timestamp]]
        self.closed_context = None
        self.collision_manager = collision_manager

    @property
    def current_context(self):
        return self.open_contexts[-1]

    @property
    def accessible_variables(self):
        return [v for context in self.open_contexts[::-1] for v in context] + [i for i in self.data]

    def is_accessible(self, variable):
        if variable in self.accessible_variables:
            return True
        if hasattr(variable, 'parent'):
            return self.is_accessible(variable.parent)
        return False

    def add_statement(self, statement, safe=True):
        for v in statement.input_variables:
            if safe:
                if not self.is_accessible(v):
                    raise ValueError(f"{v} is not accessible is this context. Have you left a WITH context?")
        self.statements.append(statement)
        self.current_context.extend(statement.output_variables)

    def remove_variable_names(self):
        for statement in self.statements:
            for v in statement.input_variables + statement.output_variables + statement.hidden_variables:
                v._name = None

    def make_variable_names(self):
        d = defaultdict(int)
        for data in self.data:
            namehint = data.namehint.lower()
            i = d[namehint]
            d[namehint] += 1
            data._name = f'{namehint}{i}'
        for statement in self.statements:
            for v in statement.input_variables + statement.output_variables + statement.hidden_variables:
                if v.name is None:
                    namehint = v.namehint.lower()
                    i = d[namehint]
                    d[namehint] += 1
                    v._name = f'{namehint}{i}'

    def render_query(self, procedure_tag='', as_lines=False):
        if not isinstance(self.statements[-1], Returns):
            self.returns(self.timestamp)
        self.make_variable_names()
        qs = [s.to_cypher() for s in self.statements]
        for i, q in enumerate(qs):
            if q.lower().startswith('with') and '$' in q:
                q = re.sub('\$[\w\d]+ as \$[\w\d]+,', '', q)
                qs[i] = q
        # TODO: make this bit above better! All it does is remove $[...] from WITH statements, there must be a better way
        datadict = {d.name: d.data for d in self.data}
        if as_lines:
            return qs, datadict
        q = '\n'.join(qs)
        return dedent(re.sub(r'(custom\.[\w\d]+)\(', fr'\1-----{procedure_tag}(', q).replace('-----', '')), datadict

    def open_context(self):
        self.open_contexts.append([])

    def close_context(self):
        self.closed_context = self.open_contexts[-1]
        del self.open_contexts[-1]

    def add_data(self, data):
        self.data.append(data)

    def returns(self, *args, **kwargs):
        if not isinstance(self.statements[-1], Returns):
            self.statements.append(Returns(*args, **kwargs))
        else:
            self.statements[-1] = Returns(*args, **kwargs)
        return self


CypherQuery._context_class = CypherQuery


class Varname:
    def __init__(self, key):
        self.key = key

    def __repr__(self):
        return f"`{self.key}`"

    def __eq__(self, other):
        return getattr(other, 'key', other) == self.key

    def __hash__(self):
        return hash(hash(self.key) + hash('varname'))


class BaseStatement:
    def __init__(self, input_variables, output_variables, hidden_variables=None):
        self.input_variables = list(input_variables)
        self.output_variables = list(output_variables)
        if hidden_variables is None:
            hidden_variables = []
        self.hidden_variables = hidden_variables

    def to_cypher(self):
        raise NotImplementedError

    def __eq__(self, other):
        return set(self.input_variables) == set(other.input_variables) \
               and set(self.output_variables) == set(other.output_variables) \
               and set(self.hidden_variables) == set(other.hidden_variables) \
               and self.__class__ is other.__class__

    def __hash__(self):
        return reduce(xor, map(hash, [tuple(self.input_variables), tuple(self.output_variables)]))


class Statement(BaseStatement):
    """A cypher statement that takes inputs and returns outputs"""
    def __init__(self, input_variables, output_variables, hidden_variables=None):
        super(Statement, self).__init__(input_variables, output_variables, hidden_variables)
        self.timestamp = CypherQuery.get_context().timestamp


class CustomStatement(Statement):
    def __init__(self, statement: Callable, input_variables, output_variables):
        super().__init__(input_variables, output_variables)
        self.statement = statement

    def to_cypher(self):
        return self.statement(*self.input_variables, *self.output_variables)


class Returns(Statement):
    def __init__(self, *unnamed_variables, **named_variables):
        self.unnamed_variables = unnamed_variables
        self.named_variables = named_variables
        self.input_variables = list(unnamed_variables) + list(named_variables.values())
        self.output_variables = []
        self.hidden_variables = []

    def to_cypher(self):
        l = list(map(str, self.unnamed_variables))
        l += [f'{v} as {k}' for k, v in self.named_variables.items()]
        return 'RETURN ' + ', '.join(l)


class TimeStamp(Statement):
    def __init__(self):
        self.input_variables = []
        self.output_variables = [CypherVariable('time')]
        self.hidden_variables = []

    def to_cypher(self):
        return f'WITH *, timestamp() as {self.output_variables[0]}'


class Alias(Statement):
    def __init__(self, input_thing, alias_namehint):
        self.out = CypherVariable(alias_namehint)
        self.input_thing = input_thing
        super(Alias, self).__init__([input_thing], [self.out])

    def to_cypher(self):
        return f"WITH *, {self.input_thing} as {self.out}"


class CypherVariable:
    def __init__(self, namehint=None):
        self.namehint = 'variable' if namehint is None else namehint
        self._name = None
        self.is_mapping = None

    @property
    def name(self):
        return self._name

    def __repr__(self):
        if self.name is None:
            return super(CypherVariable, self).__repr__()
        return self.name

    def __getitem__(self, item: Union[str, int]):
        return self.get(item, alias=True)

    def get(self, item: Union[str, int, 'CypherVariable'], alias=False):
        assert isinstance(item, (int, str, CypherVariable))
        if self.is_mapping:
            if isinstance(item, CypherVariable):
                item = CypherVariableToString(item)
            else:
                item = str(item)
        getitem = CypherVariableItem(self, item)
        if alias:
            query = CypherQuery.get_context()
            if isinstance(item, int):
                item = f'{self.namehint}_index{item}'
            if isinstance(item, CypherVariable):
                item = f"{self.namehint}_index_{item.namehint}"
            alias_statement = Alias(getitem, str(item))
            query.add_statement(alias_statement)
            return alias_statement.out
        else:
            return getitem

    def __sub__(self, other):
        query = CypherQuery.get_context()
        v =  ArithmeticCypherVariable('{} - {}', self, other)
        alias_statement = Alias(v, 'sub')
        query.add_statement(alias_statement)
        return alias_statement.out

    def __add__(self, other):
        query = CypherQuery.get_context()
        v =  ArithmeticCypherVariable('{} + {}', self, other)
        alias_statement = Alias(v, 'add')
        query.add_statement(alias_statement)
        return alias_statement.out



class DerivedCypherVariable(CypherVariable):
    def __init__(self, *args):
        super(DerivedCypherVariable, self).__init__()
        self.parent = [i for i in args if isinstance(i, CypherVariable)][0]
        self.args = args

    def string_formatter(self, *args):
        raise NotImplementedError

    @property
    def name(self):
        return self.string_formatter(*self.args)


class ArithmeticCypherVariable(DerivedCypherVariable):
    def __init__(self, op_string, *parents):
        super().__init__(op_string, *parents)

    def string_formatter(self, op_string, *parents):
        return op_string.format(*parents)


class CypherVariableItem(DerivedCypherVariable):
    def string_formatter(self, parent, attr):
        if isinstance(attr, str):
            return f"{parent}['{attr}']"
        return f"{parent}[{attr}]"


class CypherFindReplaceStr(DerivedCypherVariable):
    def string_formatter(self, parent, replace):
        return f"replace({parent}, 'X', '{replace}')"

class CypherAppendStr(DerivedCypherVariable):
    def string_formatter(self, *strings):
        s = [f"'{i}'" if isinstance(i, str) else f"{i}" for i in strings]
        return ' + '.join(s)


class CypherVariableToString(DerivedCypherVariable):
    def __init__(self, parent):
        super().__init__(parent)

    def string_formatter(self, parent):
        return f"toStringOrNull({parent})"

class Collection(CypherVariable):
    pass


class CypherData(CypherVariable):
    def __init__(self, data, name='data', delay=False):
        super(CypherData, self).__init__(name)
        self.data = data
        if not delay:
            query = CypherQuery.get_context()  # type: CypherQuery
            query.add_data(self)
        if isinstance(data, dict):
            self.is_mapping = True
        else:
            self.is_mapping = False

    def __repr__(self):
        return '$' + super(CypherData, self).__repr__()