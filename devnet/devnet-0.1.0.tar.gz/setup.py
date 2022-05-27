# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['devnet']

package_data = \
{'': ['*']}

install_requires = \
['hydra-core>=1.1.1,<2.0.0',
 'logzero>=1.7.0,<2.0.0',
 'matplotlib>=3.5.1,<4.0.0',
 'pandas==1.3.5',
 'sklearn>=0.0,<0.1',
 'torch>=1.10.2,<2.0.0']

setup_kwargs = {
    'name': 'devnet',
    'version': '0.1.0',
    'description': 'Unofficial pytorch implementation of deviation network for table data.',
    'long_description': '# Devnet\nUnofficial pytorch implementation of deviation network for table data.\n\npaper of deviation network  \nhttps://arxiv.org/abs/1911.08623\n\noriginal keras implementation by authors of the paper is here  \nhttps://github.com/GuansongPang/deviation-network\n\n## Setup\ninstall poetry followed by  \nhttps://python-poetry.org/docs/master/#installing-with-the-official-installer\n\ninstall dependencies\n```\npoetry install\n```\n\n## Usage\ntrain model with train/eval.csv under dataroot\n```\npoetry python src/main.py dataroot=data/debug epochs=10 eval_interval=10\n```\n\npredict score and output result\n```\npoetry python src/main.py predict_only=true predict_input=data/debug/eval.csv model_path=data/debug/models/example.pth\n```\n',
    'author': 'Yuji Kamiya',
    'author_email': 'y.kamiya0@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/y-kamiya/devnet',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.1,<4.0',
}


setup(**setup_kwargs)
