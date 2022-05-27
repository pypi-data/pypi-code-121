# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['hardwario', 'hardwario.cloud', 'hardwario.cloud.cli']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=5.1,<6.0',
 'click>=8.0.3,<9.0.0',
 'hardwario-common>=1.6.1,<2.0.0',
 'loguru>=0.6.0,<0.7.0',
 'python-dateutil>=2.8.2,<3.0.0',
 'requests>=2.27.1,<3.0.0']

setup_kwargs = {
    'name': 'hardwario-cloud',
    'version': '1.4.0',
    'description': 'HARDWARIO CLOUD',
    'long_description': '<a href="https://www.hardwario.com/"><img src="https://www.hardwario.com/ci/assets/hw-logo.svg" width="200" alt="HARDWARIO Logo" align="right"></a>\n\n# HARDWARIO CLOUD CLI Tools\n\n[![Main](https://github.com/hardwario/py-hardwario-cloud/actions/workflows/main.yaml/badge.svg)](https://github.com/hardwario/py-hardwario-cloud/actions/workflows/main.yaml)\n[![Release](https://img.shields.io/github/release/hardwario/py-hardwario-cloud.svg)](https://github.com/hardwario/py-hardwario-cloud/releases)\n[![PyPI](https://img.shields.io/pypi/v/hardwario-cloud.svg)](https://pypi.org/project/hardwario-cloud/)\n[![License](https://img.shields.io/github/license/hardwario/py-hardwario-cloud.svg)](https://github.com/hardwario/py-hardwario-cloud/blob/master/LICENSE)\n[![Twitter](https://img.shields.io/twitter/follow/hardwario_en.svg?style=social&label=Follow)](https://twitter.com/hardwario_en)\n\nThis repository contains Python package [hardwario-cloud](https://pypi.org/project/hardwario-cloud/)\n\n\n## License\n\nThis project is licensed under the [MIT License](https://opensource.org/licenses/MIT/) - see the [LICENSE](LICENSE) file for details.\n\n---\n\nMade with &#x2764;&nbsp; by [**HARDWARIO s.r.o.**](https://www.hardwario.com/) in the heart of Europe.\n',
    'author': 'Karel Blavka',
    'author_email': 'karel.blavka@hardwario.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/hardwario/py-hardwario-cloud',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6',
}


setup(**setup_kwargs)
