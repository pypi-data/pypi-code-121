# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'python'}

packages = \
['clu', 'clu.legacy', 'clu.legacy.types', 'clu.legacy.types.ply', 'clu.parsers']

package_data = \
{'': ['*']}

install_requires = \
['aio_pika>=6.4.1,<7.0.0',
 'aiormq>=3.2.0,<4.0.0',
 'click>=8.0,<9.0',
 'jsonschema>=3.0.1,<4.0.0',
 'prompt_toolkit>=3.0.6,<4.0.0',
 'sdsstools>=0.4.13']

entry_points = \
{'console_scripts': ['clu = clu.__main__:main']}

setup_kwargs = {
    'name': 'sdss-clu',
    'version': '1.6.2',
    'description': 'A new protocol for SDSS actors.',
    'long_description': "`CLU <https://tron.fandom.com/wiki/Clu>`__\n==========================================\n\n|py| |pypi| |black| |Build Status| |docs| |Coverage Status| |zenodo|\n\n\n`CLU <https://tron.fandom.com/wiki/Clu>`_ implements a new protocol for SDSS actor while providing support for legacy-style actor.\n\n\nFeatures\n--------\n\n- Asynchronous API based on `asyncio <https://docs.python.org/3/library/asyncio.html>`_.\n- New-style actor with message passing based on `AMQP <https://www.amqp.org/>`_ and `RabbitMQ <https://rabbitmq.com>`_.\n- Legacy-style actor for TCP socket communication via `tron <https://github.com/sdss/tron>`__.\n- Tools for device handling.\n- Messages are validated JSON strings.\n- `click <https://click.palletsprojects.com/en/7.x/>`__-enabled command parser.\n\n\nInstallation\n------------\n\n``CLU`` can be installed using ``pip`` as\n\n.. code-block:: console\n\n    pip install sdss-clu\n\nor from source\n\n.. code-block:: console\n\n    git clone https://github.com/sdss/clu\n    cd clu\n    pip install .\n\n\nDevelopment\n^^^^^^^^^^^\n\n``clu`` uses `poetry <http://poetry.eustace.io/>`__ for dependency management and packaging. To work with an editable install it's recommended that you setup ``poetry`` and install ``clu`` in a virtual environment by doing\n\n.. code-block:: console\n\n    poetry install\n\nPip does not support editable installs with PEP-517 yet. That means that running ``pip install -e .`` will fail because ``poetry`` doesn't use a ``setup.py`` file. As a workaround, you can use the ``create_setup.py`` file to generate a temporary ``setup.py`` file. To install ``clu`` in editable mode without ``poetry``, do\n\n.. code-block:: console\n\n    pip install --pre poetry\n    pip install -U setuptools\n    python create_setup.py\n    pip install -e .\n\n\nQuick start\n-----------\n\nCreating a new actor with ``CLU`` is easy. To instantiate and run an actor you can simply do\n\n.. code-block:: python\n\n    import asyncio\n    from clu import AMQPActor\n\n    async def main(loop):\n        actor = await Actor('my_actor').start()\n        await actor.run_forever()\n\n    asyncio.run(main(loop))\n\nNext, head to the `Getting started <https://clu.readthedocs.io/en/latest/getting-started.html>`__ section for more information about using actors. More examples are available `here <https://clu.readthedocs.io/en/latest/examples.html>`__.\n\n\nWhy a new messaging protocol for SDSS?\n--------------------------------------\n\nSay whatever you want about it, the `current SDSS message passing protocol <https://clu.readthedocs.io/en/latest/legacy.html>`_ based on ``Tron``, ``opscore``, and ``actorcore`` is stable and robust. So, why should we replace it? Here is a list of reasons:\n\n- It reinvents the wheel. Ok, in all honesty ``Tron`` and ``opscore`` were written when wheel were still not completely circular, but the truth is that nowadays there are more robust, standard, and better documented technologies out there for message passing.\n- We can remove the need for a central hub product by relying in open-source message brokers such as `RabbitMQ <https://rabbitmq.com>`__.\n- ``Tron`` and ``opscore`` are Python 2 and it's unclear the amount of effort that would be needed to convert them to Python 3.\n- While there is some documentation for ``Tron`` and ``opscore``, and the code is well written, it's also cumbersome and difficult to modify by people that didn't write it. It's ultimately non-maintainable.\n- The ``opsctore``/``actorkeys`` datamodel is custom-built and extremely difficult to maintain. Standard solutions such as JSON with a `JSON schema <https://json-schema.org/>`__ validator should be preferred.\n- `asyncio <https://docs.python.org/3/library/asyncio.html>`__ provides an asynchronous API that is cleaner and easier to code than using threads. It is also more readable and less convoluted than `twisted <https://twistedmatrix.com/trac/>`__ and it's a Python core library with very active development.\n- CLU uses `click <https://click.palletsprojects.com/en/7.x>`__ for parsing commands, providing a well-defined, easy to use parser.\n\n\n.. |Build Status| image:: https://img.shields.io/github/workflow/status/sdss/clu/Test\n    :alt: Build Status\n    :target: https://github.com/sdss/clu/actions\n\n.. |Coverage Status| image:: https://codecov.io/gh/sdss/clu/branch/main/graph/badge.svg\n    :alt: Coverage Status\n    :target: https://codecov.io/gh/sdss/clu\n\n.. |py| image:: https://img.shields.io/badge/python-3.7%20|%203.8%20|%203.9-blue\n    :alt: Python Versions\n    :target: https://docs.python.org/3/\n\n.. |docs| image:: https://readthedocs.org/projects/docs/badge/?version=latest\n    :alt: Documentation Status\n    :target: https://clu.readthedocs.io/en/latest/?badge=latest\n\n.. |pypi| image:: https://badge.fury.io/py/sdss-clu.svg\n    :alt: PyPI version\n    :target: https://badge.fury.io/py/sdss-clu\n\n.. |black| image:: https://img.shields.io/badge/code%20style-black-000000.svg\n    :target: https://github.com/psf/black\n\n.. |zenodo| image:: https://zenodo.org/badge/183817446.svg\n   :target: https://zenodo.org/badge/latestdoi/183817446\n",
    'author': 'José Sánchez-Gallego',
    'author_email': 'gallegoj@uw.edu',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/sdss/clu',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
