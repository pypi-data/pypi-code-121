# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['arguebuf', 'arguebuf.models', 'arguebuf.schema', 'arguebuf.services']

package_data = \
{'': ['*']}

install_requires = \
['arg-services>=0.3.6,<0.4.0',
 'graphviz>=0.20,<0.21',
 'lxml>=4.8.0,<5.0.0',
 'networkx>=2.8,<3.0',
 'pendulum>=2.1.2,<3.0.0']

extras_require = \
{'docs': ['sphinx>=4.5.0,<5.0.0',
          'furo>=2022.4.7,<2023.0.0',
          'myst-parser>=0.17.2,<0.18.0',
          'sphinx-autoapi>=1.8.4,<2.0.0',
          'autodocsumm>=0.2.8,<0.3.0']}

setup_kwargs = {
    'name': 'arguebuf',
    'version': '0.3.0',
    'description': 'A library for loading argument graphs in various formats (e.g., AIF).',
    'long_description': '# Arguebuf\n\n- [Documentation](https://arguebuf.readthedocs.io/en/latest/)\n- [PyPI](https://pypi.org/project/arguebuf/)\n',
    'author': 'Mirko Lenz',
    'author_email': 'info@mirko-lenz.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://recap.uni-trier.de',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
