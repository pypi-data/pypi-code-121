# -*- coding: utf8 -*-

"""
A setuptools based setup module.
See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

from setuptools import setup, find_packages


setup(
    name='sisaptools',
    version='1.10.3',
    description='Eines comunes de SISAP',
    long_description='Eines comunes per a l\'execució de SISAP i SIDIAP. \
                      Per a més informació veure \
                      https://github.com/sisap-ics/sisaptools/',
    url='https://github.com/sisap-ics/sisaptools',
    author='SISAP',
    author_email='sisap@gencat.cat',
    license='MIT',
    install_requires=[
        'cx-Oracle',
        'future',
        'jdcal',
        'mysqlclient',
        'paramiko',
        'pycryptodome',
        'python-dateutil',
        'redis'
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ],
    keywords='sisap database development',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    package_data={'': ['*.json']}
)
