# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pydamain',
 'pydamain.domain',
 'pydamain.domain.messages',
 'pydamain.domain.models',
 'pydamain.domain.service',
 'pydamain.port',
 'pydamain.service']

package_data = \
{'': ['*']}

install_requires = \
['typing-extensions>=4.2.0,<5.0.0']

setup_kwargs = {
    'name': 'pydamain',
    'version': '0.7.1',
    'description': '도메인 주도 설계 라이브러리.',
    'long_description': '# Pydamain\n\n작성중...',
    'author': 'Jongbeom-Kwon',
    'author_email': 'bolk9652@naver.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/by-Exist/pydamain',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
