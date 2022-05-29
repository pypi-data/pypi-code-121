from setuptools import setup
import re


def version():
    with open('joyoussync/__init__.py', 'r') as init_file:
        _version = re.search('__version__ = \'([^\']+)\'',
                             init_file.read()).group(1)
    return _version


def readme():
    with open('README.md', 'r') as readme_file:
        _readme = readme_file.read()
    return _readme


setup(
    name='joyoussync',
    version=version(),
    description='A small Django app for adding calendar sync support to ls.joyous',
    long_description=readme(),
    long_description_content_type='text/markdown',
    url='https://github.com/frcl/joyoussync',
    author='Lars Franke',
    author_email='frcl@mailbox.org',
    license='MIT',
    packages=['joyoussync'],
    install_requires=[
        'Django',
        'wagtail',
        'ls.joyous',
        'requests',
        'django-q',
    ],
)
