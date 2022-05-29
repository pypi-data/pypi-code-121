#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `seamm_ff_util` package."""

import seamm_ff_util  # noqa: F401


def test_middle_bond_torsion_3_explicit(pcff):
    """Test of middle_bond_torsion_3 parameters, which should find
    explicit ones"""

    expected = {
        "V1": "-10.0179",
        "V2": "-2.8145",
        "V3": "0.1665",
        "reference": "1",
        "R0": "1.5300",
    }

    i = "h"
    j = "c"
    k = "c"
    l = "c_0"  # noqa: E741
    ptype, key, form, parameters = pcff.middle_bond_torsion_3_parameters(i, j, k, l)
    assert ptype == "explicit"
    assert key == ("c_0", "c", "c", "h")
    assert parameters == expected


def test_middle_bond_torsion_3_explicit_lkji(pcff):
    """known middle_bond_torsion_3 parameters, ordered backwards"""

    expected = {
        "V1": "-10.0179",
        "V2": "-2.8145",
        "V3": "0.1665",
        "reference": "1",
        "R0": "1.5300",
    }

    i = "c_0"
    j = "c"
    k = "c"
    l = "h"  # noqa: E741
    ptype, key, form, parameters = pcff.middle_bond_torsion_3_parameters(i, j, k, l)
    assert ptype == "explicit"
    assert key == ("c_0", "c", "c", "h")
    assert parameters == expected


def test_middle_bond_torsion_3_equivalent(pcff):
    """Simple test of middle_bond_torsion_3 parameters using equivalencies"""
    expected = {
        "V1": "-5.5679",
        "V2": "1.4083",
        "V3": "0.3010",
        "reference": "1",
        "R0": "1.5010",
    }

    i = "h"
    j = "c"
    k = "c5"
    l = "c5"  # noqa: E741
    ptype, key, form, parameters = pcff.middle_bond_torsion_3_parameters(i, j, k, l)
    assert ptype == "equivalent"
    assert key == ("h", "c", "cp", "cp")
    assert parameters == expected
