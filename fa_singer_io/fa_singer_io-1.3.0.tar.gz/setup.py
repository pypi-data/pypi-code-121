# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fa_singer_io',
 'fa_singer_io.json_schema',
 'fa_singer_io.singer',
 'fa_singer_io.singer.record',
 'fa_singer_io.singer.schema',
 'fa_singer_io.singer.state']

package_data = \
{'': ['*']}

install_requires = \
['Deprecated>=1.2.12,<2.0.0',
 'fa-purity>=1.8.0,<2.0.0',
 'jsonschema>=3.2.0,<4.0.0',
 'pyRFC3339>=1.1,<2.0',
 'pytz>=2021.1,<2022.0']

setup_kwargs = {
    'name': 'fa-singer-io',
    'version': '1.3.0',
    'description': 'Singer io SDK with strict types',
    'long_description': None,
    'author': 'Product Team',
    'author_email': 'development@fluidattacks.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
