import pytest
import numpy as np
from astropy.table import Table

from weaveio.basequery.tests.example_structures.one2one import HierarchyA, HierarchyB


def test_instantiate_db(database_one2one):
    pass


def test_return_homogeneous(database_one2one):
    for h in database_one2one.hierarchyas():
        assert isinstance(h, HierarchyA)
        assert h.a_factor_a == 'a'
        assert h.a_factor_b == 'b'


def test_return_single(database_one2one):
    b = database_one2one.hierarchyas['1.fits'].hierarchyb()
    assert isinstance(b, HierarchyB)
    assert b.otherid == '1.fits'


def test_empty_id_raise_keyerror(database_one2one):
    with pytest.raises(KeyError, match="nonexistent_id"):
        database_one2one.hierarchyas['nonexistent_id'].hierarchyb()


def test_uchained_queries(database_one2one):
    first = database_one2one.hierarchyas
    second = first.hierarchybs
    first()
    second()


def test_multiple_ids(database_one2one):
    names = ['1.fits', '2.fits', '1.fits']
    a = database_one2one.hierarchyas[names]()
    assert [i.id for i in a] == names


def test_multiple_ids_keyerror(database_one2one):
    names = ['1.fits', '2.fits', 'nan']
    with pytest.raises(KeyError, match='nan'):
        database_one2one.hierarchyas[names]()


def test_single_factor_is_scalar(database_one2one):
    assert database_one2one.hierarchyas['1.fits'].a_factor_a() == 'a'


def test_column_factor_is_vector(database_one2one):
    np.testing.assert_array_equal(database_one2one.hierarchyas['1.fits', '2.fits'].a_factor_as(), ['a', 'a'])


def convert_object_array_of_lists2_array(array):
    if array.dtype == object and not isinstance(array.ravel()[0], str):
        shape = array.shape
        return np.reshape([np.asarray(i) for i in array.ravel()], shape + (-1,))
    else:
        return array

@pytest.mark.parametrize('columns,colshape,is_unstructured',
                         (
                                 ['c_factor_as', (2, ), False], [['c_factor_as'], (2, ), False],
                                 ['a_factor_a', tuple(), False], [['a_factor_a'], tuple(), False],
                                 ['f_factor_as', (1, ), True], [['f_factor_as'], (1, ), True]
                         ),
                          ids=["['c_factor_as']", "[['c_factor_as']]",
                               "['a_factor_a']", "[['a_factor_a']]",
                               "['f_factor_as']", "[['f_factor_as']]"])
@pytest.mark.parametrize('idfilter,idshape', ([None, (5,)], [('1.fits', ), (1, )], [['1.fits'], (1,)]),
                         ids=["", "['1.fits']", "[['1.fits']]"])
def test_table_return_shape(database_one2one, columns, is_unstructured, idfilter, idshape, colshape):
    """
    Test that [[colname]] type getitems always return astropy tables with the correct shape,
    plural colnames should make a list structure within it.
    """
    parent = database_one2one.hierarchyas
    if idfilter is not None:
        parent = parent.__getitem__(idfilter)
    structure = parent.__getitem__(columns)
    result = structure()
    if isinstance(columns, list):
        assert isinstance(result, Table)
        result = result[result.colnames[0]].data
    else:
        assert isinstance(result, np.ndarray)
    if is_unstructured:
        assert isinstance(result[0], list)
    result = convert_object_array_of_lists2_array(result)
    expected = np.empty(idshape + colshape, dtype=str)
    expected[:] = 'a'
    np.testing.assert_array_equal(result, expected)


def test_names_with_dots_resolve_correctly(database_one2one):
    # cypher doesn't allow dots in its names, but we want the dots in our table
    table = database_one2one.hierarchyas[['hierarchyd.shared_factor_name']]()
    assert table.colnames == ['hierarchyd.shared_factor_name']

