from setuptools import setup, find_packages
 
classifiers = [
       "Development Status :: 1 - Planning",
        "Intended Audience :: Education",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
 
setup(
  name='pyundergraduate',
  version='0.0.3',
  description='A package for numerical analysis with python',
  long_description=open('README.md').read() + '\n\n' + open('CHANGELOG.txt').read(),
  long_description_content_type="text/markdown",
  url='https://github.com/ScientificArchisman/pyundergraduate',  
  author='Archisman Chakraborti',
  author_email='archismanninja@gmail.com',
  license='MIT', 
  classifiers=classifiers,
  keywords=['python', 'scince', 'numerical analysis', 'physics'], 
  packages=find_packages(),
  install_requires=['numpy', 'scipy', 'matplotlib', 'jupyter', 'scienceplots'] 
)