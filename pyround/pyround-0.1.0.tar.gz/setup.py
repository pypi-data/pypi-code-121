# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['pyround']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'pyround',
    'version': '0.1.0',
    'description': 'PYPI package with only 1 function to round float numbers to the number of significant digits',
    'long_description': '==============================\npyround\n==============================\n\n.. image:: https://img.shields.io/github/last-commit/stas-prokopiev/pyround\n   :target: https://img.shields.io/github/last-commit/stas-prokopiev/pyround\n   :alt: GitHub last commit\n\n.. image:: https://img.shields.io/github/license/stas-prokopiev/pyround\n    :target: https://github.com/stas-prokopiev/pyround/blob/master/LICENSE.txt\n    :alt: GitHub license<space><space>\n\n.. image:: https://img.shields.io/pypi/v/pyround\n   :target: https://img.shields.io/pypi/v/pyround\n   :alt: PyPI\n\n.. image:: https://img.shields.io/pypi/pyversions/pyround\n   :target: https://img.shields.io/pypi/pyversions/pyround\n   :alt: PyPI - Python Version\n\n\n.. contents:: **Table of Contents**\n\nOverview.\n=========================\npyround is a one function PYPI package made only with one\ngoal to round float numbers in python to asked number of signifacant digits\n\n\n.. code-block:: python\n\n    import pyround\n\n    pyround.pyround(0.23234, 2)  # 0.23\n    pyround.pyround(0.235, 2)  # 0.24\n    pyround.pyround(105.3, 1)  # 100\n    pyround.pyround(125.3, 2)  # 130\n\nInstallation via pip:\n======================\n\n.. code-block:: bash\n\n    pip install pyround\n\nLinks\n=====\n\n    * `PYPI <https://pypi.org/project/pyround/>`_\n    * `GitHub <https://github.com/stas-prokopiev/pyround>`_\n\nContacts\n========\n\n    * Email: stas.prokopiev@gmail.com\n    * `vk.com <https://vk.com/stas.prokopyev>`_\n    * `Facebook <https://www.facebook.com/profile.php?id=100009380530321>`_\n\nLicense\n=======\n\nThis project is licensed under the MIT License.\n',
    'author': 'stanislav',
    'author_email': 'stas.prokopiev@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6',
}


setup(**setup_kwargs)
