#!/usr/bin/env python

"""Tests for `arcos_py` package."""

from numpy import int64
import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from arcos4py import ARCOS
from arcos4py.tools._errors import noDataError


@pytest.fixture
def no_bin_data():
    """
    pytest fixture to generate test data
    """
    data = [item for i in range(10) for item in list(range(1, 11))]
    m = [0 for i in range(100)]
    d = {'id': data, 'time': data, 'm': m, 'x': data}
    print(d)
    df = pd.DataFrame(d)
    return df


def test_empty_data(no_bin_data: pd.DataFrame):
    with pytest.raises(noDataError, match='Input is empty'):
        test_data = no_bin_data[no_bin_data['m'] > 0]
        pos = ['x']
        ts = ARCOS(
            test_data, posCols=pos, frame_column='time', id_column='id', measurement_column='m', clid_column='clTrackID'
        )
        ts.trackCollev(eps=1, minClsz=1, nPrev=2)


def test_1_central_1_prev():
    df_in = pd.read_csv('tests/testdata/1central_in.csv')
    df_true = pd.read_csv('tests/testdata/1central_res.csv')
    pos = ['x']
    ts = ARCOS(
        df_in, posCols=pos, frame_column='time', id_column='trackID', measurement_column='m', clid_column='clTrackID'
    )
    ts.bin_col = 'm'
    out = ts.trackCollev(eps=1, minClsz=1, nPrev=1)
    out = out.drop(columns=['m', 'x'])
    assert_frame_equal(out, df_true, check_dtype=False)


def test_1_central_2_prev():
    df_in = pd.read_csv('tests/testdata/1central_in.csv')
    df_true = pd.read_csv('tests/testdata/1central2prev_res.csv')
    pos = ['x']
    ts = ARCOS(
        df_in, posCols=pos, frame_column='time', id_column='trackID', measurement_column='m', clid_column='clTrackID'
    )
    ts.bin_col = 'm'
    out = ts.trackCollev(eps=1, minClsz=1, nPrev=2)
    out = out.drop(columns=['m', 'x'])
    assert_frame_equal(out, df_true, check_dtype=False)


def test_1_central_3D():
    df_in = pd.read_csv('tests/testdata/1central3D_in.csv')
    df_true = pd.read_csv('tests/testdata/1central3D_res.csv')
    pos = ['x', 'y', 'z']
    ts = ARCOS(
        df_in, posCols=pos, frame_column='time', id_column='trackID', measurement_column='m', clid_column='clTrackID'
    )
    ts.bin_col = 'm'
    out = ts.trackCollev(eps=1, minClsz=1, nPrev=1)
    out = out.drop(columns=['m', 'x', 'y', 'z'])
    assert_frame_equal(out, df_true)


def test_1_central_growing():
    df_in = pd.read_csv('tests/testdata/1centralGrowing_in.csv')
    df_true = pd.read_csv('tests/testdata/1centralGrowing_res.csv')
    pos = ['x']
    ts = ARCOS(
        df_in, posCols=pos, frame_column='time', id_column='trackID', measurement_column='m', clid_column='clTrackID'
    )
    ts.bin_col = 'm'
    out = ts.trackCollev(eps=1, minClsz=1, nPrev=1)
    out = out.drop(columns=['m', 'x'])
    assert_frame_equal(out, df_true)


def test_2_central_growing():
    df_in = pd.read_csv('tests/testdata/2centralGrowing_in.csv')
    df_true = pd.read_csv('tests/testdata/2centralGrowing_res.csv')
    pos = ['x']
    ts = ARCOS(
        df_in, posCols=pos, frame_column='time', id_column='trackID', measurement_column='m', clid_column='clTrackID'
    )
    ts.bin_col = 'm'
    out = ts.trackCollev(eps=1, minClsz=1, nPrev=1)
    out = out.drop(columns=['m', 'x'])
    assert_frame_equal(out, df_true)


def test_2_with_1_common_symmetric():
    df_in = pd.read_csv('tests/testdata/2with1commonSym_in.csv')
    df_true = pd.read_csv('tests/testdata/2with1commonSym_res.csv')
    pos = ['x']
    ts = ARCOS(
        df_in, posCols=pos, frame_column='time', id_column='trackID', measurement_column='m', clid_column='clTrackID'
    )
    ts.bin_col = 'm'
    out = ts.trackCollev(eps=1.0, minClsz=1, nPrev=1)
    out = out.drop(columns=['m', 'x'])
    assert_frame_equal(out, df_true)


def test_2_with_1_common_asymmetric():
    df_in = pd.read_csv('tests/testdata/2with1commonAsym_in.csv')
    df_true = pd.read_csv('tests/testdata/2with1commonAsym_res.csv')
    pos = ['x']
    ts = ARCOS(
        df_in, posCols=pos, frame_column='time', id_column='trackID', measurement_column='m', clid_column='clTrackID'
    )
    ts.bin_col = 'm'
    out = ts.trackCollev(eps=1.0, minClsz=1, nPrev=1)
    out = out.drop(columns=['m', 'x'])
    assert_frame_equal(out, df_true)


def test_3_spreading_1_prev():
    df_in = pd.read_csv('tests/testdata/3spreading_in.csv')
    df_true = pd.read_csv('tests/testdata/3spreading_res.csv')
    pos = ['x']
    ts = ARCOS(
        df_in, posCols=pos, frame_column='time', id_column='trackID', measurement_column='m', clid_column='clTrackID'
    )
    ts.bin_col = 'm'
    out = ts.trackCollev(eps=1.0, minClsz=1, nPrev=1)
    out = out.drop(columns=['m', 'x'])
    assert_frame_equal(out, df_true)


def test_3_spreading_2_prev():
    df_in = pd.read_csv('tests/testdata/3spreading_in.csv')
    df_true = pd.read_csv('tests/testdata/3spreading2prev_res.csv')
    pos = ['x']
    ts = ARCOS(
        df_in, posCols=pos, frame_column='time', id_column='trackID', measurement_column='m', clid_column='clTrackID'
    )
    ts.bin_col = 'm'
    out = ts.trackCollev(eps=1.0, minClsz=1, nPrev=2)
    out = out.drop(columns=['m', 'x'])
    assert_frame_equal(out, df_true)


def test_5_overlapping_1_prev():
    df_in = pd.read_csv('tests/testdata/5overlapping_in.csv')
    df_true = pd.read_csv('tests/testdata/5overlapping_res.csv')
    pos = ['x']
    ts = ARCOS(
        df_in, posCols=pos, frame_column='time', id_column='trackID', measurement_column='m', clid_column='clTrackID'
    )
    ts.bin_col = 'm'
    out = ts.trackCollev(eps=1.0, minClsz=1, nPrev=1)
    out = out.drop(columns=['m', 'x'])
    assert_frame_equal(out, df_true)


def test_5_overlapping_2_prev():
    df_in = pd.read_csv('tests/testdata/5overlapping_in.csv')
    df_true = pd.read_csv('tests/testdata/5overlapping2prev_res.csv')
    pos = ['x']
    ts = ARCOS(
        df_in, posCols=pos, frame_column='time', id_column='trackID', measurement_column='m', clid_column='clTrackID'
    )
    ts.bin_col = 'm'
    out = ts.trackCollev(eps=1.0, minClsz=1, nPrev=2)
    out = out.drop(columns=['m', 'x'])
    assert_frame_equal(out, df_true)


def test_6_overlapping():
    df_in = pd.read_csv('tests/testdata/6overlapping_in.csv')
    df_true = pd.read_csv('tests/testdata/6overlapping_res.csv')
    pos = ['x']
    ts = ARCOS(
        df_in, posCols=pos, frame_column='time', id_column='trackID', measurement_column='m', clid_column='clTrackID'
    )
    ts.bin_col = 'm'
    out = ts.trackCollev(eps=1.0, minClsz=1, nPrev=1)
    out = out.drop(columns=['m', 'x'])
    out['trackID'] = out['trackID'].astype(int64)
    assert_frame_equal(out, df_true)


def test_split_from_single():
    df_in = pd.read_csv('tests/testdata/1objSplit_in.csv')
    df_true = pd.read_csv('tests/testdata/1objSplit_res.csv')
    pos = ['pos']
    ts = ARCOS(df_in, posCols=pos, frame_column='t', id_column='id', measurement_column=None, clid_column='collid')
    out = ts.trackCollev(eps=1.0, minClsz=1, nPrev=1)
    out = out.drop(columns=['pos'])
    assert_frame_equal(out, df_true)


def test_split_from_2_objects():
    df_in = pd.read_csv('tests/testdata/2objSplit_in.csv')
    df_true = pd.read_csv('tests/testdata/2objSplit_res.csv')
    pos = ['pos']
    ts = ARCOS(df_in, posCols=pos, frame_column='t', id_column='id', measurement_column=None, clid_column='collid')
    out = ts.trackCollev(eps=1.0, minClsz=1, nPrev=1)
    out = out.drop(columns=['pos'])
    assert_frame_equal(out, df_true)


def test_cross_2_objects():
    df_in = pd.read_csv('tests/testdata/2objCross_in.csv')
    df_true = pd.read_csv('tests/testdata/2objCross_res.csv')
    pos = ['pos']
    ts = ARCOS(df_in, posCols=pos, frame_column='t', id_column='id', measurement_column=None, clid_column='collid')
    out = ts.trackCollev(eps=1.0, minClsz=1, nPrev=1)
    out = out.drop(columns=['pos'])
    assert_frame_equal(out, df_true)


def test_merge_split_2_objects_with_common():
    df_in = pd.read_csv('tests/testdata/2objMergeSplitCommon_in.csv')
    df_true = pd.read_csv('tests/testdata/2objMergeSplitCommon_res.csv')
    pos = ['pos']
    ts = ARCOS(df_in, posCols=pos, frame_column='t', id_column='id', measurement_column=None, clid_column='collid')
    out = ts.trackCollev(eps=1.0, minClsz=1, nPrev=1)
    out = out.drop(columns=['pos'])
    assert_frame_equal(out, df_true)


## if algorithm behaves differently (like in R) a different output is produced regarding collective events
def test_merge_split_2_objects_crossing():
    df_in = pd.read_csv('tests/testdata/2objMergeSplitCross_in.csv')
    df_true = pd.read_csv('tests/testdata/2objMergeSplitCross_res.csv')
    pos = ['pos']
    ts = ARCOS(df_in, posCols=pos, frame_column='t', id_column='id', measurement_column=None, clid_column='collid')
    out = ts.trackCollev(eps=1.0, minClsz=1, nPrev=1)
    out = out.drop(columns=['pos'])
    assert_frame_equal(out, df_true)


## if algorithm behaves differently (like in R) a different output is produced regarding collective events
def test_merge_and_split_2_objects_near():
    df_in = pd.read_csv('tests/testdata/2objMergeSplitNear_in.csv')
    df_true = pd.read_csv('tests/testdata/2objMergeSplitNear_res.csv')
    pos = ['pos']
    ts = ARCOS(df_in, posCols=pos, frame_column='t', id_column='id', measurement_column=None, clid_column='collid')
    out = ts.trackCollev(eps=1.0, minClsz=1, nPrev=1)
    out = out.drop(columns=['pos'])
    assert_frame_equal(out, df_true)


def test_4_objects_in_2_events():
    df_in = pd.read_csv('tests/testdata/4obj2events_in.csv')
    df_true = pd.read_csv('tests/testdata/4obj2events_res.csv')
    pos = ['x']
    ts = ARCOS(df_in, posCols=pos, frame_column='frame', id_column='id', measurement_column=None, clid_column='collId')
    out = ts.trackCollev(eps=1.0, minClsz=1, nPrev=1)
    out = out.drop(columns=['x'])
    assert_frame_equal(out, df_true)
