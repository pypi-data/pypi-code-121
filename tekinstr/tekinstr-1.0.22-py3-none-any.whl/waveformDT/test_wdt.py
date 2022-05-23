"""Test WaveformDT"""
from datetime import datetime
import numpy as np
from pytest import approx
from unyt import s, m, unyt_array  # pylint: disable=no-name-in-module
from .waveform import WaveformDT

# pylint: disable=missing-docstring
# pylint: disable=pointless-statement
# pylint: disable=no-member
# pylint: disable=invalid-name
def test_attributes_nounits():
    wf = WaveformDT([0, 1, 2], 1, 0)
    assert isinstance(wf.Y, np.ndarray)
    assert wf.dt == 1
    assert wf.t0 == 0
    assert wf.yunit == None
    assert wf.xunit == None
    assert wf.size == 3
    x, y = wf.to_xy()
    assert (x == np.asarray([0.0, 1.0, 2.0])).all()
    assert (y == np.asarray([0, 1, 2])).all()
    wf = WaveformDT(list(range(10)), 1, 0)
    assert (wf.head().Y == np.arange(5)).all()
    assert (np.asarray(wf.tail()) == np.arange(5, 10)).all()
    x, _ = wf.tail().to_xy()
    assert (x == np.arange(5.0, 10.0)).all()
    assert wf.min == 0
    assert wf.max == 9
    assert wf.std == approx(2.8722813232690143)
    wf.set_attributes(attr="custom")
    assert wf.attr == "custom"
    assert (wf["x"] == np.arange(10.0)).all()
    assert (wf["y"] == np.arange(10)).all()


def test_math_nounits():
    wf = WaveformDT([0, 1, 2], 1, 0)
    assert (np.asarray(2 * wf) == np.asarray([0, 2, 4])).all()
    assert (np.asarray(wf + 2) == np.asarray([2, 3, 4])).all()
    np.multiply.at(wf, [0, 1, 2], 2.0)
    assert (wf.Y == np.asarray([0.0, 2.0, 4.0])).all()
    arr_out = np.asarray([0.0] * 3)
    np.multiply(wf, 2.0, out=arr_out)
    assert (arr_out == np.asarray([0.0, 4.0, 8.0])).all()
    wf_out = WaveformDT([0.0] * 3, 1, 0)
    assert isinstance(wf_out, WaveformDT)
    np.multiply(wf, 2.0, out=wf_out)
    assert (wf_out.Y == np.asarray([0.0, 4.0, 8.0])).all()


def test_attributes_withunits():
    wf = WaveformDT([0, 1, 2], 1, 0)
    wf.yunit = "m"
    wf.xunit = "s"
    x, y = wf.to_xy()
    assert (x == unyt_array([0.0, 1.0, 2.0], "s")).all()
    assert (y == unyt_array([0, 1, 2], "m")).all()
    wf = WaveformDT([0, 1, 2] * m, 1 * s, 0 * s)
    assert wf.yunit == m
    assert wf.xunit == s
    x, y = wf.to_xy(inunits=False)
    assert (x == np.arange(3.0)).all()
    assert (y == np.arange(3)).all()


def test_absolute_xy():
    t = lambda s: datetime(2020, 1, 1, 0, 0, s)
    wf = WaveformDT([0, 1, 2], 1, t(0))
    x, _ = wf.to_xy(relative=False)
    expected = np.asarray([t(s) for s in range(3)], dtype="datetime64[ns]")
    assert (x == expected).all()
