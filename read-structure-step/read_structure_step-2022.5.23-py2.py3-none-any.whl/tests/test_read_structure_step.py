#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `read.py` module."""

import pytest  # noqa: F401
import read_structure_step  # noqa: F401
from . import build_filenames

from molsystem.system_db import SystemDB


@pytest.fixture(scope="module")
def configuration():
    """Create a system db, system and configuration."""
    db = SystemDB(filename="file:seamm_db?mode=memory&cache=shared")
    system = db.create_system(name="default")
    configuration = system.create_configuration(name="default")

    yield configuration

    db.close()
    try:
        del db
    except:  # noqa: E722
        print("Caught error deleting the database")


@pytest.mark.parametrize("file_name", [1, [], {}, 1.0])
def test_read_filename_type(configuration, file_name):

    with pytest.raises(TypeError):
        read_structure_step.read(file_name, configuration)


def test_empty_filename(configuration):

    with pytest.raises(NameError):
        read_structure_step.read("", configuration)


def test_unregistered_reader(configuration):

    with pytest.raises(KeyError):

        xyz_file = build_filenames.build_data_filename("spc.xyz")
        read_structure_step.read(xyz_file, configuration, extension=".mp3")
