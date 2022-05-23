import os, re
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

NAME = "Cookies_Auth"

def read_file(path):
    with open(os.path.join(os.path.dirname(__file__), path)) as fp:
        return fp.read()

def _get_version_match(content):
    # Search for lines of the form: # __version__ = 'ver'
    regex = r"^__version__ = ['\"]([^'\"]*)['\"]"
    version_match = re.search(regex, content, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

def get_version(path):
    return _get_version_match(read_file(path))

setup(
  name=NAME,
  packages=[NAME],
  version=get_version(os.path.join(NAME, '__init__.py')),
  description='Simple authentication system for HWID using pastebin',
  long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
  url='https://www.github.com/Callumgm',
  author='Callumgm',
  author_email='Callumgm20052005@gmail.com',
  license='MIT',
  keywords=['authentication', 'pastebin', 'simpleauth'], 
  install_requires=['requests', 'colorama'],
  # see classifiers https://pypi.org/pypi?%3Aaction=list_classifiers
  classifiers=[
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Education',
    'Operating System :: Microsoft :: Windows :: Windows 10',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3.8'
  ]
)
