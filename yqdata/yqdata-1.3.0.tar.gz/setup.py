# -*- coding: utf-8 -*-

#         详细的授权流程，请联系 public@ricequant.com 获取。
import sys
import setuptools

requirements = [
    'requests',
    'numpy',
    'pandas',
    'python-dateutil',
    'six',
    'logbook',
    'click >=7.0.0',
    'jsonpickle',
    'simplejson',
    'PyYAML',
    'tabulate',
    'rqrisk',
    'h5py',
    'matplotlib >=2.2.0',
]

with open("README.md", "r") as fh:
    long_description = fh.read()

if sys.version_info < (3, 5):
    requirements.append('typing')

if sys.version_info.major == 2 and sys.version_info.minor == 7:
    requirements.extend([
        "enum34",
        "fastcache",
        "funcsigs",
        "backports.tempfile",
    ])

setuptools.setup(
    name="yqdata",
    version="1.3.0",
    author="Hu Min",
    author_email="humin11@icloud.com",
    description="小容量化数据平台",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="http://gitlab.intellinker.com/intellinker-prd-rong-001/jupyterhub-deploy-01",
    packages=setuptools.find_packages(),
    install_requires=['opensearch-py'],
    entry_points={
        'console_scripts': [
            'yqdata=yqdata:main'
        ],
    },
    classifiers=[
        'Programming Language :: Python',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)
