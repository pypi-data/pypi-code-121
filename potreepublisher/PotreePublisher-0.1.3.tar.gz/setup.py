# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['potreepublisher']

package_data = \
{'': ['*'], 'potreepublisher': ['viewer_templates/*']}

install_requires = \
['PyYAML>=6.0,<7.0', 'typer[all]>=0.4.0,<0.5.0']

entry_points = \
{'console_scripts': ['PotreePublisher = potreepublisher.main:app']}

setup_kwargs = {
    'name': 'potreepublisher',
    'version': '0.1.3',
    'description': 'Small CLI to quickly publish a single LAS file or a whole folder to a Potree server.',
    'long_description': "# PotreePublisher\nSmall CLI to quickly publish a single LAS file or a whole folder to a Potree server.\n\n\n## Prerequisites\nIt is assumed that you have a **Potree server** installed on your machine.\n<details>\n<summary>Expand for instructions if you don't :wink:</summary>\n\n1. Clone the potree repository: `git clone https://github.com/potree/potree`\n\n2. Make sure you have the Node Package Manager (npm) installed (usually delivered with node.js).\n\n3. Inside potree's repository, run `npm install`. It will install dependencies (specified in package.json) and create a build in ./build/potree.\n\n4. Move the potree folder to you favorite http server.\n\n5. Make sure you spot the location where you want to:\n + store the point clouds\n + store the viewer html files\n\n6. You're good to go! \n</details>\n\nIt is also assumed that you have **PotreeConverter** installed. See [this page](https://github.com/potree/PotreeConverter) for instructions.\n\n## Installation\n```\npip install potreepublisher\n```\n\n## Usage\n```\nUsage: PotreePublisher [OPTIONS] INPUT_PATH\n\nArguments:\n  INPUT_PATH  Path to the point cloud or a folder of point clouds to process.\n              Any type supported by PotreeConverter is possible.  [required]\n\nOptions:\n  --potree-server-root TEXT  Root path of the potree server.  [default:\n                             /var/www/potree]\n  --point-cloud-folder TEXT  Folder where the point cloud will be stored after\n                             conversion to Potree Format.  [default:\n                             pointclouds]\n  --viewer-folder TEXT       Folder where the viewer html page will be stored.\n                             [default: results]\n  --help                     Show this message and exit.\n```\n",
    'author': 'Elie-Alban LESCOUT',
    'author_email': 'elie-alban.lescout@ensg.eu',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
