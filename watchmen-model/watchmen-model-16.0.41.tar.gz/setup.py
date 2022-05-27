# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['watchmen_model',
 'watchmen_model.admin',
 'watchmen_model.analysis',
 'watchmen_model.chart',
 'watchmen_model.common',
 'watchmen_model.console',
 'watchmen_model.dqc',
 'watchmen_model.gui',
 'watchmen_model.indicator',
 'watchmen_model.pipeline_kernel',
 'watchmen_model.system']

package_data = \
{'': ['*']}

install_requires = \
['pydantic>=1.9.0,<2.0.0', 'watchmen-utilities==16.0.41']

setup_kwargs = {
    'name': 'watchmen-model',
    'version': '16.0.41',
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
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
