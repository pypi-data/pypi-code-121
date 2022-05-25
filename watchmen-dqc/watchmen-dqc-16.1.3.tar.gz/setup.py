# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['watchmen_dqc',
 'watchmen_dqc.boot',
 'watchmen_dqc.common',
 'watchmen_dqc.monitor',
 'watchmen_dqc.monitor.rule',
 'watchmen_dqc.topic_profile',
 'watchmen_dqc.util']

package_data = \
{'': ['*']}

install_requires = \
['APScheduler>=3.9.1,<4.0.0',
 'pandas-profiling>=3.1.0,<4.0.0',
 'pandas>=1.4.2,<2.0.0',
 'watchmen-data-kernel==16.1.3',
 'watchmen-meta==16.1.3',
 'watchmen-pipeline-kernel==16.1.3']

extras_require = \
{'mongodb': ['watchmen-storage-mongodb==16.1.3'],
 'mssql': ['watchmen-storage-mssql==16.1.3'],
 'mysql': ['watchmen-storage-mysql==16.1.3'],
 'oracle': ['watchmen-storage-oracle==16.1.3'],
 'postgresql': ['watchmen-storage-postgresql==16.1.3']}

setup_kwargs = {
    'name': 'watchmen-dqc',
    'version': '16.1.3',
    'description': '',
    'long_description': None,
    'author': 'botlikes',
    'author_email': '75356972+botlikes456@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
