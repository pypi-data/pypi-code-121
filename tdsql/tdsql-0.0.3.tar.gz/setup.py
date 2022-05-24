# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tdsql', 'tdsql.client']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0', 'pandas>=1.4.2,<2.0.0']

extras_require = \
{'bigquery': ['google-cloud-bigquery>=3.1.0,<4.0.0', 'db-dtypes>=1.0.1,<2.0.0']}

entry_points = \
{'console_scripts': ['tdsql = tdsql.command:main']}

setup_kwargs = {
    'name': 'tdsql',
    'version': '0.0.3',
    'description': 'Minimum test flamework for sql',
    'long_description': "# Test Driven SQL\nTdsql is a minimum test flamework for sql.\nYou can replace any part of sql and check if the result is as expected.\nYou can define test cases as yaml file.\n\n## Install\nCurrently, only bigquery is supported.\n\n```bash\npip install tdsql[bigquery]\n```\n\n## Quick start\nSave these files in your working directory.\n\n```yaml\n# ./tdsql.yaml\ndatabase: bigquery\ntests:\n  - filepath: ./hello-world.sql\n    replace:\n      data: |\n        SELECT * FROM UNNEST([\n          STRUCT('2020-01-01' AS dt, 100 AS id),\n          STRUCT('2020-01-01', 100),\n          STRUCT('2020-01-01', 200)\n        ])\n      master: |\n        FROM (\n          SELECT 100 AS id, 1 AS category\n        )\n    expected: |\n      SELECT * FROM UNNEST([\n        STRUCT('2020-01-01' AS dt, 1 AS category, 2 AS cnt),\n        STRUCT('2020-01-01', NULL, 1)\n      ])\n```\n\n```sql\n-- ./hello-world.sql\nWITH data AS (\n  -- tdsql-start: data\n  SELECT dt, id\n  FROM `data_table`\n  -- tdsql-end: data\n), master AS (\n  SELECT id, category\n  FROM `master_table` -- tdsql-line: master\n)\nSELECT\n  dt,\n  category,\n  COUNT(*) AS cnt\nFROM data INNER JOIN master USING(id)\nGROUP BY 1, 2\n```\n\nThen, run this command.\nYou'll see an error message.\n\n```sh\ntdsql\n```\n\nFix `hello-world.sql` and run `tdsql` again,\nyou won't see any error message this time.\n\n```diff\n- FROM data INNER JOIN master USING(id)\n+ FROM data LEFT JOIN master USING(id)\n```\n\nQuite simple, isn't it?\n\n## Examples\nHeavily documented sample codes are [here](./sample).\n\n## Feedback\nIf you find any bugs, please feel free to create an issue.\n",
    'author': 'dr666m1',
    'author_email': 'skndr666m1@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<3.11',
}


setup(**setup_kwargs)
