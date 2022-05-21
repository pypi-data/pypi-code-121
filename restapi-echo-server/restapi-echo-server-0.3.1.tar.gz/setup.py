# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['restapi_echo_server']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'restapi-echo-server',
    'version': '0.3.1',
    'description': 'Simple REST-API echo server',
    'long_description': '# restapi-echo-server\nSimple REST-API echo server.\n\n```\npython -m restapi_echo_server --host 0.0.0.0 --port 8080\n```\n\n\n# Requirements\n- Python >= 3.8\n\n\n# Installation\n```\npip install restapi-echo-server\n```\n\n\n# License\nMIT\n',
    'author': 'dei',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/kthrdei/restapi-echo-server',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
