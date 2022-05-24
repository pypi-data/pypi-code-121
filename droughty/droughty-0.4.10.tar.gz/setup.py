# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['droughty', 'droughty.cube_parser']

package_data = \
{'': ['*']}

install_requires = \
['GitPython==3.1.26',
 'Jinja2==3.0.1',
 'Markdown>=3.3.6,<4.0.0',
 'PyYAML==6.0',
 'SQLAlchemy==1.4.22',
 'Sphinx>=4.4.0,<5.0.0',
 'click==8.0.1',
 'glom>=22.1.0,<23.0.0',
 'jinjasql==0.1.8',
 'lkml==1.1.0',
 'pandas-gbq==0.15.0',
 'pandas==1.3.5',
 'protobuf==3.19.4',
 'pycryptodomex==3.10.1',
 'ruamel.base==1.0.0',
 'ruamel.yaml>=0.17.20,<0.18.0',
 'six==1.16.0',
 'snowflake-connector-python>=2.7.2,<3.0.0',
 'snowflake-sqlalchemy==1.3.3',
 'snowflake==0.0.3',
 'tqdm==4.62.3',
 'typer==0.4.0']

entry_points = \
{'console_scripts': ['droughty = droughty.main:start']}

setup_kwargs = {
    'name': 'droughty',
    'version': '0.4.10',
    'description': 'droughty is an analytics engineering toolkit, helping keep your workflow dry.',
    'long_description': '[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![Read the Docs](https://img.shields.io/readthedocs/lkml)](https://droughty.readthedocs.io/en/latest/)\n\n# droughty\n\ndroughty is an analytics engineering toolkit, helping keep your workflow dry.\n\n**Read the documentation on [Read the Docs](https://droughty.readthedocs.io/en/latest/).**\n\ninvoke using:\n\n- droughty lookml - generates a base layer.lkml file with views and explores from a warehouse schema \n- droughty dbt-tests - generates a base schema from specified warehouse schemas. Includes standard testing routines\n- droughty dbml - generates an ERD based on the warehouse layer of your warehouse. Includes pk, fk relationships\n\nThe purpose of this project is to automate the repetitive, dull elements of analytics engineering in the modern data stack. It turns out this also leads to cleaner projects, less human error and increases the likelihood of the basics getting done...\n\nInterested in contributing to `droughty`? Check out the [contributor guidelines](CONTRIBUTING.md).\n\n## How do I install it?\n\n`droughty` is available to install on [pip](https://pypi.org/project/droughty/) via the following command:\n\n```\npip install droughty\n```',
    'author': 'Lewis',
    'author_email': 'lewischarlesbaker@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/lewischarlesbaker/droughty',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7.1,<3.11',
}


setup(**setup_kwargs)
