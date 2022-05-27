from setuptools import setup, find_packages
 
classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Education',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]
 
setup(
  name='FCropping',
  version='0.0.1',
  description='Face Cropping App',
  long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
  url='',  
  author='Abdul Rafay',
  author_email='rafayrana036@gmail.com',
  license='MIT', 
  classifiers=classifiers,
  keywords='Face Crop', 
  packages=find_packages(),
  install_requires=[''] 
)