import re
import sys
from os.path import join, dirname

from setuptools import setup, find_packages

with open(join(dirname(__file__), 'README.rst'), 'r', encoding='utf-8') as fd:
    long_description = fd.read()


def read_version():
    p = join(dirname(__file__), 'kikyo_api', '__init__.py')
    with open(p, 'r', encoding='utf-8') as f:
        return re.search(r"__version__ = '([^']+)'", f.read()).group(1)


version = read_version()

install_requires = [
    'requests>=2.25.1',
    'requests-toolbelt>=0.9.1',
    'pydantic>=1.8.1',
]


def main():
    if sys.version_info < (3, 6):
        raise RuntimeError('The minimal supported Python version is 3.6')

    setup(
        name='kikyo-api',
        version=version,
        description='kikyo API',
        long_description=long_description,
        zip_safe=False,
        packages=find_packages(exclude=('tests',)),
        include_package_data=True,
        python_requires='>=3.6',
        install_requires=install_requires,
    )


if __name__ == '__main__':
    main()
