# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['yog', 'yog.host', 'yog.repo', 'yog.res']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0', 'docker>=5.0.3,<6.0.0', 'paramiko>=2.8.0,<3.0.0']

entry_points = \
{'console_scripts': ['yog = yog.host.main:main',
                     'yog-repo = yog.repo.main:main']}

setup_kwargs = {
    'name': 'yog',
    'version': '1.3.0',
    'description': 'The Gate and Key',
    'long_description': '## Yog\n\nAn opinionated docker-and-ssh-centric declarative system management tool.\n\nSome features:\n* Like puppet or ansible but a lot smaller and focused on docker.\n* "agentless" in the same sense that ansible is, in that it (ab)uses ssh to do lots of its functionality.\n* (ab)uses ssh as a poor-person\'s Envoy - it prefers to tunnel traffic over ssh even if it could otherwise just hit the port directly.\n\nCommand summary:\n\n* `yog`: Applies configurations to hosts. e.g. `yog myhost.mytld` applies the config from `./domains/mytld.myhost.yml`.\n* `yog-repo`: Manages a docker repository. `yog-repo push` uses the contents of `./Yogfile` to build an image and push it to the configured registry with the configured name and tag.\n',
    'author': 'Josh Hertlein',
    'author_email': 'jmhertlein@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
