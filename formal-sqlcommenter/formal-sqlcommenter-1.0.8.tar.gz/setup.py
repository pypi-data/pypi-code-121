import os

from setuptools import find_packages, setup


def read_file(filename):
    with open(os.path.join(os.path.dirname(__file__), filename)) as file:
        return file.read()


setup(
    name='formal-sqlcommenter',
    version='1.0.8',
    packages=find_packages(exclude=['tests']),
    extras_require={
        'psycopg2': ['psycopg2'],
        'django':   ['django'],
    },
    author='Formal',
    author_email='hello@joinformal.com',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Utilities',
    ],
    description='Formal sql commenter',
    long_description=read_file('README.md'),
    long_description_content_type='text/markdown',
    license='BSD',
    keywords='postgresql sql database',
    url='https://github.com/formalco/sqlcommenter',
)
