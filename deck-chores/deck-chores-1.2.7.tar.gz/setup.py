# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['deck_chores']

package_data = \
{'': ['*']}

install_requires = \
['apscheduler>=3.6,<4.0',
 'cerberus>=1.3.4,<2.0.0',
 'docker[ssh,tls]>=5.0,<6.0',
 'fasteners>=0.14,<0.15',
 'python-dateutil>=2.8.1,<3.0.0']

entry_points = \
{'console_scripts': ['deck-chores = deck_chores.main:main']}

setup_kwargs = {
    'name': 'deck-chores',
    'version': '1.2.7',
    'description': 'Job scheduler for Docker containers, configured via container labels.',
    'long_description': 'deck-chores\n===========\n\n.. image:: https://img.shields.io/docker/pulls/funkyfuture/deck-chores.svg\n        :target: https://hub.docker.com/r/funkyfuture/deck-chores/\n\n.. image:: https://images.microbadger.com/badges/image/funkyfuture/deck-chores.svg\n        :target: https://microbadger.com/images/funkyfuture/deck-chores\n\n.. image:: https://img.shields.io/pypi/v/deck-chores.svg\n        :target: https://pypi.org/project/deck-chores/\n\n**A job scheduler for Docker containers, configured via container labels.**\n\n* Documentation: https://deck-chores.readthedocs.io\n* Image repositories:\n    * https://github.com/funkyfuture/deck-chores/pkgs/container/deck-chores\n    * https://hub.docker.com/r/funkyfuture/deck-chores\n* Code repository: https://github.com/funkyfuture/deck-chores\n* Issue tracker: https://github.com/funkyfuture/deck-chores/issues\n* Free software: ISC license\n\n\nFeatures\n--------\n\n- define regular jobs to run within a container context with container and optionally with image\n  labels\n- use date, interval and cron-like triggers\n- set a maximum of simultaneously running instances per job\n- restrict job scheduling to one container per service\n- multi-architecture image supports ``amd64``, ``arm64`` and ``arm`` platforms\n  (the latter are currently not provided for download)\n\n\nExample\n-------\n\nLet\'s say you want to dump the database of a Wordpress once a day. Here\'s a ``docker-compose.yml``\nthat defines a job that will be handled by *deck-chores*:\n\n.. code-block:: yaml\n\n    version: "3.7"\n\n    services:\n      wordpress:\n        image: wordpress\n      mysql:\n        image: mariadb\n        volumes:\n          - ./database_dumps:/dumps\n        labels:\n          deck-chores.dump.command: sh -c "mysqldump --all-databases > /dumps/dump-$$(date -Idate)"\n          deck-chores.dump.interval: daily\n\nIt is however recommended to use scripts with a proper shebang for such actions. Their outputs to\n``stdout`` and ``stderr`` as well as their exit code will be logged by *deck-chores*.\n\n\nMaintenance\n-----------\n\nThe final release is supposed to receive monthly updates that includes updates\nof all updateable dependencies. If one is skipped, don\'t worry. When a second\nmaintenance release is skipped, feel free to open an issue to ask what the\nstatus is.\n\nYou can always build images upon an up-to-date base image with::\n\n    make build\n\n\nLimitations\n-----------\n\nWhen running on a cluster of `Docker Swarm <https://docs.docker.com/engine/swarm/>`_\nnodes, each ``deck-chores`` instance can only observe the containers on the\nnode it\'s running on, and hence only restrict to run one job per service within\nthe node\'s context.\n\n\nAcknowledgements\n----------------\n\nIt wouldn\'t be as charming to write this piece of software without these projects:\n\n* `APScheduler <https://apscheduler.readthedocs.io>`_ for managing jobs\n* `cerberus <http://python-cerberus.org>`_ for processing metadata\n* `docker-py <https://docker-py.readthedocs.io>`_ for Docker interaction\n* `flake8 <http://flake8.pycqa.org/>`_, `mypy <http://mypy-lang.org>`_,\n  `pytest <http://pytest.org>`_ and `tox <https://tox.readthedocs.io>`_ for testing\n* `Python <https://www.python.org>`_\n\n\nAuthors\n-------\n\n- Frank Sachsenheim (maintaining)\n- aeri4list\n- alpine-digger\n- Brynjar Smári Bjarnason\n- Garret Hohmann\n',
    'author': 'Frank Sachsenheim',
    'author_email': 'funkyfuture@riseup.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/funkyfuture/deck-chores',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
