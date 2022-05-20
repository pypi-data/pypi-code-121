#!/usr/bin/env python

"""Tests for `threaded_mvc` package."""

import pytest

# import threaded_mvc.Model as Model
from threaded_mvc import Model, View, Controller


def test_model_class_is_abstract():
    with pytest.raises(TypeError):
        mvcmodel = Model()


def test_view_class_is_abstract():
    with pytest.raises(TypeError):
        mvcview = View()


def test_controller_class_is_abstract():
    with pytest.raises(TypeError):
        mvccontroller = Controller()
