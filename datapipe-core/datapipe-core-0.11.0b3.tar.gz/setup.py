# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['datapipe', 'datapipe.debug_ui', 'datapipe.store']

package_data = \
{'': ['*']}

install_requires = \
['Pillow>=9.0.0,<10.0.0',
 'PyYAML>=5.3.1',
 'SQLAlchemy>=1.4.25,<2.0.0',
 'cityhash>=0.2.3,<0.3.0',
 'click>=7.1.2',
 'cloudpickle>=1.6.0',
 'fsspec>=2021.11.1',
 'gcsfs>=2021.11.1',
 'iteration-utilities>=0.11.0',
 'numpy>=1.21.0,<2.0.0',
 'pandas>=1.2.0,<2.0.0',
 'psycopg2_binary>=2.8.4',
 'requests>=2.24.0',
 's3fs>=2021.11.1',
 'toml>=0.10.2',
 'tqdm>=4.60.0']

extras_require = \
{':extra == "opentelemetry"': ['opentelemetry-api>=1.8.0,<2.0.0',
                               'opentelemetry-sdk>=1.8.0,<2.0.0',
                               'opentelemetry-instrumentation-sqlalchemy>=0.27b0,<0.28'],
 'excel': ['xlrd>=2.0.1', 'openpyxl>=3.0.7'],
 'milvus': ['pymilvus>=2.0.2,<3.0.0'],
 'opentelemetry': ['opentelemetry-exporter-jaeger>=1.8.0,<2.0.0'],
 'ui': ['dash>=2.3.0,<2.4.0',
        'dash_bootstrap_components>=0.12.0,<0.13.0',
        'dash_interactive_graphviz>=0.3.0,<0.4.0']}

setup_kwargs = {
    'name': 'datapipe-core',
    'version': '0.11.0b3',
    'description': '',
    'long_description': None,
    'author': 'Andrey Tatarinov',
    'author_email': 'a@tatarinov.co',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
