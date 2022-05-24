# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pyfltr']

package_data = \
{'': ['*']}

install_requires = \
['black',
 'flake8-bugbear',
 'isort>=5.0',
 'joblib',
 'mypy',
 'pylint>=2.12',
 'pyproject-flake8',
 'pytest',
 'pyupgrade',
 'tomli']

entry_points = \
{'console_scripts': ['pyfltr = pyfltr.pyfltr:main']}

setup_kwargs = {
    'name': 'pyfltr',
    'version': '1.2.1',
    'description': 'Python Formatters, Linters, and Testers Runner.',
    'long_description': '# pyfltr: Python Formatters, Linters, and Testers Runner.\n\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![Lint&Test](https://github.com/ak110/pyfltr/actions/workflows/python-app.yml/badge.svg)](https://github.com/ak110/pyfltr/actions/workflows/python-app.yml)\n[![PyPI version](https://badge.fury.io/py/pyfltr.svg)](https://badge.fury.io/py/pyfltr)\n\nPythonの各種ツールをまとめて呼び出すツール。\n\n- Formatters\n    - pyupgrade\n    - isort\n    - black\n- Linters\n    - pflake8 + flake8-bugbear\n    - mypy\n    - pylint\n- Testers\n    - pytest\n\n## コンセプト\n\n- 各種ツールをまとめて呼び出したい\n- 各種ツールのバージョンにはできるだけ依存したくない (ので設定とかは面倒見ない)\n- exclude周りは各種ツールで設定方法がバラバラなのでできるだけまとめて解消したい (のでpyfltr側で解決してツールに渡す)\n- blackやisortはファイルを修正しつつエラーにもしたい (CIとかを想定) (pyupgradeはもともとそういう動作)\n- Q: pysenでいいのでは？ A: それはそう\n\n## インストール\n\n```shell\n$ pip install pyfltr\n```\n\n## 主な使い方\n\n### 通常\n\n```shell\n$ pyfltr [files and/or directories ...]\n```\n\n対象を指定しなければカレントディレクトリを指定したのと同じ扱い。\n\n指定したファイルやディレクトリの配下のうち、pytest以外は`*.py`のみ、pytestは`*_test.py`のみに対して実行される。\n\n終了コード:\n\n- 0: Formattersによるファイル変更無し、かつLinters/Testersでのエラー無し\n- 1: 上記以外\n\n### 特定のツールのみ実行\n\n```shell\n$ pyfltr --commands=pyupgrade,isort,black,pflake8,mypy,pylint,pytest [files and/or directories ...]\n```\n\nカンマ区切りで実行するツールだけ指定する。\n\n## 設定\n\n`pyproject.toml`で設定する。\n\n### 例\n\n```toml\n[tool.pyfltr]\npyupgrade-args = ["--py38-plus"]\npylint-args = ["--jobs=4"]\nextend-exclude = ["foo", "bar.py"]\n```\n\n### 設定項目\n\n設定項目と既定値は`pyfltr --generate-config`で確認可能。\n\n- {command} : コマンドの有効/無効\n- {command}-path : 実行するコマンド\n- {command}-args : 追加のコマンドライン引数\n- exclude : 除外するファイル名/ディレクトリ名パターン(既定値あり)\n- extend-exclude : 追加で除外するファイル名/ディレクトリ名パターン(既定値は空)\n\n## 各種設定例\n\n### pyproject.toml\n\n```toml\n[tool.poetry.dev-dependencies]\npyfltr = "*"\n\n[tool.pyfltr]\npyupgrade-args = ["--py38-plus"]\npylint-args = ["--jobs=4"]\n\n[tool.isort]\n# https://black.readthedocs.io/en/stable/guides/using_black_with_other_tools.html#isort\n# https://pycqa.github.io/isort/docs/configuration/options.html\nprofile = "black"\n\n[tool.black]\n# https://black.readthedocs.io/en/stable/usage_and_configuration/the_basics.html\ntarget-version = [\'py38\']\nskip-magic-trailing-comma = true\n\n[tool.flake8]\n# https://black.readthedocs.io/en/stable/guides/using_black_with_other_tools.html#flake8\n# https://flake8.pycqa.org/en/latest/user/configuration.html\nmax-line-length = 88\nextend-ignore = "E203,"\n\n[tool.mypy]\n# https://mypy.readthedocs.io/en/stable/config_file.html\nallow_redefinition = true\ncheck_untyped_defs = true\nignore_missing_imports = true\nstrict_optional = true\nstrict_equality = true\nwarn_no_return = true\nwarn_redundant_casts = true\nwarn_unused_configs = true\nshow_error_codes = true\n\n[tool.pytest.ini_options]\n# https://docs.pytest.org/en/latest/reference/reference.html#ini-options-ref\naddopts = "--showlocals -p no:cacheprovider"\n```\n\n### .pre-commit-config.yaml\n\n```yaml\n  - repo: local\n    hooks:\n      - id: system\n        name: pyfltr\n        entry: poetry run pyfltr --commands=pyupgrade,isort,black,pflake8\n        types: [python]\n        require_serial: true\n        language: system\n```\n\n### CI\n\n```yaml\n  - poetry install --no-interaction\n  - poetry run pyfltr\n```\n',
    'author': 'aki.',
    'author_email': 'mark@aur.ll.to',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ak110/pyfltr',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
