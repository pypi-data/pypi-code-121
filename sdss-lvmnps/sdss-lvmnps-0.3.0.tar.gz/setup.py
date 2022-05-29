# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'python'}

packages = \
['lvmnps',
 'lvmnps.actor',
 'lvmnps.actor.commands',
 'lvmnps.switch',
 'lvmnps.switch.dli',
 'lvmnps.switch.dummy']

package_data = \
{'': ['*'], 'lvmnps': ['etc/*']}

install_requires = \
['click-default-group>=1.2.2,<2.0.0',
 'httpx>=0.18.1,<0.19.0',
 'sdss-clu>=1.0.3,<2.0.0',
 'sdsstools>=0.4.0']

entry_points = \
{'console_scripts': ['lvmnps = lvmnps.__main__:lvmnps']}

setup_kwargs = {
    'name': 'sdss-lvmnps',
    'version': '0.3.0',
    'description': 'A library and actor to communicate with an SDSS-V LVM network power switch',
    'long_description': '# lvmnps\n\n![Versions](https://img.shields.io/badge/python->3.8-blue)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![Documentation Status](https://readthedocs.org/projects/lvmnps/badge/?version=latest)](https://lvmnps.readthedocs.io/en/latest/?badge=latest)\n[![Test](https://github.com/sdss/lvmnps/actions/workflows/test.yml/badge.svg)](https://github.com/sdss/lvmnps/actions/workflows/test.yml)\n[![Docker](https://github.com/sdss/lvmnps/actions/workflows/docker.yml/badge.svg)](https://github.com/sdss/lvmnps/actions/workflows/docker.yml)\n[![codecov](https://codecov.io/gh/sdss/lvmnps/branch/main/graph/badge.svg?token=M0RPGO77JH)](https://codecov.io/gh/sdss/lvmnps)\n\nLVM Network Power Switch\n\n## Features\n\n- CLU Actor based interface\n- Supports a Dummy PDU\n- Supports [iBOOT g2](https://dataprobe.com/iboot-g2/) with python code from [here](https://github.com/dprince/python-iboot)\n- Supports [Digital Loggers Web Power](https://www.digital-loggers.com/lpc7.html) with python code from [here](https://github.com/dwighthubbard/python-dlipower)\n\n\n## Installation\n\nClone this repository.\n\n```console\ngit clone https://github.com/sdss/lvmnps\ncd lvmnps\n```\n\n## Quick Start\n\n### Start the actor\n\nStart `lvmnps` actor.\n\n```console\nlvmnps start\n```\n\nIn another terminal, type `clu` and `lvmnps ping` for test.\n\n```console\nclu\nlvmnps ping\n     07:41:22.636 lvmnps >\n     07:41:22.645 lvmnps : {\n         "text": "Pong."\n         }\n```\n\nStop `lvmnps` actor.\n\n```console\nlvmnps stop\n```\n\n## Config file structure\n\n```yaml\nswitches:\n    name_your_switch_here:    # should be a unique name\n        type: dummy           # currently dummy, iboot, dli\n        num: 8                # number of ports\n        ports:\n            1:\n            name: "skyw.pwi"  # should also be a unique name\n            desc: "Something that make sense"\n    should_be_a_unique_name:\n        type: dummy\n        ports:\n            1:\n            name: "skye.pwi"\n            desc: "PlaneWavemount Skye"\n```\n\n## Status return for all commands\n\n- if `name` is not defined then the port name will be `switch name.port number`, e.g. `nps_dummy_1.port1`. Otherwise `name` from the config file will be used.\n- `STATE: 1: ON, 0: OFF, -1: UNKNOWN`\n\n```yaml\n    "STATUS": {\n    "nps_dummy_1.port1": {\n        "STATE": -1,\n        "DESCR": "was 1",\n        "SWITCH": "nps_dummy_1",\n        "PORT": 1\n    },\n```\n\n## Run the example lvmnps_dummy\n\n```console\ncd lvmnps\npoetry run lvmnps -vvv -c $(pwd)/python/lvmnps/etc/lvmnps_dummy.yml start\n\npoetry run clu\n```\n\n- Status command without parameter returns all ports of all switches.\n- The default is to return only configured ports, otherwise define \'ouo\' false in the config file, see [lvmnps_dummy.yml](https://github.com/sdss/lvmnps/blob/main/python/lvmnps/etc/lvmnps_dummy.yml)\n\n```console\n>>> lvmnps status\n\n12:02:08.649 lvmnps >\n12:02:08.660 lvmnps i {\n    "STATUS": {\n        "nps_dummy_1.port1": {\n            "STATE": -1,\n            "DESCR": "was 1",\n            "SWITCH": "nps_dummy_1",\n            "PORT": 1\n        },\n        "skye.what.ever": {\n            "STATE": -1,\n            "DESCR": "whatever is connected to skye",\n            "SWITCH": "nps_dummy_1",\n            "PORT": 2\n        },\n        "skyw.what.ever": {\n            "STATE": -1,\n            "DESCR": "Something @ skyw",\n            "SWITCH": "nps_dummy_1",\n            "PORT": 4\n        },\n        "skye.pwi": {\n            "STATE": -1,\n            "DESCR": "PlaneWavemount Skye",\n            "SWITCH": "skye.nps",\n            "PORT": 1\n        },\n            "skyw.pwi": {\n            "STATE": -1,\n            "DESCR": "PlaneWavemount Skyw",\n            "SWITCH": "nps_dummy_3",\n            "PORT": 1\n        }\n    }\n}\n```\n\n- status command with port name skyw.what.ever\n\n```console\n>>> lvmnps status skyw.what.ever\n\n12:07:12.349 lvmnps >\n12:07:12.377 lvmnps i {\n    "STATUS": {\n        "skyw.what.ever": {\n            "STATE": -1,\n            "DESCR": "Something @ skyw",\n            "SWITCH": "nps_dummy_1",\n            "PORT": 4\n}\n```\n\n- status command with switch name nps_dummy_1\n\n```console\n>>> lvmnps status nps_dummy_1\n\n12:07:12.349 lvmnps >\n12:12:21.349 lvmnps i {\n    "STATUS": {\n        "nps_dummy_1.port1": {\n            "STATE": -1,\n            "DESCR": "was 1",\n            "SWITCH": "nps_dummy_1",\n            "PORT": 1\n        },\n        "skye.what.ever": {\n            "STATE": -1,\n            "DESCR": "whatever is connected to skye",\n            "SWITCH": "nps_dummy_1",\n            "PORT": 2\n        },\n        "skyw.what.ever": {\n            "STATE": -1,\n            "DESCR": "Something @ skyw",\n            "SWITCH": "nps_dummy_1",\n            "PORT": 4\n        }\n    }\n}\n```\n\n- status command with switch name nps_dummy_1 and port 4 returns\n\n```console\n      lvmnps status nps_dummy_1 4\n\n      12:07:12.349 lvmnps >\n      12:12:21.349 lvmnps i {\n          "STATUS": {\n              "skyw.what.ever": {\n                  "STATE": -1,\n                  "DESCR": "Something @ skyw",\n                  "SWITCH": "nps_dummy_1",\n                  "PORT": 4\n              }\n          }\n      }\n\n\n- the commands on and off use the same addressing scheme as status\n\n## Test\n\n```console\npoetry run pytest\npoetry run pytest -p no:logging -s -vv\n```\n',
    'author': 'Florian Briegel',
    'author_email': 'briegel@mpia.de',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/sdss/lvmnps',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
