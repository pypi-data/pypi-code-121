# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['exfill', 'exfill.parsers', 'exfill.scrapers', 'exfill.tests']

package_data = \
{'': ['*'], 'exfill': ['support/*']}

install_requires = \
['black>=22.3.0,<23.0.0',
 'bs4>=0.0.1,<0.0.2',
 'pandas>=1.4.2,<2.0.0',
 'selenium>=4.1.5,<5.0.0',
 'setuptools-scm>=6.4.2,<7.0.0']

entry_points = \
{'console_scripts': ['cli-script = src.exfill.extractor:main']}

setup_kwargs = {
    'name': 'exfill',
    'version': '0.1.17',
    'description': 'A small app to grab job postings from online job boards',
    'long_description': '# Introduction\n\nJob boards (like LinkedIn) can be a good source for finding job openings.  Unfortunately the search results cannot always be filtered to a usable degree.  This application lets users scrape and parse jobs with more flexability provided by the default search.\n\nCurrently only LinkedIn is supported.\n\n# Project Structure\n\nDirectories:\n- `src/exfill/parsers` - Contains parser(s)\n- `src/exfill/scrapers` - Contains scraper(s)\n- `src/exfill/support` \n    - Contains `geckodriver` driver for FireFox which is used by Selenium\n    - Download the latest driver from the [Mozilla GeckoDriver repo in GitHub](https://github.com/mozilla/geckodriver)\n- `data/html` \n    - Not in source control\n    - Contains HTML elements for a specific job posting\n    - Populated by a scraper\n- `data/csv` \n    - Not in source control\n    - Contains parsed information in a csv table\n    - Populated by a parser\n    - Also contains an error table\n- `logs` \n    - Not in source control\n    - Contains logs created during execution\n\n## `creds.json` File\n\nSyntax should be as follows:\n\n```json\n{\n    "linkedin": {\n        "username": "jay-law@gmail.com",\n        "password": "password1"\n    }\n}\n```\n\n# Usage\n\nThere are two phase.  First is scraping the postings.  Second is parsing the scraped information.  Therefore the scraping phase must occur before the parsing phase.\n\n## Use as Code\n\n```bash\n# Install with git\n$ git clone git@github.com:jay-law/job-scraper.git\n\n# Create and populate creds.json\n\n# Execute - Scrape linkedin\n$ python3 src/exfill/extractor.py linkedin scrape\n\n# Execute - Parse linkedin\n$ python3 src/exfill/extractor.py linkedin parse\n```\n\n## Use as Module\n\n```bash\n# Install\n$ python3 -m pip install --upgrade exfill\n\n# Execute - Scrape linkedin\n$ python3 -m exfill.extractor linkedin scrape\n\n# Execute - Parse linkedin\n$ python3 -m exfill.extractor linkedin parse\n```\n\n# Roadmap\n\n* [ ] Write unit tests\n* [ ] Improve secret handling\n* [x] Add packaging\n* [x] Move paths to config file\n* [x] Move keyword logic\n* [x] Set/include default config.ini for users installing with PIP\n* [x] Add CICD\n* [x] Automate versioning\n* [x] Add formatter (black module)\n* [x] Add static type checking (mypy module)\n* [x] Add import sorter (isort module)\n* [x] Add linter (flake8 module)\n* [x] Update string interpolation from %f to f-string\n* [x] Replace sys.exit calls with exceptions\n* [x] Update how the config object is accessed\n* [x] Migrate to `poetry` for virtual env, building, and publishing',
    'author': 'jay-law',
    'author_email': 'jay-law@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/jay-law/job-scraper',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
