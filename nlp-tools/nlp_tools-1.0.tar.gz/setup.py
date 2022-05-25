import codecs
import os
import pathlib
import re

from setuptools import find_packages, setup




__name__ = 'nlp_tools'
__author__ = "fanfanfeng"
__copyright__ = "Copyright 2020, fanfanfeng"
__credits__ = []
__license__ = "Apache License 2.0"
__maintainer__ = "fanfanfeng"
__email__ = "544855237@qq.com"
__url__ = ''
__description__ = '参考Kashgari项目，然后会扩充一些自己做的项目'

__version__ = '1.0.1'
README = __description__

# with codecs.open('requirements.txt', 'r', 'utf8') as reader:
#    install_requires = list(map(lambda x: x.strip(), reader.readlines()))
install_requires = [
    "tensorflow-gpu==2.8.0",
    "numpy==1.22.3",
    "seqeval==0.0.10",
    "pandas==1.3.5",
    "seaborn==0.11.2",
    "scipy==1.7.2",
    "Pillow==8.4.0",
    "tensorflow-addons==0.16.1",
    "transformers==4.17.0",
    "gensim==4.1.2",
    "jieba==0.42.1",
    "sklearn"
]


setup(
    name="nlp_tools",
    version='1.0',
    description='工程提取字段相关的一些定义以及一些常用函数封装',
    author='qiufengfeng',
    install_requires = install_requires,
    author_email='544855237@qq.com',
    package_dir={'nlp_tools': 'nlp_tools'},
    packages=find_packages(),
    include_package_data=True,
    license='LGPL',
    zip_safe=False,
)


