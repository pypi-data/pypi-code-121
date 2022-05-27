# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['hipopy']

package_data = \
{'': ['*']}

install_requires = \
['awkward>=1.3.0,<2.0.0', 'hipopybind>=0.0.6,<0.0.7', 'numpy>=1.19.2,<2.0.0']

setup_kwargs = {
    'name': 'hipopy',
    'version': '1.0.1',
    'description': 'UpROOT-Like I/O Interface for CLAS12 HIPO Files',
    'long_description': '# HIPOPy: UpROOT-like I/O Interface for CLAS12 HIPO Files\n\n## Installation\n\nTo install from source:\n```bash\ngit clone https://github.com/mfmceneaney/hipopy.git\n```\n\nThen add to following to your startup script:\n```bash\nexport PYTHONPATH=$PYTHONPATH:/path/to/hipopy\n```\nYou will also need to install the project dependencies:\n* [numpy](https://numpy.org)\n* [awkward](https://awkward-array.readthedocs.io/en/latest/)\n* [hipopybind](https://github.com/mfmceneaney/hipopybind.git)\n\n(All available with pip.)\n\nTo install with pip:\n```bash\npip install hipopy\n```\n\n## Getting Started\n\nCheck out the example scripts in `tutorials`.  More functionality coming soon!\n\n## Documentation\n\nFull documentation available on [Read the Docs](https://hipopy.readthedocs.io/en/latest/index.html)!\n\n#\n\nContact: matthew.mceneaney@duke.edu\n',
    'author': 'Matthew McEneaney',
    'author_email': 'matthew.mceneaney@duke.edu',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/mfmceneaney/hipopy.git',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.3,<4.0.0',
}


setup(**setup_kwargs)
