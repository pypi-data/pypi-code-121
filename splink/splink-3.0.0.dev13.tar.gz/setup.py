# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['splink', 'splink.athena', 'splink.duckdb', 'splink.spark', 'splink.sqlite']

package_data = \
{'': ['*'],
 'splink': ['files/*',
            'files/chart_defs/*',
            'files/chart_defs/del/*',
            'files/external_js/*',
            'files/splink_cluster_studio/*',
            'files/splink_comparison_viewer/*',
            'files/splink_vis_utils/*',
            'files/templates/*']}

install_requires = \
['Jinja2>=3.0.3,<4.0.0',
 'altair>=4.2.0,<5.0.0',
 'duckdb==0.3.2',
 'jsonschema>=3.2,<4.0',
 'pandas>=1.0.0,<2.0.0',
 'sqlglot==1.23.1']

setup_kwargs = {
    'name': 'splink',
    'version': '3.0.0.dev13',
    'description': 'Fast probabilistic data linkage at scale',
    'long_description': "# Splink: Super fast data linkage at any scale\n\n![image](https://user-images.githubusercontent.com/7570107/85285114-3969ac00-b488-11ea-88ff-5fca1b34af1f.png)\n\n`splink` is a Python package for probabilistic record linkage (entity resolution), within the Fellegi-Sunter framework.\n\nIt's key features are:\n\n- It is extremely fast. It is capable of linking a million records on a laptop in around a minute.\n\n- It is highly accurate, with support for term frequency adjustments, and sophisticated fuzzy matching logic.\n\n- It supports multiple SQL backends, meaning it's capable of running at any scale. For smaller linkages of up to a few million records, no additional infrastructure is needed. For larger linkages, Splink currently supports Apache Spark or AWS Athena as backends.\n\n- It produces a wide variety of interactive outputs, helping users to understand their model and diagnose linkage problems.\n\n## Acknowledgements\n\nWe are very grateful to [ADR UK](https://www.adruk.org/) (Administrative Data Research UK) for providing funding for this work as part of the [Data First](https://www.adruk.org/our-work/browse-all-projects/data-first-harnessing-the-potential-of-linked-administrative-data-for-the-justice-system-169/) project.\n\nWe are also very grateful to colleagues at the UK's Office for National Statistics for their expert advice and peer review of this work.\n",
    'author': 'Robin Linacre',
    'author_email': 'robinlinacre@hotmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/moj-analytical-services/splink',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
