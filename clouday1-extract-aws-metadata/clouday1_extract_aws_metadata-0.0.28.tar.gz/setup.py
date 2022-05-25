from setuptools import setup, find_packages
 
classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Education',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]
 
setup(
  name='clouday1_extract_aws_metadata',
  version='0.0.28',
  description='A tool to extract metadata from AWS',
  long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
  url='',  
  author='Brandon Wymer',
  author_email='brandon.wymer@rocketmail.com',
  license='MIT', 
  classifiers=classifiers,
  keywords='AWSMetadataExtractor', 
  packages=find_packages(),
  install_requires=[''] 
)
