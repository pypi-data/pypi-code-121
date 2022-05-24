# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['bowyer',
 'bowyer._meta',
 'bowyer.cfg',
 'bowyer.cfg._meta',
 'bowyer.cfg.data',
 'bowyer.cfg.data._meta',
 'bowyer.cli',
 'bowyer.exception',
 'bowyer.exception._meta',
 'bowyer.gen',
 'bowyer.gen._meta',
 'bowyer.host',
 'bowyer.host._meta',
 'bowyer.log',
 'bowyer.node._meta',
 'bowyer.proc',
 'bowyer.proc._meta',
 'bowyer.queue',
 'bowyer.queue._meta',
 'bowyer.signal',
 'bowyer.signal._meta',
 'bowyer.sys',
 'bowyer.sys._meta',
 'bowyer.test',
 'bowyer.util',
 'bowyer.util._meta']

package_data = \
{'': ['*'],
 'bowyer': ['lib/test/native/native_controller.pyx',
            'lib/test/native/native_controller.pyx',
            'lib/test/native/native_printer.pyx',
            'lib/test/native/native_printer.pyx',
            'node/*']}

install_requires = \
['Cython>=0.29.26,<0.30.0',
 'PyYAML>=6.0,<7.0',
 'click>=8.0.3,<9.0.0',
 'dill>=0.3.4,<0.4.0',
 'jsonschema>=4.4.0,<5.0.0',
 'loguru>=0.5.3,<0.6.0',
 'numpy>=1.22.1,<2.0.0',
 'zmq>=0.0.0,<0.0.1']

entry_points = \
{'console_scripts': ['bowyer = bowyer.cli.command:grp_main']}

setup_kwargs = {
    'name': 'bowyer',
    'version': '0.1.1',
    'description': 'Model based design for developers',
    'long_description': '======\nBowyer\n======\n\nA tool for making polyglot distributed dataflow process networks.',
    'author': 'William Payne',
    'author_email': 'wtpayne@gmail.com',
    'maintainer': 'William Payne',
    'maintainer_email': 'wtpayne@gmail.com',
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}
from build import *
build(setup_kwargs)

setup(**setup_kwargs)
