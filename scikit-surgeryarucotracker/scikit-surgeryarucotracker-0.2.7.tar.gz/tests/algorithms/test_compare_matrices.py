#  -*- coding: utf-8 -*-
"""Tests for the rigid body classes"""
import numpy as np
from sksurgeryarucotracker.algorithms.compare_matrices import \
        matrices_equivalent

def test_matrices_equiv():
    """
    Tests that matrices_equivalent works
    """
    assert matrices_equivalent(np.eye(4), np.eye(4))
    assert not matrices_equivalent(np.eye(4), np.eye(4)*-1.0)
