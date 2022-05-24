# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['faser',
 'faser.generators',
 'faser.generators.scalar',
 'faser.generators.scalar.gibson_lanny',
 'faser.generators.scalar.phasenet',
 'faser.generators.vectorial.stephane',
 'faser.napari',
 'faser.retrievers']

package_data = \
{'': ['*'], 'faser.generators': ['vectorial/*']}

install_requires = \
['magicgui>=0.4.0,<0.5.0',
 'napari-plugin_engine>=0.1.4,<0.2.0',
 'numpy>=1.22.4,<2.0.0',
 'pydantic>=1.9.1,<2.0.0']

entry_points = \
{'console_scripts': ['faser = faser.napari.main:main'],
 'napari.manifest': ['faser = faser:napari.yaml'],
 'napari.plugin': ['faser = faser.napari.plugin']}

setup_kwargs = {
    'name': 'faser',
    'version': '0.2.3',
    'description': '',
    'long_description': None,
    'author': 'jhnnsrs',
    'author_email': 'jhnnsrs@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
