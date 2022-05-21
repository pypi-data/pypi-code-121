# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['autoregistry']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'autoregistry',
    'version': '0.4.0',
    'description': 'Automatic registry design-pattern for mapping names to functionality.',
    'long_description': '.. image:: https://raw.githubusercontent.com/BrianPugh/autoregistry/main/assets/logo_400w.png\n\n|Python compat| |PyPi| |GHA tests| |Codecov report| |readthedocs|\n\n.. inclusion-marker-do-not-remove\n\nAutoRegistry\n============\n\nInvoking functions and class-constructors from a string is a common design pattern\nthat AutoRegistry aims to solve.\nFor example, a user might specify a backend of type ``"sqlite"`` in a yaml configuration\nfile, for which our program needs to construct the ``SQLite`` subclass of our ``Database`` class.\nClassically, you would need to manually create a lookup, mapping the string ``"sqlite"`` to\nthe ``SQLite`` constructor.\nWith AutoRegistry, the lookup is automatically created for you.\n\n\nAutoRegistry has a single  powerful class ``Registry`` that can do the following:\n\n* Be inherited to automatically register subclasses by their name.\n\n* Be directly invoked ``my_registery = Registry()`` to create a decorator\n  for registering callables like functions.\n\n* Traverse and automatically create registries for other python libraries.\n\n.. inclusion-marker-remove\n\nInstallation\n============\nAutoRegistry requires Python ``>=3.8``.\n\n.. code-block:: bash\n\n   python -m pip install autoregistry\n\n\nExamples\n========\n\nClass Inheritance\n^^^^^^^^^^^^^^^^^\n\n``Registry`` adds a dictionary-like interface to class constructors\nfor looking up subclasses.\n\n.. code-block:: python\n\n   from dataclasses import dataclass\n   from autoregistry import Registry, abstractmethod\n\n\n   @dataclass\n   class Pokemon(Registry):\n       level: int\n       hp: int\n\n       @abstractmethod\n       def attack(self, target):\n           """Attack another Pokemon."""\n\n\n   class Charmander(Pokemon):\n       def attack(self, target):\n           return 1\n\n\n   class Pikachu(Pokemon):\n       def attack(self, target):\n           return 2\n\n\n   class SurfingPikachu(Pikachu):\n       def attack(self, target):\n           return 3\n\n\n   print(f"{len(Pokemon)} Pokemon registered:")\n   print(f"    {list(Pokemon)}")\n   # By default, lookup is case-insensitive\n   charmander = Pokemon["cHaRmAnDer"](level=7, hp=31)\n   print(f"Created Pokemon: {charmander}")\n\nThis code block produces the following output:\n\n.. code-block::\n\n   3 Pokemon registered:\n       [\'charmander\', \'pikachu\', \'surfingpikachu\']\n   Created Pokemon: Charmander(level=7, hp=31)\n\n\nFunction Registry\n^^^^^^^^^^^^^^^^^\n\nDirectly instantiating a ``Registry`` object allows you to\nregister functions by decorating them.\n\n.. code-block:: python\n\n   from autoregistry import Registry\n\n   pokeballs = Registry()\n\n\n   @pokeballs\n   def masterball(target):\n       return 1.0\n\n\n   @pokeballs\n   def pokeball(target):\n       return 0.1\n\n\n   for ball in ["pokeball", "masterball"]:\n       success_rate = pokeballs[ball](None)\n       print(f"Ash used {ball} and had {success_rate=}")\n\nThis code block produces the following output:\n\n.. code-block:: text\n\n   Ash used pokeball and had success_rate=0.1\n   Ash used masterball and had success_rate=1.0\n\n\nModule Registry\n^^^^^^^^^^^^^^^\n\nCreate a registry for another python module.\n\n.. code-block:: python\n\n   import torch\n   from autoregistry import Registry\n\n   optims = Registry(torch.optim)\n\n   # "adamw" and ``lr`` could be coming from a configuration file.\n   optimizer = optims["adamw"](model.parameterse(), lr=3e-3)\n\n   assert list(optims) == [\n       "asgd",\n       "adadelta",\n       "adagrad",\n       "adam",\n       "adamw",\n       "adamax",\n       "lbfgs",\n       "nadam",\n       "optimizer",\n       "radam",\n       "rmsprop",\n       "rprop",\n       "sgd",\n       "sparseadam",\n       "lr_scheduler",\n       "swa_utils",\n   ]\n\n\n.. |GHA tests| image:: https://github.com/BrianPugh/autoregistry/workflows/tests/badge.svg\n   :target: https://github.com/BrianPugh/autoregistry/actions?query=workflow%3Atests\n   :alt: GHA Status\n.. |Codecov report| image:: https://codecov.io/github/BrianPugh/autoregistry/coverage.svg?branch=main\n   :target: https://codecov.io/github/BrianPugh/autoregistry?branch=main\n   :alt: Coverage\n.. |readthedocs| image:: https://readthedocs.org/projects/autoregistry/badge/?version=latest\n        :target: https://autoregistry.readthedocs.io/en/latest/?badge=latest\n        :alt: Documentation Status\n.. |Python compat| image:: https://img.shields.io/badge/>=python-3.8-blue.svg\n.. |PyPi| image:: https://img.shields.io/pypi/v/autoregistry.svg\n        :target: https://pypi.python.org/pypi/autoregistry\n',
    'author': 'Brian Pugh',
    'author_email': 'None',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/BrianPugh/autoregistry',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
