from setuptools import setup
 
classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]
 
setup(
  name='pytermtables',
  version='1.0',
  description='CSV Python tables in terminal',
  long_description=open('README.md').read(),
  long_description_content_type='text/markdown',
  url='https://github.com/Spacerulerwill/pytermtables',  
  author='William Redding',
  author_email='williamdredding@gmail.com',
  license='MIT', 
  classifiers=classifiers,
  keywords='csv', 
  packages=["pytermtables"],
  install_requires=[''] 
)