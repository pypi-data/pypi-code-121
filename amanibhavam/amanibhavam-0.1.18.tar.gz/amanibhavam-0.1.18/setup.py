# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['amanibhavam']

package_data = \
{'': ['*']}

install_requires = \
['cdktf-cdktf-provider-aws>=7.0.55,<8.0.0',
 'cdktf-cdktf-provider-digitalocean>=0.0.40,<0.0.41',
 'cdktf-cdktf-provider-github>=0.7.62,<0.8.0',
 'cdktf-cdktf-provider-kubernetes>=0.7.63,<0.8.0',
 'cdktf-cdktf-provider-null>=0.6.55,<0.7.0',
 'cdktf-cdktf-provider-tfe>=0.2.58,<0.3.0',
 'cdktf>=0.10.4,<0.11.0',
 'defn-cdktf-provider-boundary>=0.4.0,<0.5.0',
 'defn-cdktf-provider-buildkite>=0.4.0,<0.5.0',
 'defn-cdktf-provider-cloudflare>=0.4.0,<0.5.0',
 'defn-cdktf-provider-vault>=0.4.0,<0.5.0']

entry_points = \
{'console_scripts': ['amanibhavam = config:main']}

setup_kwargs = {
    'name': 'amanibhavam',
    'version': '0.1.18',
    'description': '',
    'long_description': None,
    'author': 'Amanibhavam',
    'author_email': 'iam@defn.sh',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
