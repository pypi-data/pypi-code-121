# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['magnifier', 'magnifier.evaluation', 'magnifier.transformer']

package_data = \
{'': ['*']}

install_requires = \
['matplotlib>=3.5.1,<4.0.0',
 'mlflow>=1.22.0,<2.0.0',
 'numpy>=1.20.0,<2.0.0',
 'pandas>=1.1.4,<2.0.0',
 'pydub>=0.25.1,<0.26.0',
 'python_speech_features>=0.6,<0.7',
 'scikit-learn>=1.0.2,<2.0.0',
 'scipy>=1.7.0,<1.8.0',
 'seaborn>=0.11.2,<0.12.0',
 'typing-extensions>=4.0.1,<5.0.0']

setup_kwargs = {
    'name': 'magnifier',
    'version': '0.0.5',
    'description': '精度検証やパラメータチューニングで使用する関数群のライブラリ',
    'long_description': '精度検証やパラメータチューニングで使用する関数群のライブラリ。\n\n[Document](https://koreander2001.github.io/magnifier/)\n\n',
    'author': 'koreander2001',
    'author_email': 'neokamiyama@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/koreander2001/magnifier',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<3.10',
}


setup(**setup_kwargs)
