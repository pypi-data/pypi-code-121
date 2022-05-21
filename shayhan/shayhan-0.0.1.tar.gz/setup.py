from setuptools import setup, find_packages
 
classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Education',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]
 
setup(
  name='shayhan',
  version='0.0.1',
  description='This is a libriry of some fuctions',
  long_description=open('README.md').read() + '\n\n' + open('CHANGELOG.md').read(),
  url='',  
  author='Shayhan Ameen Chowdhury',
  author_email='shayhan.ameen@gmail.com',
  license='MIT', 
  classifiers=classifiers,
  keywords='print', 
  packages=find_packages(),
  install_requires=[''] 
)