from setuptools import setup, find_packages

VERSION = '0.1.1' 
DESCRIPTION = 'Thales Graphing Library'
LONG_DESCRIPTION = 'A library for Cartesian graphing using PyGame. See the source code at https://github.com/JacobSinger42/thales.'

# Setting up
setup(
       # the name must match the folder name 'verysimplemodule'
        name="thales", 
        version=VERSION,
        author="Jacob Singer",
        author_email="<jesingermz@gmail.com>",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=['pygame', 'sympy'], # add any additional packages that 
        # needs to be installed along with your package. Eg: 'caer'
        
        keywords=['python', 'graphing', 'pygame'],
        classifiers= [
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Education",
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 3",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
        ]
)