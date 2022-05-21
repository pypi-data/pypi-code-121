"""This is not module that configure library mypythontools, but module that help create config
for your project.

What
====

1) Simple and short syntax.
2) Ability to have docstrings on variables (not dynamically, so visible in IDE) and good for sphinx docs.
3) Type checking and Literal checking via MyProperty.
4) Also function evaluation from other config values (not only static value stored).
5) Options hierarchy (nested options).

Examples:
=========

    >>> from __future__ import annotations
    >>> from typing_extensions import Literal
    ...
    >>> class SimpleConfig(Config):
    ...     @MyProperty
    ...     @staticmethod  # You can add this for Pylint complain (needs to be after @MyProperty)
    ...     def var() -> int:  # Type hints are validated.
    ...         '''
    ...         Type:
    ...             int
    ...
    ...         Default:
    ...             123
    ...
    ...         This is docstrings (also visible in IDE, because not defined dynamically).
    ...         Also visible in Sphinx documentation.'''
    ...
    ...         return 123  # This is initial value that can be edited.
    ...
    ...     @MyProperty
    ...     @staticmethod
    ...     def var_literal() -> Literal[1, 2, 3]:  # Literal options are also validated
    ...         return 2
    ...
    ...     @MyProperty   # If other defined value is changed, computed property is also updated
    ...     def evaluated(self) -> int | float:
    ...         return self.var + 1
    ...
    >>> config = SimpleConfig()
    >>> config.var
    123
    >>> config.var = 665
    >>> config.var
    665
    >>> config['var']  # You can also access params as in a dictionary
    665
    >>> config.var = "String is problem"
    Traceback (most recent call last):
    TypeError: ...
    ...
    >>> config.var_literal = 4
    Traceback (most recent call last):
    TypeError: ...
    ...
    >>> config.evaluated
    666

    You can still setup a function (or lambda expression) as a new value
    and returned value still will be validated

    >>> config.var = lambda self: self.var_literal + 1

This is how help looks like in VS Code

.. image:: /_static/intellisense.png
    :width: 620
    :alt: intellisense
    :align: center


Hierarchical config
-------------------

It is possible to use another config object as a value in config and thus hierarchical configs can be created.
Note:
    Use unique values for all config variables even if they are in various subconfig.

>>> from mypythontools.config import Config as mypythontools_config
...
>>> class Config(mypythontools_config):
...     def __init__(self) -> None:
...         self.subconfig1 = self.SubConfiguration1()
...         self.subconfig2 = self.SubConfiguration2()
...
...     class SubConfiguration1(Config):
...         def __init__(self) -> None:
...             self.subsubconfig = self.SubSubConfiguration()
...
...         class SubSubConfiguration(Config):
...             @MyProperty
...             @staticmethod
...             def value1() -> Literal[0, 1, 2, 3]:
...                 '''Documentation here
...
...                 Options: [0, 1, 2, 3]
...                 '''
...                 return 3
...
...             @MyProperty
...             def value2(self):
...                 return self.value1 + 1
...
...     class SubConfiguration2(Config):
...         @MyProperty
...         def other_val(self):
...             return self.value2 + 1
...
...     # Also subconfig category can contain values itself
...     @MyProperty
...     def value3() -> int:
...         return 3
...
>>> config = Config()
...
>>> config.subconfig1.subsubconfig.value2
4

You can access value from config as well as from subcategory

>>> config.value2
4

Copy
----

Sometimes you need more instances of settings and you need copy of existing configuration.
Copy is deepcopy by default.

>>> config2 = config.copy()
>>> config2.value3 = 0
>>> config2.value3
0
>>> config.value3
3

Bulk update
-----------

Sometimes you want to update many values with flat dictionary.

>>> config.update({'value3': 2, 'value1': 0})
>>> config.value3
2
>>> config.update({"not_existing": "Should fail"})
Traceback (most recent call last):
AttributeError: ...

Get flat dictionary
-------------------

There is a function that will export all the values to the flat dictionary (no dynamic anymore, just values).

>>> config.get_dict()
{'value3': 2, 'value1': 0, 'value2': 1, 'other_val': 2}

Reset
-----
You can reset to default values

>>> config.value1 = 1
>>> config.reset()
>>> config.value1
3

CLI
---
CLI is provided by argparse. When using `with_argparse` method, it will

1) Create parser and add all arguments with help
2) Parse users' sys args and update config

::

    config.with_argparse()

Now you can use in terminal like.

::

    python my_file.py --value1 12


Only basic types like int, float, str, list, dict, set are possible as eval for using type like numpy
array or pandas DataFrame could be security leak.

Setter
======

If you need extra logic in setters, use normal property or implement custom descriptors.

Sphinx docs
===========

If you want to have documentation via sphinx, you can add this to conf.py::

    napoleon_custom_sections = [
        ("Types", "returns_style"),
        ("Type", "returns_style"),
        ("Options", "returns_style"),
        ("Default", "returns_style"),
        ("For example", "returns_style"),
    ]

Here is example

.. image:: /_static/config_on_sphinx.png
    :width: 620
    :alt: config_on_sphinx
    :align: center
"""
from mypythontools.config.config_internal import Config
from mypythontools.property import MyProperty

__all__ = ["Config", "MyProperty"]
