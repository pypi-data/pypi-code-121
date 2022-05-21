from ensurepip import version
from setuptools import find_packages, setup

setup(
    name="qrutils",
    version="0.0.2-beta1",
    author='VictorT',
    packages=find_packages(),
    install_requires=[
        'tqdm',
        'pandas',
    ],
    classifiers=[
        'Programming Language :: Python :: 3.8',
    ]
)
