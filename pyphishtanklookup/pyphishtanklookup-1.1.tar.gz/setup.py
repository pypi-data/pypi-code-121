# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pyphishtanklookup']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.27.1,<3.0.0']

extras_require = \
{'docs': ['Sphinx>=4.5.0,<5.0.0']}

entry_points = \
{'console_scripts': ['phishtank-lookup = pyphishtanklookup:main']}

setup_kwargs = {
    'name': 'pyphishtanklookup',
    'version': '1.1',
    'description': 'Python CLI and module for PhishtankLookup',
    'long_description': '# PyPhishtank Lookup\n\nThis is the client API for [Phishtank Lookup](https://github.com/Lookyloo/phishtank-lookup),\nnot the official phishtank API.\n\n## Installation\n\n```bash\npip install pyphishtanklookup\n```\n\n## Usage\n\n### Command line\n\nYou can use the `phishtank-lookup` command to search in the database:\n\n```bash\nusage: phishtank-lookup [-h] [--url URL] (--info | --url_query url | --urls_by_cc cc | --urls_by_ip ip | --urls_by_asn asn)\n\nSearch a URL in Phishtank Lookup.\n\noptional arguments:\n  -h, --help         show this help message and exit\n  --url URL          URL of the instance (defaults to https://phishtankapi.circl.lu/).\n  --info             Info avout the instance.\n  --url_query url    URL to search.\n  --urls_by_cc cc    Country Code to search.\n  --urls_by_ip ip    IP address to search.\n  --urls_by_asn asn  ASN to search.\n```\n\n### Library\n\nSee [API Reference](https://pyphishtanklookup.readthedocs.io/en/latest/)\n',
    'author': 'Raphaël Vinot',
    'author_email': 'raphael.vinot@circl.lu',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/lookyloo/PyPhishtankLookup',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
