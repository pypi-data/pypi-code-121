# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sigmadsp',
 'sigmadsp.application',
 'sigmadsp.communication',
 'sigmadsp.generated',
 'sigmadsp.generated.backend_service',
 'sigmadsp.hardware',
 'sigmadsp.helper']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0',
 'RPi.GPIO>=0.7.1,<0.8.0',
 'grpcio>=1.44.0,<2.0.0',
 'protobuf>=3.20.1,<4.0.0',
 'retry>=0.9.2,<0.10.0',
 'smbus2>=0.4.1,<0.5.0',
 'spidev>=3.5,<4.0']

entry_points = \
{'console_scripts': ['sigmadsp = sigmadsp.application.frontend:main',
                     'sigmadsp-backend = sigmadsp.application.backend:main']}

setup_kwargs = {
    'name': 'sigmadsp',
    'version': '1.6.0',
    'description': 'A package for controlling Analog Devices Sigma DSP chipsets.',
    'long_description': '[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit) [![pre-commit.ci status](https://results.pre-commit.ci/badge/github/elagil/sigmadsp/main.svg)](https://results.pre-commit.ci/latest/github/elagil/sigmadsp/main)\n# Analog Devices Sigma DSP control software\n\nThis software package is a Python application, which controls Analog Devices\ndigital signal processor ([DSP](https://en.wikipedia.org/wiki/Digital_signal_processor)) chipsets. It exposes a TCP server for\nconnecting with SigmaStudio, allowing to upload new applications to the DSP, as well as debugging it. Essentially, it\nbehaves like a wired debug probe, but with an Ethernet connection. This source code was inspired by [the original TCP service](https://wiki.analog.com/resources/tools-software/linux-software/sigmatcp),\nas well as the [hifiberry-dsp](https://github.com/hifiberry/hifiberry-dsp) project.\n\nHowever, this application was written completely from scratch, in an effort to make it more efficient, stable, and faster.\n\nThis software package contains two separate components: a backend service, as well as a frontend interface. It is meant\nto run on single-board computers that connect to an Analog Devices DSP via the serial peripheral interface ([SPI](https://en.wikipedia.org/wiki/Serial_Peripheral_Interface)).\n\n## Backend service\n\nThe backend service is the core application, which\n- connects to the DSP via SPI,\n- exposes a TCP interface towards SigmaStudio,\n- and provides a remote procedure call (RPC) interface, based on [grpc](https://grpc.io/).\n\nWith the latter, a frontend can connect to the backend service and control it remotely.\n\n## Frontend interface\n\nThe frontend interface connects to the RPC service of the backend, allowing the user to control\nsettings via a command-line interface (CLI).\n\n## Supported chipsets\n\nThis is not an extensive list, but only comprises chips that are tested or likely compatible.\n\nDSP|Status|Backend settings `dsp_type`\n---|---|--\n[ADAU145X](https://www.analog.com/media/en/technical-documentation/data-sheets/ADAU1452_1451_1450.pdf) | Fully tested (ADAU1452) | `adau14xx`\n[ADAU146X](https://www.analog.com/media/en/technical-documentation/data-sheets/ADAU1463-1467.pdf) | Untested, register compatible with ADAU145X | `adau14xx`\n\n## Installation\n:zap: **Running the installation will overwrite your existing configuration.** For upgrading, see [Upgrading](#upgrading)!\n\nFor installing, please install git first, then clone this repository and run the installation script.\n\n```bash\nsudo apt install git &&\ngit clone https://github.com/elagil/sigma-dsp.git &&\ncd sigma-dsp &&\n./install.sh\n```\n\nThe script installs the Python package, which includes the `sigmadsp-backend` (the backend) and `sigmadsp` (the frontend) executables.\nIt also sets up a system service, which runs `sigmadsp-backend` in the background.\n\n## Upgrading\n\nFor upgrading, the installation procedure can be repeated, but will overwrite the current configuration file.\n\nInstead, simply upgrade the Python package and restart the backend service:\n\n```bash\nsudo pip3 install sigmadsp --upgrade &&\nsudo systemctl restart sigmadsp-backend.service\n```\n\n\n## Removal\n\nFrom within the previously cloned repository folder `sigma-dsp` run\n\n```bash\n./uninstall.sh\n```\n\n## Configuration\n\nConfiguration of `sigmadsp` is done via a `*.yaml` file, which is created during installation. Its default path is `/var/lib/config.yaml`.\n\n## Usage\n\nFor a list of commands that can be emitted by the frontend, simply type\n\n```bash\nsigmadsp -h\n```\n',
    'author': 'Adrian Figueroa',
    'author_email': 'elagil@takanome.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/elagil/sigmadsp',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
