# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cihai_cli']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=3.12,<6', 'cihai>=0.12.0,<0.14.0', 'click>=7']

entry_points = \
{'console_scripts': ['cihai = cihai_cli.cli:cli']}

setup_kwargs = {
    'name': 'cihai-cli',
    'version': '0.9.0a0',
    'description': 'Command line frontend for the cihai CJK language library',
    'long_description': '# cihai-cli\n\nCommand line interface to the [cihai](https://cihai.git-pull.com)\n[CJK](https://cihai.git-pull.com/glossary.html#term-cjk)-language library\n\n[![Python Package](https://img.shields.io/pypi/v/cihai_cli.svg)](https://pypi.org/project/cihai-cli/)\n[![Docs](https://github.com/cihai/cihai-cli/workflows/docs/badge.svg)](https://cihai-cli.git-pull.com/)\n[![Build Status](https://github.com/cihai/cihai-cli/workflows/tests/badge.svg)](https://github.com/cihai/cihai-cli/actions?query=workflow%3A%22tests%22)\n[![Code Coverage](https://codecov.io/gh/cihai/cihai-cli/branch/master/graph/badge.svg)](https://codecov.io/gh/cihai/cihai-cli)\n[![License](https://img.shields.io/github/license/cihai/cihai-cli.svg)](https://github.com/cihai/cihai-cli/blob/master/LICENSE)\n\nThis project is under active development. Follow our progress and check back for updates!\n\n## Installation\n\n```console\n$ pip install --user cihai[cli]\n```\n\n### Developmental releases\n\nYou can test the unpublished version of cihai-cli before its released.\n\n- [pip](https://pip.pypa.io/en/stable/):\n\n  ```console\n  $ pip install --user --upgrade --pre cihai[cli]\n  ```\n\n- [pipx](https://pypa.github.io/pipx/docs/):\n\n  ```console\n  $ pipx install --suffix=@next \'cihai[cli]\' --pip-args \'\\--pre\' --include-deps --force\n  ```\n\n  Then use `cihai@next info 好`.\n\nFor more information see\n[developmental releases](https://cihai-cli.git-pull.com/quickstart.html#developmental-releases)\n\n## Character lookup\n\nSee [CLI](https://cihai-cli.git-pull.com/cli.html) in the documentation for full usage information.\n\n```console\n$ cihai info 好\nchar: 好\nkCantonese: hou2 hou3\nkDefinition: good, excellent, fine; well\nkHangul: 호\nkJapaneseOn: KOU\nkKorean: HO\nkMandarin: hǎo\nkTang: \'*xɑ̀u *xɑ̌u\'\nkTotalStrokes: \'6\'\nucn: U+597D\n\n# retrieve all character information (including book indices)\n$ cihai info 好 -a\nchar: 好\nkCangjie: VND\nkCantonese: hou2 hou3\nkCihaiT: \'378.103\'\nkDefinition: good, excellent, fine; well\nkFenn: 552A\nkFourCornerCode: \'4744.7\'\nkFrequency: \'1\'\nkGradeLevel: \'1\'\nkHKGlyph: 0871\nkHangul: 호\nkHanyuPinlu: hǎo(6060) hāo(142) hào(115)\nkHanyuPinyin: 21028.010:hǎo,hào\nkJapaneseKun: KONOMU SUKU YOI\nkJapaneseOn: KOU\nkKorean: HO\nkMandarin: hǎo\nkPhonetic: \'481\'\nkRSAdobe_Japan1_6: C+1975+38.3.3 C+1975+39.3.3\nkRSKangXi: \'38.3\'\nkTang: \'*xɑ̀u *xɑ̌u\'\nkTotalStrokes: \'6\'\nkVietnamese: háo\nkXHC1983: 0445.030:hǎo 0448.030:hào\nucn: U+597D\n```\n\n## Reverse lookup\n\n```console\n$ cihai reverse library\nchar: 圕\nkCantonese: syu1\nkDefinition: library\nkJapaneseOn: TOSHOKAN SHO\nkMandarin: tú\nkTotalStrokes: \'13\'\nucn: U+5715\n--------\nchar: 嫏\nkCantonese: long4\nkDefinition: the place where the supreme stores his books; library\nkJapaneseOn: ROU\nkMandarin: láng\nkTotalStrokes: \'11\'\nucn: U+5ACF\n--------\n```\n\n## Developing\n\n[poetry](https://python-poetry.org/) is a required package to develop.\n\n`git clone https://github.com/cihai/cihai-cli.git`\n\n`cd cihai-cli`\n\n`poetry install -E "docs test coverage lint format"`\n\nMakefile commands prefixed with `watch_` will watch files and rerun.\n\n### Tests\n\n`poetry run py.test`\n\nHelpers: `make test` Rerun tests on file change: `make watch_test` (requires\n[entr(1)](http://eradman.com/entrproject/))\n\n### Documentation\n\nDefault preview server: <http://localhost:8037>\n\n`cd docs/` and `make html` to build. `make serve` to start http server.\n\nHelpers: `make build_docs`, `make serve_docs`\n\nRebuild docs on file change: `make watch_docs` (requires [entr(1)](http://eradman.com/entrproject/))\n\nRebuild docs and run server via one terminal: `make dev_docs` (requires above, and a `make(1)` with\n`-J` support, e.g. GNU Make)\n\n### Formatting / Linting\n\nThe project uses [black](https://github.com/psf/black) and [isort](https://pypi.org/project/isort/)\n(one after the other) and runs [flake8](https://flake8.pycqa.org/) via CI. See the configuration in\n<span class="title-ref">pyproject.toml</span> and \\`setup.cfg\\`:\n\n`make black isort`: Run `black` first, then `isort` to handle import nuances `make flake8`, to watch\n(requires `entr(1)`): `make watch_flake8`\n\n### Releasing\n\nAs of 0.6, [poetry](https://python-poetry.org/) handles virtualenv creation, package requirements,\nversioning, building, and publishing. Therefore there is no setup.py or requirements files.\n\nUpdate <span class="title-ref">\\_\\_version\\_\\_</span> in <span\nclass="title-ref">\\_\\_about\\_\\_.py</span> and \\`pyproject.toml\\`:\n\n    git commit -m \'build(cihai-cli): Tag v0.1.1\'\n    git tag v0.1.1\n    git push\n    git push --tags\n    poetry build\n    poetry deploy\n\n## Quick links\n\n- [Quickstart](https://cihai-cli.git-pull.com/quickstart.html)\n- Python [API](https://cihai-cli.git-pull.com/api.html)\n- [2017 roadmap](https://cihai.git-pull.com/design-and-planning/2017/spec.html)\n- Python support: >= 3.7, pypy\n- Source: <https://github.com/cihai/cihai-cli>\n- Docs: <https://cihai-cli.git-pull.com>\n- Changelog: <https://cihai-cli.git-pull.com/history.html>\n- API: <https://cihai-cli.git-pull.com/api.html>\n- Issues: <https://github.com/cihai/cihai-cli/issues>\n- Test coverage <https://codecov.io/gh/cihai/cihai-cli>\n- pypi: <https://pypi.python.org/pypi/cihai-cli>\n- OpenHub: <https://www.openhub.net/p/cihai-cli>\n- License: MIT\n',
    'author': 'Tony Narlock',
    'author_email': 'tony@git-pull.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://cihai-cli.git-pull.com',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
