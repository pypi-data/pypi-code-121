from .base import CypherQuery, Statement, CypherVariable, Collection


class Unwind(Statement):
    def __init__(self, *args: CypherVariable, enumerated=False):
        output_variables = [CypherVariable('unwound_' + a.namehint.replace('$', "")) for a in args]
        super(Unwind, self).__init__(args, output_variables)
        self.passed_outputs = self.output_variables.copy()
        if enumerated or len(self.input_variables) > 1:
            self.indexer_variable = CypherVariable('i')
            self.output_variables.append(self.indexer_variable)
            if enumerated:
                self.passed_outputs.append(self.indexer_variable)
        self.enumerated = enumerated

    def to_cypher(self):
        if len(self.input_variables) == 1 and not self.enumerated:
            return f"WITH * UNWIND {self.input_variables[0]} as {self.output_variables[0]}"
        else:
            outaliasstr = 'WITH *'
            for n, (i, o) in enumerate(zip(self.input_variables, self.output_variables[:-1])):
                outaliasstr += f', {i}[{self.indexer_variable}] as {o}'
            inliststr = f'[{",".join(map(str, self.input_variables))}]'
            return f"WITH *, apoc.coll.max([x in {inliststr} | SIZE(x)])-1 as m\n" \
                   f"UNWIND range(0, m) as {self.indexer_variable} {outaliasstr}"


class Collect(Statement):
    def __init__(self, previous, *args):
        self.previous = previous
        super(Collect, self).__init__(args, [Collection(a.namehint + 's') for a in args])

    def to_cypher(self):
        collections = ','.join([f'collect({a}) as {b}' for a, b in zip(self.input_variables, self.output_variables)])
        r = f"WITH " + ', '.join(map(str, self.previous))
        if len(collections):
            r += ', ' + collections
        return r

    def __getitem__(self, inarg):
        i = self.input_variables.index(inarg)
        try:
            return self.output_variables[i]
        except IndexError:
            raise KeyError(f"Cannot access {inarg} in this context, have you unwound it previously or left a WITH context?")

    def __delitem__(self, key):
        i = self.input_variables.index(key)
        del self.input_variables[i]


class NodeMap(CypherVariable):
    def __getitem__(self, item):
        query = CypherQuery.get_context()  # type: CypherQuery
        statement = GetItemStatement(self, item)
        query.add_statement(statement)
        return statement.out


class GetItemStatement(Statement):
    def __init__(self, mapping, item):
        self.mapping = mapping
        self.item = item
        ins = [mapping]
        if isinstance(item, CypherVariable):
            ins.append(item)
        itemname = getattr(item, 'namehint', 'item') if not isinstance(item, str) else item
        self.out = CypherVariable(mapping.namehint + '_' + itemname)
        self.temp = CypherVariable('temp')
        super(GetItemStatement, self).__init__(ins, [self.out], [self.temp])

    def to_cypher(self):
        if isinstance(self.item, CypherVariable):
            item = f'{self.item}'
        else:
            item = f"'{self.item}'"
        convert = f"WITH *, CASE WHEN apoc.meta.type({item}) = 'STRING' THEN {item} ELSE toString(toFloat({item})) END as {self.temp}"
        result = f'WITH *, {self.mapping}[{self.temp}] as {self.out}'
        return '\n'.join([convert, result])


class Copy(Statement):
    def __init__(self, *args):
        outs = [CypherVariable(a.namehint + '_copy') for a in args]
        super(Copy, self).__init__(args, outs)

    def to_cypher(self):
        eq = [f'{a} as {b}' for a, b in zip(self.input_variables, self.output_variables)]
        return f"WITH *, {', '.join(eq)}"

class GroupBy(Statement):
    def __init__(self, nodelist, propertyname):
        super(GroupBy, self).__init__([nodelist], [NodeMap(propertyname+'_dict')])
        self.propertyname = propertyname

    def to_cypher(self):
        return f"WITH *, apoc.map.groupBy({self.input_variables[0]}, '{self.propertyname}') as {self.output_variables[0]}"