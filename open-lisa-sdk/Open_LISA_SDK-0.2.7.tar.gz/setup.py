
from setuptools import setup, find_packages

VERSION_PLACEHOLDER = '0.2.7'

setup(
  name = 'Open_LISA_SDK',         # How you named your package folder (MyLib)
  packages=find_packages(),
  version = VERSION_PLACEHOLDER,      # Start with a small number and increase it with every change you make
  license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'SDK for Laboratory Instrument Station Adapter',   # Give a short description about your library
  author = 'Ariel Alvarez Windey & Gabriel Robles',                   # Type in your name
  author_email = 'ajalvarez@fi.uba.ar',      # Type in your E-Mail
  url = 'https://github.com/aalvarezwindey/Open-LISA-SDK',   # Provide either the link to your github or to your website
  download_url = 'https://github.com/aalvarezwindey/Open-LISA-SDK/archive/refs/tags/{}.tar.gz'.format(VERSION_PLACEHOLDER),
  keywords = ['SDK', 'ELECTRONIC', 'INSTRUMENT', 'ADAPTER', 'FIUBA', 'OPEN', 'LISA', 'LABORATORY'],   # Keywords that define your package best
  install_requires=[],
  classifiers=[
    'Development Status :: 4 - Beta',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3.6',      #Specify which pyhton versions that you want to support
  ],
)

