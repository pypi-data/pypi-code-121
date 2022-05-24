import os
import pytest

from firepit.dataframe import DataFrame

from .helpers import tmp_storage


@pytest.fixture
def store(tmpdir):
    cwd = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(cwd, 'test_bundle.json')
    store = tmp_storage(tmpdir)
    store.cache('q1', path)
    store.extract('urls', 'url', 'q1', "[url:value LIKE '%page/1%']")
    store.extract('conns', 'network-traffic', 'q1', "[ipv4-addr:value LIKE '10.%']")
    return store


@pytest.mark.parametrize(
    'view, column, op, expected', [
        ('urls', 'value', 'count', 14),
        ('urls', 'value', 'nunique', 14),
        ('urls', 'value', 'min', 'http://www11.example.com/page/108'),
        ('urls', 'value', 'max', 'http://www91.example.com/page/104'),
        ('conns', 'src_port', 'count', 100),
        ('conns', 'src_port', 'min', 49434),
        ('conns', 'src_port', 'max', 65528),
        ('conns', 'dst_port', 'sum', 130350),
        ('conns', 'src_port', 'nunique', 100),
        ('conns', 'dst_port', 'nunique', 5),
    ]
)
def test_series(store, view, column, op, expected):
    df = DataFrame(view, store)
    if op == 'count':
        assert df[column].count() == expected
    elif op == 'nunique':
        assert df[column].nunique() == expected
    elif op == 'min':
        assert df[column].min() == expected
    elif op == 'max':
        assert df[column].max() == expected
    elif op == 'sum':
        assert df[column].sum() == expected


@pytest.mark.parametrize(
    'view, columns', [
        ('urls', ['type', 'value', 'x_root', 'id', 'x_contained_by_ref',
                  'first_observed', 'last_observed', 'number_observed']),
        ('conns', ['type', 'start', 'end', 'src_ref.type', 'src_ref.value',
                   'src_ref.x_root', 'src_ref.id', 'dst_ref.type', 'dst_ref.value',
                   'dst_ref.id', 'src_port', 'dst_port','protocols', 'x_root',
                   'id', 'x_contained_by_ref', 'first_observed', 'last_observed',
                   'number_observed'])
    ]
)
def test_dataframe_columns(store, view, columns):
    df = DataFrame(view, store)
    assert set(df.columns) == set(columns)


@pytest.mark.parametrize(
    'view, count', [
        ('urls', 14),
        ('conns', 100)
    ]
)
def test_dataframe_columns(store, view, count):
    df = DataFrame(view, store)
    index = df.index
    assert index[0] == 0
    assert len(index) == count


@pytest.mark.parametrize(
    'view, shape', [
        ('urls', (8, 14)),
        ('conns', (19, 100))
    ]
)
def test_dataframe_shape(store, view, shape):
    df = DataFrame(view, store)
    assert df.shape == shape    
