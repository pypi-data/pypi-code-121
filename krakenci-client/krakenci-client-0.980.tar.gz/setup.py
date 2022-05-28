# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['kraken', 'kraken.client']

package_data = \
{'': ['*']}

install_requires = \
['click>=7.1.2,<8.0.0', 'requests>=2.26.0,<3.0.0', 'tabulate>=0.8.9,<0.9.0']

entry_points = \
{'console_scripts': ['kkci = kraken.client.main:main']}

setup_kwargs = {
    'name': 'krakenci-client',
    'version': '0.980',
    'description': 'A client tool for Kraken CI server.',
    'long_description': '# Kraken CI Client\n\nThis is a client tool for accessing Kraken CI server, https://kraken.ci.\n\n\n<!-- ABOUT THE PROJECT -->\n## About Kraken CI\n\n![Kraken CI Results Page](https://kraken.ci/img/slide-branch-results.png)\n\nKraken CI is a modern, open-source, on-premise CI/CD system\nthat is highly scalable and focused on testing.\n\nMore information can be found on https://kraken.ci\n\n\n<!-- GETTING STARTED -->\n## Getting Started\n\nQuick start guide is here: https://kraken.ci/docs/quick-start\n\nFull installation manual: https://kraken.ci/docs/installation\n\nAnd here is developers guide: https://kraken.ci/docs/dev-guide\n\n\n<!-- USAGE EXAMPLES -->\n## Usage\n\nGuides can be found here: https://kraken.ci/docs/guide-intro\n\nDemo site is available here: https://lab.kraken.ci/\n\n\n<!-- ROADMAP -->\n## Roadmap\n\nSee the [open issues](https://github.com/kraken-ci/kraken/issues) for a list of proposed features (and known issues).\n\n\n<!-- CONTRIBUTING -->\n## Contributing\n\nContributions are what make the open source community such an amazing place to be learn, inspire, and create. Any contributions you make are **greatly appreciated**.\n\nDetails on https://kraken.ci/docs/contrib-kraken\n\n\n<!-- LICENSE -->\n## License\n\nDistributed under the Apache 2.0 License. See `LICENSE` for more information.\n\n\n<!-- CONTACT -->\n## Contact\n\nMichal Nowikowski - godfryd@gmail.com\n\nProject Link: [https://kraken.ci](https://kraken.ci)\n',
    'author': 'Michal Nowikowski',
    'author_email': 'godfryd@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://kraken.ci/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
