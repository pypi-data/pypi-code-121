from setuptools import setup, find_packages
 
classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Education',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3.10'
]
 
setup(
  name='Mathician',
  version='1.3.3',
  description='Math package',
  long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
  url='https://github.com/ajsharda17/Mathician',  
  author="Arjun Sharda",
  author_email='chairbfroblox@gmail.com',
  license='MIT', 
  classifiers=classifiers,
  keywords='mathician', 
  packages=find_packages(),
  install_requires=[''] 
)