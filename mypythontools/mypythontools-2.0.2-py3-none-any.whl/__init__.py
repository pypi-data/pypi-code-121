"""Some tools/functions/snippets/files used across projects.

.. image:: https://img.shields.io/pypi/pyversions/mypythontools.svg
    :target: https://pypi.python.org/pypi/mypythontools/
    :alt: Python versions

.. image:: https://badge.fury.io/py/mypythontools.svg
    :target: https://badge.fury.io/py/mypythontools
    :alt: PyPI version

.. image:: https://pepy.tech/badge/mypythontools
    :target: https://pepy.tech/project/mypythontools
    :alt: Downloads

.. image:: https://img.shields.io/lgtm/grade/python/github/Malachov/mypythontools.svg
    :target: https://lgtm.com/projects/g/Malachov/mypythontools/context:python
    :alt: Language grade: Python

.. image:: https://readthedocs.org/projects/mypythontools/badge/?version=latest
    :target: https://mypythontools.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. image:: https://img.shields.io/badge/License-MIT-yellow.svg
    :target: https://opensource.org/licenses/MIT
    :alt: License: MIT

.. image:: https://codecov.io/gh/Malachov/mypythontools/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/Malachov/mypythontools
    :alt: Codecov


It's called mypythontools, but it's also made for you...

Many projects - one codebase.

There is also some extra stuff, that is not bundled via PyPI (CSS for readthedocs etc.),
such a content is under the `Tools` topic.


Links
=====

Official documentation - https://mypythontools.readthedocs.io/

Official repo - https://github.com/Malachov/mypythontools

Installation
============

Python >=3.6 (Python 2 is not supported).

Install with::

    pip install mypythontools


Python library
==============

**subpackages**

- :py:mod:`mypythontools.config`
- :py:mod:`mypythontools.misc`
- :py:mod:`mypythontools.paths`
- :py:mod:`mypythontools.plots`
- :py:mod:`mypythontools.property`
- :py:mod:`mypythontools.system`
- :py:mod:`mypythontools.terminal`
- :py:mod:`mypythontools.types`

Subpackages names are self describing and you can find documentation in subpackages docstrings.

Mypythontools_cicd
==================

There is extra library in separate repository

https://github.com/Malachov/mypythontools_cicd

This can help you with a lot of stuff around CICD like getting project paths, generating docs, testing,
deploying to PyPi etc.

Tools
=====

There are some extra tools not included in in python library (installable via pip), but still on GitHub
repository. Some tools were big enough to be refactored to own repository. Still listed here though. 

Link where you can find that content:

https://github.com/Malachov/mypythontools/tree/master/tools

Link where you can read about how to use it:

https://mypythontools.readthedocs.io/#Tools

Some examples of what you can find only on GitHub

requirements
------------

Install many libraries at once (no need for Anaconda). Download `requirements.txt` file from
https://github.com/Malachov/mypythontools/tree/master/tools/requirements and in that folder use::

    pip install -r requirements.txt

It's good for python libraries that other users with different versions of libraries will use. If not
standalone application where freezing into virtual env is good idea - here is possible to use these
requirements with using --upgrade from time to time to be sure that your library will be working for
up-to-date version of dependencies.

sphinx-alabaster-css
--------------------

Its good idea to generate documentation from code. If you are using sphinx and alabaster theme, you can use
this css file for formatting.

Tested on readthedocs hosting (recommended).

CSS are served from GitHub, and it's possible to change on one place and edit how all projects docs look like
at once.

Just add this to sphinx conf.py::

>>> html_css_files = ["https://malachov.github.io/readthedocs-sphinx-alabaster-css/custom.css"]

Also, of course if you want you can download it and use locally from project if you need.

Result should look like this

.. image:: /_static/sphinx-alabaster-css.png
    :width: 620
    :alt: sphinx-alabaster-css
    :align: center
"""
from mypythontools import config, misc, paths, plots, property, system, types

__all__ = ["config", "misc", "paths", "plots", "property", "system", "types"]

__version__ = "2.0.2"

__author__ = "Daniel Malachov"
__license__ = "MIT"
__email__ = "malachovd@seznam.cz"
