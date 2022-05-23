__author__ = 'Alex Rogozhnikov'

from setuptools import setup

setup(
    name="newpyter",
    version='0.4.2',
    packages=['newpyter', 'newpyter.storage'],
    install_requires=[
        # useful for grammars
        'parsimonious',
        'nbformat',
        'sh',
        # download / upload to aws
        'boto3',
        # to parse configuration
        'toml',
        # for exception types, but it should be installed by jupyter
        'tornado',
    ],
    entry_points={
        'console_scripts': [
            'newpyter=newpyter.__main__:main',
        ]
    },
)