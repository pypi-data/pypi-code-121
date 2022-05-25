# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['irdata']

package_data = \
{'': ['*']}

install_requires = \
['defusedxml>=0.7.1,<0.8.0']

setup_kwargs = {
    'name': 'irdata',
    'version': '0.2.5',
    'description': 'Data processing library for iRefIndex',
    'long_description': '# irdata\n\nA data processing library for [iRefIndex](https://github.com/abotzki/irefindex).\nThe source code is originally by @iandonaldson. It copied/extracted from [here](https://github.com/iandonaldson/irefindex/tree/master/irdata).\n',
    'author': 'VIB Bioinformatics Core Facility',
    'author_email': 'bits@vib.be',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/vibbits/irdata',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
