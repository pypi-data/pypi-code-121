#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `seamm_ff_util` package."""

import seamm_ff_util  # noqa: F401


def test_oop_explicit(pcff):
    """Test of out-of-plane parameters, which should find explicit ones"""

    expected = {"Chi0": "0.0000", "K": "10.8102", "reference": "1"}

    i = "h"
    j = "cp"
    k = "np"
    l = "op"  # noqa: E741
    ptype, key, form, parameters = pcff.oop_parameters(i, j, k, l)
    assert ptype == "explicit"
    assert key == ("h", "cp", "np", "op")
    assert parameters == expected


def test_oop_explicit_lkji(pcff):
    """known out-of-plane parameters, ordered backwards"""
    i = "h"
    j = "cp"
    k = "np"
    l = "op"  # noqa: E741
    ptype, key, form, parameters = pcff.oop_parameters(i, j, k, l)
    ptype2, key2, form, parameters2 = pcff.oop_parameters(l, j, k, i)
    assert ptype2 == "explicit"
    assert key == ("h", "cp", "np", "op")
    assert parameters == parameters2


def test_oop_equivalent(pcff):
    """Simple test of out-of-plane parameters using equivalencies"""
    expected = {"Chi0": "0.0000", "K": "10.8102", "reference": "1"}

    i = "hp"
    j = "c5"
    k = "np"
    l = "op"  # noqa: E741
    ptype, key, form, parameters = pcff.oop_parameters(i, j, k, l)
    assert ptype == "equivalent"
    assert key == ("h", "cp", "np", "op")
    assert parameters == expected


def test_oop_auto(pcff):
    """test of out-of-plane parameters using automatic parameters"""
    expected = {"Chi0": "0.0000", "K": "36.0000", "reference": "1"}

    i = "hp"
    j = "c_0"
    k = "co"
    l = "br"  # noqa: E741
    ptype, key, form, parameters = pcff.oop_parameters(i, j, k, l)
    assert ptype == "automatic"
    assert key == ("*", "c'_", "*", "*")
    assert parameters == expected
