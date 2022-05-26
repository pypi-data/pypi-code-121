import textwrap

import networkx as nx

from weaveio.basequery.factor import FactorFrozenQuery
from weaveio.hierarchy import Hierarchy, Graphable, GraphableMeta


def _convert_obj(obj, data=None):
    if isinstance(obj, str):
        obj = obj.lower()
        try:
            obj = data.singular_hierarchies[obj]
        except KeyError:
            obj = data.plural_hierarchies[obj]
    elif isinstance(obj, (Graphable, GraphableMeta)):
        obj = obj
    elif hasattr(obj, 'handler'):
        data = obj.handler.data
        obj = obj.hierarchy_type
    else:
        raise TypeError(f"{obj} is not a recognised type of object. Use a name (string), a query, or the type directly")
    return obj, data


def attributes(obj, data=None):
    obj, data = _convert_obj(obj, data)
    return sorted(set(obj.products_and_factors))


def objects(obj, data=None):
    obj, data = _convert_obj(obj, data)
    neighbors = set(data.relation_graph.predecessors(obj)) | set(data.relation_graph.successors(obj))
    relations = []
    for b in neighbors:
        try:
            data.find_hierarchy_paths(obj, b, plural=False)
        except (nx.NetworkXNoPath, KeyError):
            relations.append(b.plural_name)
        else:
            relations.append(b.singular_name)
    relations.sort()
    return relations


def explain_object(obj, data=None):
    obj, data = _convert_obj(obj, data)
    objs = objects(obj, data)
    attrs = attributes(obj, data)
    print(f"{obj.singular_name:=^40s}")
    if obj.__doc__:
        print('\n'.join(textwrap.wrap(textwrap.dedent('\n'.join(obj.__doc__.split('\n'))))))
        print()
    if obj.__bases__ != (Hierarchy, ):
        print(f"A {obj.singular_name} is a type of {obj.__bases__[0].singular_name}")
    if obj.idname is not None:
        print(f"A {obj.singular_name} has a unique id called '{obj.idname}'")
    else:
        print(f"A {obj.singular_name} has no unique id that can be used")
    if obj.identifier_builder:
        print(f"{obj.plural_name} are identified by {tuple(obj.identifier_builder)}")
    print(f'one {obj.singular_name} is linked to:')
    for o in objs:
        if data.is_plural_name(o):
            print('\t- many', o)
        else:
            print('\t- 1', o)
    print(f'a {obj.singular_name} directly owns these attributes:')
    for a in attrs:
        print('\t-', a)



def explain_factor(factor, data = None):
    if isinstance(factor, FactorFrozenQuery):
        for f in factor.factors:
            explain_factor(f, factor.data)
    else:
        factor = data.singular_name(factor)
        hierarchies = {h for h in data.factor_hierarchies[factor] if not h.is_template}
        if len(hierarchies) > 1:
            print(f'{factor}s are owned by multiple different objects ({[h.singular_name for h in hierarchies]}).'
                  f'\nThey could be entirely different things.')
            print(f'You will need to specify one of the parent objects below for {factor} when querying.')
        for h in hierarchies:
            if factor in h.products:
                print(f'A {factor} is a product (binary data kept out-of-database) of a {h.singular_name}')
            elif factor == h.idname:
                print(f'{factor} is the unique id name of a {h.singular_name}')
            else:
                print(f"{factor} is an attribute belonging to {h.singular_name}")


def explain_relation(a, b, data = None):
    a, data = _convert_obj(a, data)
    try:
        b, data = _convert_obj(b, data)
        try:
            data.find_hierarchy_paths(a, b, plural=False)
        except nx.NetworkXNoPath:
            print(f"- A {a.singular_name} has many {b.plural_name}")
        else:
            print(f"- A {a.singular_name} has only one {b.singular_name}")
    except (KeyError, TypeError):
        if isinstance(b, FactorFrozenQuery):
            data = b.data
            b = b.factors[0]
        hierarchies = ', '.join({i.singular_name for i in data.factor_hierarchies[b]})
        try:
            data.find_factor_paths(a, b, plural=False)
        except nx.NetworkXNoPath:
            print(f"- A {a.singular_name} has many {b}s (belonging to {hierarchies})")
        else:
            print(f"- A {a.singular_name} has 1 {b} (belonging to {hierarchies})")


def explain(a, b=None, data=None):
    try:
        explain_object(a, data)
    except (KeyError, AttributeError):
        if data is None:
            raise ValueError(f"You must supply `data=data` to `explain` when asking about a string name")
        explain_factor(a, data)
    if b is not None:
        try:
            explain_object(b, data)
        except (KeyError, AttributeError):
            if data is None:
                raise ValueError(f"You must supply `data=data` to `explain` when asking about a string name")
            explain_factor(b, data)
        print('='*40)
        explain_relation(a, b, data)
        explain_relation(b, a, data)
    print('='*40)
