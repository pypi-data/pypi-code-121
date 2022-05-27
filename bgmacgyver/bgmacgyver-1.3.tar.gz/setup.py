from distutils.core import setup
from setuptools import find_packages

setup(
    name='bgmacgyver',
    version='1.3',
    packages=find_packages(),
    package_data={'': ['*.template', '*.svg']},
    author='Jordi Deu-Pons',
    author_email='jordi.deu@irbbarcelona.org',
    description='',
    requires=["netifaces"],
    entry_points={
        'console_scripts': [
            'bgmacgyver = bgmacgyver.indicator:cmdline'
        ]
    }
)
