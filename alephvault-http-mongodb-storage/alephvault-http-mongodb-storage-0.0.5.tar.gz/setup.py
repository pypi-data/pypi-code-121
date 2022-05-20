import os
from setuptools import setup, find_namespace_packages

setup(
    name='alephvault-http-mongodb-storage',
    version='0.0.5',
    packages=find_namespace_packages(),
    url='https://github.com/AlephVault/http-mongodb-storage',
    license='MIT',
    author='luismasuelli',
    author_email='luismasuelli@hotmail.com',
    description='A lightweight server to work as a simple storage for games, done with MongoDB and Flask',
    install_requires=[
        'Cerberus==1.3.4',
        'click==8.1.2',
        'Flask==2.1.1',
        'importlib-metadata==4.11.3',
        'itsdangerous==2.1.2',
        'Jinja2==3.1.1',
        'MarkupSafe==2.1.1',
        'pymongo==4.1.1',
        'Werkzeug==2.1.1',
        'zipp==3.8.0'
    ]
)
