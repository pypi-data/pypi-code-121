#!/usr/bin/env python
import ast
import os
import re

from setuptools import find_packages, setup

HERE = os.path.abspath(os.path.dirname(__file__))
init = os.path.join(HERE, "src", "unicef_security", "__init__.py")

_version_re = re.compile(r'__version__\s+=\s+(.*)')
_name_re = re.compile(r'NAME\s+=\s+(.*)')

with open(init, 'rb') as f:
    content = f.read().decode('utf-8')
    VERSION = str(ast.literal_eval(_version_re.search(content).group(1)))
    NAME = str(ast.literal_eval(_name_re.search(content).group(1)))


setup(
    name=NAME,
    version=VERSION,
    url='https://github.com/unicef/unicef-security',
    author='UNICEF',
    author_email='rapidpro@unicef.org',
    description='Provides Basic UNICEF User model and integration with Azure',
    platforms=['any'],
    license='Apache 2 License',
    classifiers=[
        'Environment :: Web Environment',
        'Programming Language :: Python :: 3.9',
        'Framework :: Django',
        'Framework :: Django :: 3.2',
        'Framework :: Django :: 4.0',
        'Intended Audience :: Developers'
    ],
    install_requires=[
        'celery',
        'cryptography',
        'django',
        'django-admin-extra-buttons',
        'django-constance',
        'django-countries',
        'django-picklefield',
        'requests',
        'social-auth-app-django',
        'PyJWT'
    ],
    extras_require={
        'test': [
            'django-webtest',
            'factory-boy',
            'flake8',
            'httpretty',
            'isort',
            'mock',
            'pytest',
            'pytest-cov',
            'pytest-django',
            'pytest-echo',
            'pytest-pythonpath',
            'pytest-redis',
            'requests-mock',
            'unittest2',
            'vcrpy',
        ],
    },
    package_dir={'': 'src'},
    packages=find_packages('src'),
    include_package_data=True,
)
