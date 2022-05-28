# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['ramka',
 'ramka.middleware',
 'ramka.request',
 'ramka.response',
 'ramka.routing',
 'ramka.static',
 'ramka.templates',
 'ramka.test',
 'ramka.views']

package_data = \
{'': ['*']}

install_requires = \
['Jinja2>=3.1.2,<4.0.0',
 'WebOb>=1.8.7,<2.0.0',
 'gunicorn>=20.1.0,<21.0.0',
 'parse>=1.19.0,<2.0.0',
 'requests>=2.27.1,<3.0.0',
 'whitenoise>=6.0.0,<7.0.0']

setup_kwargs = {
    'name': 'ramka',
    'version': '0.1.1',
    'description': 'ramka - a simple Python web framework',
    'long_description': '# ramka\n\n[![Tests](https://github.com/mateuszcisek/ramka/actions/workflows/tests.yaml/badge.svg)](https://github.com/mateuszcisek/ramka/actions/workflows/tests.yaml)\n[![Linting](https://github.com/mateuszcisek/ramka/actions/workflows/linting.yaml/badge.svg)](https://github.com/mateuszcisek/ramka/actions/workflows/linting.yaml)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)\n[![linting: pylint](https://img.shields.io/badge/linting-pylint-yellowgreen)](https://github.com/PyCQA/pylint)\n\n\nramka is a very small web framework written in Python.\n\n## Documentation\n\nComing soon :)\n\n## Installation\n\nComing soon :)\n\n## License\n\nMIT\n',
    'author': 'Mateusz Cisek',
    'author_email': 'cismat@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/mateuszcisek/ramka',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
