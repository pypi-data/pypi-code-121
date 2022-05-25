# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['robonomicsinterface', 'robonomicsinterface.classes']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0.4,<9.0.0', 'substrate-interface>=1.1.7']

entry_points = \
{'console_scripts': ['robonomics_interface = '
                     'robonomicsinterface.robonomics_interface_io:cli']}

setup_kwargs = {
    'name': 'robonomics-interface',
    'version': '1.0.3',
    'description': 'Robonomics wrapper over https://github.com/polkascan/py-substrate-interface created to facilitate programming with Robonomics',
    'long_description': '# robonomics-interface\nThis is a simple wrapper over https://github.com/polkascan/py-substrate-interface used to facilitate writing code for applications using Robonomics.\n\nRobonomics project: https://robonomics.network/\n\nRobonomics parachain dapp: https://parachain.robonomics.network/\n\nDocumentation: https://multi-agent-io.github.io/robonomics-interface/\n_______\n# Installation \n```bash\npip3 install robonomics-interface\n```\n# Contributing\n\nWhen contributing to this repository, please first discuss the change you wish to make via issue,\nemail, or any other method with the owners of this repository before making a change. \n\n## Pull Request Process\n\n1. Install [poetry](https://python-poetry.org/docs/) \n2. Git clone the repository\n3. Install requirements with\n```bash\npoetry install\n```\nInstalling `substrate_interface` may require [Rust](https://www.rust-lang.org/tools/install) and \n[Rustup nightly](https://rust-lang.github.io/rustup/concepts/channels.html).\n\n4. Add functions/edit code/fix issues.\n5. Make a PR.\n6. ...\n7. Profit!\n\n\n## Some important rules\n- If needed, install dependencies with\n```bash\npoetry add <lib>\n```\n- Use `ReStructuredText` docstrings.\n- Respect typing annotation.\n- Add documentation. Please take in consideration that if a new class was created, add it to `docs/source/modules.rst`.\nOther functionality is better to be described in `docs/source/usage.rst`\n- Black it:\n```bash\nblack -l 120 <modified_file>\n```\n- Check how the docs look via `make html` from the `docs` folder and checking the `docs/build/html/index.html` page.\n- Do not bump version.\n- One may test the code by\n```bash\n# in project root\npoetry build\npip3 uninstall robonomcis_interface -y  #if was installed previously\npip3 install pip3 install dist/robonomics_interface-<version>-py3-none-any.whl \npython3 <testing_script>\n```',
    'author': 'Pavel Tarasov',
    'author_email': 'p040399@outlook.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Multi-Agent-io/robonomics-interface',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
