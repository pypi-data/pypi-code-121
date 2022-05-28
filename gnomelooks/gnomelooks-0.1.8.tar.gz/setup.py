# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['getlooks']

package_data = \
{'': ['*']}

install_requires = \
['beautifulsoup4',
 'colorama',
 'lxml',
 'requests',
 'rich>=12.4.0',
 'typer>=0.4.1,<0.5.0']

entry_points = \
{'console_scripts': ['gnomelooks = getlooks.cli:app']}

setup_kwargs = {
    'name': 'gnomelooks',
    'version': '0.1.8',
    'description': '',
    'long_description': '# Gnome-looks themes cli downloader\n\n**A cli-tool to install and update gnome based Icons, GTK, Cursor themes easily**\n\n### Supported desktop environments\n\n- **Gnone**\n- **Xfce**\n- **KDE Plasma**\n\n![image 1](./.github/images/get.png)\n\n## gnomelooks\n\n\n\n- To Install themes for current user\n        \n        gnomelooks get [THEME-URL]\n\n- To Install themes globally\n\n        sudo gnomelooks get [THEME-URL]\n\n### Installation\n\n    pip3 install -U gnomelooks\n\n## gnomelooks help Page\n\n    ~$ gnomelooks --help\n        Usage: gnomelooks [OPTIONS] COMMAND [ARGS]...\n\n        Theme Installer for Gnome, Xfce4, Kde \n\n        Options:\n        --install-completion  Install completion for the current shell.\n        --show-completion     Show completion for the current shell, to copy it or\n                                customize the installation.\n        --help                Show this message and exit.\n\n        Commands:\n        askenv  | ask deskenv\n        get     | Install new UI themes/icons\n        ls      | List installed themes and icons\n        rm      | Remove installed themes and icons\n        update  | Update installed themes and icons via this tool\n\n## update all themes and icons\n\nRun: `gnomelooks update --themes`\n',
    'author': 'Rishang',
    'author_email': 'rishangbhavsarcs@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
