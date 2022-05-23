# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['gha_stats']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.7.4,<4.0.0',
 'cachetools>=5.1.0,<6.0.0',
 'gidgethub>=5.0.1,<6.0.0',
 'matplotlib>=3.5.2,<4.0.0',
 'more-itertools>=8.13.0,<9.0.0',
 'pandas>=1.4.2,<2.0.0',
 'peewee>=3.14.10,<4.0.0',
 'pysqlite3>=0.4.7,<0.5.0',
 'python-dateutil>=2.8.2,<3.0.0',
 'python-dotenv>=0.17.1,<0.18.0',
 'rich>=12.4.2,<13.0.0',
 'typer>=0.4.1,<0.5.0']

entry_points = \
{'console_scripts': ['gha-stats = gha_stats.cli:cli']}

setup_kwargs = {
    'name': 'gha-stats',
    'version': '0.1.0',
    'description': '',
    'long_description': '# mtng \nGenerate meeting notes from GitHub + [Indico](https://getindico.io/)\n\n## Installation\n\n```console\npip install mtng\n```\n\n## Interface\n\n```console\n$ mtng generate --help\nUsage: mtng generate [OPTIONS] CONFIG\n\n  Generate a LaTeX fragment that includes an overview of PRs, Issues and\n  optionally an Indico agenda\n\nArguments:\n  CONFIG  [required]\n\nOptions:\n  --token TEXT                    Github API token to use. Can be supplied\n                                  with environment variable GH_TOKEN\n\n  --since [%Y-%m-%d|%Y-%m-%dT%H:%M:%S|%Y-%m-%d %H:%M:%S]\n                                  [required]\n  --now [%Y-%m-%d|%Y-%m-%dT%H:%M:%S|%Y-%m-%d %H:%M:%S]\n                                  [default: 2021-10-26T13:10:29]\n  --event TEXT\n  --help                          Show this message and exit.\n```\n\n## Configuration\n\n`mtng` consumes a configuration file to specify which GitHub repositories to ingest. An example configuration could look like this:\n\n```yml\nrepos:\n  - name: acts-project/acts\n    do_stale: true\n    stale_label: Stale\n    wip_label: ":construction: WIP"\n    do_open_prs: true\n    do_merged_prs: true\n    do_recent_issues: false\n```\n\nThis configuration will look up the `acts-project/acts` repository. The output will contain sections on \n\n1. Stale PRs and issues. If this is turned on, the `stale_label` key must be given as well\n2. A list of open PRs, optionally filtered to not include the label given by `wip_label`\n3. Merged PRs since the date given by the `--since` option\n4. Issues opened since the date given by the `--since` option\n\n\nIn addition and independent of this config, a meeting agenda can be attached at the end if the `--event` option is provided and contains a valid Indico URL.\n\n## Making a presentation\n\nThe output of `mtng generate` is a LaTeX fragment. It has to be incorporated into a set of Beamer/LaTeX slides, for example like\n\n```console\n$ mtng generate spec.yml > gen.tex\n```\n\nwith a LaTeX file like\n\n```latex\n% Preamble and beginnig of slides\n\\input{gen.tex}\n% Rest of slides\n```\n',
    'author': 'Paul Gessinger',
    'author_email': 'hello@paulgessinger.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
