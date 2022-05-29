#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `seamm_ff_util` package."""

import seamm_ff_util  # noqa: F401


def test_end_bond_torsion_3_explicit(pcff):
    """Test of end_bond_torsion_3 parameters, which should find
    explicit ones"""

    expected = {
        "V1_L": "0.0870",
        "V1_R": "0.2217",
        "V2_L": "0.5143",
        "V2_R": "0.4780",
        "V3_L": "-0.2448",
        "V3_R": "-0.0817",
        "reference": "1",
        "R0_L": "1.5140",
        "R0_R": "1.1010",
    }

    i = "h"
    j = "c"
    k = "c"
    l = "c_0"  # noqa: E741
    ptype, key, form, parameters = pcff.end_bond_torsion_3_parameters(i, j, k, l)
    assert ptype == "explicit"
    assert key == ("h", "c", "c", "c_0")
    assert parameters == expected


def test_end_bond_torsion_3_explicit_kji(pcff):
    """known end_bond_torsion_3 parameters, ordered backwards"""

    expected = {
        "V1_L": "0.2217",
        "V1_R": "0.0870",
        "V2_L": "0.4780",
        "V2_R": "0.5143",
        "V3_L": "-0.0817",
        "V3_R": "-0.2448",
        "reference": "1",
        "R0_L": "1.5140",
        "R0_R": "1.1010",
    }

    i = "c_0"
    j = "c"
    k = "c"
    l = "h"  # noqa: E741
    ptype, key, form, parameters = pcff.end_bond_torsion_3_parameters(i, j, k, l)
    assert ptype == "explicit"
    assert key == ("c_0", "c", "c", "h")
    assert parameters == expected


def test_end_bond_torsion_3_equivalent(pcff):
    """Simple test of end_bond_torsion_3 parameters using equivalencies"""
    expected = {
        "V1_L": "1.3997",
        "V1_R": "-0.5835",
        "V2_L": "0.7756",
        "V2_R": "1.1220",
        "V3_L": "0.0000",
        "V3_R": "0.3978",
        "reference": "1",
        "R0_L": "1.1010",
        "R0_R": "1.4170",
    }

    i = "h"
    j = "c"
    k = "c5"
    l = "c5"  # noqa: E741
    ptype, key, form, parameters = pcff.end_bond_torsion_3_parameters(i, j, k, l)
    assert ptype == "equivalent"
    assert key == ("h", "c", "cp", "cp")
    assert parameters == expected
