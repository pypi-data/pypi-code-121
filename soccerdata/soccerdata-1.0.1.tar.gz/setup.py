# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['soccerdata']

package_data = \
{'': ['*']}

install_requires = \
['PySocks>=1.7.1,<2.0.0',
 'Unidecode>=1.2.0,<2.0.0',
 'fake_useragent>=0.1.11,<0.2.0',
 'html5lib>=1.1,<2.0',
 'lxml>=4.6,<5.0',
 'pandas>=1.0,<2.0',
 'pretty-errors>=1.2.25,<2.0.0',
 'requests>=2.23,<3.0',
 'rich>=12.0.0,<13.0.0',
 'selenium>=4.0.0,<5.0.0',
 'undetected-chromedriver>=3.1.3,<4.0.0',
 'unicode>=2.7,<3.0']

setup_kwargs = {
    'name': 'soccerdata',
    'version': '1.0.1',
    'description': 'A collection of wrappers over soccer data from various websites / APIs.',
    'long_description': ".. image:: https://raw.githubusercontent.com/probberechts/soccerdata/master/docs/_static/logo2.png\n   :align: center\n   :alt: SoccerData\n   :width: 600px\n\n.. badges-begin\n\n|PyPI| |Python Version| |License| |Read the Docs| |Tests| |Codecov| |pre-commit| |Black|\n\n.. |PyPI| image:: https://img.shields.io/pypi/v/soccerdata.svg\n   :target: https://pypi.org/project/soccerdata/\n   :alt: PyPI\n.. |Python Version| image:: https://img.shields.io/pypi/pyversions/soccerdata\n   :target: https://pypi.org/project/soccerdata\n   :alt: Python Version\n.. |License| image:: https://img.shields.io/pypi/l/soccerdata.svg\n   :target: https://opensource.org/licenses/Apache-2.0\n   :alt: License\n.. |Read the Docs| image:: https://img.shields.io/readthedocs/soccerdata/latest.svg?label=Read%20the%20Docs\n   :target: https://soccerdata.readthedocs.io/\n   :alt: Read the documentation at https://soccerdata.readthedocs.io/\n.. |Tests| image:: https://github.com/probberechts/soccerdata/workflows/CI/badge.svg\n   :target: https://github.com/probberechts/soccerdata/actions?workflow=CI\n   :alt: Tests\n.. |Codecov| image:: https://codecov.io/gh/probberechts/soccerdata/branch/master/graph/badge.svg\n   :target: https://app.codecov.io/gh/probberechts/soccerdata\n   :alt: Codecov\n.. |pre-commit| image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white\n   :target: https://github.com/pre-commit/pre-commit\n   :alt: pre-commit\n.. |Black| image:: https://img.shields.io/badge/code%20style-black-000000.svg\n   :target: https://github.com/psf/black\n   :alt: Black\n\n.. badges-end\n\nSoccerData is a collection of wrappers over soccer data from `Club Elo`_,\n`ESPN`_, `FBref`_, `FiveThirtyEight`_, `Football-Data.co.uk`_, `SoFIFA`_ and\n`WhoScored`_. You get Pandas DataFrames with sensible, matching column names\nand identifiers across datasets. Data is downloaded when needed and cached\nlocally.\n\n.. code:: python\n\n   import soccerdata as sd\n\n   # Create scraper class instance for the Premier League\n   five38 = sd.FiveThirtyEight('ENG-Premier League', '1819')\n\n   # Fetch dataframes\n   games = five38.read_games()\n\nTo learn how to install, configure and use SoccerData, see the\n`Quickstart guide <https://soccerdata.readthedocs.io/en/latest/usage.html>`__. For documentation on each of the\nsupported data sources, see the `example notebooks <https://soccerdata.readthedocs.io/en/latest/datasources/>`__ and `API reference <https://soccerdata.readthedocs.io/en/latest/reference/>`__.\n\n.. _Club Elo: https://www.clubelo.com/\n.. _ESPN: https://www.espn.com/soccer/\n.. _FBref: https://www.fbref.com/en/\n.. _FiveThirtyEight: https://fivethirtyeight.com/soccer-predictions/\n.. _Football-Data.co.uk: https://www.football-data.co.uk/\n.. _SoFIFA: https://sofifa.com/\n.. _WhoScored: https://www.whoscored.com/\n\n**Disclaimer:** As soccerdata relies on web scraping, any changes to the\nscraped websites will break the package. Hence, do not expect that all code\nwill work all the time. If you spot any bugs, then please `fork it and start\na pull request <https://github.com/probberechts/soccerdata/blob/master/CONTRIBUTING.rst>`__.\n",
    'author': 'Pieter Robberechts',
    'author_email': 'pieter.robberechts@kuleuven.be',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/probberechts/soccerdata',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0.0',
}


setup(**setup_kwargs)
