from setuptools import setup, find_packages
 
classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Education',
  'Operating System :: OS Independent',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]
 
setup(
  name='leoncalculator',
  version='0.0.8',
  description='basic calculator',
  long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
  url='',  
  author='Martin Leon',
  author_email='martinleontech23@gmail.com',
  license='MIT', 
  classifiers=classifiers,
  keywords='calculator', 
  packages=find_packages(include=['leoncalculator']),
  install_requires=[''],
  setup_requires=['pytest-runner'],
  tests_require=['pytest==4.4.1'],
  test_suite='tests',
)