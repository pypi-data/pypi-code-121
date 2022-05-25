# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['chouseisan_py']

package_data = \
{'': ['*']}

install_requires = \
['beautifulsoup4>=4.10.0,<5.0.0', 'requests>=2.27.1,<3.0.0']

setup_kwargs = {
    'name': 'chouseisan-py',
    'version': '0.1.1',
    'description': 'Automate the operation of chouseisan.com',
    'long_description': '# chouseisan_py\nchouseisan_py automates the operations of [調整さん](https://chouseisan.com/)(Chouseisan).\nCurrently, it only supports creating events.\n\n![Test](https://github.com/ryu22e/chouseisan_py/actions/workflows/test.yml/badge.svg)\n[![codecov](https://codecov.io/gh/ryu22e/chouseisan_py/branch/main/graph/badge.svg?token=rB5RS1bewF)](https://codecov.io/gh/ryu22e/chouseisan_py)\n\n## Installation\n\n```python\n$ pip install chouseisan-py\n```\n\n## Usage\n\n```python\n>>> from datetime import datetime\n>>> from chouseisan_py.chouseisan import Auth, Chouseisan\n>>> auth = Auth(email="test@example.com", password="<secret>")\n>>> chouseisan = Chouseisan(auth)\n>>> chouseisan.create_event(\n...    title="test event",\n...    candidate_days=[datetime(2021, 10, 17, 19, 0), datetime(2021, 10, 18, 19, 0)]\n... )\n\'https://chouseisan.com/s?h=f7b7fc11995b441782844bc3fddaf456\'\n```\n',
    'author': 'Ryuji TSUTSUI',
    'author_email': 'ryu22e@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ryu22e/chouseisan_py',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
