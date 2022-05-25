# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['unbelipy']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.7.4.post0,<4.0.0', 'aiolimiter>=1.0.0b1,<2.0.0']

extras_require = \
{'docs': ['sphinx>=4.0.0,<5.0.0', 'sphinx-book-theme>=0.3.2,<0.4.0']}

setup_kwargs = {
    'name': 'unbelipy',
    'version': '2.0.0b0',
    'description': "Asynchronous wrapper for UnbelievaBoat's API written in Python.",
    'long_description': "# unbelipy\n\n[![forthebadge made-with-python](http://ForTheBadge.com/images/badges/made-with-python.svg)](https://www.python.org/)\n\n[![PyPI status](https://img.shields.io/pypi/status/unbelipy.svg)](https://pypi.python.org/pypi/unbelipy/)\n[![PyPI version fury.io](https://badge.fury.io/py/unbelipy.svg)](https://pypi.python.org/pypi/unbelipy/)\n[![PyPI downloads](https://img.shields.io/pypi/dm/unbelipy.svg)](https://pypi.python.org/pypi/unbelipy/)\n[![PyPI license](https://img.shields.io/pypi/l/unbelipy.svg)](https://pypi.python.org/pypi/unbelipy/)\n\nAsynchronous wrapper for UnbelievaBoat's API written in Python.\n\n## Characteristics\n- Easy to use\n- Full error handling\n- Type hinted readable code\n- Active maintenance\n- Fully Asynchronous\n\n## Note\nThis wrapper has not been declared to be official by the UnbelievaBoat developers. Any internal library issues/feature requests are to be directed here.\n\n## Project status\nEarly beta stage. It's not yet production ready.  \nAlthough most of the functionality is operational, rate limits are still being worked on.  \n\n## Installation\n**Python 3.8 or above required, due to typehinting.**\n\nTo install unbelipy from PyPI, use the following command:  \n```py\npip install -U unbelipy\n```\n\nOr to install from Github:  \n```py\npip install -U git+https://github.com/chrisdewa/unbelipy/\n```\n\n## Dependencies\nThe following libraries will be needed and automatically installed with unbelipy:  \n- [aiohttp](https://github.com/aio-libs/aiohttp/) - async requests\n- [aiolimiter](https://github.com/mjpieters/aiolimiter/) - implementation of async rate limiter\n\n## Feature Requests\nFor feature requests, please [open a Pull Request](https://github.com/chrisdewa/unbelipy/pulls) with detailed instructions.  \nLikewise, if you encounter any issues, you may [create a new Issue](https://github.com/chrisdewa/unbelipy/issues).\n\n## Examples\nTo start off, you may [check out some examples](https://github.com/chrisdewa/unbelipy/tree/master/examples) in this repository!\n\n## Links\n- [Documentation](https://unbelipy.readthedocs.io/en/latest/)\n\n## Contact\nAs of now, there is no support server for this library.\nHowever, you may contact the following people on Discord:\n- [ChrisDewa#4552](https://discord.com/users/365957462333063170)\n- [invalid-user#1119](https://discord.com/users/714731543309844561)\n\n<!-- # Known Issues:\n- `'-Infinity'` is accepted by the API as a parameter for cash or bank (edit_balance and set_balance),\n  but it does not appear to affect the balance. This is caused because the API receives -Infinity as null which is also \n  used when the value didn't change. At the moment there is no word this is going to be fixed.\n  \n------- maybe make a file in /docs for known issues -->",
    'author': 'chrisdewa',
    'author_email': 'alexdewa@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/chrisdewa/unbelipy',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
