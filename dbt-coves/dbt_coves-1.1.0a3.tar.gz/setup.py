# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dbt_coves',
 'dbt_coves.config',
 'dbt_coves.core',
 'dbt_coves.tasks',
 'dbt_coves.tasks.extract',
 'dbt_coves.tasks.generate',
 'dbt_coves.tasks.load',
 'dbt_coves.tasks.setup',
 'dbt_coves.ui',
 'dbt_coves.utils']

package_data = \
{'': ['*'], 'dbt_coves': ['templates/*']}

install_requires = \
['Jinja2>=2.11.2,<2.12.0',
 'PyYAML>=5.4.1',
 'bumpversion>=0.6.0,<0.7.0',
 'click>=8.0.3,<9.0.0',
 'cookiecutter>=1.7.3,<2.0.0',
 'dbt-core>=0.18.0,<2.0.0',
 'luddite>=1.0.1,<2.0.0',
 'packaging>=20.8,<21.0',
 'pre-commit>=2.15.0,<3.0.0',
 'pretty-errors>=1.2.19,<2.0.0',
 'pydantic>=1.8,<2.0',
 'pyfiglet>=0.8.post1,<0.9',
 'python-slugify<5.0.0',
 'questionary>=1.9.0,<2.0.0',
 'rich>=10.4.0,<11.0.0',
 'sqlfluff-templater-dbt==0.11.2',
 'sqlfluff==0.11.2',
 'yamlloader>=1.0.0,<2.0.0']

entry_points = \
{'console_scripts': ['dbt-coves = dbt_coves.core.main:main']}

setup_kwargs = {
    'name': 'dbt-coves',
    'version': '1.1.0a3',
    'description': 'CLI tool for dbt users adopting analytics engineering best practices.',
    'long_description': '# dbt-coves\n\n[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/datacoves/dbt-coves/graphs/commit-activity)\n[![PyPI version\nfury.io](https://badge.fury.io/py/dbt-coves.svg)](https://pypi.python.org/pypi/dbt-coves/)\n[![Code\nStyle](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)\n[![Checked with\nmypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org)\n[![Imports:\nisort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)\n[![Imports:\npython](https://img.shields.io/badge/python-3.8%20%7C%203.9-blue)](https://img.shields.io/badge/python-3.8%20%7C%203.9-blue)\n[![Build](https://github.com/datacoves/dbt-coves/actions/workflows/main_ci.yml/badge.svg)](https://github.com/datacoves/dbt-coves/actions/workflows/main_ci.yml/badge.svg)\n[![pre-commit.ci\nstatus](https://results.pre-commit.ci/badge/github/bitpicky/dbt-coves/main.svg)](https://results.pre-commit.ci/latest/github/datacoves/dbt-coves/main)\n[![codecov](https://codecov.io/gh/datacoves/dbt-coves/branch/main/graph/badge.svg?token=JB0E0LZDW1)](https://codecov.io/gh/datacoves/dbt-coves)\n[![Maintainability](https://api.codeclimate.com/v1/badges/1e6a887de605ef8e0eca/maintainability)](https://codeclimate.com/github/datacoves/dbt-coves/maintainability)\n[![Downloads](https://pepy.tech/badge/dbt-coves)](https://pepy.tech/project/dbt-coves)\n\n## What is dbt-coves?\n\ndbt-coves is a complimentary CLI tool for [dbt](https://www.getdbt.com)\nthat allows users to quickly apply [Analytics\nEngineering](https://www.getdbt.com/what-is-analytics-engineering/) best\npractices.\n\ndbt-coves helps with the generation of scaffold for dbt by analyzing\nyour data warehouse schema in Redshift, Snowflake, or Big Query and\ncreating the necessary configuration files (sql and yml).\n\n⚠️ **dbt-coves is in alpha version. Don\'t use on your prod models unless\nyou have tested it before.**\n\n### Here\\\'s the tool in action\n\n[![image](https://cdn.loom.com/sessions/thumbnails/74062cf71cbe4898805ca508ea2d9455-1624905546029-with-play.gif)](https://www.loom.com/share/74062cf71cbe4898805ca508ea2d9455)\n\n## Supported dbt versions\n\n  |Version          |Status|\n  |---------------- |------------------|\n  |\\<= 0.17.0       |❌ Not supported|\n  |0.18.x - 0.21x   |✅ Tested|\n  |1.x              |✅ Tested|\n\n## Supported adapters\n\n  |Feature|                  Snowflake|   Redshift|         BigQuery|        Postgres|\n  |------------------------| -----------| ----------------| ---------------| ---------------|\n  |profile.yml generation|   ✅ Tested|   🕥 In progress|   ❌ Not tested|   ❌ Not tested|\n  |sources generation|       ✅ Tested|   🕥 In progress|   ❌ Not tested|   ❌ Not tested|\n\n# Installation\n\n``` console\npip install dbt-coves\n```\n\nWe recommend using [python\nvirtualenvs](https://docs.python.org/3/tutorial/venv.html) and create\none separate environment per project.\n\n⚠️ **if you have dbt \\< 0.18.0 installed, dbt-coves will automatically\nupgrade dbt to the latest version**\n\n# Main Features\n\n## Project initialization\n\n``` console\ndbt-coves init\n```\n\nInitializes a new ready-to-use dbt project that includes recommended\nintegrations such as [sqlfluff](https://github.com/sqlfluff/sqlfluff),\n[pre-commit](https://pre-commit.com/), dbt packages, among others.\n\nUses a [cookiecutter](https://github.com/datacoves/cookiecutter-dbt)\ntemplate to make it easier to maintain.\n\n## Models generation\n\n``` console\ndbt-coves generate <resource>\n```\n\nWhere *\\<resource\\>* could be *sources*.\n\nCode generation tool to easily generate models and model properties\nbased on configuration and existing data.\n\nSupports [Jinja](https://jinja.palletsprojects.com/) templates to adjust\nhow the resources are generated.\n\n### Metadata\n\nSupports the argument *--metadata* which allows to specify a csv file\ncontaining field types and descriptions to be inserted into the model\nproperty files.\n\n``` console\ndbt-coves generate sources --metadata metadata.csv\n```\n\nMetadata format:\n\n  \n  |database|   schema|     relation|   column|     key|         type|       description|\n  |----------| ----------| ----------| ----------| -----------| ----------| -------------|\n  |raw|        master|     person|     name|       (empty)|     varchar|    The full name|\n  |raw|        master|     person|     name|       groupName|   varchar|    The group name|\n  \n\n## Quality Assurance\n\n``` console\ndbt-coves check\n```\n\nRuns a set of checks in your local environment to ensure high code\nquality.\n\nChecks can be extended by implementing [pre-commit\nhooks](https://pre-commit.com/#creating-new-hooks).\n\n## Environment setup\n\n``` console\ndbt-coves setup\n```\n\nRuns a set of checks in your local environment and helps you configure\nit properly: ssh key, git, dbt profiles.yml, vscode extensions.\n\n## Extract configuration from Airbyte\n\n``` console\ndbt-coves extract airbyte\n```\n\nExtracts the configuration from your Airbyte sources, connections and\ndestinations (excluding credentials) and stores it in the specified\nfolder. The main goal of this feature is to keep track of the\nconfiguration changes in your git repo, and rollback to a specific\nversion when needed.\n\n## Load configuration to Airbyte\n\n``` console\ndbt-coves load airbyte\n```\n\nLoads the Airbyte configuration generated with *dbt-coves extract\nairbyte* on an Airbyte server. Secrets folder needs to be specified\nseparatedly. You can use [git-secret](https://git-secret.io/) to encrypt\nthem and make them part of your git repo.\n\n# Settings\n\nDbt-coves could optionally read settings from `.dbt_coves.yml` or\n`.dbt_coves/config.yml`. A standard settings files could looke like\nthis:\n\n``` yaml\ngenerate:\n  sources:\n    schemas:\n      - RAW\n    destination: "models/sources/{{ schema }}/{{ relation }}.sql"\n    model_props_strategy: one_file_per_model\n    templates_folder: ".dbt_coves/templates"\n```\n\nIn this example options for the `generate` command are provided:\n\n`schemas`: List of schema names where to look for source tables\n\n`destination`: Path to generated model, where `schema` represents the\nlowercased schema and `relation` the lowercased table name.\n\n`model_props_strategy`: Defines how dbt-coves generates model properties\nfiles, currently just `one_file_per_model` is available, creates one\nyaml file per model.\n\n`templates_folder`: Folder where source generation jinja templates are\nlocated.\n\n## Override source generation templates\n\nCustomizing generated models and model properties requires placing\nspecific files under the `templates_folder` folder like these:\n\n### source_model.sql\n\n``` sql\nwith raw_source as (\n\n    select\n        *\n    from {% raw %}{{{% endraw %} source(\'{{ relation.schema.lower() }}\', \'{{ relation.name.lower() }}\') {% raw %}}}{% endraw %}\n\n),\n\nfinal as (\n\n    select\n{%- if adapter_name == \'SnowflakeAdapter\' %}\n{%- for key, cols in nested.items() %}\n  {%- for col in cols %}\n        {{ key }}:{{ \'"\' + col + \'"\' }}::{{ cols[col]["type"] }} as {{ cols[col]["id"] }}{% if not loop.last or columns %},{% endif %}\n  {%- endfor %}\n{%- endfor %}\n{%- elif adapter_name == \'BigQueryAdapter\' %}\n{%- for key, cols in nested.items() %}\n  {%- for col in cols %}\n        cast({{ key }}.{{ col }} as {{ cols[col]["type"].replace("varchar", "string") }}) as {{ cols[col]["id"] }}{% if not loop.last or columns %},{% endif %}\n  {%- endfor %}\n{%- endfor %}\n{%- elif adapter_name == \'RedshiftAdapter\' %}\n{%- for key, cols in nested.items() %}\n  {%- for col in cols %}\n        {{ key }}.{{ col }}::{{ cols[col]["type"] }} as {{ cols[col]["id"] }}{% if not loop.last or columns %},{% endif %}\n  {%- endfor %}\n{%- endfor %}\n{%- endif %}\n{%- for col in columns %}\n        {{ \'"\' + col.name + \'"\' }} as {{ col.name.lower() }}{% if not loop.last %},{% endif %}\n{%- endfor %}\n\n    from raw_source\n\n)\n\nselect * from final\n```\n\n### source_model_props.yml\n\n``` yaml\nversion: 2\n\nsources:\n  - name: {{ relation.schema.lower() }}\n{%- if source_database %}\n    database: {{ source_database }}\n{%- endif %}\n    schema: {{ relation.schema.lower() }}\n    tables:\n      - name: {{ relation.name.lower() }}\n        identifier: {{ relation.name }}\n\nmodels:\n  - name: {{ model.lower() }}\n    columns:\n{%- for cols in nested.values() %}\n  {%- for col in cols %}\n      - name: {{ cols[col]["id"] }}\n      {%- if cols[col]["description"] %}\n        description: "{{ cols[col][\'description\'] }}"\n      {%- endif %}\n  {%- endfor %}\n{%- endfor %}\n{%- for col in columns %}\n      - name: {{ col.name.lower() }}\n{%- endfor %}\n```\n\n# Thanks\n\nThe project main structure was inspired by\n[dbt-sugar](https://github.com/bitpicky/dbt-sugar). Special thanks to\n[Bastien Boutonnet](https://github.com/bastienboutonnet) for the great\nwork done.\n\n# Authors\n\n-   Sebastian Sassi [\\@sebasuy](https://twitter.com/sebasuy) --\n    [Convexa](https://convexa.ai)\n-   Noel Gomez [\\@noel_g](https://twitter.com/noel_g) --\n    [Ninecoves](https://ninecoves.com)\n\n# About\n\nLearn more about [Datacoves](https://datacoves.com).\n\n# CLI Reference\n\nFor a complete detail of usage, please run:\n\n``` console\ndbt-coves -h\n```\n',
    'author': 'Datacoves',
    'author_email': 'hello@datacoves.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://datacoves.com',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7.2,<3.10',
}


setup(**setup_kwargs)
