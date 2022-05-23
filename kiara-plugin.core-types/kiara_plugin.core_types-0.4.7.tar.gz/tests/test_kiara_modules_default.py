#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `kiara_plugin.core_types` package."""

import pytest  # noqa

import kiara_plugin.core_types


def test_assert():

    assert kiara_plugin.core_types.get_version() is not None
