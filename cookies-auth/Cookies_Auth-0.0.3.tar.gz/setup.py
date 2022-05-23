from setuptools import setup, find_packages
__version__ = "0.0.3"

classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Education',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]
 
setup(
  name='Cookies_Auth',
  packages=['Cookies_Auth'],
  version=__version__,
  description='Personal simple authentication system for HWID using pastebin',
  long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
  url='',  
  author='Callumgm',
  author_email='Callumgm20052005@gmail.com',
  license='MIT', 
  classifiers=classifiers,
  keywords=['authentication', 'pastebin', 'simpleauth'], 
  install_requires=['requests', 'colorama']
)
