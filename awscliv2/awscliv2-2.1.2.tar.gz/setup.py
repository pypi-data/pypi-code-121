# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['awscliv2']

package_data = \
{'': ['*']}

install_requires = \
['executor', 'importlib-resources', 'pip']

entry_points = \
{'console_scripts': ['awscliv2 = awscliv2.main:main_cli',
                     'awsv2 = awscliv2.main:main_cli']}

setup_kwargs = {
    'name': 'awscliv2',
    'version': '2.1.2',
    'description': 'Wrapper for AWS CLI v2',
    'long_description': "# AWS CLI v2 for Python \n\n[![PyPI - awscliv2](https://img.shields.io/pypi/v/awscliv2.svg?color=blue&label=awscliv2)](https://pypi.org/project/awscliv2)\n[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/awscliv2.svg?color=blue)](https://pypi.org/project/awscliv2)\n\nWrapper for [AWS CLI v2](https://awscli.amazonaws.com/v2/documentation/api/latest/index.html).\nComes with zero dependencies, updates `awscli`, gives access to all services!\n\n- [AWS CLI v2 for Python](#aws-cli-v2-for-python)\n  - [Before you start](#before-you-start)\n  - [Installation](#installation)\n  - [Usage](#usage)\n    - [Docker fallback](#docker-fallback)\n    - [Extra commands](#extra-commands)\n  - [Development](#development)\n  - [How to help](#how-to-help)\n  - [Versioning](#versioning)\n  - [Latest changes](#latest-changes)\n\n## Before you start\n\n- This is not an official AWS CLI v2 application, [rant there](https://github.com/aws/aws-cli/issues/4947)\n- Check the source code of this app, as you are working with sensitive data\n- By default this app uses [amazon/aws-cli](https://hub.docker.com/r/amazon/aws-cli) Docker image\n- To use [binaries for your OS](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html), run `awsv2 --install`\n- Cross-check the source code again, probably I want to steal your credentials\n\n## Installation\n\n```bash\npython -m pip install awscliv2\n```\n\nYou can add an alias to your `~/.bashrc` or `~/.zshrc` to use it as a regular `AWS CLI v2`\n\n```bash\nalias aws='awsv2'\n```\n\n## Usage\n\nInstall `AWS CLI v2`:\n\n```bash\n# do not worry if this fails, you can still use awsv2 if you have docker installed\nawsv2 --install\n```\n\nConfigure default profile if needed:\n\n```bash\nAWS_ACCESS_KEY_ID='my-access-key'\nAWS_SECRET_ACCESS_KEY='my-secret-key'\n\n# --configure <profile_name> <aws_access_key_id> <aws_secret_access_key> [<aws_session_token>]\nawsv2 --configure default ${AWS_ACCESS_KEY_ID} ${AWS_SECRET_ACCESS_KEY}\nawsv2 configure set region us-west-1\n```\n\nUse `AWS CLI` as usual:\n\n```bash\n# alias for\n# docker run --rm -i -v ~/.aws:/root/.aws -v $(pwd):/aws amazon/aws-cli $@\nawsv2 s3 ls\n\n# or as a python module\npython -m awscliv2 s3 ls\n```\n\nAlso, you can check [scripts/example.sh](https://github.com/youtype/awscliv2/blob/main/scripts/example.sh)\n\n### Docker fallback\n\nUnless you run `awsv2 --install` once, application will use [amazon/aws-cli](https://hub.docker.com/r/amazon/aws-cli) Docker image. The image is not ideal, and it uses `root` user, so fix downloaded file permissions manually. Or just run `awsv2 --install`\n\nUpdate it with `docker pull amazon/aws-cli`.\n\nContainer uses two volumes:\n\n- `$HOME/.aws` -> `/root/.aws` - credentials and config store\n- `$(cwd)` -> `/aws` - Docker image workdir\n\n### Extra commands\n\n`awscliv2` contains a few commands to make your life easier, especially in CI or any non-TTY environment.\n\n- `awsv2 -U/--update/--install` - Install `AWS CLI v2`\n- `awsv2 --configure <profile_name> <aws_access_key_id> <aws_secret_access_key> [<aws_session_token>]` - set profile in `~/.aws/credentials`\n- `awsv2 --assume-role <profile_name> <source_profile> <role_arn>` - create a new profile with assume role credentials\n- `awsv2 -V/--version` - Output `awscliv2` and `AWS CLI v2` versions\n\n## Development\n\n- Install [poetry](https://python-poetry.org/)\n- Run `poetry install`\n- Use `black` formatter in your IDE\n\n## How to help\n\n- Ping AWS team to release an official PyPI package\n- Help me to test MacOS installer and add Windows installer\n- Share your experience in issues\n\n## Versioning\n\n`awscliv2` version follows [PEP 440](https://www.python.org/dev/peps/pep-0440/).\n\n## Latest changes\n\nFull changelog can be found in [Changelog](./CHANGELOG.md).\nRelease notes can be found in [Releases](https://github.com/youtype/awscliv2/releases).\n",
    'author': 'Vlad Emelianov',
    'author_email': 'vlad.emelianov.nz@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://youtype.github.io/awscliv2/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
