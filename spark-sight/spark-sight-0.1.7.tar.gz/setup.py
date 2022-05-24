# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['spark_sight',
 'spark_sight.create_charts',
 'spark_sight.log_parse',
 'spark_sight.log_transform']

package_data = \
{'': ['*']}

install_requires = \
['pandas>=1.1,<=1.4.2', 'plotly>=5,<=5.7.0', 'requests<=2.27.1']

entry_points = \
{'console_scripts': ['spark-sight = spark_sight.execute:main_cli']}

setup_kwargs = {
    'name': 'spark-sight',
    'version': '0.1.7',
    'description': 'Spark performance at a glance',
    'long_description': None,
    'author': 'Alfredo Fomitchenko',
    'author_email': 'alfredo.fomitchenko@mail.polimi.it',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
