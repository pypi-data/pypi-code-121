#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `seamm_ff_util.ff_assigner` package."""


def test_methane(pcff_assigner, configuration):
    """Test of atom-type assignment for methane"""
    configuration.from_smiles("C")
    assert pcff_assigner.assign(configuration) == ["c", "hc", "hc", "hc", "hc"]


def test_ethane(pcff_assigner, configuration):
    """Test of atom-type assignment for ethane"""
    configuration.from_smiles("CC")
    assert pcff_assigner.assign(configuration) == [
        "c3",
        "c3",
        "hc",
        "hc",
        "hc",
        "hc",
        "hc",
        "hc",
    ]


def test_propane(pcff_assigner, configuration):
    """Test of atom-type assignment for propane"""
    configuration.from_smiles("CCC")
    assert pcff_assigner.assign(configuration) == [
        "c3",
        "c2",
        "c3",
        "hc",
        "hc",
        "hc",
        "hc",
        "hc",
        "hc",
        "hc",
        "hc",
    ]


def test_isobutane(pcff_assigner, configuration):
    """Test of atom-type assignment for isobutane"""
    configuration.from_smiles("CC(C)C")
    assert pcff_assigner.assign(configuration) == [
        "c3",
        "c1",
        "c3",
        "c3",
        "hc",
        "hc",
        "hc",
        "hc",
        "hc",
        "hc",
        "hc",
        "hc",
        "hc",
        "hc",
    ]


def test_neopentane(pcff_assigner, configuration):
    """Test of atom-type assignment for neopentane"""
    configuration.from_smiles("CC(C)(C)C")
    assert pcff_assigner.assign(configuration) == [
        "c3",
        "c",
        "c3",
        "c3",
        "c3",
        "hc",
        "hc",
        "hc",
        "hc",
        "hc",
        "hc",
        "hc",
        "hc",
        "hc",
        "hc",
        "hc",
        "hc",
    ]
