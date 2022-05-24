# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['primapy_hub']

package_data = \
{'': ['*']}

install_requires = \
['fastapi>=0.68.1,<0.69.0',
 'primapy-koffing[yaml]>=0.2.1,<0.3.0',
 'primapy-plogging>=0.2.0,<0.3.0',
 'primapy-tracing[fastapi,aiohttp]>=0.3.0,<0.4.0',
 'primapy>=0.9.3,<0.10.0',
 'uvicorn[standard]>=0.17.6,<0.18.0']

setup_kwargs = {
    'name': 'primapy-hub',
    'version': '0.1.0',
    'description': 'Ptyhon Knative based Hub library',
    'long_description': None,
    'author': 'Team AMOps',
    'author_email': 'amops@prima.it',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/primait/primapy-hub',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.9',
}


setup(**setup_kwargs)
