import numpy as np
import pytest
from hypothesis import given, settings, note, Verbosity, HealthCheck, example, reproduce_failure, assume, reject, event
from hypothesis import strategies as st

from .test_hypothesis_strategies import create_node_from_node, node_strategy, Node, is_equal, neo4jproperty_strategy, rel_strategy, create_rel_from_rel
from .. import CypherQuery, merge_node
from ..actions import custom
from ..base import Varname, CypherData
from ..merging import PropertyOverlapError, are_different
from ...graph import Graph, is_null

SYSTEM_PROPERTIES = ['_dbupdated', '_dbcreated']

def assert_is_equal(a, b):
    if not is_equal(a, b):  # can handle nans
        assert a == b  # cant handle nans, but has a nicer output


@pytest.mark.parametrize('nantype', [np.nan, float('nan')])
def test_nans_convert_to_none(write_database, nantype):
    r = write_database.execute('return {a: $nan}', nan=nantype).to_table()[0][0]
    assert_is_equal({'a': None}, r)


def test_nones(write_database):
    r = write_database.execute('return {a: $none}', none=None).to_table()[0][0]
    assert_is_equal({'a': None}, r)


def _test_difference(write_database, a, b):
    with CypherQuery() as query:
        _a = CypherData(a, 'a')
        _b = CypherData(b, 'b')
        diff = custom(lambda ai, bi, out: f'WITH *, {are_different(ai, bi)} as {out}', [_a, _b], ['diff'])[0]
        query.returns(diff=diff, a=_a, b=_b)
    cypher, params = query.render_query()
    note(cypher)
    are_actually_different, neoa, neob = write_database.execute(cypher, **params).to_table()[0]
    note(f'a was input as {a} and output as {neoa}')
    note(f'b was input as {b} and output as {neob}')
    return are_actually_different

@pytest.mark.diff
@settings(deadline=None, max_examples=200, verbosity=Verbosity.normal)
@example(x=np.nan)
@example(x=[np.nan])
@example(x=None)
@example(x=[None])
@given(x=neo4jproperty_strategy)
def test_not_different(write_database, x):
    are_actually_different = _test_difference(write_database, x, x)
    assert are_actually_different == False


@pytest.mark.diff
@settings(deadline=5000, max_examples=200, verbosity=Verbosity.normal)
@example(x=np.nan, y=1)
@example(x=[1, np.nan], y=[1, 2])
@example(x=np.nan, y=[np.nan])
@example(x=None, y=1)
@example(x=[1, None], y=[1, 2])
@example(x=None, y=[None])
@given(x=neo4jproperty_strategy, y=neo4jproperty_strategy)
def test_different(write_database, x, y):
    assume(not is_equal(x, y))
    are_actually_different = _test_difference(write_database, x, y)
    assert are_actually_different == True


def test_raw_null_returns_none(write_database):
    assert write_database.execute('RETURN null').to_table()[0][0] is None


def test_input_none_returns_none(write_database):
    assert write_database.execute('RETURN $n', n=None).to_table()[0][0] == np.inf


def test_input_nan_returns_none(write_database):
    assert write_database.execute('RETURN $n', n=np.nan).to_table()[0][0] == np.inf


def test_input_list_nan_returns_none(write_database):
    assert write_database.execute('RETURN $n', n=[np.nan, 1.0]).to_table()[0][0] == [np.inf, 1]


def assert_overlapping_properties(write_database, time, node1, node2, collision_manager, exclude=None):
    """
    Once node1 and node2 have been identified as the same, assert that the set properties are correct
    If collisions occur, the behaviour is set by collision_manager (overwrite, ignore, or track&flag)
        overwrite will replace colliding keys
        ignore will do nothing with colliding keys
        track&flag will not change the node, but will place the colliding keys into a collision node attached to it
    New keys will always be added to the node
    Unmentioned keys (in matched node but not in proposed properties) will always be ignored
    If the entire properties dict is different, then this policy has the effect of just adding more properties.
    """
    if exclude is None:
        exclude = []
    exclude = ' AND '.join([f'NOT n:{e}' for e in exclude])
    if len(exclude):
        exclude = f' AND {exclude} '
    collision = None
    same_keys = set(node1.properties.keys()) & set(node2.properties.keys())
    colliding_keys = [k for k in same_keys if not is_equal(node1.properties[k], node2.properties[k])]
    added_keys = set(node2.properties.keys()) - set(node1.properties.keys())

    new = {k: node2.properties[k] for k in added_keys}
    expected = node1.allproperties.copy()
    expected.update(new)  # always add new
    expected.update({'_dbcreated': time, '_dbupdated': time})

    if collision_manager == 'ignore':
        pass
    elif collision_manager == 'overwrite':
        expected.update(node2.properties)
    elif collision_manager == 'track&flag':
        if len(colliding_keys):
            collision = {k: node2.properties[k] for k in colliding_keys}
            collision.update({'_dbcreated': time})
    else:
        raise ValueError(f"Unknown collision_manager {collision_manager}")

    nodes = write_database.execute(f'MATCH (n) WHERE NOT n:_Collision {exclude}\n'
                                   'OPTIONAL MATCH (n)<-[:COLLIDES]-(c:_Collision)\n'
                                   'RETURN {properties: properties(n), labels: labels(n)} as n, {properties: properties(c), labels: labels(c)} as c').to_table()
    assert len(nodes) == 1
    node, collision_node = nodes[0]
    assert is_equal(node['properties'], expected)
    if collision is None:
        assert is_equal(collision_node, {'properties': None, 'labels': None})
    else:
        assert is_equal(collision_node['properties'], collision)


def assert_overlapping_rel_properties(write_database, time, parent, child, rel1, rel2, collision_manager):
    collision = None
    same_keys = set(rel1.properties.keys()) & set(rel2.properties.keys())
    colliding_keys = [k for k in same_keys if not is_equal(rel1.properties[k], rel2.properties[k])]
    added_keys = set(rel2.properties.keys()) - set(rel1.properties.keys())

    new = {k: rel2.properties[k] for k in added_keys}
    expected = rel1.allproperties.copy()
    expected.update(new)  # always add new
    expected.update({'_dbcreated': time, '_dbupdated': time})

    if collision_manager == 'ignore':
        pass
    elif collision_manager == 'overwrite':
        expected.update(rel2.properties)
    elif collision_manager == 'track&flag':
        if len(colliding_keys):
            collision = {k: rel2.properties[k] for k in colliding_keys}
            collision.update({'_dbcreated': time})
    else:
        raise ValueError(f"Unknown collision_manager {collision_manager}")
    alabels = ':'.join(parent.labels)
    blabels = ':'.join(child.labels)
    aprops = parent.allproperties.copy()
    bprops = child.allproperties.copy()
    aprops.update({'_dbcreated': time, '_dbupdated': time})
    bprops.update({'_dbcreated': time, '_dbupdated': time})
    query = f'MATCH (a:{alabels})-[r]->(b:{blabels}) WHERE properties(a) = $aprops AND properties(b) = $bprops AND NOT r:_Collision\n'\
                                   'OPTIONAL MATCH (a)-[c:_Collision]->(b)\n'\
                                   'RETURN {properties: properties(r), type: type(r)} as r, {properties: properties(c), type: type(c)} as c'
    note(query)
    note(aprops)
    note(bprops)
    rels = write_database.execute(query, aprops=aprops, bprops=bprops).to_table()
    assert len(rels) == 1
    rel, collision_rel = rels[0]
    assert is_equal(rel['properties'], expected)
    if collision is None:
        assert is_equal(collision_rel, {'properties': None, 'type': None})
    else:
        assert is_equal(collision_rel['properties'], collision)


def assert_only_these_nodes_exist(write_database, time, *nodes, exclude=None):
    if exclude is None:
        exclude = []
    exclude = ' AND '.join([f'NOT n:{e}' for e in exclude])
    if len(exclude):
        exclude = f' AND {exclude} '
    for node in nodes:
        number = sum(node == n for n in nodes)
        labels = ':'.join(node.labels)
        props = node.allproperties.copy()
        props.update({'_dbcreated': time, '_dbupdated': time})
        props = {k: v for k, v in props.items()}
        query = f'MATCH (n:{labels}) WHERE properties(n) = $props AND size(labels(n)) = {len(node.labels)} {exclude} RETURN n'
        note(query)
        result = write_database.execute(query, props=props).to_table()
        assert len(result) == number
    assert write_database.execute(f'MATCH (n) RETURN count(n)').to_table()[0][0] == len(nodes)


def assert_merge_node_tests(node1, node2, collision_manager, write_database, time):
    has_equivalent_labels = all(l in node1.labels for l in node2.labels)
    has_equivalent_ident = all(node1.identproperties.get(k, None) == v for k,v in node2.identproperties.items())
    matched = has_equivalent_labels and has_equivalent_ident
    if matched:
        assert_overlapping_properties(write_database, time, node1, node2, collision_manager)
    else:
        assert_only_these_nodes_exist(write_database, time, node1, node2)

@settings(max_examples=1000, deadline=None, suppress_health_check=[HealthCheck.data_too_large],
          # verbosity=Verbosity.verbose,
          print_blob=True)
@given(node=node_strategy, sampler=st.data(),
collision_manager=st.sampled_from(['track&flag', 'overwrite', 'ignore']),
different_labels=st.sampled_from(['crop', 'entire', False, 'extend', 'crop&extend']),
different_properties=st.sampled_from([False, 'entirekeys', 'crop', 'addkeys', 'overwritekeys']),
different_identproperties=st.sampled_from([False, 'entirekeys', 'crop', 'addkeys', 'overwritekeys']))
def test_node_pair(node, sampler, different_properties, different_identproperties, different_labels, collision_manager, write_database):
    write_database.neograph.run('MATCH (n) DETACH DELETE n')
    write_database.neograph.run('CALL apoc.schema.assert({},{},true) YIELD label, key RETURN *')
    write_database.neograph.run('call db.clearQueryCaches')
    node1 = node
    node2 = create_node_from_node(node, sampler, different_labels, different_properties, different_identproperties)
    note(node1)
    note(node2)
    assume(not any(any(k in n.identproperties for k in n.properties) for n in [node1, node2]))  # no overlaps

    with CypherQuery() as query:
        a = merge_node(node1.labels, node1.identproperties, node1.properties, collision_manager=collision_manager)
        b = merge_node(node2.labels, node2.identproperties, node2.properties, collision_manager=collision_manager)
    cypher, params = query.render_query()
    time = write_database.execute(cypher, **params).to_table()[0][0]
    assert_merge_node_tests(node1, node2, collision_manager, write_database, time)


@pytest.mark.parametrize('collision_manager', ['track&flag', 'overwrite', 'ignore'])
def test_node_pair_with_parents_different_rels_properties(write_database: Graph, collision_manager):
    """
    create the nparent nodes
    """
    write_database.neograph.run('MATCH (n) DETACH DELETE n')
    write_database.neograph.run('CALL apoc.schema.assert({},{},true) YIELD label, key RETURN *')
    write_database.neograph.run('call db.clearQueryCaches')
    with CypherQuery() as query:
        a = merge_node(['A'], {})
        b = merge_node(['B'], {})
        for i in range(3):
            merge_node(['C'], {'id': 1}, {'c': 1}, parents={a: [f'arel', {'a': 1}, {'b': i}],
                                                            b: ['brel', {'a': 2}, {'b': i}]},
                       collision_manager=collision_manager)
    cypher, params = query.render_query()
    time = write_database.execute(cypher, **params).to_table()[0][0]
    assert len(write_database.execute('MATCH (c:_Collision) RETURN c').to_table()) == 0
    collision_result = write_database.execute('MATCH ()-[c:_Collision]->() RETURN c ORDER BY c.b, c._reltype').to_series()
    if collision_manager == 'track&flag':
        assert len(collision_result) == 4  # one is create, the other 2 collide, times by 2 and so there should be 4
        assert [i['b'] for i in collision_result.values] == [1, 1, 2, 2]  #  two collisions, two properties in each
        assert [i['_reltype'] for i in collision_result.values] == ['arel', 'brel', 'arel', 'brel']  #  two collisions, two properties in each
    else:
        assert len(collision_result) == 0
    result = write_database.execute('MATCH (a:A)-[ar:arel]->(c:C)<-[br:brel]-(b:B) '
                                    'RETURN properties(a) as a, properties(b) as b, properties(c) as c, '
                                    'properties(ar) as ar, properties(br) as br').to_data_frame()
    assert len(result) == 1
    result = result.iloc[0]
    assert result['c'] == {'c': 1, 'id': 1, '_dbupdated': time, '_dbcreated': time}
    if collision_manager == 'overwrite':
        assert result['ar'] == {'a': 1, 'b': 2, '_dbupdated': time, '_dbcreated': time}
        assert result['br'] == {'a': 2, 'b': 2, '_dbupdated': time, '_dbcreated': time}
    else:
        assert result['ar'] == {'a': 1, 'b': 0, '_dbupdated': time, '_dbcreated': time}
        assert result['br'] == {'a': 2, 'b': 0, '_dbupdated': time, '_dbcreated': time}


@pytest.mark.parametrize('collision_manager', ['track&flag', 'overwrite', 'ignore'])
def test_node_pair_with_parents_different_parents(write_database: Graph, collision_manager):
    """
    create the nparent nodes
    """
    write_database.neograph.run('MATCH (n) DETACH DELETE n')
    write_database.neograph.run('CALL apoc.schema.assert({},{},true) YIELD label, key RETURN *')
    write_database.neograph.run('call db.clearQueryCaches')
    with CypherQuery() as query:
        a = merge_node(['A'], {})
        b1 = merge_node(['B'], {'id': 1})
        b2 = merge_node(['B'], {'id': 2})
        merge_node(['C'], {'id': 1}, {'c': 1}, parents={a: [f'arel', {'a': 1}, {'b': 1}],
                                                        b1: ['brel', {'a': 2}, {'b': 1}]},
                   collision_manager=collision_manager)
        merge_node(['C'], {'id': 1}, {'c': 1}, parents={a: [f'arel', {'a': 1}, {'b': 1}],
                                                        b2: ['brel', {'a': 2}, {'b': 1}]},
                   collision_manager=collision_manager)
    cypher, params = query.render_query()
    time = write_database.execute(cypher, **params).to_table()[0][0]
    assert len(write_database.execute('MATCH (c:_Collision) RETURN c').to_table()) == 0
    collision_result = write_database.execute('MATCH ()-[c:_Collision]->() RETURN c ORDER BY c.b, c._reltype').to_series()
    assert len(collision_result) == 0
    result = write_database.execute('MATCH (a:A)-[ar:arel]->(c:C)<-[br:brel]-(b:B) '
                                    'RETURN properties(a) as a, properties(b) as b, properties(c) as c, '
                                    'properties(ar) as ar, properties(br) as br').to_data_frame()
    assert len(result) == 2


@pytest.mark.parametrize('collision_manager', ['track&flag', 'overwrite', 'ignore'])
def test_node_pair_with_parents_different_childprops(write_database: Graph, collision_manager):
    """
    create the nparent nodes
    """
    write_database.neograph.run('MATCH (n) DETACH DELETE n')
    write_database.neograph.run('CALL apoc.schema.assert({},{},true) YIELD label, key RETURN *')
    write_database.neograph.run('call db.clearQueryCaches')
    with CypherQuery() as query:
        a = merge_node(['A'], {})
        b1 = merge_node(['B'], {'id': 1})
        random = merge_node(['B'], {'id': 2})
        merge_node(['C'], {'id': 1}, {'c': 1}, parents={a: [f'arel', {'a': 1}, {'b': 1}],
                                                        b1: ['brel', {'a': 2}, {'b': 1}]},
                   collision_manager=collision_manager)
        merge_node(['C'], {'id': 2}, {'c': 1}, parents={a: [f'arel', {'a': 1}, {'b': 1}],
                                                        b1: ['brel', {'a': 2}, {'b': 1}]},
                   collision_manager=collision_manager)
    cypher, params = query.render_query()
    time = write_database.execute(cypher, **params).to_table()[0][0]
    assert len(write_database.execute('MATCH (c:_Collision) RETURN c').to_table()) == 0
    collision_result = write_database.execute('MATCH ()-[c:_Collision]->() RETURN c ORDER BY c.b, c._reltype').to_series()
    assert len(collision_result) == 0
    result = write_database.execute('MATCH (a:A)-[ar:arel]->(c:C)<-[br:brel]-(b:B) '
                                    'RETURN properties(a) as a, properties(b) as b, properties(c) as c, '
                                    'properties(ar) as ar, properties(br) as br').to_data_frame()
    assert len(result) == 2


def assert_merge_dependent_node_tests(node1, node2, parenta1, parentb1, parenta2, parentb2, rela1, relb1, rela2, relb2, ndifferent_parents, collision_manager, write_database, time):
    has_equivalent_labels = all(l in node1.labels for l in node2.labels)
    has_equivalent_ident = all(node1.identproperties.get(k, None) == v for k,v in node2.identproperties.items())
    has_equivalent_parent_labels = all(all(l in old.labels for l in new.labels) for old, new in [[parenta1, parenta2], [parentb1, parentb2]])
    has_equivalent_parent_ident = all(all(old.identproperties.get(k, None) == v for k, v in new.identproperties.items()) for old, new in [[parenta1, parenta2], [parentb1, parentb2]])
    has_equivalent_rel_labels = all(old.reltype == new.reltype for old, new in [[rela1, rela2], [relb1, relb2]])
    has_equivalent_rel_ident = all(all(old.identproperties.get(k, None) == v for k, v in new.identproperties.items()) for old, new in [[rela1, rela2], [relb1, relb2]])

    matched = has_equivalent_labels and has_equivalent_ident and has_equivalent_parent_labels and has_equivalent_parent_ident\
              and has_equivalent_rel_labels and has_equivalent_rel_ident
    if matched:
        assert_overlapping_properties(write_database, time, node1, node2, collision_manager, ['ParentA', 'ParentB'])
        assert_overlapping_rel_properties(write_database, time, parenta1, node1, rela1, rela2, collision_manager)
        assert_overlapping_rel_properties(write_database, time, parentb1, node1, relb1, relb2, collision_manager)
    else:
        if ndifferent_parents == 0:
            assert_only_these_nodes_exist(write_database, time, node1, node2, parenta1, parentb1)
        elif ndifferent_parents == 1:
            assert_only_these_nodes_exist(write_database, time, node1, node2, parenta1, parentb1, parenta2)
        elif ndifferent_parents == 2:
            assert_only_these_nodes_exist(write_database, time, node1, node2, parenta1, parentb1, parenta2, parentb2)
        else:
            raise NotImplementedError(f"Unhandled number of different parents {ndifferent_parents}")


@settings(max_examples=1000, deadline=None, suppress_health_check=[HealthCheck.data_too_large, HealthCheck.too_slow],
          print_blob=True)
@given(
    node1=node_strategy, sampler=st.data(), rela=rel_strategy, relb=rel_strategy,
    collision_manager=st.sampled_from(['overwrite', 'ignore', 'track&flag']),
    different_labels=st.sampled_from([False, 'crop', 'entire', 'extend', 'crop&extend']),
    different_properties=st.sampled_from([False, 'entirekeys', 'crop', 'addkeys', 'overwritekeys']),
    different_identproperties=st.sampled_from([False, 'entirekeys', 'crop', 'addkeys', 'overwritekeys']),
    ndifferent_parents=st.sampled_from([0, 1, 2]),
    different_rela_reltype=st.sampled_from([False, 'entire']),  # rels only have one
    different_rela_properties=st.sampled_from([False, 'entirekeys', 'crop', 'addkeys', 'overwritekeys']),
    different_rela_identproperties=st.sampled_from([False, 'entirekeys', 'crop', 'addkeys', 'overwritekeys']),
    different_relb_reltype=st.sampled_from([False, 'entire']),  # rels only have one
    different_relb_properties=st.sampled_from([False, 'entirekeys', 'crop', 'addkeys', 'overwritekeys']),
    different_relb_identproperties=st.sampled_from([False, 'entirekeys', 'crop', 'addkeys', 'overwritekeys']),
)
def test_dependent_node_merge(write_database, node1, rela, relb, sampler, collision_manager, different_labels, different_properties,
                              different_identproperties, ndifferent_parents, different_rela_reltype,
                              different_rela_properties, different_rela_identproperties, different_relb_reltype,
                              different_relb_properties, different_relb_identproperties):

    write_database.neograph.run('MATCH (n) DETACH DELETE n')
    write_database.neograph.run('CALL apoc.schema.assert({},{},true) YIELD label, key RETURN *')
    write_database.neograph.run('call db.clearQueryCaches')

    parenta = Node(['ParentA'], {}, identproperties={'id': 1})  # no props so we dont get extra collisions
    parentb = Node(['ParentB'], {}, identproperties={'id': 1})  # no props so we dont get extra collisions
    parenta2 = Node(['ParentA'], {}, identproperties={'id': 1})  # clone it
    parentb2 = Node(['ParentB'], {}, identproperties={'id': 1})  # clone it
    if ndifferent_parents > 0:
        parenta2.identproperties['id'] = 2
    if ndifferent_parents > 1:
        parentb2.identproperties['id'] = 2

    node2 = create_node_from_node(node1, sampler, different_labels, different_properties, different_identproperties)
    rela2 = create_rel_from_rel(rela, sampler, different_rela_reltype, different_rela_properties, different_rela_identproperties)
    relb2 = create_rel_from_rel(relb, sampler, different_relb_reltype, different_relb_properties, different_relb_identproperties)

    assume(not any(any(k in n.identproperties for k in n.properties) for n in [node1, node2, rela, relb, rela2, relb2, parenta, parentb, parenta2, parentb2]))  # no overlaps
    for pa, pb, ch in [[parenta, parentb, node1], [parenta2, parentb2, node2]]:
        for thing in ['labels', 'identproperties']:
            assume(not is_equal(getattr(pa, thing), getattr(ch, thing)))
            assume(not is_equal(getattr(pb, thing), getattr(ch, thing)))

    note(f'node1 = {node1}')
    note(f'node2 = {node2}')
    note(f'parenta1 = {parenta}')
    note(f'parenta2 = {parenta2}')
    note(f'parentb1 = {parentb}')
    note(f'parentb2 = {parentb2}')
    note(f'rela2 = {rela2}')
    note(f'relb2 = {relb2}')

    with CypherQuery() as query:
        parenta_node = merge_node(parenta.labels, parenta.identproperties, parenta.properties, collision_manager=collision_manager)
        parentb_node = merge_node(parentb.labels, parentb.identproperties, parentb.properties, collision_manager=collision_manager)
        parenta2_node = merge_node(parenta2.labels, parenta2.identproperties, parenta2.properties, collision_manager=collision_manager)
        parentb2_node = merge_node(parentb2.labels, parentb2.identproperties, parentb2.properties, collision_manager=collision_manager)

        child1 = merge_node(node1.labels, node1.identproperties, node1.properties, parents={parenta_node: (rela.reltype, rela.identproperties, rela.properties),
                                                                                           parentb_node: (relb.reltype, relb.identproperties, relb.properties)},
                            collision_manager=collision_manager)
        child2 = merge_node(node2.labels, node2.identproperties, node2.properties, parents={parenta2_node: (rela2.reltype, rela2.identproperties, rela2.properties),
                                                                                            parentb2_node: (relb2.reltype, relb2.identproperties, relb2.properties)},
                            collision_manager=collision_manager)
    cypher, params = query.render_query()
    time = write_database.execute(cypher, **params).to_table()[0][0]

    assert_merge_dependent_node_tests(node1, node2, parenta, parentb, parenta2, parentb2, rela, relb, rela2, relb2, ndifferent_parents, collision_manager, write_database, time)