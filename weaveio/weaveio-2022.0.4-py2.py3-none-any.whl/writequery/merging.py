from textwrap import dedent
from typing import List, Dict, Union, Tuple, Optional, Iterable, Type

from . import CypherQuery
from .base import camelcase, Varname, Statement, CypherVariable, CypherData, CypherVariableItem, Collection


def are_different(a: str, b: str) -> str:
    return f"apoc.coll.different([apoc.coll.flatten([[{a}]]), apoc.coll.flatten([[{b}]])])"


def neo4j_dictionary(d: Union[dict, CypherVariable]) -> Tuple[Union[dict, CypherVariable], List[CypherVariable]]:
    """
    If d is a cyphervariable, return it
    If not, then we submit all the individual entries as data params to neo4j
    This avoids translating the data types ourselves!
    """
    if isinstance(d, CypherVariable):
        return d, [d]
    assert all(isinstance(k, str) for k in d.keys()), "keys must be strings"
    newd = {}
    ins = []
    for k, v in d.items():
        assert v is not None
        k = Varname(k)
        if not isinstance(v, CypherVariable):
            v = CypherData(v)
        ins.append(v)
        newd[k] = v
    return newd, ins


def sanitise_variablename(v):
    return f'`{str(v).replace("$", "")}`'


def expand_to_cypher_dict(*collections: Union[Dict[str, CypherVariable], CypherVariable]) -> str:
    inputs = []
    for collection in collections:
        if isinstance(collection, dict):
            inputs += list(collection.values())
        elif isinstance(collection, list):
            inputs += collection
        elif isinstance(collection, CypherVariable):
            inputs.append(collection)
        else:
            raise TypeError(f"Cannot convert {collection} to a cypher input dict of form `{{x:x}}` ")
    inputs = [getattr(i, 'parent') if isinstance(i, CypherVariableItem) else i for i in inputs]
    l = set([f"{sanitise_variablename(v)}: {v}" for v in inputs])
    return ', '.join(l)


def expand_to_cypher_alias(*collections: Union[Dict[str, CypherVariable], CypherVariable],
                           prefix='$') -> str:
    inputs = []
    for collection in collections:
        if isinstance(collection, dict):
            inputs += list(collection.values())
        elif isinstance(collection, list):
            inputs += collection
        elif isinstance(collection, CypherVariable):
            inputs.append(collection)
        else:
            raise TypeError(f"Cannot convert {collection} to a cypher input dict of form `{{x:x}}` ")
    inputs = [getattr(i, 'parent') if isinstance(i, CypherVariableItem) else i for i in inputs]
    l = set([f"{prefix}{sanitise_variablename(v)} as {sanitise_variablename(v)}" for v in inputs])
    return ', '.join(l)


class MatchNode(Statement):
    keyword = 'MATCH'

    def __init__(self, labels: List[str], properties: dict, optional=False):
        self.labels = [camelcase(l) for l in labels]
        self.properties, inputs = neo4j_dictionary(properties)
        self.out = CypherVariable(labels[0])
        self.optional = optional
        if optional:
            self.keyword = 'OPTIONAL MATCH'
        super(MatchNode, self).__init__(inputs, [self.out])

    def to_cypher(self):
        labels = ':'.join(map(str, self.labels))
        return f"{self.keyword} ({self.out}:{labels} {self.properties})"


class MatchRelationship(Statement):
    keyword = 'MATCH'

    def __init__(self, parent, child, reltype: str, properties: dict, optional=False):
        self.parent = parent
        self.child = child
        self.reltype = reltype
        self.properties, inputs = neo4j_dictionary(properties)
        self.optional = optional
        if optional:
            self.keyword = 'OPTIONAL MATCH'
        inputs += [self.parent, self.child]
        self.out = CypherVariable(reltype)
        super().__init__(inputs, [self.out])

    def to_cypher(self):
        if self.reltype is None and not len(self.properties):
            reldata = f'[{self.out}]'
        elif self.reltype is None:
            reldata = f'[{self.out}: {self.properties}]'
        else:
            reldata = f'[{self.out}:{self.reltype} {self.properties}]'
        return f"{self.keyword} ({self.parent})-{reldata}->({self.child})"


class MatchPatternNode(Statement):
    def __init__(self, labels: List[str], properties: Dict[str, Union[str, int, float, CypherVariable]],
                 parents: List[CypherVariable], children: List[CypherVariable], exclude: List[CypherVariable]):
        self.labels = [camelcase(l) for l in labels]
        self.properties, inputs = neo4j_dictionary(properties)
        self.parents = [p for p in parents if not isinstance(p, Collection)]
        self.collection_parents = [p for p in parents if isinstance(p, Collection)]
        self.children = [c for c in children if not isinstance(c, Collection)]
        self.collection_children = [c for c in children if isinstance(c, Collection)]
        self.exclude = [e for e in exclude if not isinstance(e, Collection)]
        self.exclude_collection = [e for e in exclude if isinstance(e, Collection)]
        self.out = CypherVariable(labels[0])
        super().__init__(inputs+parents+children+exclude, [self.out], [])

    def to_cypher(self):
        labels = ':'.join(self.labels)
        match = f'({self.out}: {labels} {self.properties})'
        extras = ', '.join([f'({self.out})<--({p})' for p in self.parents] +
                            [f'({self.out})-->({c})' for c in self.children])
        wheres = ' AND '.join([f"({self.out} <> {e})" for e in self.exclude] +
                              [f"({self.out} <> {e})" for e in self.exclude_collection] +
                              [f"all(p in {p} where exists( ({self.out})<--(p) ))" for p in self.collection_parents] +
                              [f"all(c in {c} where exists( ({self.out})-->(c) ))" for c in self.collection_children])
        if len(extras):
            extras = f',{extras}'
        if len(wheres):
            wheres = f' WHERE {wheres}'
        return f'WITH * OPTIONAL MATCH {match}{extras}{wheres}'

class MatchBranchNode(Statement):
    def __init__(self, *nodes_or_labels):
        self.nodes_or_labels = nodes_or_labels
        self.out = CypherVariable(nodes_or_labels)
        inputs = [i for i in nodes_or_labels if isinstance(i, CypherVariable)]
        outputs = [i  if isinstance(i, CypherVariable) else CypherVariable(i) for i in nodes_or_labels]
        super().__init__(inputs, outputs, [])

    def to_cypher(self):
        nodes = [f'({o}:{n})' if isinstance(n, str) else f'({o})' for n, o in zip(self.nodes_or_labels, self.output_variables)]
        path = '--'.join(map('{}'.format, nodes))
        return f'WITH * OPTIONAL MATCH {path}'

class PropertyOverlapError(Exception):
    pass


class NullPropertyError(Exception):
    pass


class CollisionManager(Statement):
    def __init__(self, out, identproperties: Dict[str, Union[str, int, float, CypherVariable]],
                 properties: Dict[str, Union[str, int, float, CypherVariable]], collision_manager='track&flag'):
        self.out = out
        self.properties, propinputs = neo4j_dictionary(properties)
        self.identproperties, identinputs = neo4j_dictionary(identproperties)
        self.validate_properties()
        self.propvar = CypherVariable('props')
        self.colliding_keys = CypherVariable('colliding_keys')
        self.value = CypherVariable('unnamed')
        inputs = propinputs + identinputs
        outputs = [self.out, self.propvar]
        if collision_manager == 'track&flag':
            outputs += [self.value, self.colliding_keys]
        elif collision_manager not in ['overwrite', 'ignore']:
            raise ValueError(f"Unknown collision_manager {collision_manager}")
        self.collision_manager = collision_manager
        super().__init__(inputs, outputs)

    def validate_properties(self):
        if any(p in self.identproperties for p in self.properties.keys()):
            raise PropertyOverlapError(f"Cannot have the same key in both properties and identproperties")
        for k, v in self.identproperties.items():
            if v != v:
                raise NullPropertyError(f"Cannot assign a nan to a node identify property")

    @property
    def on_match(self):
        if self.collision_manager == 'overwrite':
            return f"SET {self.out} += {self.propvar}   // overwrite with new colliding properties"
        return f"SET {self.out} = apoc.map.merge({self.propvar}, properties({self.out}))   // update, keeping the old colliding properties"

    @property
    def on_create(self):
        return f"SET {self.out}._dbcreated = time0, {self.out} += {self.propvar}  // setup as standard"

    @property
    def on_run(self):
        return f'SET {self.out}._dbupdated = time0  // always set updated time '

    @property
    def merge_statement(self):
        raise NotImplementedError

    @property
    def collision_record(self):
        raise NotImplementedError

    @property
    def collision_record_input(self):
        raise NotImplementedError

    @property
    def post_merge(self):
        return dedent(f"""
    ON MATCH {self.on_match}
    ON CREATE {self.on_create}
    {self.on_run}""")

    @property
    def pre_merge(self):
        return f"WITH *, {self.properties} as {self.propvar}"

    @property
    def merge_paragraph(self):
        return f"""
        {self.pre_merge}
        {self.merge_statement}
        {self.post_merge}
        """

    def to_cypher(self):
        query = self.merge_paragraph
        if self.collision_manager == 'track&flag':
            query += f"""
            WITH *, [x in apoc.coll.intersection(keys({self.propvar}), keys(properties({self.out}))) where ({self.propvar}[x] is null or {self.out}[x] is null) or {self.propvar}[x] <> {self.out}[x]] as {self.colliding_keys}
            CALL apoc.do.when(size({self.colliding_keys}) > 0, 
                "{self.collision_record} SET c = $collisions SET c._dbcreated = $time RETURN $time", 
                "RETURN $time",
                {{{self.collision_record_input}, collisions: apoc.map.fromLists({self.colliding_keys}, apoc.map.values({self.propvar}, {self.colliding_keys})), time:time0}}) yield value as {self.value}
            """
        return dedent(query)


class MergeNode(CollisionManager):
    def __init__(self, labels: List[str], identproperties: Dict[str, Union[str, int, float, CypherVariable]],
                 properties: Dict[str, Union[str, int, float, CypherVariable]], collision_manager='track&flag'):
        self.labels = [camelcase(l) for l in labels]
        out = CypherVariable(labels[0])
        super().__init__(out, identproperties, properties, collision_manager)

    @property
    def merge_statement(self):
        labels = ':'.join(map(str, self.labels))
        return f'MERGE ({self.out}: {labels} {self.identproperties})'

    @property
    def collision_record(self):
        return f"WITH $innode as innode CREATE (c:_Collision)-[:COLLIDES]->(innode)"

    @property
    def collision_record_input(self):
        return f"innode: {self.out}"


class MergeRelationship(CollisionManager):
    def __init__(self, parent, child, reltype: str, identproperties: dict, properties: dict, collision_manager='track&flag'):
        self.parent = parent
        self.child = child
        self.reltype = reltype
        out = CypherVariable(reltype)
        self.value = CypherVariable('value')
        super().__init__(out, identproperties, properties, collision_manager)
        self.output_variables.append(self.value)

    def to_cypher(self):
        return super().to_cypher()

    @property
    def merge_statement(self):
        return f'call apoc.merge.relationship($parent, "{self.reltype}", $ident, $props, $child, $onmatch) yield rel as {self.out}'


    @property
    def merge_paragraph(self):
        return f"""{self.pre_merge} 
        call apoc.do.when({self.parent} is null or {self.child} is null, 'return null as {self.out}','
        {self.merge_statement}
        RETURN {self.out}', {{parent: {self.parent}, child:{self.child}, ident:{self.identproperties}, 
                              props: {self.propvar}, onmatch: {{}}}}) yield value as {self.value}
        OPTIONAL MATCH ({self.parent})-[{self.out}:{self.reltype} {self.identproperties}]->({self.child})
        """

    @property
    def collision_record(self):
        return f"WITH $a as a, $b as b CREATE (a)-[c:COLLIDES]->(b)"

    @property
    def collision_record_input(self):
        return f"a:{self.parent}, b:{self.child}"


class MergeDependentNode(CollisionManager):
    def __init__(self, labels: List[str], identproperties: Dict[str, Union[str, int, float, CypherVariable]],
                 properties: Dict[str, Union[str, int, float, CypherVariable]],
                 parents: List[CypherVariable],
                 reltypes: List[str],
                 relidentproperties: List[Dict[str, Union[str, int, float, CypherVariable]]],
                 relproperties: List[Dict[str, Union[str, int, float, CypherVariable]]],
                 collision_manager='track&flag'):
        if not (len(parents) == len(reltypes) == len(relproperties) == len(relidentproperties)):
            raise ValueError(f"Parents must have the same length as reltypes, relproperties, relidentproperties")
        self.labels = [camelcase(l) for l in labels]
        self.relidentproperties, relidentpropins = [], []
        self.relproperties, relpropins = [], []
        for ident, prop in zip(relidentproperties, relproperties):
            identdict, identpropins = neo4j_dictionary(ident)
            propdict, propins = neo4j_dictionary(prop)
            self.relidentproperties.append(identdict)
            self.relproperties.append(propdict)
            relidentpropins += identpropins
            relpropins += propins
        self.parents = parents
        self.outnode = CypherVariable(labels[0])
        self.relvars = [CypherVariable(reltype) for reltype in reltypes]
        self.dummyrelvars = [CypherVariable('dummy'+reltype) for reltype in reltypes]
        self.dummy = CypherVariable('dummy')
        self.reltypes = reltypes
        self.relpropsvars = [CypherVariable(f'{t}_props') for t in reltypes]
        self.colliding_rel_keys = [CypherVariable('colliding_rel_keys') for _ in reltypes]
        super().__init__(self.outnode, identproperties, properties, collision_manager)
        self.child_holder = CypherVariable('child_holder')
        self.unnamed = CypherVariable('unnamed')
        self.input_variables += parents
        self.input_variables += relidentpropins
        self.input_variables += relpropins
        self.output_variables += self.relvars
        self.output_variables += self.dummyrelvars
        self.output_variables += self.relpropsvars
        self.hidden_variables += self.colliding_rel_keys
        self.output_variables.append(self.dummy)
        self.output_variables.append(self.child_holder)
        self.output_variables.append(self.unnamed)

    def validate_properties(self):
        super(MergeDependentNode, self).validate_properties()
        for idents, props in zip(self.relidentproperties, self.relproperties):
            if any(p in idents for p in props.keys()):
                raise ValueError(f"Cannot have the same key in both properties and identproperties")
            for k, v in idents.items():
                if v != v:
                    raise NullPropertyError(f"Cannot assign a nan to a node identify property")

    @property
    def pre_merge(self):
        line = f"WITH *, {self.properties} as {self.propvar}"
        for relprop, relpropsvar in zip(self.relproperties, self.relpropsvars):
            line += f', {relprop} as {relpropsvar}'
        return line

    @property
    def merge_statement(self):
        labels = ':'.join(map(str, self.labels))
        real_relations = []
        temp_relations = []
        test_relations = []
        parent_list = []
        for i, (parent, reltype, relidentprop, dummyrelvar, relvar) in enumerate(zip(self.parents, self.reltypes, self.relidentproperties, self.dummyrelvars, self.relvars)):
            if i == 0:
                child = f'({self.dummy}: {labels} {self.identproperties})'
            else:
                child = f'({self.dummy})'
            rel = f'({parent})-[{dummyrelvar}:{reltype} {relidentprop}]->'
            real_rel = f'({parent})-[{relvar}:{reltype} {relidentprop}]->'
            real_child = f'({self.out})'
            real_relations.append(real_rel + real_child)
            temp_relations.append(rel + '(temp)')
            test_relations.append(rel + child)
            parent_list.append(f"{parent}")
        dct = expand_to_cypher_dict(self.dummy, self.propvar, self.identproperties, *self.parents + self.relidentproperties + self.dummyrelvars)
        aliases = expand_to_cypher_alias(self.identproperties, *self.parents + self.relidentproperties)
        variables = set()
        for p in self.parents:
            variables.add(p)
        for v in self.identproperties.values():
            try:
                v = v.parent
            except AttributeError:
                pass
            if not isinstance(v, CypherData):
                variables.add(v)
        for rel in self.relidentproperties:
            for v in rel.values():
                try:
                    v = v.parent
                except AttributeError:
                    pass
                if not isinstance(v, CypherData):
                    variables.add(v)
        merge_temp_relations = '\n'.join([f'MERGE {r}' for r in temp_relations])
        merge_final_temp_relation = f"MERGE (temp)-[:TemporaryMerge]->({self.out}: {labels} {self.identproperties})"
        merge_real_relations = '\n'.join([f'MERGE {r}' for r in real_relations])
        on_create_rel_returns = ', '.join([f'{relvar}' for relvar in self.relvars])
        on_match_rel_returns = ', '.join([f'${dummy}[0] as {real}' for dummy, real in zip(self.dummyrelvars, self.relvars)])
        rel_expansion = expand_to_cypher_alias(self.out, *self.relvars, prefix=f'{self.child_holder}.')
        optional_match = f'OPTIONAL MATCH {test_relations[0]}'
        matches = '\n'.join([f'MATCH {t}' for t in test_relations])
        rel_collection = ', '.join([f'collect({drel}) as {drel}' for rel, drel in zip(self.relvars, self.dummyrelvars)])
        collection = f'CALL {{ WITH {", ".join(map(str, variables))}\n' \
                     f'{optional_match}\n' \
                     f'{matches}\n' \
                     f'RETURN collect({self.dummy}) as {self.dummy}, {rel_collection}\n' \
                     f'}}'
        condition = f"size({self.dummy}) = 0"
        iftrue = f"""
        WITH {aliases}
        MERGE (temp: TemporaryMerge {{id: $time0}})
        {merge_temp_relations}
        {merge_final_temp_relation}
        {merge_real_relations}
        DETACH DELETE temp
        SET {self.out} += ${self.propvar}
        RETURN {self.out}, {on_create_rel_returns}
        """
        iffalse = f"RETURN ${self.dummy}[0] as {self.out}, {on_match_rel_returns}"
        when = f'CALL apoc.do.when({condition}, "{iftrue}", "{iffalse}", {{ {dct}, time0:time0}}) yield value as {self.child_holder}'
        when += f"\n WITH *, {rel_expansion}"
        return dedent(f"CALL apoc.lock.nodes({self.parents})\n{collection}\n{when}")

    @property
    def on_match(self):  # remember, we are in a call context
        query = ''
        for i, (r, rprops, colliding_keys) in enumerate(zip(self.relvars+[self.out], self.relpropsvars+[self.propvar], self.colliding_rel_keys+[self.colliding_keys])):
            if self.collision_manager == 'track&flag':
                if r != self.out:  # handled by the base class above
                    query += dedent(f"""
                        WITH *, [x in apoc.coll.intersection(keys({rprops}), keys(properties({r}))) where ({rprops}[x] is null or {r}[x] is null) or {rprops}[x] <> {r}[x]] as {colliding_keys}
                        CALL apoc.do.when(size({colliding_keys}) > 0, 
                            'WITH $inrel as inrel 
                             MATCH (a)-[inrel]->(b)  
                             CREATE (a)-[c:_Collision]->(b) SET c = $collisions 
                             SET c._dbcreated = $time
                             SET c._reltype = type(inrel)
                             RETURN $time', 
                            'RETURN $time',
                            {{inrel: {r}, collisions: apoc.map.fromLists({colliding_keys}, apoc.map.values({rprops}, {colliding_keys})), time:$time0}}) yield value as _{i}{self.value}
                    """)
            elif self.collision_manager == 'overwrite':
                query += f"\nSET {r} += {rprops}   // overwrite with new colliding properties"
            else:
                query += f"\nSET {r} = apoc.map.merge({rprops}, properties({r}))  // update, keeping the old colliding properties"
        return query

    @property
    def on_create(self):  # remember, we are in a call context
        query = f"SET {self.out}._dbcreated = $time0, {self.out} += {self.propvar}  // setup as standard"
        for r, rprops in zip(self.relvars, self.relpropsvars):
            query += f'\nSET {r}._dbupdated = $time0, {r}._dbcreated = $time0, {r} += {rprops}'
        return query

    @property
    def on_run(self):  # remember, we are in a call context
        query = f"SET {self.out}._dbupdated = time0  // always set updated time"
        for r in self.relvars:
            query += f'\nSET {r}._dbupdated = time0'
        return query

    @property
    def post_merge(self):
        dct = expand_to_cypher_dict(self.out, self.propvar, *self.relvars+self.relpropsvars)
        if len(dct):
            dct += ', '
        dct += 'time0:time0'
        aliases = expand_to_cypher_alias(self.out, self.propvar, *self.relvars+self.relpropsvars)
        return dedent(f"""
        // post merge
        call apoc.do.when(size({self.dummy}) = 0,
        "WITH {aliases}\n{self.on_create}\n RETURN $time0",
        "WITH {aliases}\n{self.on_match}\n RETURN $time0",
        {{ {dct} }}) yield value as {self.unnamed}
        {self.on_run}\n""")

    @property
    def collision_record(self):
        return f"WITH $innode as innode CREATE (c:_Collision)-[:COLLIDES]->(innode)"

    @property
    def collision_record_input(self):
        return f"innode: {self.out}"

    def to_cypher(self):
        return super().to_cypher()


class SetVersion(Statement):
    def __init__(self, parents: List[CypherVariable], reltypes: List[str], childlabel: str, child: CypherVariable, childproperties: dict):
        if len(reltypes) != len(parents):
            raise ValueError(f"reltypes must be the same length as parents")
        self.parents = parents
        self.reltypes = reltypes
        self.childlabel = camelcase(childlabel)
        self.childproperties, other_ins = neo4j_dictionary(childproperties)
        self.child = child
        other_ins.append(child)
        super(SetVersion, self).__init__(self.parents+other_ins, [])

    def to_cypher(self):
        matches = ', '.join([f'({p})-[:{r}]->(c:{self.childlabel} {self.childproperties})' for p, r in zip(self.parents, self.reltypes)])
        query = [
            f"WITH * CALL {{",
                f"\t WITH {','.join(map(str, self.parents))}, {self.child}",
                f"\t OPTIONAL MATCH {matches}"
                f"\t WHERE id(c) <> id({self.child})",
                f"\t WITH {self.child}, max(c.version) as maxversion",
                f"\t SET {self.child}.version = coalesce({self.child}['version'], maxversion + 1, 0)",
                f"\t RETURN {self.child}['version']",
            f"}}"
        ]
        return '\n'.join(query)


def match_node(labels, properties, optional=False):
    query = CypherQuery.get_context()  # type: CypherQuery
    statement = MatchNode(labels, properties, optional)
    query.add_statement(statement)
    return statement.out


def match_relationship(parent, child, reltype, properties, optional=False):
    query = CypherQuery.get_context()  # type: CypherQuery
    statement = MatchRelationship(parent, child, reltype, properties, optional)
    query.add_statement(statement)
    return statement.out


def match_pattern_node(labels: List[str], properties: Dict[str, Union[str, int, float, CypherVariable]] = None,
                       parents: List[CypherVariable] = None, children: List[CypherVariable] = None,
                       exclude: List[CypherVariable] = None):
    query = CypherQuery.get_context()  # type: CypherQuery
    if properties is None:
        properties = {}
    if parents is None:
        parents = []
    if children is None:
        children = []
    if exclude is None:
        exclude = []
    statement = MatchPatternNode(labels, properties, parents, children, exclude)
    query.add_statement(statement)
    return statement.out


def match_branch_node(*nodes_or_labels: Union[str, Type[CypherVariable]]):
    query = CypherQuery.get_context()  # type: CypherQuery
    statement = MatchBranchNode(*nodes_or_labels)
    query.add_statement(statement)
    return statement.output_variables


def merge_single_node(labels, identproperties, properties, collision_manager='track&flag'):
    query = CypherQuery.get_context()  # type: CypherQuery
    statement = MergeNode(labels, identproperties, properties, collision_manager)
    query.add_statement(statement)
    return statement.out


def merge_relationship(parent, child, reltype, identproperties, properties, collision_manager='track&flag'):
    query = CypherQuery.get_context()  # type: CypherQuery
    statement = MergeRelationship(parent, child, reltype, identproperties, properties, collision_manager)
    query.add_statement(statement)
    return statement.out


def merge_dependent_node(labels, identproperties, properties, parents, reltypes, relidentproperties, relproperties,
                         collision_manager='track&flag'):
    query = CypherQuery.get_context()  # type: CypherQuery
    statement = MergeDependentNode(labels, identproperties, properties, parents, reltypes, relidentproperties, relproperties,
                                   collision_manager)
    query.add_statement(statement)
    return statement.outnode


def set_version(parents, reltypes, childlabel, child, childproperties):
    query = CypherQuery.get_context()  # type: CypherQuery
    statement = SetVersion(parents, reltypes, childlabel, child, childproperties)
    query.add_statement(statement)


def merge_node(labels, identproperties, properties=None,
               parents: Dict[CypherVariable, Union[Tuple[str, Optional[Dict], Optional[Dict]], str]] = None,
               versioned_label=None,
               versioned_properties=None,
               collision_manager='track&flag') -> CypherVariable:
    if properties is None:
        properties = {}
    if parents is None:
        parents = {}
    parent_list = []
    reltype_list = []
    relidentproperties_list = []
    relproperties_list = []
    for parent, reldata in parents.items():
        if isinstance(reldata, str):
            reldata = [reldata]
        parent_list.append(parent)
        reltype_list.append(reldata[0])
        if len(reldata) > 1:
            relidentproperties_list.append(reldata[1])
        else:
            relidentproperties_list.append({})
        if len(reldata) > 2:
            relproperties_list.append(reldata[2])
        else:
            relproperties_list.append({})
    if len(parents):
        node = merge_dependent_node(labels, identproperties, properties, parent_list,
                                    reltype_list, relidentproperties_list, relproperties_list,
                                    collision_manager)
    else:
        node = merge_single_node(labels, identproperties, properties, collision_manager)
    if versioned_label is not None:
        if versioned_properties is None:
            versioned_properties = {}
        set_version(parent_list, reltype_list, versioned_label, node, versioned_properties)
    return node
