# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['residuated_binars']

package_data = \
{'': ['*'], 'residuated_binars': ['resources/*']}

install_requires = \
['graphviz', 'isabelle-client']

setup_kwargs = {
    'name': 'residuated-binars',
    'version': '0.0.1',
    'description': 'Package for generating and validating examples of different algebraic structures using Isabelle proof assistant',
    'long_description': '..\n  Copyright 2021-2022 Boris Shminke\n\n  Licensed under the Apache License, Version 2.0 (the "License");\n  you may not use this file except in compliance with the License.\n  You may obtain a copy of the License at\n\n      https://www.apache.org/licenses/LICENSE-2.0\n\n  Unless required by applicable law or agreed to in writing, software\n  distributed under the License is distributed on an "AS IS" BASIS,\n  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.\n  See the License for the specific language governing permissions and\n  limitations under the License.\n\n|Binder|\\ |PyPI version|\\ |CircleCI|\\ |codecov|\\ |RTFD|\n\nGenerating Algebraic Structures with Isabelle\n==============================================\n\n.. attention::\n   If you\'re looking for a reproducible example for AITP 2021 paper, find it `here <https://residuated-binars.readthedocs.io/en/latest/aitp2021.html>`__.\n\nThis package serves for generating and validating examples of different algebraic structures using `Isabelle proof assistant <https://isabelle.in.tum.de>`__.\n\n.. _how-to-install:\n\nDependencies\n=============\nMake sure that an installation of Isabelle is on the ``$PATH``\n\nHow to Install\n===============\n\nThe best way to install ``residuated-binars`` is to use ``pip``::\n  \n    pip install residuated-binars\n     \nAlternatively, one can use Docker:\n\n.. code:: sh\n\n      docker build -t residuated-binars https://github.com/inpefess/residuated-binars.git\n      docker run -it --rm -p 8888:8888 residuated-binars jupyter-lab --ip=0.0.0.0 --port=8888 --no-browser\n\nFinally, one can run it on\n`Binder <https://mybinder.org/v2/gh/inpefess/residuated-binars/HEAD?labpath=reproducing-residuated-binars-papers.ipynb>`__\n\n\nHow to Use\n===========\n\nSee ``examples/residuated-binars-example.ipynb``.\n\n.. |CircleCI| image:: https://circleci.com/gh/inpefess/residuated-binars.svg?style=svg\n   :target: https://circleci.com/gh/inpefess/residuated-binars\n.. |codecov| image:: https://codecov.io/gh/inpefess/residuated-binars/branch/master/graph/badge.svg\n   :target: https://codecov.io/gh/inpefess/residuated-binars\n.. |RTFD| image:: https://readthedocs.org/projects/residuated-binars/badge/?version=latest\n   :target: https://residuated-binars.readthedocs.io/en/latest/?badge=latest\n   :alt: Documentation Status\n.. |Binder| image:: https://mybinder.org/badge_logo.svg\n   :target: https://mybinder.org/v2/gh/inpefess/residuated-binars/HEAD?labpath=reproducing-residuated-binars-papers.ipynb\n.. |PyPI version| image:: https://badge.fury.io/py/residuated-binars.svg\n   :target: https://badge.fury.io/py/residuated-binars\n',
    'author': 'Boris Shminke',
    'author_email': 'boris@shminke.ml',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/inpefess/residuated-binars',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.1,<3.11',
}


setup(**setup_kwargs)
