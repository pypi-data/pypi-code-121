# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['friktionless']

package_data = \
{'': ['*']}

install_requires = \
['altair-saver>=0.5.0,<0.6.0',
 'altair>=4.2.0,<5.0.0',
 'google-cloud-bigquery>=3.1.0,<4.0.0',
 'google-cloud-storage>=2.3.0,<3.0.0',
 'pandas-gbq>=0.17.5,<0.18.0',
 'pandas>=1.4.2,<2.0.0',
 'selenium>=4.1.5,<5.0.0']

setup_kwargs = {
    'name': 'friktionless',
    'version': '0.0.2',
    'description': 'Friktionless is a Python package providing simplified interfaces to Friktion data. It aims to be the fundamental building block for doing data engineering and data analysis in Python for Friktion. Additionally, it has the broader goal of becoming **the most powerful and flexible open.',
    'long_description': "# friktionless: a powerful Friktion data analysis library for Python\n\n## What is it?\n\n**friktionless** is a Python package providing simplified interfaces to \nFriktion data. It aims to be the fundamental building block for doing \ndata engineering and data analysis in Python for Friktion. Additionally, \nit has the broader goal of becoming **the most powerful and flexible open \nsource data analysis / manipulation tool available for any protocol**.\n\n## Main Features\nHere are just a few of the things that friktionless does (or will do) well:\n  - Easy engineering of meaningful performance data about Friktion to enrich\n    an analytical data warehouse.\n  - Easy dashboarding and portal management for Friktion to manage the \n    growing body of analytics reporting and stakeholder needs.\n  - Intuitive python first apis under the hood on everything - we're building \n    on top of pandas, altair, seaborn, and other popular python tools so the \n    community is enabled.\n  - a Python and CLI api to enable data scientists and data engineers off the \n    same, singular codebase.\n\n## Where to get it\nThe source code is currently hosted on GitHub at:\nhttps://github.com/Friktion-Labs/friktionless\n\nBinary installers for the latest released version are available at the [Python\nPackage Index (PyPI)](https://pypi.org/project/friktionless)\n\n```sh\n#PyPI\npip install friktionless\n```\n\n# License\nTBA\n\n# Documentation\nTBA\n\n# Background\nWork on ``friktionless`` began as an abstraction designed by a few early DAO contributors and was quickly adopted by the core team as a mechanism to power up the team and enable the community greater ownership of their Friktion data.",
    'author': 'Friktion core team',
    'author_email': 'team@friktionlabs.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Friktion-Labs/friktionless',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.10',
}


setup(**setup_kwargs)
