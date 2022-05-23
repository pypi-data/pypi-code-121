# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mognet',
 'mognet.app',
 'mognet.backend',
 'mognet.broker',
 'mognet.cli',
 'mognet.context',
 'mognet.decorators',
 'mognet.exceptions',
 'mognet.middleware',
 'mognet.model',
 'mognet.primitives',
 'mognet.service',
 'mognet.state',
 'mognet.tasks',
 'mognet.testing',
 'mognet.tools',
 'mognet.tools.backports',
 'mognet.worker']

package_data = \
{'': ['*']}

install_requires = \
['aio-pika>=6.8.0,<7.0.0',
 'aiorun>=2021.10.1,<2022.0.0',
 'pydantic>=1.8.0,<2.0.0',
 'redis[hiredis]>=4.2.2,<5.0.0',
 'tabulate>=0.8.0,<0.9.0',
 'treelib>=1.6.0,<2.0.0',
 'typer>=0.4.0,<0.5.0']

extras_require = \
{':python_version < "3.10"': ['typing-extensions>=3.10.0.0']}

entry_points = \
{'console_scripts': ['mognet = mognet.cli.main:main']}

setup_kwargs = {
    'name': 'mognet',
    'version': '1.4.0',
    'description': 'Mognet is a fast, simple framework to build distributed applications using task queues.',
    'long_description': '# Mognet\n\nMognet is a fast, simple framework to build distributed applications using task queues.\n\n## Installing\n\nMognet can be installed via pip, with:\n\n```\npip install mognet\n```\n\n## Getting Started and Documentation\n\nWe recommend having a look at the [Documentation](https://ds4sd.github.io/project-mognet/).\n\n## Contributing\n\nPlease read [Contributing to Mognet](./CONTRIBUTING.md) for details.\n\n\n## References\n\nIf you use `Mognet` in your projects, please consider citing the following:\n\n```bib\n@software{Project Mognet,\nauthor = {DeepSearch Team},\nmonth = {4},\ntitle = {{Project Mognet}},\nurl = {https://github.com/DS4SD/project-mognet},\nversion = {main},\nyear = {2022}\n}\n```\n\n## License\n\nThe `Mognet` codebase is under MIT license.\nFor individual model usage, please refer to the model licenses found in the original packages.\n',
    'author': 'André Carvalho',
    'author_email': 'afecarvalho@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://ds4sd.github.io/project-mognet/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
