# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['noggin_messages', 'noggin_messages.tests']

package_data = \
{'': ['*']}

install_requires = \
['fedora-messaging>=2.0.1']

entry_points = \
{'fedora.messages': ['noggin.group.member.sponsor.v1 = '
                     'noggin_messages:MemberSponsorV1',
                     'noggin.user.create.v1 = noggin_messages:UserCreateV1',
                     'noggin.user.update.v1 = noggin_messages:UserUpdateV1']}

setup_kwargs = {
    'name': 'noggin-messages',
    'version': '1.0.2',
    'description': 'Fedora Messaging message schemas for Noggin.',
    'long_description': None,
    'author': 'Fedora Infrastructure',
    'author_email': 'admin@fedoraproject.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/fedora-infra/noggin-messages',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6.7,<4.0.0',
}


setup(**setup_kwargs)
