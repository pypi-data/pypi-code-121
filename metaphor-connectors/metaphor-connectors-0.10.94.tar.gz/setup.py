# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['metaphor',
 'metaphor.airflow_plugin',
 'metaphor.airflow_plugin.lineage',
 'metaphor.bigquery',
 'metaphor.bigquery.lineage',
 'metaphor.bigquery.profile',
 'metaphor.bigquery.query',
 'metaphor.bigquery.usage',
 'metaphor.common',
 'metaphor.dbt',
 'metaphor.dbt.cloud',
 'metaphor.dbt.generated',
 'metaphor.google_directory',
 'metaphor.looker',
 'metaphor.manual',
 'metaphor.manual.lineage',
 'metaphor.metabase',
 'metaphor.postgresql',
 'metaphor.postgresql.profile',
 'metaphor.postgresql.usage',
 'metaphor.power_bi',
 'metaphor.redshift',
 'metaphor.redshift.lineage',
 'metaphor.redshift.profile',
 'metaphor.redshift.usage',
 'metaphor.slack_directory',
 'metaphor.snowflake',
 'metaphor.snowflake.lineage',
 'metaphor.snowflake.profile',
 'metaphor.snowflake.usage',
 'metaphor.tableau',
 'metaphor.thought_spot']

package_data = \
{'': ['*'], 'metaphor.common': ['docs/*']}

install_requires = \
['PyYAML>=6.0,<7.0',
 'aws-assume-role-lib>=2.9.0,<3.0.0',
 'boto3>=1.20.45,<2.0.0',
 'botocore>=1.23.45,<2.0.0',
 'canonicaljson>=1.4.0,<2.0.0',
 'fastjsonschema>=2.15.1,<3.0.0',
 'metaphor-models>=0.7.9,<0.8.0',
 'pydantic>=1.9.0,<2.0.0',
 'python-dateutil>=2.8.1,<3.0.0',
 'requests>=2.27.1,<3.0.0',
 'smart-open>=5.0.0,<6.0.0']

extras_require = \
{'all': ['asyncpg>=0.25.0,<0.26.0',
         'google-api-python-client>=2.36.0,<3.0.0',
         'google-auth-oauthlib>=0.5.0,<0.6.0',
         'google-cloud-bigquery>=2.21.0,<3.0.0',
         'google-cloud-logging>=2.7.0,<3.0.0',
         'lkml>=1.2.0,<2.0.0',
         'looker-sdk>=22.4.0,<23.0.0',
         'msal>=1.17.0,<2.0.0',
         'slack-sdk>=3.5.1,<4.0.0',
         'snowflake-connector-python>=2.7.0,<2.8.0',
         'sql-metadata==2.3.0',
         'tableauserverclient>=0.17.0,<0.18.0',
         'thoughtspot-rest-api-sdk>=1.9.0,<2.0.0'],
 'bigquery': ['google-cloud-bigquery>=2.21.0,<3.0.0',
              'google-cloud-logging>=2.7.0,<3.0.0',
              'sql-metadata==2.3.0'],
 'google_directory': ['google-api-python-client>=2.36.0,<3.0.0',
                      'google-auth-oauthlib>=0.5.0,<0.6.0'],
 'looker': ['lkml>=1.2.0,<2.0.0',
            'looker-sdk>=22.4.0,<23.0.0',
            'sql-metadata==2.3.0'],
 'metabase': ['sql-metadata==2.3.0'],
 'postgresql': ['asyncpg>=0.25.0,<0.26.0'],
 'power_bi': ['msal>=1.17.0,<2.0.0'],
 'redshift': ['asyncpg>=0.25.0,<0.26.0'],
 'slack_directory': ['slack-sdk>=3.5.1,<4.0.0'],
 'snowflake': ['snowflake-connector-python>=2.7.0,<2.8.0',
               'sql-metadata==2.3.0'],
 'tableau': ['tableauserverclient>=0.17.0,<0.18.0'],
 'throughtspot': ['thoughtspot-rest-api-sdk>=1.9.0,<2.0.0']}

setup_kwargs = {
    'name': 'metaphor-connectors',
    'version': '0.10.94',
    'description': "A collection of Python-based 'connectors' that extract metadata from various sources to ingest into the Metaphor app.",
    'long_description': None,
    'author': 'Metaphor',
    'author_email': 'dev@metaphor.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<3.11',
}


setup(**setup_kwargs)
