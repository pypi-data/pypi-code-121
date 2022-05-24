# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['extract_emails',
 'extract_emails.browsers',
 'extract_emails.console',
 'extract_emails.data_extractors',
 'extract_emails.data_savers',
 'extract_emails.errors',
 'extract_emails.factories',
 'extract_emails.link_filters',
 'extract_emails.models',
 'extract_emails.utils',
 'extract_emails.workers']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.1.2,<9.0.0', 'loguru>=0.5.3,<0.6.0', 'pydantic>=1.8.2,<2.0.0']

entry_points = \
{'console_scripts': ['extract-emails = '
                     'extract_emails.console.application:main']}

setup_kwargs = {
    'name': 'extract-emails',
    'version': '5.3.1',
    'description': 'Extract email addresses and linkedin profiles from given URL.',
    'long_description': '# Extract Emails\n\n![Image](https://github.com/dmitriiweb/extract-emails/blob/docs_improvements/images/email.png?raw=true)\n\n[![PyPI version](https://badge.fury.io/py/extract-emails.svg)](https://badge.fury.io/py/extract-emails)\n\nExtract emails and linkedins profiles from a given website\n\n**Support the project with BTC**: *bc1q0cxl5j3se0ufhr96h8x0zs8nz4t7h6krrxkd6l*\n\n[Documentation](https://dmitriiweb.github.io/extract-emails/)\n\n## Requirements\n- Python >= 3.7\n\n## Installation\n```\npip install extract_emails\n```\n\n## Simple Usage\n### As library\n```python\nfrom pathlib import Path\n\nfrom extract_emails import DefaultFilterAndEmailFactory as Factory\nfrom extract_emails import DefaultWorker\nfrom extract_emails.browsers.requests_browser import RequestsBrowser as Browser\nfrom extract_emails.data_savers import CsvSaver\n\n\nwebsites = [\n    "website1.com",\n    "website2.com",\n]\n\nbrowser = Browser()\ndata_saver = CsvSaver(save_mode="a", output_path=Path("output.csv"))\n\nfor website in websites:\n    factory = Factory(\n        website_url=website, browser=browser, depth=5, max_links_from_page=1\n    )\n    worker = DefaultWorker(factory)\n    data = worker.get_data()\n    data_saver.save(data)\n```\n### As CLI tool\n```bash\n$ extract-emails --help\n\n$ extract-emails --url https://en.wikipedia.org/wiki/Email -of output.csv -d 1\n$ cat output.csv\nemail,page,website\nbob@b.org,https://en.wikipedia.org/wiki/Email,https://en.wikipedia.org/wiki/Email\n```\n',
    'author': 'Dmitrii Kurlov',
    'author_email': 'dmitriik@tutanota.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/dmitriiweb/extract-emails',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<3.11',
}


setup(**setup_kwargs)
