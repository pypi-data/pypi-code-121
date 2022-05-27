#  -*- coding: utf-8 -*-
"""Tests for the rigid body classes"""
import pytest
import numpy as np
import sksurgeryarucotracker.markerpatterns.makemarkerpatterns as mkpt

def test_make_wholeboard():
    """
    Not implemented
    """
    with pytest.raises(NotImplementedError):
        mkpt.makemarkerpattern_wholeboard(None)


def test_make_wholeboard_bymarker():
    """
    Doesn't do much yet
    """
    class _testboard():
        def __init__(self):
            self.dictionary = 'hello'
            self.ids = 'from'
            self.objPoints = 'the board.' #pylint: disable=invalid-name


    mkpt.makemarkerpattern_bymarker(_testboard())


def test_float_to_int():
    """
    Scales a float array to an integer array
    """
    array_in = np.array([[0.25, 1.0],[0.75, 0.0]], dtype = np.float32)
    array_out, good_scale = mkpt.float_to_int(array_in)

    assert good_scale == 4
    assert np.array_equal(array_out,
                    np.array([[1., 4.0],[3., 0.0]],
                            dtype = np.float32))
