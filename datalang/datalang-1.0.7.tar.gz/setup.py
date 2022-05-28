from setuptools import setup, find_packages

readme = open('README.md')

setup(
    name='datalang',
    version='1.0.7',
    author='Sendokame',
    description='A parser for Datalang.',
    long_description=readme.read(),
    long_description_content_type='text/markdown',
    packages=(find_packages(include=['datalang']))
)