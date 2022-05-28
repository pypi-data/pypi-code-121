from setuptools import setup, find_packages
 
classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Education',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3',
  'Programming Language :: Python :: 3.7',
  'Programming Language :: Python :: 3.9'
]
 
setup(
  name='vbspython',
  version='0.1.7',
  description='Interact with vbscript in python.',
  long_description=open('README.txt').read() + '\n\n\n' + open('CHANGELOG.txt').read(),
  url='',  
  author='J3ldo',
  author_email='jeldojelle@gmail.com',
  license='MIT', 
  classifiers=classifiers,
  packages=["vbspython"],
  include_package_date=True,
  keywords='vbs vbscript vbspython', 
  install_requires=[''] 
)
