
from setuptools import setup, find_namespace_packages


setup(
    name='qtoggleserver-eq3bt',
    version='1.4.0',
    description='Eqiva eQ-3 bluetooth thermostat support for qToggleServer',
    author='Calin Crisan',
    author_email='ccrisan@gmail.com',
    license='Apache 2.0',

    packages=find_namespace_packages(),

    install_requires=[
        'bleak'
    ]
)
