# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['buildtools',
 'buildtools.buildsystem',
 'buildtools.ext',
 'buildtools.ext.salt',
 'buildtools.maestro',
 'buildtools.maestro.enumwriters',
 'buildtools.posix',
 'buildtools.repo',
 'buildtools.wrapper',
 'buildtools.wrapper.repo']

package_data = \
{'': ['*']}

install_requires = \
['Jinja2==3.1.2',
 'MarkupSafe>=2.1.1,<3.0.0',
 'colorama>=0.4.4,<0.5.0',
 'lxml>=4.8.0,<5.0.0',
 'psutil>=5.9.1,<6.0.0',
 'pygit2>=1.9.1,<2.0.0',
 'requests>=2.27.1,<3.0.0',
 'ruamel.yaml>=0.17.21,<0.18.0',
 'six>=1.16.0,<2.0.0',
 'toml>=0.10.2,<0.11.0',
 'tqdm>=4.64.0,<5.0.0']

extras_require = \
{'nuitka': ['Nuitka>=0.8.1,<0.9.0'],
 'pyqt5': ['PyQt5>=5.15.6,<6.0.0'],
 'twisted': ['Twisted>=22.4.0,<23.0.0']}

setup_kwargs = {
    'name': 'pybuildtools',
    'version': '0.4.13',
    'description': 'A set of tools for putting together buildscripts and other CLI applications',
    'long_description': "# python-build-tools\n\nA toolkit containing many powerful utilities, including:\n\n * OS utilities (buildtools.os_utils)\n * Indented logging with colorama support (buildtools.bt_logging.log)\n * The powerful Maestro build management system (buildtools.maestro)\n * A powerful VCS repository wrapper system (buildtools.repo)\n * A mess of other random things.\n\n## os_utils\n```python\nfrom buildtools import os_utils\n\n# Ensure test/ exists\nos_utils.ensureDirExists('test')\n\n# Get copy of current environmental variables.\nENV = os_utils.ENV.clone()\n\n# Add .bin/ to the beginning of PATH in our virtual environment\nENV.prependTo('PATH', '.bin/')\n\n# Remove any duplicate entries from PATH\nENV.removeDuplicatedEntries('PATH')\n\n# Find gcc in our virtual environment (checks PATHEXT on Windows, too!)\n# Returns the path to gcc, or None if it couldn't be found.\nGCC = ENV.which('gcc')\n\n# Ensure bash exists before continuing (same rules as above)\nENV.assertWhich('bash')\n\n# Bring up gcc's help page. Crash if non-0 exit code, echo command to console, and output STDOUT/STDERR to console.\nos_utils.cmd([GCC, '--help'], critical=True, echo=True, show_output=True)\n```\n\n## Logging\n```python\nfrom buildtools import log\n\ndef a():\n  log.info('This will be indented if a() is called in a log block.')\n\nlog.info('No indentation, yet.')\nwith log.warning('A warning. Next line will be indented.'):\n  log.error('Error!')\n  with log.info('The following function\\'s log output will be indented by another layer.')\n    a()\n    log.critical('So will %s!', 'this')\n```\n\n## Maestro\n```python\nfrom buildtools.maestro import BuildMaestro\nfrom buildtools.maestro.fileio import ReplaceTextTarget\nfrom buildtools.maestro.coffeescript import CoffeeBuildTarget\nfrom buildtools.maestro.web import SCSSBuildTarget, SCSSConvertTarget\n\nbm = BuildMaestro()\n\n# Compile CoffeeScript to JS\nbm.add(CoffeeBuildTarget('htdocs/js/vgws.js',                 ['coffee/src/vgws.coffee']))\nbm.add(CoffeeBuildTarget('htdocs/js/editpoll.multichoice.js', ['coffee/editpoll.multichoice.coffee'], dependencies=['htdocs/js/vgws.js']))\nbm.add(CoffeeBuildTarget('htdocs/js/editpoll.option.js',      ['coffee/editpoll.editpoll.coffee'], dependencies=['htdocs/js/vgws.js']))\n\n# Convert CSS to SCSS\nbm.add(SCSSBuildTarget('htdocs/css/style.css', ['style/style.scss'], [], import_paths=['style'], compass=True))\n\n# Compile, taking dependencies into count when ordering operations.\nbm.run()\n\n# Same as above, but providing command line arguments such as --clean, and --rebuild.\nbm.as_app()\n```\n",
    'author': 'Rob Nelson',
    'author_email': 'nexisentertainment@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/N3X15/python-build-tools',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
