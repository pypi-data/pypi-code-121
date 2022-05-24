# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['vidhash']

package_data = \
{'': ['*'], 'vidhash': ['stubs/*']}

install_requires = \
['ImageHash>=4.2.1,<5.0.0',
 'Pillow>=9.1.1,<10.0.0',
 'ffmpy3>=0.2.4,<0.3.0',
 'numpy>=1.22.4,<2.0.0']

setup_kwargs = {
    'name': 'vidhash',
    'version': '0.1.4',
    'description': 'A package for hashing videos and checking for similarity',
    'long_description': '# Vidhash\n[Vidhash](https://pypi.org/project/vidhash/) is a perceptual video hashing and checking library, to detect similar videos, or videos containing similar scenes.\n\n\n## Todo\n- Code\n  - Ability to ignore blank frames\n  - Ensure hash settings are the same when checking similarity\n  - Wrapper for imagehash.ImageHash\n  - Datastore\n    - (For looking up matching videos from a collection)\n- Documentation\n- Tests\n',
    'author': 'Your Name',
    'author_email': 'you@example.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/SpangleLabs/vidhash',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
