"""
Tests to ensure that
Query(predicates, return_properties, return_nodes, conditions, exists)
are written to neo4j correctly.e

I.e.
"""
from textwrap import dedent

import pytest
from weaveio.basequery.query import FullQuery
from weaveio.basequery.query_objects import Collection, Path, Generator, Condition


@pytest.fixture(scope='function')
def g():
    return Generator()


def test_matches_must_overlap(g):
    a, b, c, d = g.nodes('A', 'B', 'C', 'D')
    path1 = Path(a, '->', b)
    path2 = Path(c, '->', d)
    with pytest.raises(ValueError):
        FullQuery([path1, path2])


def test_cannot_return_nodes_that_dont_end_a_path(g):
    a, b, c, d, e, f = g.nodes('A', 'B', 'C', 'D', 'E', 'F')
    path1 = Path(a, '->', b)
    path2 = Path(b, '->', c)
    with pytest.raises(KeyError):
        FullQuery([path1, path2], returns=[a])
    with pytest.raises(KeyError):
        FullQuery([path1, path2], returns=[a.property_a])


def test_current_node(g):
    a, b, c = g.nodes('A', 'B', 'C')
    path1 = Path(a, '->', b)
    path2 = Path(b, '->', c)
    query = FullQuery([path1, path2])
    assert query.current_node == c


def test_matches_only(g):
    a, b, c = g.nodes('A', 'B', 'C')
    path1 = Path(a, '->', b)
    path2 = Path(b, '->', c)
    query = FullQuery([path1, path2])
    q, _ = query.to_neo4j()
    assert q == f'MATCH (a0:A)->(b0:B)\nMATCH (b0)->(c0:C)\nWITH b0, c0\nRETURN'


def test_return_nodes(g):
    a, b, c = g.nodes('A', 'B', 'C')
    path1 = Path(a, '->', b)
    path2 = Path(b, '->', c)
    query = FullQuery([path1, path2], returns=[c, b])
    q, _ = query.to_neo4j()
    expected = dedent("""
    MATCH (a0:A)->(b0:B)
    MATCH (b0)->(c0:C)
    WITH b0, c0
    RETURN c0, b0
    """).strip('\n')
    assert q == expected


def test_return_properties(g):
    a, b, c = g.nodes('A', 'B', 'C')
    path1 = Path(a, '->', b)
    path2 = Path(b, '->', c)
    query = FullQuery([path1, path2], returns=[c.property_c, b.property_b])
    q, _ = query.to_neo4j()
    expected = dedent("""
    MATCH (a0:A)->(b0:B)
    MATCH (b0)->(c0:C)
    WITH b0, c0, c0.property_c as c0_property_c, b0.property_b as b0_property_b
    RETURN c0_property_c, b0_property_b
    """).strip('\n')
    assert q == expected


def test_return_nodes_properties(g):
    a, b, c = g.nodes('A', 'B', 'C')
    path1 = Path(a, '->', b)
    path2 = Path(b, '->', c)
    query = FullQuery([path1, path2], returns=[c.property_c, b.property_b, b, c])
    q, _ = query.to_neo4j()
    expected = dedent("""
    MATCH (a0:A)->(b0:B)
    MATCH (b0)->(c0:C)
    WITH b0, c0, c0.property_c as c0_property_c, b0.property_b as b0_property_b
    RETURN c0_property_c, b0_property_b, b0, c0
    """).strip('\n')
    assert q == expected


def test_condition_on_property(g):
    a, b, c = g.nodes('A', 'B', 'C')
    path1 = Path(a, '->', b)
    path2 = Path(b, '->', c)
    condition = Condition(a.id, '=', 'idvalue')
    query = FullQuery([path1, path2], conditions=condition)
    q, _ = query.to_neo4j()
    expected = dedent("""
    MATCH (a0:A)->(b0:B)
    MATCH (b0)->(c0:C)
    WHERE (a0.id = 'idvalue')
    WITH b0, c0
    RETURN
    """).strip('\n')
    assert q == expected


def test_property_branches_add_with_statements(g):
    a, b, c, d, e, f = g.nodes('A', 'B', 'C', 'D', 'E', 'F')
    path1 = Path(a, '->', b)
    path2 = Path(b, '->', c)
    branch1 = Path(c, '->', d)
    branch2 = Path(c, '->', e, '->', f)
    query = FullQuery([path1, path2],
                      branches={branch1: [d.property_d], branch2: [f.property_f]},
                      returns=[c, b.property_b, d.property_d, f.property_f])
    q, _ = query.to_neo4j()
    expected = dedent("""
    MATCH (a0:A)->(b0:B)
    MATCH (b0)->(c0:C)
    WITH b0, c0, b0.property_b as b0_property_b
    OPTIONAL MATCH (c0)->(d0:D)
    WITH b0, c0, b0_property_b, d0.property_d as d0_property_d
    OPTIONAL MATCH (c0)->(e0:E)->(f0:F)
    WITH b0, c0, b0_property_b, d0_property_d, f0.property_f as f0_property_f
    RETURN c0, b0_property_b, d0_property_d, f0_property_f
    """).strip('\n')
    assert q == expected


def test_collect_property_branches_uses_collection(g):
    a, b, c = g.nodes('A', 'B', 'C')
    path1 = Path(a, '->', b)
    path2 = Path(b, '->', c)
    query = FullQuery([path1, path2], returns=[Collection(b.property_b, 'property_b')])
    q, _ = query.to_neo4j()
    expected = dedent("""
    MATCH (a0:A)->(b0:B)
    MATCH (b0)->(c0:C)
    WITH b0, c0, collect(b0.property_b) as property_b
    RETURN property_b
    """).strip('\n')
    assert q == expected


def test_collect_property_of_root_uses_collection(g):
    a, b, c, d, e, f = g.nodes('A', 'B', 'C', 'D', 'E', 'F')
    path1 = Path(a, '->', b)
    path2 = Path(b, '->', c)
    branch1 = Path(c, '->', d)
    branch2 = Path(c, '->', e, '->', f)
    collect_f = Collection(f.property_f, 'property_f')
    query = FullQuery([path1, path2],
                      branches={branch1: [d.property_d], branch2: [collect_f]},
                      returns=[c, Collection(b.property_b, 'property_b'), d.property_d, collect_f])
    q, _ = query.to_neo4j()
    expected = dedent("""
    MATCH (a0:A)->(b0:B)
    MATCH (b0)->(c0:C)
    WITH b0, c0, collect(b0.property_b) as property_b
    OPTIONAL MATCH (c0)->(d0:D)
    WITH b0, c0, property_b, d0.property_d as d0_property_d
    OPTIONAL MATCH (c0)->(e0:E)->(f0:F)
    WITH b0, c0, property_b, d0_property_d, collect(f0.property_f) as property_f
    RETURN c0, property_b, d0_property_d, property_f
    """).strip('\n')
    assert q == expected
