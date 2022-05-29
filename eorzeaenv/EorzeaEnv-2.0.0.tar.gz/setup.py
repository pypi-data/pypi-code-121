# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': '.'}

packages = \
['EorzeaEnv', 'EorzeaEnv.Data']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.19.2,<2.0.0', 'rapidfuzz>=2.0.11,<3.0.0']

extras_require = \
{':python_version >= "3.6" and python_version < "3.7"': ['dataclasses>=0.8,<0.9']}

setup_kwargs = {
    'name': 'eorzeaenv',
    'version': '2.0.0',
    'description': 'Final Fantasy XIV weather & time tools.',
    'long_description': "[![Pypi](https://img.shields.io/pypi/v/eorzeaenv.svg?style=flat-square)](https://pypi.org/project/EorzeaEnv/)\n[![Pypi](https://img.shields.io/pypi/pyversions/eorzeaenv.svg?style=flat-square)](https://pypi.org/project/EorzeaEnv/)\n[![Build Status](https://img.shields.io/endpoint.svg?url=https%3A%2F%2Factions-badge.atrox.dev%2FEltonChou%2FEorzeaEnv%2Fbadge&style=flat-square)](https://github.com/EltonChou/EorzeaEnv/actions)\n![PyPI - Downloads](https://img.shields.io/pypi/dm/EorzeaEnv?style=flat-square)\n\n# EorzeaEnv\n\n+ [CHANGELOG](https://github.com/EltonChou/EorzeaEnv/blob/master/CHANGELOG.md)\n\n## Installation\n```\npip install eorzeaenv\n```\n\n## Usage\n```py\nfrom EorzeaEnv import EorzeaLang, EorzeaTime, EorzeaWeather, EorzeaPlaceName\n```\n\n### Eorzea Time\n\n```sh\n>>> EorzeaTime.now()\n'EorzeaTime(Sixth Embral Moon, 11, 21, 56, Phase:0.50, Althyk)'\n\n>>> EorzeaTime.now().moon\n'Sixth Embral Moon'\n\n>>> EorzeaTime.now().sun\n11\n\n>>> EorzeaTime.now().hour\n21\n\n>>> EorzeaTime.now().minute\n56\n\n>>> EorzeaTime.now().phase\n0.50\n\n>>> EorzeaTime.now().guardian\n'Althyk'\n```\n\n### Weather Forecast\n+ Using period as tuple or list\n```python\n# defalut step value is 5\n# This method return a generator if you need to re-use it save the values as `tuple` or `list`.\nt = tuple(EorzeaTime.weather_period(step=3))\n\n# Use EorzeaPlaceName to ensure the place is valid or\n# you can directly pass the place string to forecast.\nplace_name = EorzeaPlaceName('Eureka Pyros')\n\n# Defalut lang is 'en'\n# Defalut strict is `True` for strict mode `False` for fuzzy mode.\n# eg. `eurekaa puros` is valid in fuzzy mode.\n\n# In fuzzy mode, you can set the cutoff score to prevent unexpected place name to be passed.\n# default value is 80. (100 >= value >= 0)\nEorzeaWeather.set_fuzzy_cutoff(95)\n\nweather_en = EorzeaWeather.forecast(place_name, t, strict=True)\nweather_ja = EorzeaWeather.forecast(place_name, t, lang=EorzeaLang.JA, strict=True)\nweather_de = EorzeaWeather.forecast(place_name, t, lang=EorzeaLang.DE, strict=True)\nweather_fr = EorzeaWeather.forecast(place_name, t, lang=EorzeaLang.FR, strict=True)\n```\n```sh\n>>> print(weather_en)\n['Thunder', 'Snow', 'Blizzards']\n\n>>> print(weather_ja)\n['雷', '雪', '吹雪']\n\n>>> print(weather_de)\n['Gewittrig', 'Schnee', 'Schneesturm']\n\n>>> print(weather_fr)\n['Orages', 'Neige', 'Blizzard']\n```\n+ Using period in for-loop\n```py\nweather_en = []\nfor t in EorzeaTime.weather_period(step=3):\n    w = EorzeaWeather.forecast('Eureka Pyros', t)\n    weather_en.append(w)\n```\n```sh\n>>> print(weather_en)\n['Thunder', 'Snow', 'Blizzards']\n```\n+ Using period generator directly\n```py\nweather = EorzeaWeather.forecast('Eureka Pyros', EorzeaTime.weather_period(step=3))\n```\n```sh\n>>> print(weather_en)\n['Thunder', 'Snow', 'Blizzards']\n```\n+ Also support float type\n```py\nweather = EorzeaWeather.forecast('Eureka Pyros', 1603644000.0)\n```\n```sh\n>>> print(weather)\n'Thunder'\n```\n\n### Eorzea place name\n\nAn instance of EorzeaPlaceName would be always a valid place name in this pacakge.\n\nAn invalid place name will raises `InvalidEorzeaPlaceName` error.\n\n```py\nplace_name = EorzeaPlaceName(\n    'The Ruby Sea',\n    # `False` to fuzzy mode, default is `True`\n    strict=True,\n    # Stricted scope for validation of place name.\n    # default is all supports locale.\n    locale_scopes=[\n        EorzeaLang.EN,\n        EorzeaLang.JA,\n        EorzeaLang.FR,\n        EorzeaLang.DE],\n    # Used in fuzzy mode to cut-off the result under the score.\n    # default is `80`.\n    fuzzy_cutoff=80\n)\n```\n```sh\n>>> place_name\nEorrzeaPlaceName('The Ruby Sea')\n\n>>> print(place_name)\n'The Ruby Sea`\n```\n\nBelowings are valid place names in strict mode with full locale scopes (default settings).\n```py\nEorzeaPlaceName('The Ruby Sea') # valid `The Ruby Sea`\nEorzeaPlaceName('the ruby sea') # valid `The Ruby Sea`\nEorzeaPlaceName('ruby sea') # valid `The Ruby Sea`\nEorzeaPlaceName('rubinsee') # valid `Rubinsee`\nEorzeaPlaceName('紅玉海') # valid `紅玉海`\n```\n\nWith stricted scopes.\n```py\nscopes = [EorzeaLang.JA, EorzeaLang.DE]\n\nEorzeaPlaceName('The Ruby Sea', locale_scopes=scopes) # raises error\nEorzeaPlaceName('the ruby sea', locale_scopes=scopes) # raises error\nEorzeaPlaceName('ruby sea', locale_scopes=scopes) # raises error\nEorzeaPlaceName('rubinsee', locale_scopes=scopes) # valid `Rubinsee`\nEorzeaPlaceName('紅玉海', locale_scopes=scopes) # valid `紅玉海`\n```\n\nIn fuzzy mode.\n```py\nEorzeaPlaceName('the ruby see', strict=False) # valid `The Ruby Sea`\nEorzeaPlaceName('ruby see', strict=False) # valid `The Ruby Sea`\nEorzeaPlaceName('rubisee', strict=False) # valid `Rubinsee`\nEorzeaPlaceName('紅玉貝', strict=False) # raises error\nEorzeaPlaceName('紅玉貝', strict=False, fuzzy_cutoff=66) # valid `紅玉海`\n```\n\n### Errors\n```py\nfrom EorzeaEnv.errors import \\\n    EorzeaEnvError, \\\n    InvalidEorzeaPlaceName, \\\n    WeatherRateDataError\n```\n`EorzeaEnvError` is base exception.\nOther exceptions are inherited from it.\n\n\n## Thanks\n- [Rogueadyn-SaintCoinach](https://github.com/Rogueadyn/SaintCoinach)\n",
    'author': 'Elton Chou',
    'author_email': 'plscd748@gmail.com',
    'maintainer': 'Elton Chou',
    'maintainer_email': 'plscd748@gmail.com',
    'url': 'https://github.com/EltonChou/EorzeaEnv',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6,<3.10',
}


setup(**setup_kwargs)
