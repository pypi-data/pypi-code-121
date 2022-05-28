# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['purgatory',
 'purgatory.domain',
 'purgatory.domain.messages',
 'purgatory.service',
 'purgatory.service._async',
 'purgatory.service._sync']

package_data = \
{'': ['*']}

extras_require = \
{'aioredis': ['aioredis>=2.0.1,<3.0.0'], 'redis': ['redis>=4.1.0,<5.0.0']}

setup_kwargs = {
    'name': 'purgatory',
    'version': '1.0.1',
    'description': 'A circuit breaker implementation for asyncio',
    'long_description': 'Purgatory\n=========\n\n.. image:: https://readthedocs.org/projects/purgatory/badge/?version=latest\n   :target: https://purgatory.readthedocs.io/en/latest/?badge=latest\n   :alt: Documentation Status\n\n.. image:: https://github.com/mardiros/purgatory/actions/workflows/main.yml/badge.svg\n   :target: https://github.com/mardiros/purgatory/actions/workflows/main.yml\n   :alt: Continuous Integration Status\n\n.. image:: https://codecov.io/gh/mardiros/purgatory/branch/main/graph/badge.svg?token=LFVOQC2C9E\n   :target: https://codecov.io/gh/mardiros/purgatory\n   :alt: Code Coverage Report\n    \n\nPurgatory is an implementation of the circuit breaker pattern.\n\n.. note::\n\n   It is used to detect failures and encapsulates the logic of preventing\n   a failure from constantly recurring, during maintenance, temporary\n   external system failure or unexpected system difficulties. \n\n   Source: https://en.wikipedia.org/wiki/Circuit_breaker_design_pattern\n\n\nWhy another Circuit Breaker implementation ?\n--------------------------------------------\n\nThe Purgatory library has been develop to be used in `blacksmith`_ where\nthe library aiobreaker was used but I encountered limitation so, I decide\nto build my own implementation that feet well with `blacksmith`_.\n\n\n.. _`blacksmith`: https://python-blacksmith.readthedocs.io/en/latest/\n\n\nFeatures\n--------\n\nPurgatory supports the creation of many circuit breakers easily, that \ncan be used as context manager or decorator.\nCircuit breaker can be asynchronous or synchronous.\n\nExample with a context manager for an async API\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\n::\n\n   from purgatory import AsyncCircuitBreakerFactory\n\n   circuitbreaker = AsyncCircuitBreakerFactory()\n   async with await circuitbreaker.get_breaker("my_circuit"):\n      ...\n\n\nExample with a decorator\n~~~~~~~~~~~~~~~~~~~~~~~~\n\n::\n\n   from purgatory import AsyncCircuitBreakerFactory\n\n   circuitbreaker = AsyncCircuitBreakerFactory()\n\n   @circuitbreaker("another circuit")\n   async def function_that_may_fail():\n      ...\n\n\n\nExample with a context manager for an synchronous API\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\n::\n\n   from purgatory import SyncCircuitBreakerFactory\n\n   circuitbreaker = SyncCircuitBreakerFactory()\n   with circuitbreaker.get_breaker("my_circuit"):\n      ...\n\n\nCircuit breakers states and monitoring\n--------------------------------------\n\nThe state of every circuits can be stored in memory, shared in redis, or\nbe completly customized.\n\nIt also support monitoring, using event hook.\n\nPurgatory is fully typed and fully tested.\n\n\nRead More\n---------\n\nYou can read the `full documentation of this library here`_.\n\n.. _`full documentation of this library here`: https://purgatory.readthedocs.io/en/latest/user/introduction.html\n\n\nAlternatives\n------------\n\nHere is a list of alternatives, which may or may not support coroutines.\n\n * aiobreaker - https://pypi.org/project/aiobreaker/\n * circuitbreaker - https://pypi.org/project/circuitbreaker/\n * pycircuitbreaker - https://pypi.org/project/pycircuitbreaker/\n * pybreaker - https://pypi.org/project/pybreaker/\n * lasier - https://pypi.org/project/lasier/\n * breakers - https://pypi.org/project/breakers/\n * pybreaker - https://pypi.org/project/pybreaker/\n * python-circuit - https://pypi.org/project/python-circuit/\n',
    'author': 'Guillaume Gauvrit',
    'author_email': 'guillaume@gauvr.it',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/mardiros/purgatory',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
