# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['clearcut']

package_data = \
{'': ['*']}

install_requires = \
['opentelemetry-api>=1.11.1,<2.0.0',
 'opentelemetry-exporter-otlp-proto-http>=1.11.1,<2.0.0',
 'opentelemetry-instrumentation-logging>=0.30b1,<0.31',
 'opentelemetry-sdk>=1.11.1,<2.0.0']

setup_kwargs = {
    'name': 'clearcut',
    'version': '0.2.1',
    'description': 'A straightforward and lightweight logging and tracing library',
    'long_description': '# Clearcut: A straightforward and lightweight logging wrapper library\n\n[![Build Status](https://cloud.drone.io/api/badges/tangibleintelligence/clearcut/status.svg)](https://cloud.drone.io/tangibleintelligence/clearcut)\n\nThis provides some helpful wrapper and util functions for logging, and formats log messages in a more human-readable way by default.\n\n## Use\n\nAt the top of the file:\n\n```python\nfrom clearcut import get_logger\n\n...\n\nlogger = get_logger(__name__)\n```\n\nLogging can be performed ad-hoc:\n\n```python\nlogger.info("info log")\nlogger.warning("warn log", exc_info=e)\n```\n\n"log blocks" can also be created which automatically log entrance/exits as well as performance information\n\n```python\nfrom clearcut import log_block, get_logger\n\n...\n\nlogger = get_logger(__name__)\n\n...\n\nwith log_block("block name", logger):\n    ...\n```\n\n## TODO\n- Would like to use contextvars to create a contextmanager where additional "metadata" can be specified (and unspecified) which would be\nincluded with logging automatically. (may not be import with OTLP tracing.)\n- json logging',
    'author': 'Austin Howard',
    'author_email': 'austin@tangibleintelligence.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/tangibleintelligence/clearcut',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
