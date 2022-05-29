#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Fixtures for testing the 'seamm_ff_util' package."""

import pytest

from molsystem import SystemDB
from seamm_ff_util import Forcefield
from seamm_ff_util import FFAssigner


@pytest.fixture(scope="session")
def pcff():
    """A forcefield object initialized with PCFF"""
    pcff = Forcefield("data/pcff2018.frc")
    pcff.initialize_biosym_forcefield()
    return pcff


@pytest.fixture(scope="session")
def pcff_assigner(pcff):
    """A forcefield object initialized with PCFF"""
    pcff_assigner = FFAssigner(pcff)
    return pcff_assigner


@pytest.fixture()
def configuration():
    """Create a system db with no systems."""
    db = SystemDB(filename="file:seamm_db?mode=memory&cache=shared")
    system = db.create_system(name="default")
    configuration = system.create_configuration(name="default")

    yield configuration

    db.close()
    try:
        del db
    except:  # noqa: E722
        print("Caught error deleting the database")
