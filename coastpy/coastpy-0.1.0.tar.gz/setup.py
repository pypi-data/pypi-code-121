# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['coastpy', 'coastpy.geometries']

package_data = \
{'': ['*']}

install_requires = \
['geopandas>=0.10.2,<0.11.0', 'pygeos>=0.12.0,<0.13.0']

setup_kwargs = {
    'name': 'coastpy',
    'version': '0.1.0',
    'description': 'Python tools for Coastal Monitoring with Remote Sensing data',
    'long_description': '# coastpy\n\nCoastal Monitoring with Remote Sensing \n\n## Installation\n\n```bash\n$ pip install coastpy\n```\n\n## Usage\n\n- TODO\n\n## Contributing\n\nInterested in contributing? Check out the contributing guidelines. Please note that this project is released with a Code of Conduct. By contributing to this project, you agree to abide by its terms.\n\n## License\n\n`coastpy` was created by Floris Calkoen. It is licensed under the terms of the MIT license.\n\n## Credits\n\n`coastpy` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).\n',
    'author': 'Floris Calkoen',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
