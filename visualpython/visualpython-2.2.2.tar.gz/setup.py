# coding: utf-8
import os
#from distutils.core import setup
#from distutils.command.build_py import build_py
#from distutils.command.sdist import sdist
#from os.path import join as pjoin

from setuptools import setup, find_packages

name = 'visualpython'

setup(
    name             = name,
    version          = '2.2.2',
    packages         = find_packages(),
    package_data     = {"": ["*"], 'visualpython' : ['visualpython.yaml', 'README.md']},
    #package_data     = {"blackpen": ["*"]},
    scripts          = ['visualpython/bin/visualpy', 'visualpython/bin/visualpy.bat'],
    description      = 'visualpython',
    #author           = 'BlackLogic',
    author           = 'Black Logic Co.,Ltd.',
    author_email     = 'blacklogic.dev@gmail.com',
    #url              = 'https://bl-vp.blogspot.com/',
    url              = 'http://visualpython.ai',
    license          = 'GPLv3',
    install_requires = [],
    platforms        = "Linux, Mac OS X, Windows",
    keywords         = ['Visual', 'visual', 'BlackPen', 'visualpython', 'blackpen', 'BlackPen', 'black', 'Black'],
    python_requires  = '>=3.6',
    )
