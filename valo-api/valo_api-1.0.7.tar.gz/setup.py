# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['valo_api',
 'valo_api.endpoints',
 'valo_api.exceptions',
 'valo_api.responses',
 'valo_api.utils']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['valo_api = valo_api.__main__:app']}

setup_kwargs = {
    'name': 'valo-api',
    'version': '1.0.7',
    'description': 'Valorant API Wrapper for https://github.com/Henrik-3/unofficial-valorant-api',
    'long_description': '# valo_api\n\n<div align="center">\n\n[![Build status](https://github.com/raimannma/ValorantAPI/workflows/build/badge.svg?branch=master&event=push)](https://github.com/raimannma/ValorantAPI/actions?query=workflow%3Abuild)\n[![Python Version](https://img.shields.io/pypi/pyversions/valo_api.svg)](https://pypi.org/project/valo_api/)\n[![Dependencies Status](https://img.shields.io/badge/dependencies-up%20to%20date-brightgreen.svg)](https://github.com/raimannma/ValorantAPI/pulls?utf8=%E2%9C%93&q=is%3Apr%20author%3Aapp%2Fdependabot)\n\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![Security: bandit](https://img.shields.io/badge/security-bandit-green.svg)](https://github.com/PyCQA/bandit)\n[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/raimannma/ValorantAPI/blob/master/.pre-commit-config.yaml)\n[![Semantic Versions](https://img.shields.io/badge/%20%20%F0%9F%93%A6%F0%9F%9A%80-semantic--versions-e10079.svg)](https://github.com/raimannma/ValorantAPI/releases)\n[![License](https://img.shields.io/github/license/raimannma/ValorantAPI)](https://github.com/raimannma/ValorantAPI/blob/master/LICENSE)\n[![Codacy Badge](https://app.codacy.com/project/badge/Grade/3b23d2a3b1694356bc95255a2edb83e6)](https://www.codacy.com/gh/raimannma/ValorantAPI/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=raimannma/ValorantAPI&amp;utm_campaign=Badge_Grade)\n[![Codacy Badge](https://app.codacy.com/project/badge/Coverage/3b23d2a3b1694356bc95255a2edb83e6)](https://www.codacy.com/gh/raimannma/ValorantAPI/dashboard?utm_source=github.com&utm_medium=referral&utm_content=raimannma/ValorantAPI&utm_campaign=Badge_Coverage)\n[![Downloads](https://pepy.tech/badge/valo-api)](https://pepy.tech/project/valo-api)\n\nValorant API Wrapper for https://github.com/Henrik-3/unofficial-valorant-api\n\n</div>\n\n## Installation\n\n    pip install valo-api\n\n## Documentation\n\nAfter installing the package dependencies `pip install -r requirements.txt`, you can use the following commands to get the documentation:\n\n    cd docs/ && make html\n\nOpen the index.html file in the docs/_build/html/ directory.\n',
    'author': 'Manuel Raimann',
    'author_email': 'raimannma@outlook.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/raimannma/ValorantAPI',
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
