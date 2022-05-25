from setuptools import find_packages, setup

with open("../README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='Flask-Security-Utils',
    author_email='email@alejivo.com',
    packages=find_packages(include=['security_utils']),
    version='1.0.0',
    description='Library for flask security enhancement and retro-compatibility',
    long_description = long_description,
    long_description_content_type="text/markdown",
    author='Alejivo (Alejandro Javier Moyano)',
    license='BSD 3-Clause License',
    install_requires=['Flask>=1.1.4','IP2Location<=8.7.4']
)