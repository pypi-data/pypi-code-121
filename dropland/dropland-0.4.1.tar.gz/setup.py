# -*- coding: utf-8 -*-
import os

from setuptools import setup

setup_kwargs = {
    'dependency_links': [
        os.path.join(os.getcwd(), 'backends', 'sqla'),
        os.path.join(os.getcwd(), 'backends', 'gino'),
    ]
}

setup(**setup_kwargs)
