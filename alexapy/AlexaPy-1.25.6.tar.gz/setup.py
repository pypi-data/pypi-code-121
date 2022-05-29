# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['alexapy', 'alexapy.aiohttp']

package_data = \
{'': ['*']}

install_requires = \
['aiofiles>=0,<1',
 'authcaptureproxy>=1,<2',
 'backoff>=1.10',
 'beautifulsoup4',
 'certifi',
 'cryptography>=35.0',
 'pyotp>=2.4',
 'requests',
 'simplejson',
 'yarl']

setup_kwargs = {
    'name': 'alexapy',
    'version': '1.25.6',
    'description': 'Python API to control Amazon Echo Devices Programmatically.',
    'long_description': '# alexapy\n\n[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)\n[![Python version compatibility](https://img.shields.io/pypi/pyversions/alexapy)](https://pypi.org/project/alexapy)\n[![Version on PyPi](https://img.shields.io/pypi/v/alexapy)](https://pypi.org/project/alexapy)\n[![pipeline status](https://gitlab.com/keatontaylor/alexapy/badges/master/pipeline.svg)](https://gitlab.com/keatontaylor/alexapy/commits/master)\n![PyPI - Downloads](https://img.shields.io/pypi/dd/alexapy)\n![PyPI - Downloads](https://img.shields.io/pypi/dw/alexapy)\n![PyPI - Downloads](https://img.shields.io/pypi/dm/alexapy)\n\nPython Package for controlling Alexa devices (echo dot, etc) programmatically. This was originally designed for [alexa_media_player](https://github.com/custom-components/alexa_media_player) a custom_component for [Home Assistant](https://www.home-assistant.io/).\n\n**NOTE:** Alexa has no official API; therefore, this library may stop\nworking at any time without warning.\n\n# Credits\nOriginally inspired by [this blog](https://blog.loetzimmer.de/2017/10/amazon-alexa-hort-auf-die-shell-echo.html) [(GitHub)](https://github.com/thorsten-gehrig/alexa-remote-control).\nAdditional scaffolding from [simplisafe-python](https://github.com/bachya/simplisafe-python)\n\n# Contributing\n\n1.  [Check for open features/bugs](https://gitlab.com/keatontaylor/alexapy/issues)\n  or [initiate a discussion on one](https://gitlab.com/keatontaylor/alexapy/issues/new).\n2.  [Fork the repository](https://gitlab.com/keatontaylor/alexapy/forks/new).\n3.  Install the dev environment: `make init`.\n4.  Enter the virtual environment: `pipenv shell`\n5.  Code your new feature or bug fix.\n6.  Write a test that covers your new functionality.\n7.  Update `README.md` with any new documentation.\n8.  Run tests and ensure 100% code coverage for your contribution: `make coverage`\n9.  Ensure you have no linting errors: `make lint`\n10. Ensure you have typed your code correctly: `make typing`\n11. Add yourself to `AUTHORS.md`.\n12. Submit a pull request!\n\n# License\n[Apache-2.0](LICENSE). By providing a contribution, you agree the contribution is licensed under Apache-2.0.\n\n# API Reference\n[See the docs 📚](https://alexapy.readthedocs.io/en/latest/index.html).\n',
    'author': 'Keaton Taylor',
    'author_email': 'keatonstaylor@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/keatontaylor/alexapy',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
