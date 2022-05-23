# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['lightkit',
 'lightkit.data',
 'lightkit.estimator',
 'lightkit.nn',
 'lightkit.utils']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.20.0,<2.0.0',
 'pytorch-lightning>=1.5.8,<2.0.0',
 'torch>=1.8.0,<2.0.0']

setup_kwargs = {
    'name': 'lightkit',
    'version': '0.4.4',
    'description': 'Utilities for PyTorch and PyTorch Lightning.',
    'long_description': "# LightKit\n\nLightKit provides simple utilities for working with PyTorch and PyTorch Lightning. At the moment,\nit provides three simple features:\n\n- A data loader for tabular data that is orders of magnitude faster than PyTorch's builtin data\n  loader for medium-sized datasets and larger ones.\n- A mixin for modules that allows to save not only weights, but also the configuration to the file\n  system such that it is easier to retrieve trained models.\n- A typed base class for estimators that enables users to easily create estimators with PyTorch and\n  PyTorch Lightning which are fully compatible with Scikit-learn.\n\nFor more details, consult the [documentation](https://lightkit.borchero.com).\n\n## Installation\n\nLightKit is available via `pip`:\n\n```bash\npip install lightkit\n```\n\nIf you are using [Poetry](https://python-poetry.org/):\n\n```bash\npoetry add lightkit\n```\n",
    'author': 'Oliver Borchert',
    'author_email': 'me@borchero.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/borchero/lightkit',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.10',
}


setup(**setup_kwargs)
