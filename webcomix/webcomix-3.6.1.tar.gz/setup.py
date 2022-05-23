# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['webcomix',
 'webcomix.scrapy',
 'webcomix.scrapy.download',
 'webcomix.scrapy.download.tests',
 'webcomix.scrapy.tests',
 'webcomix.scrapy.verification',
 'webcomix.tests',
 'webcomix.tests.fake_websites']

package_data = \
{'': ['*'],
 'webcomix.tests.fake_websites': ['one_webpage/*',
                                  'one_webpage_searchable/*',
                                  'three_webpages/*',
                                  'three_webpages_alt_text/*',
                                  'three_webpages_classes/*']}

install_requires = \
['Scrapy>=2.5.1,<3.0.0',
 'click>=7.1.1,<8.0.0',
 'docker>=5.0.3,<6.0.0',
 'scrapy-fake-useragent>=1.4.4,<2.0.0',
 'scrapy-splash>=0.8.0,<0.9.0',
 'tqdm>=4.43.0,<5.0.0']

entry_points = \
{'console_scripts': ['webcomix = webcomix.cli:cli']}

setup_kwargs = {
    'name': 'webcomix',
    'version': '3.6.1',
    'description': 'Webcomic downloader',
    'long_description': '# webcomix\n\n[![Build Status](https://github.com/J-CPelletier/webcomix/workflows/Build/badge.svg?branch=master)](https://github.com/J-CPelletier/webcomix/actions)[![Coverage Status](https://coveralls.io/repos/github/J-CPelletier/webcomix/badge.svg?branch=master)](https://coveralls.io/github/J-CPelletier/webcomix?branch=master)[![PyPI version](https://badge.fury.io/py/webcomix.svg)](https://badge.fury.io/py/webcomix)\n\n## Description\n\nwebcomix is a webcomic downloader that can additionally create a .cbz (Comic Book ZIP) file once downloaded.\n\n## Notice\n\nThis program is for personal use only. Please be aware that by making the downloaded comics publicly available without the permission of the author, you may be infringing upon various copyrights.\n\n## Installation\n\n### Dependencies\n\n* Python (3.6 or newer)\n* click\n* scrapy (Some additional steps might be required to include this package and can be found [here](https://doc.scrapy.org/en/latest/intro/install.html#intro-install-platform-notes))\n* scrapy-splash\n* scrapy-fake-useragent\n* tqdm\n* [Docker](https://www.docker.com/) (To be able to download JavaScript-dependent websites with `-j` option)\n\n### Process\n\n#### End user\n\n1. Install [Python 3](https://www.python.org/downloads/)\n2. Install the command line interface tool with `pip install webcomix`\n\n#### Developer\n\n1. Install [Python 3](https://www.python.org/downloads/)\n2. Clone this repository and open a terminal in its directory\n3. Install [poetry](https://github.com/python-poetry/poetry) with `pip install poetry`\n3. Download the dependencies by running `poetry install`\n4. Install pre-commit hooks with `pre-commit install`\n\n## Usage\n\n`webcomix [OPTIONS] COMMAND [ARGS]`\n\n### Global Flags\n\n#### help\n\nShow the help message and exit.\n\n#### Version\n\nShow the version number and exit.\n\n### Commands\n\n#### comics\n\nShows all predefined comics which can be used with the `download` command.\n\n#### download\n\nDownloads a predefined comic. Supports the `--cbz` flag, which creates a .cbz archive of the downloaded comic.\n\n#### search\n\nSearches for an XPath that can download the whole comic. Supports the `--cbz` flag, which creates a .cbz archive of the downloaded comic,`-s`, which verifies only the provided page of the comic, `-y`, which skips the verification prompt, and `-j`, which runs the javascript on pages before downloading.\n\n#### custom\n\nDownloads a user-defined comic. To download a specific comic, you\'ll need a link to the first page, an XPath expression giving out the link to the next page and an XPath expression giving out the link to the image. More info [here](http://www.w3schools.com/xml/xpath_syntax.asp). Supports the `--cbz` flag, which creates a .cbz archive of the downloaded comic, `-s`, which verifies only the provided page of the comic, and `-y`, which skips the verification prompt.\n\n### Examples\n\n* `webcomix download xkcd`\n* `webcomix search xkcd --start-url=http://xkcd.com/1/`\n* `webcomix custom --cbz` (You will be prompted about other needed arguments)\n* `webcomix custom xkcd --start-url=http://xkcd.com/1/ --next-page-xpath="//a[@rel=\'next\']/@href" --image-xpath="//div[@id=\'comic\']//img/@src" --cbz` (Same as before, but with all arguments declared beforehand)\n\n### Making an XPath selector\n\nUsing an HTML inspector, spot a html path to the next link\'s `href` attribute/comic image\'s `src` attribute.\n\ne.g.: `//div[@class=\'foo\']/img/@src`\nThis will select the src attribute of the first image whose class is: foo\n\nNote: `webcomix` works best on static websites, since `scrapy`(the framework we use to travel web pages) doesn\'t process Javascript.\n\nTo make sure your XPath is correct, you have to go into `scrapy shell`, which should be downloaded when you\'ve installed `webcomix`.\n\n```\nscrapy shell <website> --> Use the website\'s url to go to it.\n> response.body --> Will give you the html from the website.\n> response.xpath --> Test an xpath selection. If you get [], this means your XPath expression hasn\'t gotten anything from the webpage.\n```\n\n## Contribution\n\nThe procedure depends on the type of contribution:\n\n* If you simply want to request the addition of a comic to the list of supported comics, make an issue with the label "Enhancement".\n* If you want to request the addition of a feature to the system or a bug fix, make an issue with the appropriate label.\n\n### Running the tests\n\nTo run the tests, you have to use the `pytest` command in the webcomix folder.\n',
    'author': 'Jean-Christophe Pelletier',
    'author_email': 'pelletierj97@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/J-CPelletier/webcomix',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6.1,<4.0.0',
}


setup(**setup_kwargs)
