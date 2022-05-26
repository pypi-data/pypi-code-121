# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['poetry_plugin_export']

package_data = \
{'': ['*']}

install_requires = \
['poetry>=1.2.0b1dev0,<2.0.0']

entry_points = \
{'poetry.application.plugin': ['export = '
                               'poetry_plugin_export.plugins:ExportApplicationPlugin']}

setup_kwargs = {
    'name': 'poetry-plugin-export',
    'version': '1.0.4',
    'description': 'Poetry plugin to export the dependencies to various formats',
    'long_description': '# Poetry Plugin: Export\n\nThis package is a plugin that allows the export of locked packages to various formats.\n\n**Note**: For now, only the `requirements.txt` format is available.\n\nThis plugin provides the same features as the existing `export` command of Poetry which it will eventually replace.\n\n\n## Installation\n\nThe easiest way to install the `export` plugin is via the `plugin add` command of Poetry.\n\n```bash\npoetry plugin add poetry-plugin-export\n```\n\nIf you used `pipx` to install Poetry you can add the plugin via the `pipx inject` command.\n\n```bash\npipx inject poetry poetry-plugin-export\n```\n\nOtherwise, if you used `pip` to install Poetry you can add the plugin packages via the `pip install` command.\n\n```bash\npip install poetry-plugin-export\n```\n\n\n## Usage\n\nThe plugin provides an `export` command to export to the desired format.\n\n```bash\npoetry export -f requirements.txt --output requirements.txt\n```\n\n**Note**: Only the `requirements.txt` format is currently supported.\n\n### Available options\n\n* `--format (-f)`: The format to export to (default: `requirements.txt`). Currently, only `requirements.txt` is supported.\n* `--output (-o)`: The name of the output file.  If omitted, print to standard output.\n* `--without`: The dependency groups to ignore when exporting.\n* `--with`: The optional dependency groups to include when exporting.\n* `--only`: The only dependency groups to include when exporting.\n* `--default`: Only export the main dependencies. (**Deprecated**)\n* `--dev`: Include development dependencies. (**Deprecated**)\n* `--extras (-E)`: Extra sets of dependencies to include.\n* `--without-hashes`: Exclude hashes from the exported file.\n* `--with-credentials`: Include credentials for extra indices.\n',
    'author': 'Sébastien Eustace',
    'author_email': 'sebastien@eustace.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
