#!/usr/bin/python3

from setuptools import setup

setup(
    name='prometheus-splitwise-exporter',
    version='0.9',
    maintainer='Jelmer Vernooij',
    maintainer_email='jelmer@jelmer.uk',
    scripts=['prometheus-splitwise-exporter.py'],
    url='https://github.com/jelmer/prometheus-splitwise-exporter',
    license='Apachev2',
    install_requires=['splitwise', 'prometheus-client'],
)
