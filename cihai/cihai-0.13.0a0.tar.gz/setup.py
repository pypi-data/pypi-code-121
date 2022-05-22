# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cihai', 'cihai.data', 'cihai.data.decomp', 'cihai.data.unihan']

package_data = \
{'': ['*']}

install_requires = \
['appdirs', 'kaptan', 'sqlalchemy<1.4', 'unihan-etl>=0.14.0a0,<0.15.0']

extras_require = \
{'cli': ['cihai-cli>=0.9.0a0,<0.10.0']}

setup_kwargs = {
    'name': 'cihai',
    'version': '0.13.0a0',
    'description': 'Library for CJK (chinese, japanese, korean) language data.',
    'long_description': '# cihai\n\nPython library for [CJK](https://cihai.git-pull.com/glossary.html#term-cjk) (chinese, japanese,\nkorean) data\n\n[![Python Package](https://img.shields.io/pypi/v/cihai.svg)](https://pypi.org/project/cihai/)\n[![Docs](https://github.com/cihai/cihai/workflows/docs/badge.svg)](https://cihai.git-pull.com/)\n[![Build Status](https://github.com/cihai/cihai/workflows/tests/badge.svg)](https://github.com/cihai/cihai/actions?query=workflow%3A%22tests%22)\n[![Code Coverage](https://codecov.io/gh/cihai/cihai/branch/master/graph/badge.svg)](https://codecov.io/gh/cihai/cihai)\n[![License](https://img.shields.io/github/license/cihai/cihai.svg)](https://github.com/cihai/cihai/blob/master/LICENSE)\n\nThis project is under active development. Follow our progress and check back for updates!\n\n## Quickstart\n\n### API / Library (this repository)\n\n```console\n$ pip install --user cihai\n```\n\n```python\nfrom cihai.core import Cihai\n\nc = Cihai()\n\nif not c.unihan.is_bootstrapped:  # download and install Unihan to db\n    c.unihan.bootstrap(unihan_options)\n\nquery = c.unihan.lookup_char(\'好\')\nglyph = query.first()\nprint("lookup for 好: %s" % glyph.kDefinition)\n# lookup for 好: good, excellent, fine; well\n\nquery = c.unihan.reverse_char(\'good\')\nprint(\'matches for "good": %s \' % \', \'.join([glph.char for glph in query]))\n# matches for "good": 㑘, 㑤, 㓛, 㘬, 㙉, 㚃, 㚒, 㚥, 㛦, 㜴, 㜺, 㝖, 㤛, 㦝, ...\n```\n\nSee [API](https://cihai.git-pull.com/api.html) documentation and\n[/examples](https://github.com/cihai/cihai/tree/master/examples).\n\n### CLI ([cihai-cli](https://cihai-cli.git-pull.com))\n\n```console\n$ pip install --user cihai[cli]\n```\n\n```console\n# character lookup\n$ cihai info 好\nchar: 好\nkCantonese: hou2 hou3\nkDefinition: good, excellent, fine; well\nkHangul: 호\nkJapaneseOn: KOU\nkKorean: HO\nkMandarin: hǎo\nkTang: \'*xɑ̀u *xɑ̌u\'\nkTotalStrokes: \'6\'\nkVietnamese: háo\nucn: U+597D\n\n# reverse lookup\n$ cihai reverse library\nchar: 圕\nkCangjie: WLGA\nkCantonese: syu1\nkCihaiT: \'308.302\'\nkDefinition: library\nkMandarin: tú\nkTotalStrokes: \'13\'\nucn: U+5715\n--------\n```\n\n### UNIHAN data\n\nAll datasets that cihai uses have stand-alone tools to export their data. No library required.\n\n- [unihan-etl](https://unihan-etl.git-pull.com) - [UNIHAN](http://unicode.org/charts/unihan.html)\n  data exports for csv, yaml and json.\n\n## Developing\n\n[poetry](https://python-poetry.org/) is a required package to develop.\n\n`git clone https://github.com/cihai/cihai.git`\n\n`cd cihai`\n\n`poetry install -E "docs test coverage lint format"`\n\nMakefile commands prefixed with `watch_` will watch files and rerun.\n\n### Tests\n\n`poetry run py.test`\n\nHelpers: `make test` Rerun tests on file change: `make watch_test` (requires\n[entr(1)](http://eradman.com/entrproject/))\n\n### Documentation\n\nDefault preview server: <http://localhost:8035>\n\n`cd docs/` and `make html` to build. `make serve` to start http server.\n\nHelpers: `make build_docs`, `make serve_docs`\n\nRebuild docs on file change: `make watch_docs` (requires [entr(1)](http://eradman.com/entrproject/))\n\nRebuild docs and run server via one terminal: `make dev_docs` (requires above, and a `make(1)` with\n`-J` support, e.g. GNU Make)\n\n### Formatting / Linting\n\nThe project uses [black](https://github.com/psf/black) and [isort](https://pypi.org/project/isort/)\n(one after the other) and runs [flake8](https://flake8.pycqa.org/) via CI. See the configuration in\n<span class="title-ref">pyproject.toml</span> and \\`setup.cfg\\`:\n\n`make black isort`: Run `black` first, then `isort` to handle import nuances `make flake8`, to watch\n(requires `entr(1)`): `make watch_flake8`\n\n### Releasing\n\nAs of 0.10, [poetry](https://python-poetry.org/) handles virtualenv creation, package requirements,\nversioning, building, and publishing. Therefore there is no setup.py or requirements files.\n\nUpdate <span class="title-ref">\\_\\_version\\_\\_</span> in <span\nclass="title-ref">\\_\\_about\\_\\_.py</span> and \\`pyproject.toml\\`:\n\n    git commit -m \'build(cihai): Tag v0.1.1\'\n    git tag v0.1.1\n    git push\n    git push --tags\n    poetry build\n    poetry deploy\n\n## Quick links\n\n- [Quickstart](https://cihai.git-pull.com/quickstart.html)\n- [Datasets](https://cihai.git-pull.com/datasets.html) a full list of current and future data sets\n- Python [API](https://cihai.git-pull.com/api.html)\n- [Roadmap](https://cihai.git-pull.com/design-and-planning/)\n- Python support: >= 3.6, pypy\n- Source: <https://github.com/cihai/cihai>\n- Docs: <https://cihai.git-pull.com>\n- Changelog: <https://cihai.git-pull.com/history.html>\n- API: <https://cihai.git-pull.com/api.html>\n- Issues: <https://github.com/cihai/cihai/issues>\n- Test coverage: <https://codecov.io/gh/cihai/cihai>\n- pypi: <https://pypi.python.org/pypi/cihai>\n- OpenHub: <https://www.openhub.net/p/cihai>\n- License: MIT\n',
    'author': 'Tony Narlock',
    'author_email': 'tony@git-pull.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://cihai.git-pull.com',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
