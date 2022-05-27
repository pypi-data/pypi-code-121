from setuptools import setup, Extension
import os

# read the contents of your README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'Readme.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='soteria',
    packages=['soteria', 'soteria.handlers'],
    version='0.2.2',
    license='MIT',
    description='Scheduling tool for system monitoring.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Euan Campbell',
    author_email='dev@euan.app',
    url='https://github.com/euanacampbell/soteria',
    download_url='https://github.com/euanacampbell/soteria/archive/refs/heads/master.tar.gz',
    keywords=['schedule', 'task'],
    include_package_data=True,
    install_requires=[
        'holidays',
        'PyMySQL',
        'PyYAML',
        'flask',
        'pyodbc',
    ],
    classifiers=[
        # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
