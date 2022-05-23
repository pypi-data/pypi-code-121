import re

from setuptools import setup, find_packages

NAME = 'tvmbase'
URL = f'https://github.com/abionics/{NAME}'


def get_version() -> str:
    code = read_file(f'{NAME}/__init__.py')
    return re.search(r'__version__ = \'(.+?)\'', code).group(1)


def load_readme() -> str:
    return read_file('README.md')


def read_file(filename: str) -> str:
    with open(filename) as file:
        return file.read()


setup(
    name=NAME,
    version=get_version(),
    description='Part of Evertrace project | Base TVM models and utils',
    long_description=load_readme(),
    long_description_content_type='text/markdown',
    author='Alex Ermolaev',
    author_email='abionics.dev@gmail.com',
    url=URL,
    keywords='evertrace tvm utils',
    classifiers=[
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    packages=find_packages(exclude=['tests', 'examples']),
    install_requires=[
        'ton-client-py>=1.33.1.0',
        'attrs>=21.4.0',
        'loguru>=0.6.0',
        'jsonizer>=1.2.0',
    ],
    zip_safe=False,
)
