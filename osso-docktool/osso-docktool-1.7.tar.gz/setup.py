# osso-docktool -- HDD administration and maintenance
# Copyright (C) 2015-2022 OSSO B.V.

from setuptools import setup, find_packages
from os.path import dirname, join

long_descriptions = []
with open(join(dirname(__file__), 'README.rst')) as file:
    long_descriptions.append(file.read())
version = '1.7'

setup(
    name='osso-docktool',
    version=version,
    data_files=[('share/doc/osso-docktool', [
        'README.rst', 'local_settings.py.template'])],
    entry_points={'console_scripts': [
        'osso-docktool = osso_docktool.docktool:main']},
    packages=find_packages(include=['osso_docktool', 'osso_docktool.*']),
    description='HDD administration and maintenance',
    long_description=('\n\n\n'.join(long_descriptions)),
    author='OSSO B.V.',
    author_email='dev+osso-docktool@osso.nl',
    url='https://git.osso.nl/osso-io/docktool',  # osso-int[ernal]?
    license='Undecided',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: System Administrators',
        # ('License :: OSI Approved :: GNU General Public License v3 '
        #  'or later (GPLv3+)'),
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: System :: Filesystems',
        'Topic :: Utilities',
    ],
    install_requires=[
        'requests',
    ],
)

# vim: set ts=8 sw=4 sts=4 et ai tw=79:
