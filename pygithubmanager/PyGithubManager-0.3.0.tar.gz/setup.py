# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['pygithubmanager',
 'pygithubmanager.modules',
 'pygithubmanager.ui',
 'pygithubmanager.ui.widgets',
 'pygithubmanager.utils',
 'pygithubmanager.widgets']

package_data = \
{'': ['*'], 'pygithubmanager': ['resources/icons/*']}

install_requires = \
['GitPython>=3.1.27,<4.0.0',
 'PyGithub>=1.55,<2.0',
 'PySide6>=6.3.0,<7.0.0',
 'QtAwesome>=1.1.1,<2.0.0',
 'matplotlib>=3.5.2,<4.0.0',
 'pygit2>=1.9.2,<2.0.0']

setup_kwargs = {
    'name': 'pygithubmanager',
    'version': '0.3.0',
    'description': 'GitHub desktop version created with Python',
    'long_description': '[![Stargazers][stars-shield]][stars-url]\n[![Issues][issues-shield]][issues-url]\n[![MIT License][license-shield]][license-url]\n\n# GitHub Manager\n\nGitHub desktop version created with Python and PySide6.\n\n## Installation\n\n```bash\n$ pip install pygithubmanager\n```\n\n## Usage\n\n- TODO\n\n## Contributing\n\nInterested in contributing? Check out the contributing guidelines. Please note that this project is released with a Code of Conduct. By contributing to this project, you agree to abide by its terms.\n\n## License\n\n`githubmanager` was created by DomiTP. It is licensed under the terms of the GNU General Public License v3.0 license.\n\n## Credits\n\n`githubmanager` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).\n\n<!-- MARKDOWN LINKS & IMAGES -->\n[stars-shield]: https://img.shields.io/github/stars/DomiTP/GitHubManager.svg?style=for-the-badge\n[stars-url]: https://github.com/DomiTP/GitHubManager/stargazers\n[issues-shield]: https://img.shields.io/github/issues/DomiTP/GitHubManager.svg?style=for-the-badge\n[issues-url]: https://github.com/DomiTP/GitHubManager/issues\n[license-shield]: https://img.shields.io/github/license/DomiTP/GitHubManager.svg?style=for-the-badge\n[license-url]: https://github.com/DomiTP/GitHubManager/blob/master/LICENSE.md',
    'author': 'DomiTP',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<3.11',
}


setup(**setup_kwargs)
