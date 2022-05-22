# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ehrapy',
 'ehrapy.anndata',
 'ehrapy.core',
 'ehrapy.data',
 'ehrapy.io',
 'ehrapy.plot',
 'ehrapy.preprocessing',
 'ehrapy.preprocessing.encoding',
 'ehrapy.tools',
 'ehrapy.tools.nlp',
 'ehrapy.util']

package_data = \
{'': ['*'], 'ehrapy.preprocessing': ['laboratory_reference_tables/*']}

install_requires = \
['Jinja2>=3.0.1',
 'PyYAML>=5.4.1',
 'anndata>=0.7.8',
 'camelot-py[base]>=0.10.1',
 'category_encoders>=2.2.2',
 'click>=7.0.0',
 'deep-translator>=1.6.1',
 'deepl>=1.2.0',
 'fancyimpute>=0.7.0',
 'ipython>=7.30.1',
 'leidenalg>=0.8.7',
 'lifelines>=0.27.0,<0.28.0',
 'miceforest>=5.3.0',
 'mudata',
 'pandas>=1.3.3',
 'pyhpo[all]>=3.0.0',
 'pynndescent>=0.5.4',
 'pypi-latest>=0.1.1',
 'questionary>=1.10.0',
 'requests>=2.26.0',
 'rich>=10.12.0',
 'scanpy>=1.8.2',
 'scikit-learn>=1.0',
 'scikit-misc>=0.1.4',
 'session-info>=1.0.0']

extras_require = \
{'medcat': ['medcat>=1.2.6'],
 'scikit-learn-intelex': ['scikit-learn-intelex>=2021.5.3']}

entry_points = \
{'console_scripts': ['ehrapy = ehrapy.__main__:main']}

setup_kwargs = {
    'name': 'ehrapy',
    'version': '0.2.0',
    'description': 'Electronic Health Record Analysis with Python.',
    'long_description': '[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![Build](https://github.com/theislab/ehrapy/workflows/Build%20ehrapy%20Package/badge.svg)](https://github.com/theislab/ehrapy/actions?workflow=Package)\n[![Codecov](https://codecov.io/gh/theislab/ehrapy/branch/master/graph/badge.svg)](https://codecov.io/gh/theislab/ehrapy)\n[![License](https://img.shields.io/github/license/theislab/ehrapy)](https://opensource.org/licenses/Apache2.0)\n[![PyPI](https://img.shields.io/pypi/v/ehrapy.svg)](https://pypi.org/project/ehrapy/)\n[![Python Version](https://img.shields.io/pypi/pyversions/ehrapy)](https://pypi.org/project/ehrapy)\n[![Read the Docs](https://img.shields.io/readthedocs/ehrapy/latest.svg?label=Read%20the%20Docs)](https://ehrapy.readthedocs.io/)\n[![Test](https://github.com/theislab/ehrapy/workflows/Run%20ehrapy%20Tests/badge.svg)](https://github.com/theislab/ehrapy/actions?workflow=Tests)\n[![PyPI](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)\n\n<img src="https://user-images.githubusercontent.com/21954664/156930990-0d668468-0cd9-496e-995a-96d2c2407cf5.png" alt="ehrapy logo">\n\n# ehrapy overview\n\n<img src="https://user-images.githubusercontent.com/21954664/150370356-9f9b170d-76d1-4376-9fd7-54f9f3fb2ae4.png" alt="ehrapy overview">\n\n## Features\n\n-   Exploratory analysis of Electronic Health Records\n-   Quality control & preprocessing\n-   Clustering & trajectory inference\n-   Visualization & Exploration\n\n## Installation\n\nYou can install _ehrapy_ via [pip] from [PyPI]:\n\n```console\n$ pip install ehrapy\n```\n\n## Usage\n\nPlease see the [Usage documentation][usage] for details.\n\n```python\nimport ehrapy as ep\n```\n\n## Credits\n\nThis package was created with [cookietemple] using [Cookiecutter] based on [Hypermodern_Python_Cookiecutter].\n\n[cookiecutter]: https://github.com/audreyr/cookiecutter\n[cookietemple]: https://cookietemple.com\n[hypermodern_python_cookiecutter]: https://github.com/cjolowicz/cookiecutter-hypermodern-python\n[pip]: https://pip.pypa.io/\n[pypi]: https://pypi.org/\n[usage]: https://ehrapy.readthedocs.io/en/latest/usage/usage.html\n',
    'author': 'Lukas Heumos',
    'author_email': 'lukas.heumos@posteo.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/theislab/ehrapy',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.8.0,<4',
}


setup(**setup_kwargs)
