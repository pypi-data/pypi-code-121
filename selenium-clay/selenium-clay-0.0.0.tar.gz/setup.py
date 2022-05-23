from setuptools import setup, find_packages

setup(
  name='selenium-clay',
  version='0.0.0',
  description='it is hard to use a web browser nowadays',
#  long_description=open('README.md').read(),
#  long_description_content_type='text/markdown',
  url='https://github.com/xloem/selenium-clay',
  keywords=['selenium','headless'],
  classifiers=[
    'Programming Language :: Python :: 3',
    'License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)',
    'Operating System :: OS Independent',
  ],
  packages = find_packages(),
  install_requires=[
    'webdriver_setup',
    'pyshadow',
    'selenium'
  ],
)
