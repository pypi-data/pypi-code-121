from setuptools import setup, find_packages
 
classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Education',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]
 
setup(
  name='Control Craine Drone',
  version='0.0.1',
  description='A very low-code for programming drone CRAINE',
  
  url='https://craine.io',  
  author='-',
  author_email='crainesystems956@gmail.com',
  license='MIT', 
  classifiers=classifiers,
  keywords='drone', 
  packages=find_packages(),
  install_requires=[''] 
)