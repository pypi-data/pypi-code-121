# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['cz_emoji']
install_requires = \
['commitizen>=2.27.0,<3.0.0', 'emoji>=1.7.0,<2.0.0']

setup_kwargs = {
    'name': 'cz-emoji',
    'version': '0.2.0',
    'description': 'A `commitizen` plugin like `commitizen-emoji`, but more consistent with the [Conventional Commit](https://www.conventionalcommits.org/en/v1.0.0/) spec and addition of custom emojis in messages.',
    'long_description': '# cz-emoji\nA `commitizen` plugin like `commitizen-emoji`, but more consistent with the [Conventional Commit](https://www.conventionalcommits.org/en/v1.0.0/) spec and addition of custom emojis in messages.\n',
    'author': 'Hendry, Adam',
    'author_email': 'adam.hendry@medtronic.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/adam-grant-hendry/cz-emoji',
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
