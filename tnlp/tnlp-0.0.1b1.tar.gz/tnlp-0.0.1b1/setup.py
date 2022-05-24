from ensurepip import version
from setuptools import find_packages, setup

setup(
    name="tnlp",
    version="0.0.1-beta1",
    author='VictorT',
    packages=find_packages(),
    install_requires=[
        # 'tqdm',
        # 'pandas',
    ],
    classifiers=[
        'Programming Language :: Python :: 3.8',
    ]
)
