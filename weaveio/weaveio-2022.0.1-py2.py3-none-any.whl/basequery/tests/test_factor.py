import pytest

from weaveio.basequery.factor import SingleFactorFrozenQuery, ColumnFactorFrozenQuery, RowFactorFrozenQuery, TableFactorFrozenQuery
from weaveio.basequery.hierarchy import HomogeneousHierarchyFrozenQuery
from weaveio.basequery.query import AmbiguousPathError
from weaveio.basequery.query_objects import Node, NodeProperty
from weaveio.basequery.tests.example_structures.one2one import HierarchyA, HierarchyB, HierarchyC
from weaveio.utilities import quote


def test_single_hierarchy_direct_single_factor(data_one2one):
    """get a single factor from the parent hierarchy directly"""
    single = data_one2one.hierarchyas['1'].a_factor_a
    query = single.query
    assert isinstance(single, SingleFactorFrozenQuery)
    assert query.returns[0] == NodeProperty(Node(label='HierarchyA', name='hierarchya0'), 'a_factor_a')
    assert len(query.returns) == 1   # a_factor_a and no indexer


def test_single_hierarchy_indirect_single_factor(data_one2one):
    """get a single factor from a hierarchy above the parent"""
    single = data_one2one.hierarchyas['1'].b_factor_a
    query = single.query
    assert isinstance(single, SingleFactorFrozenQuery)
    assert query.returns[0] == NodeProperty(Node(label='HierarchyB', name='hierarchyb0'), 'b_factor_a')
    assert len(query.returns) == 1   # b_factor_b and no indexer


def test_single_hierarchy_fails_with_unknown_name(data_one2one):
    with pytest.raises(AttributeError):
        data_one2one.hierarchyas['1'].unknown


def test_homogeneous_hierarchy_fails_with_unknown_name(data_one2one):
    with pytest.raises(AttributeError):
        data_one2one.hierarchyas.unknowns


def test_homogeneous_hierarchy_direct_plural_factor(data_one2one):
    single = data_one2one.hierarchyas.a_factor_as
    query = single.query
    assert isinstance(single, ColumnFactorFrozenQuery)
    assert query.returns[0] == NodeProperty(Node(label='HierarchyA', name='hierarchya0'), 'a_factor_a')
    assert len(query.returns) == 1   # a_factor_a and no indexer


def test_homogeneous_hierarchy_indirect_plural_factor(data_one2one):
    single = data_one2one.hierarchyas.b_factor_as
    query = single.query
    assert isinstance(single, ColumnFactorFrozenQuery)
    assert query.returns[0] == NodeProperty(Node(label='HierarchyB', name='hierarchyb0'), 'b_factor_a')
    assert len(query.returns) == 1   # b_factor_b and no indexer


def test_identified_homogeneous_hierarchy_fails_with_unknown_name(data_one2one):
    with pytest.raises(AttributeError):
        data_one2one.hierarchyas[['1', '2']].unknowns


def test_identified_homogeneous_hierarchy_direct_plural_factor(data_one2one):
    single = data_one2one.hierarchyas[['1', '2']].a_factor_as
    query = single.query
    assert isinstance(single, ColumnFactorFrozenQuery)
    assert query.returns[0] == NodeProperty(Node(label='HierarchyA', name='hierarchya0'), 'a_factor_a')
    assert len(query.returns) == 1   # a_factor_a and no indexer


def test_identified_homogeneous_hierarchy_indirect_plural_factor(data_one2one):
    single = data_one2one.hierarchyas[['1', '2']].b_factor_as
    query = single.query
    assert isinstance(single, ColumnFactorFrozenQuery)
    assert query.returns[0] == NodeProperty(Node(label='HierarchyB', name='hierarchyb0'), 'b_factor_a')
    assert len(query.returns) == 1   # b_factor_b and no indexer


def test_heterogeneous_plural_factor(data_one2one):
    factors = data_one2one.b_factor_as
    query = factors.query
    assert isinstance(factors, ColumnFactorFrozenQuery)
    assert query.returns[0] == NodeProperty(Node(label='HierarchyB', name='hierarchyb0'), 'b_factor_a')
    assert len(query.returns) == 1  # b_factor_b and no indexer


@pytest.mark.parametrize('typ', [tuple, list])
@pytest.mark.parametrize('hiers', [['a'], ['b'], ['a', 'b']])
def test_single_hierarchy_row_of_factors(data_one2one, typ, hiers):
    items, hiers = zip(*[(item, h) for h in hiers for item in [f'{h}_factor_{i}' for i in 'ab']])
    items = typ(items)
    row = data_one2one.hierarchyas['1'].__getitem__(items)
    assert isinstance(row, RowFactorFrozenQuery)
    for i, (item, hier) in enumerate(zip(items, hiers)):
        prop = row.branch.returns[i]
        assert prop.property_name == item
        assert prop.node.label == f'Hierarchy{hier.upper()}'
    if typ is list:
        assert row.return_keys == items
    elif typ is tuple:
        assert row.return_keys is None
    else:
        assert False, "Bad arguments"


@pytest.mark.parametrize('make_plural_name', [True, False])
@pytest.mark.parametrize('factor_name', ['a', 'b'])
@pytest.mark.parametrize('hierarchy,multiple_from_a', ([HierarchyB, False], [HierarchyC, True]))
def test_plural_factor_name_required_by_getattr(data_one2one, hierarchy, multiple_from_a, factor_name, make_plural_name):
    """
    When selecting factors by getattr, plurality is required when there will be more than one result returned
    We tests this by starting at hierarchya and selecting the factors of the parent hierarchies.
    """
    factor_name = hierarchy.__name__[-1].lower() + '_factor_' + factor_name
    name = factor_name + 's' if make_plural_name else factor_name
    parent = data_one2one.hierarchyas
    if make_plural_name:
        assert isinstance(parent.__getattr__(name), ColumnFactorFrozenQuery)
    else:
        with pytest.raises(AmbiguousPathError):
            parent.__getattr__(name)


@pytest.mark.parametrize('make_plural_name', [True, False], ids=lambda v: "s']" if v else "']")
@pytest.mark.parametrize('factor_name', ['a', 'b'], ids=lambda v: f"{v}")
@pytest.mark.parametrize('hierarchy,multiple_from_a', ([HierarchyB, False], [HierarchyC, True]), ids=["['b_factor_", "['c_factor_"])
def test_plural_factor_name_required_by_getitem(data_one2one, hierarchy, multiple_from_a, factor_name, make_plural_name):
    """
    When selecting factors by getitem, plurality is required when each item in the hierarchy before will have multiple items
    We tests this by starting at hierarchya and selecting the factors of the parent hierarchies.
    """
    factor_name = hierarchy.__name__[-1].lower() + '_factor_' + factor_name
    name = factor_name + 's' if make_plural_name else factor_name
    parent = data_one2one.hierarchyas
    if make_plural_name:  # requesting a plural is always allowed
        assert isinstance(parent.__getitem__(name), ColumnFactorFrozenQuery)
    else:
        if multiple_from_a:
            with pytest.raises(AmbiguousPathError):
                parent.__getitem__(name)
        else:
            assert isinstance(parent.__getitem__(name), ColumnFactorFrozenQuery)



@pytest.mark.parametrize('hiers', [['a'], ['b'], ['a', 'b']])
@pytest.mark.parametrize('factor_intype', [tuple, list])
@pytest.mark.parametrize('factor_names', [['a'], ['b'], ['a', 'b']], ids=lambda x: str(x))
@pytest.mark.parametrize('idfilter', ['1', ['1', '2'], ('1', '2'), None],
ids=lambda v: f'hierarchies[{quote(v)}]'.replace('(', '').replace(')', '') if v is not None else 'hierarchies')
def test_tablelike_factors_by_getitem(data_one2one, factor_intype, hiers, factor_names, idfilter):
    """
    Selecting factors by __getitem__ can yield:
        a whole factor_table for multiple hierarchies and multiple items
        a factor_row for one hierarchy and multiple items
        a factor_column for multiple hierarchies and one factor
        a single factor for one hierarchy and one factor

    In getitem, plurality is done on a "foreach" basis, so when the individual hierarchy has more than one value for a factor_name,
    it is pluralised.
    E.g.
    The hierarchy type Run has multiple values for `cname` so `cname` must become `cnames` in any __getitem__ query
        runs[id1, id2]['cnames']
    The hierarchy type Run has only has one value for `expmjd` so `expmjd` can be `expmjd` or `expmjds` depending on what you want
        runs[id1, id2]['expmjd']
        runs[id1, id2]['expmjds']
    """
    items, hiers = zip(*[(item, h) for h in hiers for item in [f'{h}_factor_{i}' for i in factor_names]])
    items = factor_intype(items)

    structure = data_one2one.hierarchyas
    if idfilter is not None:
        structure = structure.__getitem__(idfilter)

    if isinstance(idfilter, (list, tuple)) or idfilter is None:
        if isinstance(items, (list, tuple)):
            querytype = TableFactorFrozenQuery
        else:
            querytype = ColumnFactorFrozenQuery
    else:  # scalar, therefore a single
        if isinstance(items, (list, tuple)):
            querytype = RowFactorFrozenQuery
        else:
            assert False, "bad arguments"  # this is never reached in this test, see below

    table = structure.__getitem__(items)
    assert isinstance(table, querytype), f"data.hierarchyas[{idfilter}][{items}]"

    zippable_items = [items] if not isinstance(items, (tuple, list)) else items
    for i, (item, hier) in enumerate(zip(zippable_items, hiers)):
        prop = table.branch.returns[i]
        assert prop.property_name == item
        assert prop.node.label == f'Hierarchy{hier.upper()}'
    if isinstance(items, list):
        assert table.return_keys == items
    elif isinstance(items, tuple):
        assert table.return_keys is None
    elif isinstance(items, str):
        pass
    else:
        assert False, "Bad arguments"


@pytest.mark.parametrize('hier', ['a', 'b'], ids=lambda v: f"['{v}_factor_a']")
@pytest.mark.parametrize('idfilter', ['1', ['1', '2'], ('1', '2'), None],
ids=lambda v: f'hierarchies[{quote(v)}]'.replace('(', '').replace(')', '') if v is not None else 'hierarchies')
def test_direct_single_factors_by_getitem(data_one2one, idfilter, hier):
    """
    Selecting a single factor_name by getitem is identical to selecting via getattr with the same plurality rules
    """
    if idfilter is not None:
        structure = data_one2one.hierarchyas.__getitem__(idfilter)
    else:
        structure = data_one2one.hierarchyas
    if isinstance(idfilter, (list, tuple)) or idfilter is None:
        querytype = ColumnFactorFrozenQuery
    else:  # scalar, therefore a single
        querytype = SingleFactorFrozenQuery
    factor_name = f'{hier}_factor_a'
    result = structure[factor_name]
    assert isinstance(result, querytype), str(result)
    prop = result.branch.returns[0]
    assert prop.property_name == factor_name
    assert len(result.branch.returns) == 1
    assert prop.node.label == f'Hierarchy{hier.upper()}'


@pytest.mark.parametrize('a_factor_plural', [True, False])
@pytest.mark.parametrize('c_factor_plural', [True, False])
def test_tablelike_factors_by_getitem_raise_when_one_has_wrong_plurality(data_one2one, a_factor_plural, c_factor_plural):
    if a_factor_plural:
        items = ['a_factor_as']
    else:
        items = ['a_factor_a']
    if c_factor_plural:
        items.append('c_factor_as')
    else:
        items.append('c_factor_a')

    if not c_factor_plural:
        with pytest.raises(AmbiguousPathError, match="multiple `c_factor_as`"):
            var = data_one2one.hierarchyas[items]
    else:
        assert isinstance(data_one2one.hierarchyas[items], TableFactorFrozenQuery)


def test_ambiguous_factor_name_raises_error_on_getitem(data_one2one):
    with pytest.raises(AmbiguousPathError):
        var = data_one2one.hierarchyas['1']['shared_factor_name']


def test_ambiguous_factor_name_raises_error_on_getattr(data_one2one):
    with pytest.raises(AmbiguousPathError):
        var = data_one2one.hierarchyas['1'].shared_factor_name


def test_disambiguated_factor_name_on_getitem(data_one2one):
    with pytest.raises(AmbiguousPathError):
        # fails because there is more than one hierarchyc for a hierarchya.
        var = data_one2one.hierarchyas['1']['hierarchyc.shared_factor_name']
    var = data_one2one.hierarchyas['1']['hierarchyd.shared_factor_name']
    var = data_one2one.hierarchyas['1']['hierarchyc.shared_factor_names']


def test_disambiguated_factor_name_on_getattr(data_one2one):
    """Removing ambiguouity from getattr calls is basically just
    another normal getattr call with hierarchies"""
    var = data_one2one.hierarchyas['1'].hierarchyds.shared_factor_names
    var = data_one2one.hierarchyas['1'].hierarchycs.shared_factor_names
    with pytest.raises(AmbiguousPathError):
        # fails because there is more than one hierarchyc for a hierarchya.
        var = data_one2one.hierarchyas['1'].hierarchycs.shared_factor_name


def test_not_plural_raise_ambiguous_path_error(data_one2one):
    with pytest.raises(AmbiguousPathError):
        # hierarchyA has one factor
        # but there are more than one of them, so plural is required
        var = data_one2one.hierarchyas.a_factor_a
    with pytest.raises(AmbiguousPathError):
        # Requesting factors without hierarchies always requires plural
        var = data_one2one.a_factor_a
    with pytest.raises(AmbiguousPathError):
        # hierarchyC has a_factor_a below it, but there is more than one,
        # so it is plural
        var = data_one2one.hierarchycs.a_factor_a
