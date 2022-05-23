# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['pls',
 'pls.config',
 'pls.data',
 'pls.enums',
 'pls.fs',
 'pls.globals',
 'pls.log',
 'pls.models',
 'pls.models.mixins',
 'pls.output',
 'pls.output.columns',
 'pls.parser',
 'pls.parser.args',
 'pls.utils']

package_data = \
{'': ['*'], 'pls.data': ['schema/*']}

install_requires = \
['PyYAML>=6.0,<7.0', 'rich>=12.4.3,<13.0.0']

entry_points = \
{'console_scripts': ['pls = pls.main:main', 'pls-dev = pls.main:dev']}

setup_kwargs = {
    'name': 'pls',
    'version': '5.0.0',
    'description': '`pls` is a prettier and powerful `ls` for the pros.',
    'long_description': '<h1 align="center">\n  <img height="128px" src="https://raw.githubusercontent.com/dhruvkb/pls/main/readme_assets/pls.svg"/>\n\n  <p align="center">\n    <a href="https://www.python.org">\n      <img src="https://img.shields.io/pypi/pyversions/pls" alt="Python versions"/>\n    </a>\n    <a href="https://github.com/dhruvkb/pls/blob/main/LICENSE">\n      <img src="https://img.shields.io/github/license/dhruvkb/pls" alt="GPL-3.0"/>\n    </a>\n    <a href="https://pypi.org/project/pls/">\n      <img src="https://img.shields.io/static/v1?label=supported%20OS&message=posix,%20win&color=informational" alt="Platforms"/>\n    </a>\n    <a href="https://github.com/dhruvkb/pls/actions/workflows/ci.yml">\n      <img src="https://github.com/dhruvkb/pls/actions/workflows/ci.yml/badge.svg" alt="CI status"/>\n    </a>\n  </p>\n</h1>\n\n<p align="center">\n  <strong>Links:</strong>\n</p>\n<p align="center">\n  <a href="https://pypi.org/project/pls/">\n    <img src="https://img.shields.io/pypi/v/pls" alt="pls on PyPI"/>\n  </a>\n  <a href="https://dhruvkb.github.io/pls/">\n    <img src="https://img.shields.io/static/v1?label=docs&message=dhruvkb/pls:docs&color=informational" alt="Docs"/>\n  </a>\n</p>\n\n<p align="center">\n  <img src="https://raw.githubusercontent.com/dhruvkb/pls/main/readme_assets/demo.png" alt="Demo of `pls`"/>\n  <img src="https://raw.githubusercontent.com/dhruvkb/pls/main/readme_assets/help.png" alt="Help of `pls`"/>\n</p>\n\n`pls` is a prettier and powerful `ls` for the pros.\n\nThe "p" stands for\n- pretty (the output from `pls` surely looks better)\n- powerful (`pls` has lots of features and endless customisation)\n- programmer (`pls` is geared towards developers)\n- professional (`pls` can be extensively tweaked by the pros)\n- Python (`pls` is written in Python!)\n\nJust pick whichever helps you remember the command name.\n\nIt works in a manner similar to `ls`, in  that it lists directories and files in\na given directory, but it adds many more\n[developer-friendly features](https://dhruvkb.github.io/pls/features).\n\n> ⚠️ Note that `pls` is not a replacement for `ls`. `ls` is a tried, tested and\ntrusted command with lots of features. `pls`, on the other hand, is a simple\ntool for people who just want to see the contents of their directories.\n\n## Documentation\n\nWe have some very beautiful [documentation](https://dhruvkb.github.io/pls) over\non our GitHub pages site. These docs are built from the\n[`docs` branch](https://github.com/dhruvkb/pls/tree/docs) in the same\nrepository, and contributions to the docs are most welcome.\n\nThe docs contain information on almost everything, including but not limited to\nthe following:\n\n- [installation and updates](https://dhruvkb.github.io/pls/get_started/installation)\n- [features and CLI options](https://dhruvkb.github.io/pls/features)\n- [reference](https://dhruvkb.github.io/pls/reference)\n- [contribution](https://dhruvkb.github.io/pls/contribution)\n',
    'author': 'Dhruv Bhanushali',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://dhruvkb.github.io/pls',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
