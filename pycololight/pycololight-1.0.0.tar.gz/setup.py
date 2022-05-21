# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pycololight']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'pycololight',
    'version': '1.0.0',
    'description': 'A Python3 wrapper for interacting with LifeSmart Cololight',
    'long_description': '# pycololight\n\nA Python3 wrapper for interacting with LifeSmart Cololight\n\n## Usage\n\n```python\nfrom pycololight import PyCololight\n\nlight = PyCololight(host="1.1.1.1")\n\n# Turn on at 60% brightness\nlight.on = 60\n\n# Set brightness to 70%\nlight.brightness = 70\n\n# Set light colour\nlight.colour = (255, 127, 255)\n\n# Set effect\nlight.effect = "Sunrise"\n\n# Create custom effect\nlight.add_custom_effect(\n  name="custom effect",\n  colour_scheme="Shadow",\n  colour="Red, Yellow",\n  cycle_speed=11,\n  mode=1\n)\n\n# Turn off\nlight.on = 0\n```\n\nMapping of modes for custom effects can be found [here](https://github.com/BazaJayGee66/pycololight/blob/main/MODES.md)\n',
    'author': 'BazaJayGee66',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/BazaJayGee66/pycololight',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
