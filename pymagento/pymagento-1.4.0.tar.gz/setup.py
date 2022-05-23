# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['magento']

package_data = \
{'': ['*']}

install_requires = \
['api-session>=1.2.0,<2.0.0']

extras_require = \
{'docs': ['Sphinx>=4.4.0,<5.0.0', 'sphinx-rtd-theme>=1.0.0,<2.0.0']}

setup_kwargs = {
    'name': 'pymagento',
    'version': '1.4.0',
    'description': 'Python client for the Magento 2 API',
    'long_description': '# PyMagento\n\n**PyMagento** is a Python client for the Magento 2 API. Its goal is to provide an easy-to-use\nPythonic interface to the Magento 2 API, while being lightweight and extendable.\n\n* [Read the docs](https://pymagento2.readthedocs.io/)\n\n\nNote: PyMagento is not affiliated to nor endorsed by Adobe or the Magento team.\n\n## Install\n\nWe support only Python 3.8+.\n\n### Pip\n\n    python -m pip install pymagento\n\n### Poetry\n\n    poetry add pymagento\n\n## Usage\n\n```python\nimport magento\n\nclient = magento.Magento(base_url="...", token="...", scope="all")\n\nproduct = client.get_product("SKU123")\nprint(magento.get_custom_attribute(product, "description"))\n\nfor order in client.get_orders(status="processing"):\n    print(order["increment_id"], order["grand_total"])\n```\n\nFor more information, [read the docs](https://pymagento2.readthedocs.io/).\n\n## License\n\nCopyright 2020-2022 [Bixoto](https://bixoto.com/).\n',
    'author': 'Bixoto',
    'author_email': 'info@bixoto.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Bixoto/PyMagento',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
