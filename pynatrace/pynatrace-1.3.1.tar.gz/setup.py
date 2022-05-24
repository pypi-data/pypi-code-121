# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['pynatrace']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.1.3,<9.0.0',
 'dt>=1.1.48,<2.0.0',
 'requests>=2.27.1,<3.0.0',
 'termcolor>=1.1.0,<2.0.0']

entry_points = \
{'console_scripts': ['pynatrace = pynatrace.cli:main']}

setup_kwargs = {
    'name': 'pynatrace',
    'version': '1.3.1',
    'description': 'Python limited CLI for Dynatrace',
    'long_description': '# dt_log_send\nPython CLI for submitting logs to Dynatrace\n=======\n# dt_log_send\n\n## Install\n\n```bash\n$ pip install dt_log_send\n```\n\n',
    'author': 'Michael MacKenna',
    'author_email': 'mmackenna@unitedfiregroup.com',
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
