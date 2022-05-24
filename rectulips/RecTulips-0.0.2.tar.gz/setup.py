from setuptools import setup, find_packages ,  Extension
 
classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Education',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]
 
setup(
  name='RecTulips',
  version='0.0.2',
  description='Recommandation System',
  long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
  url='',  
  author='Remadnia Ouahiba',
  author_email='remadniahiba3@gmail.com',
  license='MIT', 
  classifiers=classifiers,
  keywords='Recomndation', 
  packages=find_packages(),
  install_requires=['pandas','surprise'] 
)
