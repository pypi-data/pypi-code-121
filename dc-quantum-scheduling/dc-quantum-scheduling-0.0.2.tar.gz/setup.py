# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dc_quantum_scheduling', 'dc_quantum_scheduling.qiskit']

package_data = \
{'': ['*']}

install_requires = \
['pytz', 'qiskit', 'requests', 'retry']

setup_kwargs = {
    'name': 'dc-quantum-scheduling',
    'version': '0.0.2',
    'description': '',
    'long_description': '# Scheduling Framework \n\nThis can be used for more elaborate set of experiments, in particular for hybrid classical-quantum approaches.\n\nMore to come.',
    'author': 'Carsten BLank',
    'author_email': 'blank@data-cybernetics.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/carstenblank/dc-quantum-scheduling',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4',
}


setup(**setup_kwargs)
