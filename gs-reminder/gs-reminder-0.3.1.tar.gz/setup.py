# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['gs_reminder',
 'gs_reminder.github',
 'gs_reminder.github.models',
 'gs_reminder.slack']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.1.3,<9.0.0', 'requests>=2.27.1,<3.0.0']

entry_points = \
{'console_scripts': ['gs-reminder = gs_reminder.notifier:main']}

setup_kwargs = {
    'name': 'gs-reminder',
    'version': '0.3.1',
    'description': 'Notify Slack of a review of Pull Requests in the GitHub repository.',
    'long_description': '# github-pr-slack-reminder\n\n[![Codacy Badge](https://app.codacy.com/project/badge/Grade/380a539992d941f0a6d9c045c48c580c)](https://www.codacy.com/gh/nnsnodnb/github-pr-slack-reminder/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=nnsnodnb/github-pr-slack-reminder&amp;utm_campaign=Badge_Grade)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n\n[![PyPI Package version](https://badge.fury.io/py/gs-reminder.svg)](https://pypi.org/project/gs-reminder)\n[![Python Supported versions](https://img.shields.io/pypi/pyversions/gs-reminder.svg)](https://pypi.org/project/gs-reminder)\n[![format](https://img.shields.io/pypi/format/gs-reminder.svg)](https://pypi.org/project/gs-reminder)\n[![implementation](https://img.shields.io/pypi/implementation/gs-reminder.svg)](https://pypi.org/project/gs-reminder)\n[![LICENSE](https://img.shields.io/pypi/l/gs-reminder.svg)](https://pypi.org/project/gs-reminder)\n\nNotify Slack of a review of Pull Requests in the GitHub repository.\n\n## Environments\n\n- Python 3.7 or later\n  - poetry\n\n## Usage\n\n```shell\npip install gs-reminder\ngs-reminder -r nnsnodnb/github-pr-slack-reminder -u examples/username.json\n```\n\n### Environment variables\n\n- `GITHUB_TOKEN`\n  - Required\n  - Your GitHub Personal Access Token.\n    - Create https://github.com/settings/tokens\n- `SLACK_URL`\n  - Required\n  - Incoming webhook\'s url of Slack app.\n\n### Options\n\n- `--repo` or `-r`\n  - Required\n  - Your GitHub repository name. (ex. `nnsnodnb/github-pr-slack-reminder`)\n- `--file-username` or `-u`\n  - Optional\n  - Corresponding files for GitHub and Slack usernames. (ex. `examples/username.json`)\n    ```json\n    [\n      {\n        "github": "nnsnodnb",\n        "slack": "yuya.oka"    \n      }\n    ]\n    ```\n\n- `--limit` or `-l`\n  - Optional\n  - Number of Pull Requests to notify Slack. Max: 20 (default: 20)\n\n## Example Result\n\n<img src="https://user-images.githubusercontent.com/9856514/168442310-af165e75-7329-4a37-8e67-3f2635c549ac.png" alt="example result" width="500px">\n\n## License\n\nThis software is licensed under the MIT License.\n',
    'author': 'Yuya Oka',
    'author_email': 'nnsnodnb@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/nnsnodnb/github-pr-slack-reminder',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
