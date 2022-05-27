# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['labby',
 'labby.commands',
 'labby.nornir',
 'labby.nornir.plugins',
 'labby.nornir.plugins.inventory',
 'labby.providers',
 'labby.providers.gns3']

package_data = \
{'': ['*'], 'labby': ['templates/*', 'templates/nodes_bootstrap/*']}

install_requires = \
['Jinja2>=3.1.2,<4.0.0',
 'PyYAML>=6.0,<7.0',
 'gns3fy==1.0.0-rc.1',
 'netaddr>=0.8.0,<0.9.0',
 'nornir-scrapli==2020.11.1',
 'nornir>=3.3.0,<4.0.0',
 'pydantic[dotenv]>=1.9.1,<2.0.0',
 'rich>=12.4.1,<13.0.0',
 'scrapli==2020.10.10',
 'toml>=0.10.2,<0.11.0',
 'typer>=0.4.1,<0.5.0']

entry_points = \
{'console_scripts': ['labby = labby.main:app']}

setup_kwargs = {
    'name': 'labby',
    'version': '0.1.0',
    'description': 'CLI tool to build Network Labs in an automated way',
    'long_description': '# Labby\n\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)\n<!-- [![codecov](https://codecov.io/gh/davidban77/labby/branch/develop/graph/badge.svg)](https://codecov.io/gh/davidban77/labby) -->\n<!-- [![Total alerts](https://img.shields.io/lgtm/alerts/g/davidban77/labby.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/davidban77/labby/alerts/) -->\n<!-- [![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/davidban77/labby.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/davidban77/labby/context:python) -->\n[![pypi](https://img.shields.io/pypi/v/labby.svg)](https://pypi.python.org/pypi/labby)\n[![versions](https://img.shields.io/pypi/pyversions/labby.svg)](https://github.com/davidban77/labby)\n[![Develop Tests](https://github.com/davidban77/labby/actions/workflows/tests.yml/badge.svg)](https://github.com/davidban77/labby/actions/workflows/tests.yml)\n[![Develop Docker Build](https://github.com/davidban77/labby/actions/workflows/docker_build.yml/badge.svg)](https://github.com/davidban77/labby/actions/workflows/docker_build.yml)\n\n\nCLI Tool for interacting with Network Simulation systems to build and interact with Network Labs in an automated way.\n\n## 1. Documentation\n\n> **Note**\n> Under Construction...∏\n\n- [Labby](#labby)\n  - [1. Documentation](#1-documentation)\n  - [2. Install](#2-install)\n    - [2.1 Developer version](#21-developer-version)\n    - [2.2 Using labby docker container](#22-using-labby-docker-container)\n  - [3. Requirements](#3-requirements)\n  - [4. How it works](#4-how-it-works)\n    - [4.1 Labby Configuration file](#41-labby-configuration-file)\n    - [4.2 Environments and Providers](#42-environments-and-providers)\n    - [4.3 Projects, Nodes, Templates and Links](#43-projects-nodes-templates-and-links)\n    - [4.4 Labby state file](#44-labby-state-file)\n  - [5. Extra Links](#5-extra-links)\n\n## 2. Install\n\nIt is as simple as\n\n```shell\npip install labby\n```\n\n### 2.1 Developer version\n\nYou will need to use `poetry` to handle installation and dependencies.\n\n```shell\n# Clone the repository\ngit clone https://github.com/davidban77/labby.git\ncd labby\n\n# Start poetry shell and install the dependencies\npoetry shell\npoetry install\n```\n\n### 2.2 Using labby docker container\n\nLabby is also packaged under a container, `davidban77/labby`, based on python-slim image.\n\n```shell\n > docker run -v $HOME/.config/labby/labby.toml:/opt/labby/labby.toml \\\n             -v $HOME/.config/labby/.labby.json:/opt/labby/.labby.json \\\n             -i -t \\\n             davidban77/labby:v0.1.0-py3.8 bash\n```\n\nIt is particularly useful if you don\'t want to setup a virtual environment to install all the dependencies.\n\n---\n\n## 3. Requirements\n\nBesides having the `labby` tool installed, you will need:\n\n- A [**provider**](#51-environments-and-providers). For now the only supported is GNS3.\n- A [**labby configuration file**](#51-labby-configuration-file). Sets the necessary settings for connecting to a provider.\n- `telnet` (for console connection) and/or `ssh` installed. So labby can perform some ad-hoc connections actions if needed.\n\n## 4. How it works\n\nOnce you have the configuration file setup, and `labby` installed on your system then you are good to go!.\n\nThe CLI tool serves multiple purposes, for example it is a way great to discover the projects or network topologies avaiable on the Network Virtualization system, start or stop the nodes, push configuration, etc...\n\nFor examplem to show the available projects and their status in GNS3:\n\n![Projects lists](imgs/labby_projects_lists.png)\n\nNow, let\'s get the details of the network lab `topology-01`:\n\n![Project Detail](imgs/labby_project_detail.png)\n\nIt is a small topology with 2 Arista `ceos` devices connected between each other, and also connected to a `cloud` and `mgmt` switch to allow them to be reachable to the outside world.\n\nThe **Mgmt Address** shows the IP address information for their management interfaces. The setup and configuration of those are explained in the *Docs*.\n\nYou can start the nodes of the entire project one by one, for example:\n\n![Start Project](imgs/labby_start_project.png)\n\nDevices are up and you can check their status and more details:\n\n![Node Detail](imgs/labby_node_detail.png)\n\nYou can connect to the nodes via SSH (if IP address for management is set and is reachable), or you can connect over console if available. For example:\n\n![Connect Router](imgs/labby_connect_router.png)\n\nAnd like this there are many more features...\n\n### 4.1 Labby Configuration file\n\nFor labby to work, you need a configuration file (`labby.toml`) that specifies the [**providers**](#environments-and-providers) you have at your disposal to connect.\n\nBy default `labby` will search for the configuration file at the current directory, if not found it will search at the labby configuration space of the user\'s home directory (`$HOME/.config/labby/labby.toml`)\n\nHere is an example configuration file:\n\n```toml\n[main]\nenvironment = "default"\n\n[environment.default]\nprovider = "home-gns3"\ndescription = "Home lab environment"\n\n    [environment.default.providers.home-gns3]\n    server_url = "http://gns3-server:80"\n    verify_cert = "false"\n    kind = "gns3"\n```\n\n`labby` introduces **providers** which should be seen as the Network Simulation system (a GNS3 server for example), and **environments** which should be seen as the environment where that network simulation is hosted.\n\nThe idea behind this structure is to provide flexibility to use multiple providers and labs in different environments (home lab and/or cloud based).\n\n### 4.2 Environments and Providers\n\n`labby` relies on *`providers`* to interact, create and destroy with the Network Topologies. The provider supported so far is **GNS3** by the use of [`gns3fy`](https://github.com/davidban77/gns3fy).\n\nA *provider* is just a representation of a Network Simulation systems, like a GNS3 server for example.\n\nAn *environment* serves as a construct that holds attributes and multiple *providers*.\n\n### 4.3 Projects, Nodes, Templates and Links\n\nEach **provider** provides **projects** which should be seen as network labs. These projects is where you can create **nodes** based from **templates**, and create **links** to finally build a network topology.\n\nUsing the GNS3 provider as an example:\n\n- A `labby project` is a network topology in GNS3. It needs to start in order to access it.\n- A `labby node` is a network object. This can be a router, switch, container, among others in GNS3.\n- A `labby template` is the base settings to be able to **create a node**. Is where the main information of the **node** is inherited.\n- A `labby link` is a network link in GNS3. It provides a way to connect between 2 nodes and can provide functionality like packet loss or jitter on the link.\n\nLabby is CLI tool to interact with all these entities.\n\n### 4.4 Labby state file\n\n`labby` relies havily on the state of the current **provider** to get information about the objects that interacts with.\n\nNow, labby augments these objects by providing extra attributes and storing them at a central location (`$HOME/.config/labby/.labby.json`).\n\nThese are:\n\n- `labels` which is of an array type, and these can be added at the moment of creation or update.\n- `mgmt_port` Management interface of the **node**, useful for generating bootstrap configuration for the node.\n- `mgmt_ip` Management IP Address of the **node**, useful for generating bootstrap configuration and also connecting to the node.\n\nThe attributes are generally added at the time of the object creation, but they can also be added at a later stage if needed (this is normally done with `labby update` command).\n\n## 5. Extra Links\n\n- [Node Configuration Management](docs/NODE_CONFIGURATION.md)\n',
    'author': 'David Flores',
    'author_email': 'davidflores7_8@hotmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/davidban77/labby',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
