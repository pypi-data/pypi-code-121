#!/usr/bin/env python3
from setuptools import setup, find_packages

from mockerinho import __version__


setup(
    name='mockerinho',
    description='Lightweight tool designed to simulate web API endpoints.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    version=__version__,
    url='https://github.com/mockerinho/mockerinho',
    author='Mikhail Eremeev',
    author_email='meremeev@sfedu.ru',
    license='MIT',
    platforms=['any'],
    packages=find_packages(exclude=('tests',)),
    python_requires='>=3.7,<=3.10',
    install_requires=[
        'bjoern==3.2.1',
        'PyYAML==6.0',
        'schema==0.7.5',
        'Werkzeug==2.1.2'
    ],
    project_urls={
        'Issues': 'https://github.com/mockerinho/mockerinho/issues',
        'Sources': 'https://github.com/mockerinho/mockerinho',
    },
    entry_points={
        'console_scripts': ['mockerinho=mockerinho.cli:main'],
    },
)
