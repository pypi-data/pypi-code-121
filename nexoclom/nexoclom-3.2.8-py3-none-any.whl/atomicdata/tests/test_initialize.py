import pytest
import os
import numpy as np
import pandas as pd
import io
from nexoclom import __file__ as basefile
from nexoclom.atomicdata import gValue, PhotoRate
from nexoclom.atomicdata.initialize_atomicdata import (make_gvalue_table,
                                                       make_photorates_table)


@pytest.mark.atomicdata
def test_make_gvalue_table(monkeypatch, tmpdir):
    gvalue_true_file = os.path.join(os.path.dirname(basefile), 'data', 'g-values',
                                    'g-values.pkl')
    gvalue_test_file = tmpdir.join('g-values_test.pkl')

    monkeypatch.setattr(gValue, "gvalue_filename", lambda: gvalue_test_file)
    # monkeypatch.setattr(gValue, 'gvalue_file', gvalue_test_file)
    make_gvalue_table()

    gvalue_true = pd.read_pickle(gvalue_true_file)
    gvalue_test = pd.read_pickle(gvalue_test_file)
    assert np.all(gvalue_true == gvalue_test)


@pytest.mark.atomicdata
def test_make_photorates_table(monkeypatch, tmpdir):
    monkeypatch.setattr('sys.stdin', io.StringIO('0'))
    photo_true_file = os.path.join(os.path.dirname(basefile), 'data', 'Loss',
                                   'photorates.pkl')
    photo_test_file = tmpdir.join('photorates.pkl')

    monkeypatch.setattr(PhotoRate, 'photorates_filename', lambda: photo_test_file)
    make_photorates_table()
 
    photo_true = pd.read_pickle(photo_true_file)
    photo_test = pd.read_pickle(photo_test_file)
    assert np.all(photo_true == photo_test)
