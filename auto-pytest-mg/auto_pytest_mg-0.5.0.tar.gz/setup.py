# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['auto_pytest_mg']

package_data = \
{'': ['*']}

install_requires = \
['inflection>=0.5.1,<0.6.0', 'rich>=12.4.4,<13.0.0', 'typer[all]>=0.4.0,<0.5.0']

extras_require = \
{':python_version < "3.8"': ['importlib_metadata>=4.5.0,<5.0.0']}

entry_points = \
{'console_scripts': ['auto_pytest_mg = auto_pytest_mg.__main__:app']}

setup_kwargs = {
    'name': 'auto-pytest-mg',
    'version': '0.5.0',
    'description': 'Awesome `auto_pytest_mg` is a Python cli/package created with https://github.com/TezRomacH/python-package-template',
    'long_description': '# auto_pytest_mg (Automatic pytest Mock Generator)\n\n<div align="center">\n\n[![Python Version](https://img.shields.io/pypi/pyversions/auto_pytest_mg.svg)](https://pypi.org/project/auto_pytest_mg/)\n[![Dependencies Status](https://img.shields.io/badge/dependencies-up%20to%20date-brightgreen.svg)](https://github.com/rozelie/auto_pytest_mg/pulls?utf8=%E2%9C%93&q=is%3Apr%20author%3Aapp%2Fdependabot)\n\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n![Coverage Report](assets/images/coverage.svg)\n</div>\n\n- GitHub: [https://github.com/rozelie/auto_pytest_mg](https://github.com/rozelie/auto_pytest_mg)\n- GitHub Releases: [https://github.com/rozelie/auto_pytest_mg/releases](https://github.com/rozelie/auto_pytest_mg/releases)\n- PyPi: [https://pypi.org/project/auto-pytest-mg/](https://pypi.org/project/auto-pytest-mg/)\n\nauto_pytest_mg parses the AST of an input python file to generate a new test file with boilerplate\ntest functions. Rendered tests include the `mocker` and `mg` fixtures which are available via the \n[pytest-mock](https://pypi.org/project/pytest-mock/) and [pytest-mocker-generator](https://pypi.org/project/pytest-mock-generator/) \npackages, respectively.  \n\n\n## Usage\n```bash\n# install the package\npip install auto_pytest_mg\n\n# go to project\'s source root\ncd my_project\n\n# pass the file to generate tests for\nauto_pytest_mg my_project/my_file.py\n```\n\n## Example\n\nSource file located at `my_project/my_file.py`\n```python\n# my_project/my_file.py\nfrom dataclasses import dataclass\n\n\n@dataclass\nclass DataClass:\n    a: str\n    b: int\n\n    @property\n    def property_(self) -> None:\n        ...\n\n    def method(self) -> None:\n        ...\n\n    def method_with_args(self, a: int, b: str) -> None:\n        ...\n\ndef a_function():\n    ...\n```\n\nRunning `auto_pytest_mg my_project/my_file.py` then generates `my_project/test_my_file.py`:\n\n```python\n# my_project/test_my_file.py\nimport pytest\n\nfrom my_project.my_file import a_function, DataClass\n\n\n@pytest.fixture\ndef data_class(mocker):\n    a = mocker.MagicMock()\n    b = mocker.MagicMock()\n    return DataClass(a=a, b=b)\n\n\nclass TestDataClass:\n    def test__init__(self, mocker):\n        a = mocker.MagicMock()\n        b = mocker.MagicMock()\n\n        return DataClass(a=a, b=b)\n\n    def test_property_(self, mocker, mg, data_class):\n        mg.generate_uut_mocks_with_asserts(data_class.property_)\n\n        result = data_class.property_\n\n    def test_method(self, mocker, mg, data_class):\n        mg.generate_uut_mocks_with_asserts(data_class.method)\n\n        result = data_class.method()\n\n    def test_method_with_args(self, mocker, mg, data_class):\n        a = mocker.MagicMock()\n        b = mocker.MagicMock()\n        mg.generate_uut_mocks_with_asserts(data_class.method_with_args)\n\n        result = data_class.method_with_args(a=a, b=b)\n\n\ndef test_a_function(mocker, mg):\n    mg.generate_uut_mocks_with_asserts(a_function)\n\n    result = a_function()\n```\n\n# Development\n\n## Makefile usage\n\n[`Makefile`](https://github.com/rozelie/auto_pytest_mg/blob/master/Makefile) contains a lot of functions for faster development.\n\n<details>\n<summary>1. Download and remove Poetry</summary>\n<p>\n\nTo download and install Poetry run:\n\n```bash\nmake poetry-download\n```\n\nTo uninstall\n\n```bash\nmake poetry-remove\n```\n\n</p>\n</details>\n\n<details>\n<summary>2. Install all dependencies and pre-commit hooks</summary>\n<p>\n\nInstall requirements:\n\n```bash\nmake install\n```\n\nPre-commit hooks coulb be installed after `git init` via\n\n```bash\nmake pre-commit-install\n```\n\n</p>\n</details>\n\n<details>\n<summary>3. Codestyle</summary>\n<p>\n\nAutomatic formatting uses `pyupgrade`, `isort` and `black`.\n\n```bash\nmake format\n```\n\nCodestyle checks only, without rewriting files:\n\n```bash\nmake check-format\n```\n\n> Note: `check-format` uses `isort`, `black` and `darglint` library\n\nUpdate all dev libraries to the latest version using one comand\n\n```bash\nmake update-dev-deps\n```\n\n<details>\n<summary>4. Code security</summary>\n<p>\n\n```bash\nmake check-safety\n```\n\nThis command launches `Poetry` integrity checks as well as identifies security issues with `Safety` and `Bandit`.\n\n```bash\nmake check-safety\n```\n\n</p>\n</details>\n\n</p>\n</details>\n\n<details>\n<summary>5. Type checks</summary>\n<p>\n\nRun `mypy` static type checker\n\n```bash\nmake mypy\n```\n\n</p>\n</details>\n\n<details>\n<summary>6. Tests with coverage badges</summary>\n<p>\n\nRun `pytest`\n\n```bash\nmake test\n```\n\n</p>\n</details>\n\n<details>\n<summary>7. All linters</summary>\n<p>\n\nOf course there is a command to ~~rule~~ run all linters in one:\n\n```bash\nmake lint\n```\n\nthe same as:\n\n```bash\nmake test && make check-format && make mypy && make check-safety\n```\n\n</p>\n</details>\n\n<details>\n<summary>8. Docker</summary>\n<p>\n\n```bash\nmake docker-build\n```\n\nwhich is equivalent to:\n\n```bash\nmake docker-build VERSION=latest\n```\n\nRemove docker image with\n\n```bash\nmake docker-remove\n```\n\nMore information [about docker](https://github.com/rozelie/auto_pytest_mg/tree/master/docker).\n\n</p>\n</details>\n\n<details>\n<summary>9. Cleanup</summary>\n<p>\nDelete pycache files\n\n```bash\nmake pycache-remove\n```\n\nRemove package build\n\n```bash\nmake build-remove\n```\n\nDelete .DS_STORE files\n\n```bash\nmake dsstore-remove\n```\n\nRemove .mypycache\n\n```bash\nmake mypycache-remove\n```\n\nOr to remove all above run:\n\n```bash\nmake cleanup\n```\n\n</p>\n</details>\n\n## Build and Release\n\nBuilding a new version of the application contains steps:\n\n1. Bump the version of your package `poetry version {(major|minor|patch)}`\n1. `git add pyproject.toml`\n1. Commit and push `git commit -m "Updating to version: v{version}"`\n1. Create a release on GitHub\n1. `poetry publish --build`\n\n\n## 🛡 License\n\nThis project is licensed under the terms of the `MIT` license. See [LICENSE](https://github.com/rozelie/auto_pytest_mg/blob/master/LICENSE) for more details.\n\n\n## Credits [![🚀 Your next Python package needs a bleeding-edge project structure.](https://img.shields.io/badge/python--package--template-%F0%9F%9A%80-brightgreen)](https://github.com/TezRomacH/python-package-template)\n\nThis project was generated with [`python-package-template`](https://github.com/TezRomacH/python-package-template)\n',
    'author': 'auto_pytest_mg',
    'author_email': 'ryan.ozelie@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/auto_pytest_mg/auto_pytest_mg',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
