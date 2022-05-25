from setuptools import setup, find_packages
import sys

# Python 3.0 or later needed
if sys.version_info < (3, 6, 0, 'final', 0):
    raise SystemExit('Python 3.6 or later is required!')



setup(
    name= 'pydevmgr_core',
    version= '0.5.0', # https://www.python.org/dev/peps/pep-0440/
    author='Sylvain Guieu',
    author_email='sylvain.guieu@univ-grenoble-alpes.fr',
    packages=find_packages(), 
    #scripts=scripts,
    #data_files=data_files,
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    long_description=open('README.md').read(),
    install_requires=['pyyaml',  'pydantic>=1.9',  'py_expression_eval'],
    
    extras_require={
        "QT":  ["pyqt5"],
    },
    
    dependency_links=[],
    long_description_content_type='text/markdown',
    
    include_package_data=True, 
    package_data= {
        'pydevmgr_core':    ["resources/*.yml"], 
        'pydevmgr_core_qt': ["uis/*.ui"]
    }, 
    entry_points = {
        'console_scripts': [],
    }
)
