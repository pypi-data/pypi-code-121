# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['reflekt',
 'reflekt.amplitude',
 'reflekt.avo',
 'reflekt.iteratively',
 'reflekt.reflekt',
 'reflekt.rudderstack',
 'reflekt.segment',
 'reflekt.snowplow']

package_data = \
{'': ['*'],
 'reflekt': ['templates/*',
             'templates/dbt/*',
             'templates/dbt/analyses/*',
             'templates/dbt/macros/*',
             'templates/dbt/models/*',
             'templates/dbt/seeds/*',
             'templates/dbt/snapshots/*',
             'templates/dbt/tests/*',
             'templates/plan/*',
             'templates/plan/events/*',
             'templates/project/*',
             'templates/project/.reflekt/avo/*',
             'templates/project/.reflekt/logs/*',
             'templates/project/.reflekt/tmp/*',
             'templates/project/dbt_packages/*',
             'templates/project/tracking-plans/example-plan/*',
             'templates/project/tracking-plans/example-plan/events/*']}

install_requires = \
['Cerberus>=1.3.4,<2.0.0',
 'GitPython>=3.1.27,<4.0.0',
 'PyYAML>=6.0,<7.0',
 'click>=8.1.2,<9.0.0',
 'funcy>=1.17,<2.0',
 'inflection>=0.5.1,<0.6.0',
 'loguru>=0.6.0,<0.7.0',
 'redshift-connector>=2.0.905,<3.0.0',
 'requests>=2.27.1,<3.0.0',
 'snowflake-sqlalchemy>=1.3.3,<2.0.0',
 'sqlalchemy-redshift>=0.8.9,<0.9.0']

entry_points = \
{'console_scripts': ['reflekt = reflekt:cli']}

setup_kwargs = {
    'name': 'reflekt',
    'version': '0.1.1',
    'description': 'reflekt is a command-line interface (CLI) and continuous integration (CI) tool for your tracking plan.',
    'long_description': None,
    'author': 'Greg Clunies',
    'author_email': 'greg.clunies@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
