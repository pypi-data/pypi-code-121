from setuptools import setup, find_packages

setup(
    name='pqt',
    version='0.0.1',
    description='Tools for quickly analyzing parquet content',
    author='Chris Kamphuis',
    author_email='mail@chriskamphuis.com',
    url='https://github.com/chriskamphuis/parquet-tools',
    install_requires=['duckdb'],
    packages=find_packages(),
    license='Apache License',
    entry_points={
        'console_scripts': [
            'pqt.head=pqt.head:main',
            'pqt.tail=pqt.tail:main'
        ]
    }
)
