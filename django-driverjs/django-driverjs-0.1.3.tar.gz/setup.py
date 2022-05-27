import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'readme.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-driverjs',
    version='0.1.3',
    packages=find_packages(),
    include_package_data=True,
    license='MIT License',
    description='Django wraper over Driver.js',
    long_description=README,
    url='https://github.com/iwalucas/django-driverjs/',
    author='Lucas',
    author_email='teppss@gmail.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 2.2',
        'Framework :: Django :: 3.1',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
