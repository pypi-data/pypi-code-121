# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['PythonStackTracer']

package_data = \
{'': ['*']}

install_requires = \
['robotframework>=5']

setup_kwargs = {
    'name': 'robotframework-pythonstacktrace',
    'version': '0.1.0',
    'description': 'Robot Framework listener that prints Python traceback for failing keywords.',
    'long_description': '# PythonStackTracer\n\nRobot Framework listener that prints Python traceback for failing keywords in\nthe console.\n\nThis listener prints only the trace from Python modules. For Robot Framework stack trace, check out [robotframework-stacktrace](https://github.com/MarketSquare/robotframework-stacktrace).\n\n## Installation\n\n```shell\npip install robotframework-pythonstacktrace\n```\n\n## Usage\n\n```shell\nrobot --listener PythonStackTracer\n```\n\n## Example\n\n```shell\nAtest Data & Atest Data.Atest Data.Example\n==============================================================================\nPython Traceback (most recent call last):                             F\n  File "C:\\Users\\flant\\Desktop\\pytrace\\atest_data\\ExceptionalLibrary.py", line 9, in raises_an_exception\n    first_call()\n  File "C:\\Users\\flant\\Desktop\\pytrace\\atest_data\\ExceptionalLibrary.py", line 3, in first_call\n    second_call()\n  File "C:\\Users\\flant\\Desktop\\pytrace\\atest_data\\ExceptionalLibrary.py", line 6, in second_call\n    raise Exception()\nException\n______________________________________________________________________________\n```\n',
    'author': 'Piotr Chromiński',
    'author_email': 'piot.chrom@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/aajn/robotframework-pythonstacktrace',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
