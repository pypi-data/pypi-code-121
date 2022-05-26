# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['dirlisting']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0', 'click>=8.1.3,<9.0.0']

entry_points = \
{'console_scripts': ['dirlisting = dirlisting.cli:app']}

setup_kwargs = {
    'name': 'dirlisting',
    'version': '0.1.0',
    'description': 'Create a directory listing diagram from text file',
    'long_description': '# dirlisting\n\nCreate a directory tree listing diagram from a text file.\n\n## Installation\n\n```bash\n$ pip install dirlisting\n```\n\n## Usage\n\n`dirlisting` can be used to create a directory tree digram that looks like those created\nwith the `tree` command, but from a text file instead of walking an actual directory\ntree.\n\n### From code\n\n```python\nfrom dirlisting.dirlisting import Dirlisting\nwith open("input.yaml") as f:\n    listing = Dirlisting(f)\nlisting.print()\n```\n\n### From the command line\n\njust use `dirlisting <filename>`.\n\n### File format\n\nThe input file is a [yaml](https://yaml.org/) file. The contents of a directory are\nsequences, files are final strings (`- filename`), and directories are mappings (`-\ndirname:`). A listing would look like the following.\n\n:::::{grid} 2\n::::{grid-item-card} YAML File\n```yaml\n- topdir:\n  - subdir1:\n  - file1.txt\n  - file2.txt\n  - subdir2:\n    - file3.txt\n```\n::::\n::::{grid-item-card} Output\n```\ntopdir\n├── emptydir\n├── file1.txt\n├── file2.txt\n└── subdir\n    └── file3.txt\n```\n::::\n:::::\n\n## Contributing\n\nInterested in contributing? Check out the contributing guidelines. Please note that this\nproject is released with a Code of Conduct. By contributing to this project, you agree\nto abide by its terms.\n\n## License\n\n`dirlisting` was created by Stephan Poole. It is licensed under the terms of the MIT\nlicense.\n\n## Credits\n\n`dirlisting` was created with\n[`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the\n`py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).\n',
    'author': 'Stephan Poole',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
