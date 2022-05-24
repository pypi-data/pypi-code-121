# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['boxjelly',
 'boxjelly.commands',
 'boxjelly.delegates',
 'boxjelly.lib',
 'boxjelly.models',
 'boxjelly.scripts',
 'boxjelly.ui',
 'boxjelly.ui.graphicsitems',
 'boxjelly.ui.settings',
 'boxjelly.ui.settings.tabs',
 'boxjelly.ui.track',
 'boxjelly.ui.video']

package_data = \
{'': ['*'], 'boxjelly': ['assets/*', 'assets/icons/*', 'assets/images/*']}

install_requires = \
['dataclasses-json>=0.5.7,<0.6.0',
 'intervaltree>=3.1.0,<4.0.0',
 'pyqt5>=5.15,<6.0',
 'sharktopoda-client>=0.1.4,<0.2.0']

entry_points = \
{'console_scripts': ['boxjelly = boxjelly.scripts.run:main']}

setup_kwargs = {
    'name': 'boxjelly',
    'version': '0.1.3',
    'description': 'BoxJelly is a tool for viewing and editing object tracks in video.',
    'long_description': '# BoxJelly\n\n**BoxJelly** is a tool for viewing and editing object tracks in video.\n\n[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)\n[![Python](https://img.shields.io/badge/language-Python-blue.svg)](https://www.python.org/downloads/)\n\n![BoxJelly logo](boxjelly/assets/images/boxjelly_logo_128.png)\n\nAuthor: Kevin Barnard, [kbarnard@mbari.org](mailto:kbarnard@mbari.org)\n\n---\n\n## Cthulhu Integration\n\nThis branch is for the [Cthulhu](https://github.com/mbari-media-management/cthulhu) integration. This integration is still in development. Currently, the integration has some limitations:\n\n- Cthulhu does not report video framerate, so a default of 29.97 is assumed. This is configurable in the settings (Ctrl+,).\n- Cthulhu must be running before you load a video/track file in BoxJelly.\n\n## Install\n\n### From PyPI\n\nBoxJelly is available on PyPI as `boxjelly`. To install, run:\n\n```bash\npip install boxjelly\n```\n\n### From source\n\nThis project is build with Poetry. To install from source, run (in the project root):\n\n```bash\npoetry install\n```\n\n## Run\n\nOnce BoxJelly is installed, you can run it from the command line:\n\n```bash\nboxjelly\n```\n\n---\n\nCopyright &copy; 2021&ndash;2022 [Monterey Bay Aquarium Research Institute](https://www.mbari.org)\n',
    'author': 'Kevin Barnard',
    'author_email': 'kbarnard@mbari.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
