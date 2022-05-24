# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['qualang_tools',
 'qualang_tools.addons',
 'qualang_tools.analysis',
 'qualang_tools.bakery',
 'qualang_tools.config',
 'qualang_tools.config.server',
 'qualang_tools.control_panel']

package_data = \
{'': ['*']}

install_requires = \
['dash-bootstrap-components>=1.0.0,<2.0.0',
 'dash-core-components>=2.0.0,<3.0.0',
 'dash-cytoscape>=0.3.0,<0.4.0',
 'dash-dangerously-set-inner-html>=0.0.2,<0.0.3',
 'dash-html-components>=2.0.0,<3.0.0',
 'dash-table>=5.0.0,<6.0.0',
 'dash>=2.0.0,<3.0.0',
 'docutils>=0.14.0',
 'matplotlib>=3.4.2,<4.0.0',
 'numpy>=1.20.3,<2.0.0',
 'pandas>=1.2.4,<2.0.0',
 'qm-qua>=0.3.2,<0.4.0',
 'scipy>=1.7.1,<2.0.0',
 'waitress>=2.0.0,<3.0.0']

extras_require = \
{'interplot': ['dill>=0.3.4,<0.4.0',
               'pypiwin32>=223,<224',
               'ipython>=7.31.1,<8.0.0']}

setup_kwargs = {
    'name': 'qualang-tools',
    'version': '0.9.0',
    'description': 'The qualang_tools package includes various tools related to QUA programs in Python',
    'long_description': "![PyPI](https://img.shields.io/pypi/v/qualang-tools)\n[![discord](https://img.shields.io/discord/806244683403100171?label=QUA&logo=Discord&style=plastic)](https://discord.gg/7FfhhpswbP)\n\n[![License](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)\n\n# QUA Language Tools\n\nThe QUA language tools package includes various tools useful while writing QUA programs and performing experiments.\n\nIt includes:\n\n* [Bakery](qualang_tools/bakery/README.md) - This library introduces a new framework for creating arbitrary waveforms and\nstoring them in the usual configuration file. It allows defining waveforms in a QUA-like manner while working with 1ns resolution (or higher).\n\n* [Interactive Plot Library](qualang_tools/addons/README.md) - This package drastically extends the capabilities of matplotlib,\nenables easily editing various parts of the figure, copy-pasting data between figures and into spreadsheets, \nfitting the data and saving the figures.\n\n* [Config Tools](qualang_tools/config/README.md) - This package includes tools related to the QOP configuration file, including:\n  * [Integration Weights Tools](README_integration_weights_tools.md) - This package includes tools for the creation and manipulation of integration weights. \n  * [Waveform Tools](README_waveform_tools.md) - This package includes tools for creating waveforms useful for experiments with the QOP.\n  * [Config GUI](README_config_GUI.md) - This package contains a GUI for creating and visualizing the configuration file.\n  * [Config Builder](README_config_builder.md) - This package contains an API for creating and manipulation configuration files.\n\n* [Control Panel](qualang_tools/control_panel/README.md)- This package includes tools for directly controlling the OPX.\n  * [ManualOutputControl](README_manual_output_control.md) - This module allows controlling the outputs from the OPX in CW mode. Once created, it has an API for defining which channels are on. Analog channels also have an API for defining their amplitude and frequency.\n  * [VNA](README_vna.md) - This module allows to configure the OPX as a VNA for a given element (readout resonator for instance) and operation (readout pulse for instance) already defined in the configuration. Once created, it has an API for defining which measurements are to be run depending on the down-conversion solution used (ED: envelope detector, IR: image rejection mixer, IQ: IQ mixer).\n\n## Installation\n\nInstall the current version using `pip`, the `--upgrade` flag ensures that you will get the latest version.\n\n```commandline\npip install --upgrade qualang-tools\n```\n\n## Support and Contribution\nHave an idea for another tool? A way to improve an existing one? Found a bug in our code?\n\nWe'll be happy if you could let us know by opening an [issue](https://github.com/qua-platform/py-qua-tools/issues) on the [GitHub repository](https://github.com/qua-platform/py-qua-tools).\n\nFeel like contributing code to this library? We're thrilled! Please follow [this guide](https://github.com/qua-platform/py-qua-tools/blob/main/CONTRIBUTING.md) and feel free to contact us if you need any help, you can do it by opening an [issue](https://github.com/qua-platform/py-qua-tools/issues) :)\n\n## Usage\n\nExamples for using various tools can be found on the [QUA Libraries Repository](https://github.com/qua-platform/qua-libs).\n\nExamples for using the Baking toolbox, including 1-qubit randomized benchmarking, cross-entropy benchmark (XEB), high sampling rate baking and more can be found [here](https://github.com/qua-platform/qua-libs/tree/main/examples/bakery).\n",
    'author': 'QM',
    'author_email': 'qua-libs@quantum-machines.co',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/qua-platform/py-qua-tools',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7.1,<3.10',
}


setup(**setup_kwargs)
