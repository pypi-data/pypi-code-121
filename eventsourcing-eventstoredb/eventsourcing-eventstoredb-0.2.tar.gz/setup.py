# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['eventsourcing_eventstoredb', 'eventsourcing_eventstoredb.eventstoredb']

package_data = \
{'': ['*']}

install_requires = \
['esdbclient>=0.2.1,<0.3.0', 'eventsourcing>=9.2.13,<9.3.0']

setup_kwargs = {
    'name': 'eventsourcing-eventstoredb',
    'version': '0.2',
    'description': 'Python package for eventsourcing with EventStoreDB',
    'long_description': '# Event Sourcing with EventStoreDB\n\nThis package supports using the Python\n[eventsourcing](https://github.com/pyeventsourcing/eventsourcing) library\nwith [EventStoreDB](https://www.eventstore.com/).\n\n## Installation\n\nUse pip to install the stable distribution from the Python Package Index.\n\n    $ pip install eventsourcing-eventstoredb\n\nPlease note, it is recommended to install Python packages into a Python virtual environment.\n\n## Getting started\n\nDefine aggregates and applications in the usual way. Please note, aggregate\nsequences  in EventStoreDB start from position `0`, so set INITIAL_VERSION\non your aggregate classes accordingly.\n\n```python\nfrom eventsourcing.application import Application\nfrom eventsourcing.domain import Aggregate, event\n\n\nclass TrainingSchool(Application):\n    def register(self, name):\n        dog = Dog(name)\n        self.save(dog)\n        return dog.id\n\n    def add_trick(self, dog_id, trick):\n        dog = self.repository.get(dog_id)\n        dog.add_trick(trick)\n        self.save(dog)\n\n    def get_tricks(self, dog_id):\n        dog = self.repository.get(dog_id)\n        return dog.tricks\n\n\nclass Dog(Aggregate):\n    INITIAL_VERSION = 0\n\n    @event(\'Registered\')\n    def __init__(self, name):\n        self.name = name\n        self.tricks = []\n\n    @event(\'TrickAdded\')\n    def add_trick(self, trick):\n        self.tricks.append(trick)\n```\n\nConfigure the application to use EventStoreDB. Set environment variable\n`PERSISTENCE_MODULE` to `\'eventsourcing_eventstoredb\'`, and set\n`EVENTSTOREDB_URI` to the host and port of your EventStoreDB.\n\n```python\nschool = TrainingSchool(env={\n    "PERSISTENCE_MODULE": "eventsourcing_eventstoredb",\n    "EVENTSTOREDB_URI": "localhost:2113",\n})\n```\n\nIn case you are running against a cluster, or want to use SSL/TLS certificates,\nyou can specify these things in the URI.\n\n```\n    "EVENTSTOREDB_URI": "esdb://localhost:2111,localhost:2112,localhost:2113?tls&rootCertificate=./certs/ca/ca.crt"\n```\n\nThe application\'s methods may be then called, from tests and\nuser interfaces.\n\n```python\ndog_id = school.register(\'Fido\')\nschool.add_trick(dog_id, \'roll over\')\nschool.add_trick(dog_id, \'play dead\')\ntricks = school.get_tricks(dog_id)\nassert tricks == [\'roll over\', \'play dead\']\n```\n\nFor more information, please refer to the Python\n[eventsourcing](https://github.com/johnbywater/eventsourcing) library\nand the [EventStoreDB](https://www.eventstore.com/) project.\n\n## Developers\n\nClone the `eventsourcing-eventstoredb` repository, set up a virtual\nenvironment, and install dependencies.\n\nUse your IDE (e.g. PyCharm) to open the project repository. Create a\nPoetry virtual environment, and then update packages.\n\n    $ make update-packages\n\nAlternatively, use the ``make install`` command to create a dedicated\nPython virtual environment for this project.\n\n    $ make install\n\nStart EventStoreDB.\n\n    $ make start-eventstoredb\n\nRun tests.\n\n    $ make test\n\nAdd tests in `./tests`. Add code in `./eventsourcing_eventstoredb`.\n\nCheck the formatting of the code.\n\n    $ make lint\n\nReformat the code.\n\n    $ make fmt\n\nAdd dependencies in `pyproject.toml` and then update installed packages.\n\n    $ make update-packages\n\nStop EventStoreDB.\n\n    $ make stop-eventstoredb\n',
    'author': 'John Bywater',
    'author_email': 'john.bywater@appropriatesoftware.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/pyeventsourcing/eventsourcing-eventstoredb',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
