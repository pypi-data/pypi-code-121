import re

from setuptools import setup, find_packages

NAME = 'tvmbase'
URL = f'https://github.com/abionics/{NAME}'


def get_version() -> str:
    code = read_file(f'{NAME}/__init__.py')
    return re.search(r'__version__ = \'(.+?)\'', code).group(1)


def load_readme() -> str:
    return read_file('README.md')


def load_requirements() -> list[str]:
    requirements = read_file('requirements.txt')
    return requirements.replace('==', '>=').splitlines()


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
    install_requires=load_requirements(),
    zip_safe=False,
)
