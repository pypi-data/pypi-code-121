# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['axie_utils']

package_data = \
{'': ['*']}

install_requires = \
['trezor[hidapi]>=0.13.0,<0.14.0', 'web3>=5.25.0,<6.0.0']

setup_kwargs = {
    'name': 'axie-utils',
    'version': '2.1.0',
    'description': 'Library that provides the functionality you need to build your own axie Infinity python tools',
    'long_description': '# Axie Utils Library\n\nAim of this library is to contain all the actions one might want to do when building tools around the Axie Infinity videogame. It started with me building an automation tool and needing to build different solutions. Extracting this functionality allows for that easily.\n\n**NOTE: Only v1 of this library uses free tx, from v2 and onwards all transactions consume RON. That is due to now free tx being much more rare to have available.**\n\n\n# Installation\n\nInstall and update using pip:\n\n```\npip install -U axie-utils\n```\n\n# Simple Example\n\nThis example would send 100 SLP from `ronin:from_where_to_send_SLP` to `ronin:to_where_we_send_SLP`.\n\n``` python\nfrom axie_utils import Payment\n\np = Payment(\n    "Testing Account",\n    "ronin:from_where_to_send_SLP",\n    "0x:private_key_from_the_from_acc",\n    "ronin:to_where_we_send_SLP",\n    100)\n\np.execute()\n```\n\nThis example, shows how we would claim SLP from an account.\n\n``` python\nfrom axie_utils import Claim\n\nc = Claim(\n    "Testing Account",\n    "ronin:acc_to_claim",\n    "0x:private_key_from_acc_to_claim"\n)\nc.execute()\n\n```\n\n# Documentation\n\nFor furhter documentation, please visit this [link](https://ferranmarin.github.io/axie-utils-lib/).\n',
    'author': 'Ferran Marin',
    'author_email': 'ferran.marin.llobet@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://ferranmarin.github.io/axie-utils-lib/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
