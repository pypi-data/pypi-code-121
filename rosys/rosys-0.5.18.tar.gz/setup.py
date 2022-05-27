# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['rosys',
 'rosys.actors',
 'rosys.actors.pathplanning',
 'rosys.automations',
 'rosys.automations.navigation',
 'rosys.communication',
 'rosys.hardware',
 'rosys.test',
 'rosys.ui',
 'rosys.world']

package_data = \
{'': ['*']}

install_requires = \
['aenum>=3.1.5,<4.0.0',
 'aiocache>=0.11.1,<0.12.0',
 'aiohttp>=3.7.4,<4.0.0',
 'aioserial>=1.3.0,<2.0.0',
 'asyncio>=3.4.3,<4.0.0',
 'coloredlogs>=15.0.1,<16.0.0',
 'humanize>=4.0.0,<5.0.0',
 'more-itertools>=8.10.0,<9.0.0',
 'msgpack>=1.0.3,<2.0.0',
 'networkx>=2.6.2,<3.0.0',
 'nicegui==0.7.27',
 'numpy>=1.20.1,<2.0.0',
 'objgraph>=3.5.0,<4.0.0',
 'opencv-contrib-python-headless>=4.5.4,<5.0.0',
 'opencv-python>=4.5.5,<5.0.0',
 'psutil>=5.9.0,<6.0.0',
 'pydantic==1.9',
 'pyloot>=0.0.7,<0.0.8',
 'pyserial>=3.5,<4.0',
 'python-socketio[asyncio_client]>=5.3.0,<6.0.0',
 'requests>=2.25.1,<3.0.0',
 'retry>=0.9.2,<0.10.0',
 'scipy>=1.7.2,<2.0.0',
 'sh>=1.14.2,<2.0.0',
 'simplejson>=3.17.2,<4.0.0',
 'tabulate>=0.8.9,<0.9.0',
 'ujson>=5.1.0,<6.0.0',
 'yappi>=1.3.3,<2.0.0']

setup_kwargs = {
    'name': 'rosys',
    'version': '0.5.18',
    'description': 'Modular Robot System With Elegant Automation Capabilities',
    'long_description': "# RoSys - The Robot System\n\nRoSys provides an easy-to-use robot system.\nIts purpose is similar to [ROS](https://www.ros.org/).\nBut RoSys is fully based on modern web technologies and focusses on mobile robotics.\n\nSee full documentation at [rosys.io](https://rosys.io/).\n\n## Principles\n\n**All Python**\n: Business logic is wired in Python while computation-heavy tasks are encapsulated through websockets or bindings.\n\n**Shared State**\n: All code can access and manipulate a shared and typesafe state -- this does not mean it should.\nGood software design is still necessary.\nBut it is much easier to do if you do not have to perform serialization all the time.\n\n**No Threading**\n: Thanks to [asyncio](https://docs.python.org/3/library/asyncio.html) you can write the business logic without locks and mutex mechanisms.\nThe running system feels like everything is happening in parallel.\nBut each code block is executed one after another through an event queue and yields execution as soon as it waits for I/O or heavy computation.\nThe latter is still executed in threads to not block the rest of the business logic.\n\n**Web UI**\n: Most machines need some kind of human interaction.\nWe made sure your robot can be operated fully off the grid with any web browser by incorporating [NiceGUI](https://nicegui.io/).\nIt is also possible to proxy the user interface through a gateway for remote operation.\n\n**Simulation**\n: Robot hardware is often slower than your own computer.\nTherefore RoSys supports a simulation mode for rapid development.\nTo get maximum performance the current implementation does not run a full physics engine.\n\n**Testing**\n: You can use pytest to write high-level integration tests.\nIt is based on the above-described simulation mode and accelerates the robot's time for super fast execution.\n",
    'author': 'Zauberzeug GmbH',
    'author_email': 'info@zauberzeug.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/zauberzeug/rosys',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
