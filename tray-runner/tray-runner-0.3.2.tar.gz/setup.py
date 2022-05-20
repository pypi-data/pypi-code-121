# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tray_runner',
 'tray_runner.cli',
 'tray_runner.common_utils',
 'tray_runner.gui']

package_data = \
{'': ['*'], 'tray_runner.gui': ['icons/*', 'icons/ikonate/*']}

install_requires = \
['Babel>=2.10.1,<3.0.0',
 'PySide6-Essentials>=6.3.0,<7.0.0',
 'click>=8.1.3,<9.0.0',
 'pydantic>=1.9.1,<2.0.0',
 'python-dateutil>=2.8.2,<3.0.0',
 'python-slugify>=6.1.2,<7.0.0']

extras_require = \
{':sys_platform == "win32"': ['winshell>=0.6,<0.7', 'pywin32>=304,<305']}

entry_points = \
{'console_scripts': ['tray-runner-cli = tray_runner.cli:run',
                     'tray-runner-gui = tray_runner.gui:run']}

setup_kwargs = {
    'name': 'tray-runner',
    'version': '0.3.2',
    'description': 'Tool to run and restart commands, so they can be continuously executed. The application can be run from the console or using a tray icon.',
    'long_description': '# Tray Runner\n\nTray Runner is a simple application that runs in the system tray and executes periodically the commands configured. This is util when you want to run command line scripts without having a terminal open ow worry to remember to execute them.\n\nThe application has been tested on Linux (Ubuntu) and Windows 10, but should run on any modern operating system, as the UI relies on QT.\n\n![Main configuration window](https://github.com/okelet/tray-runner/raw/main/docs/config_commands.png)\n\n![Command configuration](https://github.com/okelet/tray-runner/raw/main/docs/command_general.png)\n\nCheck [more screenshots here](#more-screenshots).\n\n## Installation\n\n**Python 3.10 or greater is required**.\n\nIt is recommended to use [`pipx`](https://github.com/pypa/pipx) so you can install Tray Runner and its dependencies without affecting other applications installed with `pip`:\n\n```bash\npipx install tray-runner\n```\n\nCheck and upgrade with:\n\n```bash\npipx upgrade tray-runner\n```\n\nIn a near future, single file binaries will be provided.\n\nOnce installed, you can run the application running the command:\n\n```bash\ntray-runner-gui\n```\n\nCheck the options running `tray-runner-gui --help`. The first time the program is executed, a shortcut in the applications menu and in the auto start directory will be created. Also, you will be asked to configure the application:\n\n![First run](https://github.com/okelet/tray-runner/raw/main/docs/first_run.png)\n\n### Fedora/RHEL based\n\n```bash\nsudo dnf install -y gnome-shell-extension-appindicator\ngnome-extensions enable appindicatorsupport@rgcjonas.gmail.com\n```\n\nNote: the indicator icon will be shown, but the notifications will remain in the notifications list.\n\n## Running\n\nFrom the CLI:\n\n```bash\ntray-runner-cli --help\n```\n\nFrom the GUI:\n\n```bash\ntray-runner-gui --help\n```\n\n## TODO\n\n* Translations (raw Python and QT)\n* One-file executables (and portables) for Linux and Windows\n* Log viewer\n\n## Development\n\n### Translations\n\nUpdate the template:\n\n```bash\npoetry run pybabel extract -o tray_runner/locale/messages.pot\n```\n\nGenerate a new language:\n\n```bash\npoetry run pybabel init -l de_DE -i tray_runner/locale/messages.pot -d tray_runner/locale\n```\n\nUpdate the languages with the new translations found:\n\n```bash\npoetry run pybabel update -i tray_runner/locale/messages.pot -d tray_runner/locale\n```\n\nCompile the translations:\n\n```bash\npoetry run pybabel compile -d tray_runner/locale\n```\n\n### Code quality\n\nRunning directly the commands:\n\n```bash\npoetry run pylint tray_runner\npoetry run black tray_runner\npoetry run mypy tray_runner\npoetry run isort tray_runner\n```\n\nUsing `pre-commit`:\n\n```bash\ngit add --intent-to-add .\npoetry run pre-commit run --all-files\n```\n\n### Credits\n\n* Icons:\n  * [Fugue Icons](https://p.yusukekamiyamane.com/)\n  * [Font Awesome](https://fontawesome.com/)\n  * [Ikonate](https://ikonate.com/)\n\n## More screenshots\n\nList of commands:\n\n![List of commands](https://github.com/okelet/tray-runner/raw/main/docs/config_commands.png)\n\nGeneral configuration:\n\n![General configuration](https://github.com/okelet/tray-runner/raw/main/docs/config_general.png)\n\nCommands common configuration:\n\n![Commands common configuration](https://github.com/okelet/tray-runner/raw/main/docs/config_common.png)\n\nCommand configuration:\n\n![Command configuration](https://github.com/okelet/tray-runner/raw/main/docs/command_general.png)\n\nCommand overrides:\n\n![Command overrides](https://github.com/okelet/tray-runner/raw/main/docs/command_options.png)\n\nCommand environment variables:\n\n![Command environment variables](https://github.com/okelet/tray-runner/raw/main/docs/command_environment.png)\n\nCommand statistics:\n\n![Command statistics](https://github.com/okelet/tray-runner/raw/main/docs/command_statistics.png)\n',
    'author': 'Juan A. S.',
    'author_email': 'okelet@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/okelet/tray-runner',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<3.11',
}


setup(**setup_kwargs)
