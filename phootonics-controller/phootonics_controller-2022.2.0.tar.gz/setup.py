#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on July 22, 2021

Copyright Alpes Lasers SA, Neuchatel, Switzerland, 2021

@author: olgare
"""

from setuptools import setup

setup(
    setup_requires=['pbr'],
    pbr=True,
    test_suite = "phootonics_controller.tests"
)