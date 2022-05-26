from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

VERSION = '1.0.4' 
DESCRIPTION = 'Python package to be used with Matrix SIM Switch Box tool'

long_description = (here / 'README.rst').read_text(encoding='utf-8')

# Setting up
setup(
        name="mssbox", 
        version=VERSION,
        author="Antonio Carlos",
        author_email="antoniocarlos048@gmail.com",
        description=DESCRIPTION,
        long_description=long_description,
        long_description_content_type='text/x-rst',
        license='MIT',
        url="https://github.com/acarlos94/MSSB_python_package",
        packages=find_packages(),
        python_requires='>=3',
        install_requires=[], # add any additional packages that 
        # needs to be installed along with your package. Eg: 'caer'
        
        keywords=['python', 'mssb', 'matrixssb', 'mssbox'],
        classifiers= [
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Education",
            "Programming Language :: Python :: 3",
            "Operating System :: MacOS",
            "Operating System :: Microsoft :: Windows",
            "Operating System :: Unix"
        ]
)
