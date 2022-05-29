# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aiopayok', 'aiopayok.models']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.8.1,<4.0.0',
 'certifi>=2022.5.18,<2023.0.0',
 'pydantic>=1.9.1,<2.0.0']

setup_kwargs = {
    'name': 'aiopayok',
    'version': '0.1.7',
    'description': 'payok.io asynchronous python wrapper',
    'long_description': '[![GitHub issues](https://img.shields.io/github/issues/layerqa/aiopayok?style=for-the-badge)](https://github.com/layerqa/aiopayok/issues)\n[![GitHub license](https://img.shields.io/github/license/layerqa/aiopayok?style=for-the-badge)](https://github.com/layerqa/aiopayok/blob/main/LICENSE)\n[![PyPI](https://img.shields.io/pypi/v/aiopayok?style=for-the-badge)](https://pypi.org/project/aiopayok/)\n## AIOPayok\n\n> payok.io asynchronous python wrapper\n\n``` python\nimport asyncio\n\nfrom aiopayok import Payok\n\n\npayok = Payok("API_ID", "API_KEY")\n\n\nasync def main() -> None:\n    print(await payok.get_balance())\n\nasyncio.run(main())\n\n```\n\n### Installing\n\n``` bash\npip install aiopayok\n```\n\n### Resources\n\n- Check out the docs at https://payok.io/cabinet/documentation/doc_main.php to learn more about PayOk,\n',
    'author': 'layerqa',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/layerqa/aiopayok',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
