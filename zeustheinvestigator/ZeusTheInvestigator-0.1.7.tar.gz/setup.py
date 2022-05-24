# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['zeustheinvestigator']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.27.1,<3.0.0',
 'rich>=12.4.3,<13.0.0',
 'typer>=0.4.1,<0.5.0',
 'urllib3>=1.26.9,<2.0.0']

entry_points = \
{'console_scripts': ['zeus = ZeusTheInvestigator.checker:main']}

setup_kwargs = {
    'name': 'zeustheinvestigator',
    'version': '0.1.7',
    'description': 'A pure python program that checks if a site is online at the moment',
    'long_description': '# Zeus the Investigator\n![ZeusTheInvestigator0.1.7-preview](https://user-images.githubusercontent.com/76993204/170004945-e1ad079f-d1eb-46f5-9da2-51bd452bf635.gif)\n\n#### **USAGE**\n```powershell\n$ zeus -u <first_url> -u <second_url> -c <cooldown(in secs. default=3)>\n```\n\n# Installation\n## Manual Installation\n**Note:** *You will need poetry for manual installation*\n```bash\n$ pip install poetry\n```\n\n1. Download or clone the repository.\n```git\n$ git clone https://github.com/777advait/Zeus-The-Investigator\n```\n\n2. Install the project by running the following command in the root of the directory.\n``` bash\n$ poetry install\n```\n\n\n## PyPi Installation\n```bash\n$ pip install ZeusTheInvestigator\n```\n',
    'author': '777advait',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/777advait/Zeus-The-Investigator',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
