# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['LevityDash',
 'LevityDash.lib',
 'LevityDash.lib.Geometry',
 'LevityDash.lib.Geometry.Grid',
 'LevityDash.lib.plugins',
 'LevityDash.lib.plugins.builtin',
 'LevityDash.lib.plugins.builtin.WeatherFlow',
 'LevityDash.lib.plugins.schema',
 'LevityDash.lib.plugins.web',
 'LevityDash.lib.ui',
 'LevityDash.lib.ui.frontends',
 'LevityDash.lib.ui.frontends.PySide',
 'LevityDash.lib.ui.frontends.PySide.Modules',
 'LevityDash.lib.ui.frontends.PySide.Modules.AttributeEditor',
 'LevityDash.lib.ui.frontends.PySide.Modules.Containers',
 'LevityDash.lib.ui.frontends.PySide.Modules.Displays',
 'LevityDash.lib.ui.frontends.PySide.Modules.Handles',
 'LevityDash.lib.utils']

package_data = \
{'': ['*'],
 'LevityDash': ['example-config/config.ini',
                'example-config/fonts/*',
                'example-config/fonts/Nunito/*',
                'example-config/fonts/Nunito/static/*',
                'example-config/plugins/*',
                'example-config/plugins/Govee/*',
                'example-config/saves/dashboards/*',
                'example-config/templates/dashboards/defaultOM.levity',
                'example-config/templates/dashboards/defaultOM.levity',
                'example-config/templates/dashboards/defaultOM.levity',
                'example-config/templates/dashboards/defaultWF.levity',
                'example-config/templates/dashboards/defaultWF.levity',
                'example-config/templates/dashboards/defaultWF.levity',
                'example-config/templates/dashboards/empty.levity',
                'example-config/templates/dashboards/empty.levity',
                'example-config/templates/dashboards/empty.levity',
                'example-config/templates/panels/*']}

install_requires = \
['PySide2>=5.15.2,<6.0.0',
 'PyYAML>=6.0,<7.0',
 'WeatherUnits>=0.5.3,<0.6.0',
 'aiohttp>=3.8.1,<4.0.0',
 'appdirs>=1.4.4,<2.0.0',
 'bleak>=0.14.2,<0.15.0',
 'numpy>=1.18.0,<2.0.0',
 'pylunar>=0.6.0,<0.7.0',
 'pysolar>=0.10,<0.11',
 'python-dateutil>=2.8.2,<3.0.0',
 'pytz>=2022.1,<2023.0',
 'qasync>=0.23.0,<0.24.0',
 'rich>=12.3.0,<13.0.0',
 'scipy>=1.8.0,<2.0.0']

entry_points = \
{'console_scripts': ['LevityDash = LevityDash:__main__.run']}

setup_kwargs = {
    'name': 'levitydash',
    'version': '0.1.0b6',
    'description': 'A lightweight, desktop native, multi-source, modulear dashboard for macOS, Windows and Linux',
    'long_description': '<p align="center">\n\t<p align="center">\n   <img width="200" height="200" src="https://github.com/noblecloud/LevityDash/raw/gh-pages/docs/_images/favicons/android-chrome-512x512.png" alt="Logo">\n  </p>\n\t<h1 align="center" color="505050">\n\t\t<strong><b>LevityDash</b></strong>\n\t</h1>\n  <p align="center">\n  \tA lightweight, desktop native, multisource dashboard for macOS, Windows and Linux\n  </p>\n</p>\n\n![Screenshot](https://user-images.githubusercontent.com/6209052/166817312-8401c7dc-f1c9-47c0-b99d-d24b4280d560.png)\n\nLevityDash aims to be a lightweight, desktop native, multisource dashboard without a required web frontend. The current version only supports PySide2/Qt. However, a key goal of this project is to support multiple frontends and\nplatforms, including embedded.\n\n*Note: This project is very much in the proof of concept stage – it functions, but it is far from the goal of a lightweight dashboard.*\n\n<p align="right">\n<img src="https://img.shields.io/badge/license-MIT-blueviolet">\n<img src="https://img.shields.io/badge/Python-3.10-blueviolet">\n<img src="https://img.shields.io/badge/aiohttp-3.6-blueviolet">\n<img src="https://img.shields.io/badge/PySide2-5.12-blueviolet">\n\n</p>\n\n# Current Features\n\n## Backend\n\n- Plugin system for adding new sources\n- Scheduling API pulls\n- Data/key maps for automatically parsing ingested data\n- Unit library for automatic localization/conversion\n- Conditional value updates. i.e. if wind speed is zero do not log the wind direction\n\n### Data Sources\n\n- REST API Pull\n- Sockets (UDP, websocket, socket.io)\n- BLE Advertisements\n\n### Builtin Plugins\n\n- [Open-Meteo](https://open-meteo.com) [REST]\n- [WeatherFlow Tempest](https://tempestwx.com) [REST, UDP, Websocket(incomplete)]\n- Govee BLE Thermometers/Hygrometers [[GVH5102](https://www.amazon.com/Govee-Hygrometer-Thermometer-Temperature-Notification/dp/B087313N8F?th=1)]\n\n## Frontend\n\n- Drag and drop dashboard design (This can be a little funky at times)\n- YAML based dashboard specifications with support for both absolute and relative size/positioning\n- Module grouping\n- Editable Margins for text modules\n- Resizable graph figures\n- Custom, value mapped, gradients for figure items\n- Text filters (i.e. lower, title, upper, digit to ordinal, etc.)\n\n## Current Modules\n\n- Realtime single line text with support for showing units and titles and mapping glyphs/emojis to values\n- Timeseries Graph\n- Customizable Clock\n- Moon Phase\n- Submodule Group for organizing modules\n\n## Planned Modules\n\n- Gauges [nearly complete]\n- Weather Radar\n- Multiline Text\n- RSS Feeds\n- Calendar\n- Mini Graphs\n- More plot types\n',
    'author': 'noblecloud',
    'author_email': 'git@noblecloud.io',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://levitydash.app',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<3.11',
}


setup(**setup_kwargs)
