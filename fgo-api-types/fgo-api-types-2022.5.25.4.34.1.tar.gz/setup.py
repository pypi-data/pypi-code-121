# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fgo_api_types']

package_data = \
{'': ['*']}

install_requires = \
['orjson>=3,<4', 'pydantic>=1,<2']

setup_kwargs = {
    'name': 'fgo-api-types',
    'version': '2022.5.25.4.34.1',
    'description': 'Provide Pydantic types from FGO API',
    'long_description': '# Types for FGO Game Data API\n\nThis is a package containing the Pydantic definitions of the objects returned by https://api.atlasacademy.io/rapidoc.\n\nExample usage:\n```\nfrom fgo_api_types.enums import Trait\nfrom fgo_api_types.gameenums import SvtType\nfrom fgo_api_types.nice import NiceServant\n\nr = httpx.get("https://api.atlasacademy.io/nice/NA/servant/200")\nfujino = NiceServant.parse_raw(r.content)\n\nassert Trait.genderFemale in fujino.traits\n```',
    'author': 'squaresmile',
    'author_email': 'squaresmile@protonmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://api.atlasacademy.io',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
