# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['data_preprocessors']

package_data = \
{'': ['*']}

install_requires = \
['bnlp-toolkit>=3.1.2,<4.0.0', 'nltk>=3.7,<4.0', 'pandas==1.3.0']

setup_kwargs = {
    'name': 'data-preprocessors',
    'version': '0.24.0',
    'description': 'An easy to use tool for Data Preprocessing specially for Text Preprocessing',
    'long_description': '<h1>\n    <img src="https://github.com/MusfiqDehan/data-preprocessors/raw/master/branding/logo.png">\n</h1>\n\n<!-- Badges -->\n\n[![](https://img.shields.io/pypi/v/data-preprocessors.svg)](https://pypi.org/project/data-preprocessors/)\n[![Downloads](https://img.shields.io/pypi/dm/data-preprocessors)](https://pepy.tech/project/data-preprocessors)\n[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1mJuRfIz__uS3xoFaBsFn5mkLE418RU19?usp=sharing)\n[![Kaggle](https://kaggle.com/static/images/open-in-kaggle.svg)](https://kaggle.com/kernels/welcome?src=https://github.com/keras-team/keras-io/blob/master/examples/vision/ipynb/mnist_convnet.ipynb)\n\n<p>\n    An easy to use tool for Data Preprocessing specially for Text Preprocessing\n</p>\n\n## **Table of Contents**\n- [Installation](#installation)\n- [Quick Start](#quick-start)\n- [Functions](#functions)\n    - [Split Textfile](#split-textfile)\n    - [Parallel Corpus Builder](#split-textfile)\n    - [Remove Punc](#split-textfile)\n\n## **Installation**\nInstall the latest stable release<br>\n**For windows**<br>\n`$ pip install -U data-preprocessors`\n\n**For Linux/WSL2**<br>\n`$ pip3 install -U data-preprocessors`\n\n## **Quick Start**\n```python\nfrom data_preprocessors import text_preprocessor as tp\nsentence = "bla! bla- ?bla ?bla."\nsentence = tp.remove_punc(sentence)\nprint(sentence)\n\n>> bla bla bla bla\n```\n\n## **Functions**\n### Split Textfile\n\n```python\nfrom data_preprocessors import text_preprocessor as tp\ntp.split_textfile(\n    main_file_path="example.txt",\n    train_file_path="splitted/train.txt",\n    val_file_path="splitted/val.txt",\n    test_file_path="splitted/test.txt",\n    train_size=0.6,\n    val_size=0.2,\n    test_size=0.2,\n    shuffle=True,\n    seed=42\n)\n\n# Total lines:  500\n# Train set size:  300\n# Validation set size:  100\n# Test set size:  100\n```\n\n',
    'author': 'Md. Musfiqur Rahaman',
    'author_email': 'musfiqur.rahaman@northsouth.edu',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/MusfiqDehan/data-preprocessors',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.1,<4.0',
}


setup(**setup_kwargs)
