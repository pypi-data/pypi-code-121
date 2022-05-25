# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['indsl',
 'indsl.data_quality',
 'indsl.data_quality.score',
 'indsl.data_quality.score.accuracy',
 'indsl.data_quality.score.completeness',
 'indsl.detect',
 'indsl.equipment',
 'indsl.filter',
 'indsl.fluid_dynamics',
 'indsl.forecast',
 'indsl.not_listed_operations',
 'indsl.oil_and_gas',
 'indsl.regression',
 'indsl.resample',
 'indsl.signals',
 'indsl.smooth',
 'indsl.statistics',
 'indsl.ts_utils']

package_data = \
{'': ['*'], 'indsl.smooth': ['img/*'], 'indsl.statistics': ['img/*']}

install_requires = \
['PyWavelets>=1.2.0,<2.0.0',
 'csaps>=1.1.0,<2.0.0',
 'emd>=0.5.3,<0.6.0',
 'kneed>=0.7.0,<0.8.0',
 'numba>=0.55.0,<0.56.0',
 'packaging>=21.3,<22.0',
 'pandas>=1.3.5,<2.0.0',
 'pytest>=6.2.2,<8.0.0',
 'scikit-image>=0.19.0,<0.20.0',
 'scipy>=1.7.3,<2.0.0',
 'sklearn>=0.0,<0.1',
 'statsmodels>=0.13.1,<0.14.0',
 'typeguard>=2.13.3,<3.0.0']

setup_kwargs = {
    'name': 'indsl',
    'version': '4.5.0',
    'description': 'Industrial Data Science Library by Cognite',
    'long_description': '[![Downloads](https://static.pepy.tech/personalized-badge/indsl?period=total&units=international_system&left_color=black&right_color=brightgreen&left_text=PyPi%20Downloads)](https://pepy.tech/project/indsl) [![Code Quality](https://github.com/cognitedata/indsl/actions/workflows/code-quality.yaml/badge.svg)](https://github.com/cognitedata/indsl/actions/workflows/code-quality.yaml) [![CodeQL](https://github.com/cognitedata/indsl/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/cognitedata/indsl/actions/workflows/codeql-analysis.yml) [![codecov](https://codecov.io/gh/cognitedata/indsl/branch/main/graph/badge.svg?token=N63jUovh1o)](https://codecov.io/gh/cognitedata/indsl)<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->\n[![All Contributors](https://img.shields.io/badge/all_contributors-9-orange.svg?style=flat-square)](#contributors-)\n<!-- ALL-CONTRIBUTORS-BADGE:END -->\n\n<a href="https://cognite.com/">\n    <img src="https://github.com/cognitedata/cognite-python-docs/blob/master/img/cognite_logo.png" alt="Cognite logo" title="Cognite" align="right" height="80" />\n</a>\n\n***\n# TEMPORARY MAINTENANCE PERIOD\n\nAs of May 16, 20022, InDSL will be in maintenance mode until further notice. We expect to conclude the required tasks\nin a period of 2-4 weeks. We are focusing on improving test coverage, documentation and quality of the technical\ndocumentation for all functions exposed on the Charts UI.\n\nUntil maintenance is concluded, the team supporting InDSL will focus on the above and down-prioritize reviewing new\nPull Requests (PRs). This means that:\n\n1. PRs with functions that are meant to be exposed in the Charts UI and that do not follow InDSL v4.4 requirements\n   will be label `breaking changes` and will be available on v5. These will take longer to be exposed in Charts as the\n   current versions of the backend and frontend depend on v4 of InDSL.\n2. PRs with breaking changes will not be reviewed/approved until the maintenance period is concluded.\n3. PRs that follow InDSL guidelines for functions exposed to Charts are welcomed but the review and approval process\n   will take longer than usual.\n4. Other type of PRs (e.g. docs, fixes) or traditional non-Charts scripts are also welcome and the review process *might*\n   take longer than usual depending on the task load of the maintenance crew and reviewers.\n\n***\n\nIndustrial Data Science Library\n=========================================\n\nThis is Cognite\'s collection of data science algorithms and models. Its objective is twofold. First, empower domain\nexperts to conduct exploratory work, root cause analysis, and analyze data via <a href="https://charts.cogniteapp.com/" target="_blank">Cognite Charts</a>.\nSecond, curate a collection industry relevant data science algorithms to be used as a regular python package.\nFor more information, consult the <a href="https://docs.cognite.com/cdf/charts/" target="_blank">Charts documentation page</a>.\n\n## Documentation\n* [InDSL Home](https://indsl.docs.cognite.com/)\n* [Data Science Developer Guidelines](https://indsl.docs.cognite.com/contribute.html)\n* [Gallery of Charts - Examples](https://indsl.docs.cognite.com/auto_examples/index.html)\n* [Publishing new versions of InDSL](./PUBLISHING.md)\n\n## Contributors ✨\n\nThanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)):\n\n<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->\n<!-- prettier-ignore-start -->\n<!-- markdownlint-disable -->\n<table>\n  <tr>\n    <td align="center"><a href="https://github.com/gzarruk"><img src="https://avatars.githubusercontent.com/u/24595022?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Gustavo</b></sub></a><br /><a href="https://github.com/cognitedata/indsl/commits?author=gzarruk" title="Documentation">📖</a> <a href="https://github.com/cognitedata/indsl/pulls?q=is%3Apr+reviewed-by%3Agzarruk" title="Reviewed Pull Requests">👀</a> <a href="#talk-gzarruk" title="Talks">📢</a> <a href="https://github.com/cognitedata/indsl/commits?author=gzarruk" title="Tests">⚠️</a> <a href="#data-gzarruk" title="Data">🔣</a> <a href="#content-gzarruk" title="Content">🖋</a> <a href="https://github.com/cognitedata/indsl/commits?author=gzarruk" title="Code">💻</a> <a href="#ideas-gzarruk" title="Ideas, Planning, & Feedback">🤔</a></td>\n    <td align="center"><a href="https://github.com/funsim"><img src="https://avatars.githubusercontent.com/u/763150?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Simon Funke</b></sub></a><br /><a href="https://github.com/cognitedata/indsl/commits?author=funsim" title="Code">💻</a> <a href="https://github.com/cognitedata/indsl/commits?author=funsim" title="Tests">⚠️</a> <a href="https://github.com/cognitedata/indsl/issues?q=author%3Afunsim" title="Bug reports">🐛</a></td>\n    <td align="center"><a href="https://github.com/neringaalt"><img src="https://avatars.githubusercontent.com/u/8692658?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Neringa Altanaite</b></sub></a><br /><a href="https://github.com/cognitedata/indsl/commits?author=neringaalt" title="Code">💻</a> <a href="https://github.com/cognitedata/indsl/pulls?q=is%3Apr+reviewed-by%3Aneringaalt" title="Reviewed Pull Requests">👀</a> <a href="https://github.com/cognitedata/indsl/commits?author=neringaalt" title="Tests">⚠️</a> <a href="https://github.com/cognitedata/indsl/commits?author=neringaalt" title="Documentation">📖</a></td>\n    <td align="center"><a href="https://www.linkedin.com/in/rhuanbarreto/"><img src="https://avatars.githubusercontent.com/u/283004?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Rhuan Barreto</b></sub></a><br /><a href="#tool-rhuanbarreto" title="Tools">🔧</a> <a href="#security-rhuanbarreto" title="Security">🛡️</a> <a href="https://github.com/cognitedata/indsl/pulls?q=is%3Apr+reviewed-by%3Arhuanbarreto" title="Reviewed Pull Requests">👀</a> <a href="#ideas-rhuanbarreto" title="Ideas, Planning, & Feedback">🤔</a> <a href="#infra-rhuanbarreto" title="Infrastructure (Hosting, Build-Tools, etc)">🚇</a></td>\n    <td align="center"><a href="https://github.com/evertoncolling"><img src="https://avatars.githubusercontent.com/u/33816483?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Everton Colling</b></sub></a><br /><a href="https://github.com/cognitedata/indsl/commits?author=evertoncolling" title="Code">💻</a> <a href="#data-evertoncolling" title="Data">🔣</a> <a href="https://github.com/cognitedata/indsl/commits?author=evertoncolling" title="Documentation">📖</a> <a href="https://github.com/cognitedata/indsl/commits?author=evertoncolling" title="Tests">⚠️</a></td>\n    <td align="center"><a href="https://github.com/redzarosliCognite"><img src="https://avatars.githubusercontent.com/u/91888036?v=4?s=100" width="100px;" alt=""/><br /><sub><b>redzarosliCognite</b></sub></a><br /><a href="https://github.com/cognitedata/indsl/commits?author=redzarosliCognite" title="Code">💻</a> <a href="https://github.com/cognitedata/indsl/pulls?q=is%3Apr+reviewed-by%3AredzarosliCognite" title="Reviewed Pull Requests">👀</a> <a href="#ideas-redzarosliCognite" title="Ideas, Planning, & Feedback">🤔</a> <a href="https://github.com/cognitedata/indsl/commits?author=redzarosliCognite" title="Documentation">📖</a> <a href="#example-redzarosliCognite" title="Examples">💡</a> <a href="#question-redzarosliCognite" title="Answering Questions">💬</a> <a href="#userTesting-redzarosliCognite" title="User Testing">📓</a></td>\n    <td align="center"><a href="https://github.com/MortGron"><img src="https://avatars.githubusercontent.com/u/42722577?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Morten Grønbech</b></sub></a><br /><a href="https://github.com/cognitedata/indsl/commits?author=MortGron" title="Code">💻</a> <a href="#example-MortGron" title="Examples">💡</a> <a href="https://github.com/cognitedata/indsl/commits?author=MortGron" title="Documentation">📖</a> <a href="https://github.com/cognitedata/indsl/pulls?q=is%3Apr+reviewed-by%3AMortGron" title="Reviewed Pull Requests">👀</a> <a href="#question-MortGron" title="Answering Questions">💬</a> <a href="#ideas-MortGron" title="Ideas, Planning, & Feedback">🤔</a></td>\n    <td align="center"><a href="https://github.com/Anitsirc22"><img src="https://avatars.githubusercontent.com/u/38993790?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Cristina Ferrer</b></sub></a><br /><a href="https://github.com/cognitedata/indsl/commits?author=Anitsirc22" title="Code">💻</a> <a href="#example-Anitsirc22" title="Examples">💡</a> <a href="#ideas-Anitsirc22" title="Ideas, Planning, & Feedback">🤔</a> <a href="https://github.com/cognitedata/indsl/pulls?q=is%3Apr+reviewed-by%3AAnitsirc22" title="Reviewed Pull Requests">👀</a></td>\n  </tr>\n  <tr>\n    <td align="center"><a href="http://treiderphoto.com"><img src="https://avatars.githubusercontent.com/u/8521241?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Håkon V. Treider</b></sub></a><br /><a href="https://github.com/cognitedata/indsl/commits?author=haakonvt" title="Code">💻</a> <a href="https://github.com/cognitedata/indsl/pulls?q=is%3Apr+reviewed-by%3Ahaakonvt" title="Reviewed Pull Requests">👀</a> <a href="#ideas-haakonvt" title="Ideas, Planning, & Feedback">🤔</a> <a href="#infra-haakonvt" title="Infrastructure (Hosting, Build-Tools, etc)">🚇</a></td>\n    <td align="center"><a href="https://github.com/KeepFloyding"><img src="https://avatars.githubusercontent.com/u/29730122?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Andris Piebalgs</b></sub></a><br /><a href="https://github.com/cognitedata/indsl/commits?author=KeepFloyding" title="Code">💻</a> <a href="https://github.com/cognitedata/indsl/pulls?q=is%3Apr+reviewed-by%3AKeepFloyding" title="Reviewed Pull Requests">👀</a> <a href="#example-KeepFloyding" title="Examples">💡</a></td>\n  </tr>\n</table>\n\n<!-- markdownlint-restore -->\n<!-- prettier-ignore-end -->\n\n<!-- ALL-CONTRIBUTORS-LIST:END -->\n\nThis project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!\n',
    'author': 'Gustavo Zarruk',
    'author_email': 'gustavo.zarruk@cognite.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://indsl.docs.cognite.com',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.10',
}


setup(**setup_kwargs)
