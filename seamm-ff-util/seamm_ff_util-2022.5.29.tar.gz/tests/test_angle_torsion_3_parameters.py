#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `seamm_ff_util` package."""

import seamm_ff_util  # noqa: F401


def test_angle_torsion_3_explicit(pcff):
    """Test of angle_torsion_3 parameters, which should find
    explicit ones"""

    expected = {
        "V1_L": "0.0492",
        "V1_R": "-1.6930",
        "V2_L": "0.7162",
        "V2_R": "-0.6252",
        "V3_L": "-0.2277",
        "V3_R": "-0.2148",
        "reference": "1",
        "Theta0_L": "108.4000",
        "Theta0_R": "110.7700",
    }

    i = "h"
    j = "c"
    k = "c"
    l = "c_0"  # noqa: E741
    ptype, key, form, parameters = pcff.angle_torsion_3_parameters(i, j, k, l)
    assert ptype == "explicit"
    assert key == ("h", "c", "c", "c_0")
    assert parameters == expected


def test_angle_torsion_3_explicit_kji(pcff):
    """known angle_torsion_3 parameters, ordered backwards"""

    expected = {
        "V1_L": "-1.6930",
        "V1_R": "0.0492",
        "V2_L": "-0.6252",
        "V2_R": "0.7162",
        "V3_L": "-0.2148",
        "V3_R": "-0.2277",
        "reference": "1",
        "Theta0_L": "108.4000",
        "Theta0_R": "110.7700",
    }

    i = "c_0"
    j = "c"
    k = "c"
    l = "h"  # noqa: E741
    ptype, key, form, parameters = pcff.angle_torsion_3_parameters(i, j, k, l)
    assert ptype == "explicit"
    assert key == ("c_0", "c", "c", "h")
    assert parameters == expected


def test_angle_torsion_3_equivalent(pcff):
    """Simple test of angle_torsion_3 parameters using equivalencies"""

    expected = {
        "V1_L": "4.6266",
        "V1_R": "0.2251",
        "V2_L": "0.1632",
        "V2_R": "0.6548",
        "V3_L": "0.0461",
        "V3_R": "0.1237",
        "reference": "1",
        "Theta0_L": "111.0000",
        "Theta0_R": "120.0500",
    }

    i = "h"
    j = "c"
    k = "c5"
    l = "c5"  # noqa: E741
    ptype, key, form, parameters = pcff.angle_torsion_3_parameters(i, j, k, l)
    assert ptype == "equivalent"
    assert key == ("h", "c", "cp", "cp")
    assert parameters == expected
