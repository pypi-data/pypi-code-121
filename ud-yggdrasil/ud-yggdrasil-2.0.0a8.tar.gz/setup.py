from setuptools import setup, find_packages
from pathlib import Path
long_description = (Path(__file__).parent / "README.md").read_text()

setup(
  name='ud-yggdrasil',
  packages=find_packages(),
  version='2.0.0-alpha.8',
  description='Apps handler for in-house python scripts',
  author='Umbriel Draken',
  long_description=long_description,
  long_description_content_type='text/markdown',
  author_email='umbriel.draken@gmail.com',
  url='https://github.com/um-en/yggdrasil',
  license='MIT',
  classifiers=[
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3.9',
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Natural Language :: English',
    'Operating System :: Microsoft :: Windows :: Windows 10',
  ],
  keywords=['yggdrasil', 'drivers', 'virtual', 'environment'],
  install_requires=[
    'pyyaml',
    'ud-dist-meta>=1.0.2'
  ],
  entry_points={
    'console_scripts': ['yggdrasil=yggdrasil.scripts:cmd_ygg']
  },
  include_package_data=True,
  package_data={'yggdrasil': ['data/*.txt', 'data/*.yaml']},
)
