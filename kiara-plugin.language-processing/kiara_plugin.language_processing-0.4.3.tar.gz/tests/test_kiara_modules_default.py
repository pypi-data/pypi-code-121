#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `kiara_plugin.language_processing` package."""

import pytest  # noqa

import kiara_plugin.language_processing


def test_assert():

    assert kiara_plugin.language_processing.get_version() is not None
