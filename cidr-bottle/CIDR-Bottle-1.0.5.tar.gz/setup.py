# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cidr_bottle']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'cidr-bottle',
    'version': '1.0.5',
    'description': 'CIDR-Bottle is yet another Patricia Trie implementation, however this one is specifically designed for parsing and validating CIDRS in routing tables and ROAs.',
    'long_description': '# CIDR-Bottle\n![Release Badge](https://gitlab.com/geoip.network/cidr_bottle/-/badges/release.svg)\n![Pipeline Badge](https://gitlab.com/geoip.network/cidr_bottle/badges/main/pipeline.svg)\n\nCIDR-Bottle is yet another implementation of a Patricia Trie for handling network routing information (such as ROAs & Routing Tables) for reconciliation.\nHowever, unlike other implementations it supports both sub-tree checking and longest-prefix matching.\n\n![An attractive screenshot of the example code below](https://gitlab.com/geoip.network/cidr_bottle/-/raw/a57fe64864d8b05d71dde9ba32687319ca4fdbb8/screenshots/screenshot.png)\n\nCIDR-Bottle was designed specifically to be used for reconciling RIR Allocation & Assignment records with actual BGP Announcements.\nIt isn\'t designed to be the fastest (it\'s written in pure python), but it should be the most full-featured implementation. \nThat said, unless you\'re writing a routing engine in python (in which case I\'d be really interested to know why), speed shouldn\'t be a significant issue.\n\n## Usage\n### Initialisation\nBy default, a CIDR-Bottle is in IPv4 mode, to use IPv6 mode you must supply an IPv6 CIDR.\n\nThe root Bottle does not need to be the entire IP space, it can be any subnet.\n```python\nfrom cidr_bottle import Bottle\nfrom ipaddress import IPv4Network, IPv6Network\n\n## Defaults to IPv4\nroot = Bottle()  # 0.0.0.0/0\n\n## IPv6 mode is initialised by passing an IPv6 CIDR (either as an instance of ipaddress.IPv6Network) \nroot6 = Bottle(prefix=IPv6Network("::/0"))  # ::/0\n\n## Supports detached (not starting at either 0.0.0.0/0 or ::/0) roots\ndetached_root = Bottle(prefix=IPv4Network("198.51.100.0/24"))\n```\n\n### Racking a Bottle (Inserting a node)\n```python\n## Supports insert with str\nroot.insert("198.51.100.0/24")\n\n## Supports insert with instances of ipaddress.IPv4Network\nroot.insert(IPv4Network("198.51.100.0/24"))\n\n## Supports insert with instances of ipaddress.IPv6Network\nroot.insert(IPv6Network("2001:db8::/48"))\n\n## Supports attaching any json serializable objects to nodes **This is important for future planned releases**\nroot.insert("198.51.100.0/24", {"example": "dict"})\nroot.insert("198.51.100.0/24", "string example")\n\n## Supports dict-style indexing\nroot["198.51.100.0/24"] = "string example"\n```\n\n### Contains CIDR?\nReturns `True` where there is a covering prefix, otherwise false.\n*NOTE: This means that it returns true 100% of the time when the root is `0.0.0.0/0` or `::/0`*\n```python\nif "198.51.100.0/24" in root:\n    ## do something\n### or\nif root.contains("198.51.100.0/24"):\n    ## do something\n```\nYou can enforce exact matches by passing `exact=True` to the `contains` method.\n```python\nif not root.contains("198.51.100.128/25", exact=True):\n    ## do something\n```\n\n### Drinking a Bottle (Get node)\nThis will return a matching covering prefix if present. \nIn the case of a detached root, this means that it can return `None` if no such covering prefix exists.\n*NOTE: This is longest prefix matching*\n```python\nprint(root["198.51.100.0/24"])\n### or\nprint(root.get("198.51.100.0/24"))\n```\nSimilar to the `.contains(...)` method, you can enforce exact matches by passing `exact=True` to the `get` method. \nThis will raise a `KeyError` if there is no exact match.\n```python\nprint(root.get("198.51.100.128/25"), exact=True)  # will raise a KeyError("no exact match found")\n```\n\n### Children / Sub-Tree checking\nWith CIDR-Bottle you can retrieve all the defined children of a bottle(node).\n```python\nroot.insert("198.51.100.0/25")\nroot.insert("198.51.100.128/25")\nprint(root["198.51.100.0/24"].children())\n```\n\n### Smashing bottles (Deleting Nodes)\nDeleting an edge node removes it completely.\n\nDeleting an intermediate node, converts it into a "passing" node, and does not affect any descendants of that node.\n```python\ndel root["198.51.100.0/24"]\n### or\nroot.delete("198.51.100.0/24")\n```\n\n\n## Installation (from pip):\n```shell\npip install cidr_bottle\n```\n\n## Installation (from source):\n```shell\ngit clone https://gitlab.com/geoip.network/cidr_bottle\npoetry install\n```',
    'author': 'Tim Armstrong',
    'author_email': 'tim@plaintextnerds.com',
    'maintainer': 'Tim Armstrong',
    'maintainer_email': 'tim@plaintextnerds.com',
    'url': 'https://geoip.network/',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
