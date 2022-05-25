# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pysaql']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'pysaql',
    'version': '0.11.0',
    'description': 'Python SAQL query builder',
    'long_description': '# pysaql\n[![](https://img.shields.io/pypi/v/pysaql.svg)](https://pypi.org/pypi/pysaql/) [![License](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)\n\nPython SAQL query builder\n\nFeatures:\n\n- <!-- list of features -->\n\nTable of Contents:\n\n- [Installation](#installation)\n- [Guide](#guide)\n- [Development](#development)\n\n## Installation\n\npysaql requires Python 3.9 or above.\n\n```bash\npip install pysaql\n# or\npoetry add pysaql\n```\n\n## Guide\n\n<!-- Subsections explaining how to use the package -->\n\n## Development\n\nTo develop pysaql, install dependencies and enable the pre-commit hook:\n\n```bash\npip install pre-commit poetry\npoetry install\npre-commit install -t pre-commit -t pre-push\n```\n\nTo run tests:\n\n```bash\npoetry run pytest\n```\n',
    'author': 'Jonathan Drake',
    'author_email': 'jon.drake@salesforce.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/NarrativeScience/pysaql',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
