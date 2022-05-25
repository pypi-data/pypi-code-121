from setuptools import setup, find_packages
import sys

# Python 3.0 or later needed
if sys.version_info < (3, 6, 0, 'final', 0):
    raise SystemExit('Python 3.6 or later is required!')



setup(
    name= 'pydevmgr_ua',
    version= '0.5.0', # https://www.python.org/dev/peps/pep-0440/
    author='Sylvain Guieu',
    author_email='sylvain.guieu@univ-grenoble-alpes.fr',
    packages=find_packages(), 
    #scripts=scripts,
    #data_files=data_files,
    license='CeCILL Free Software License Agreement v2.1',
    long_description=open('README.md').read(),
    install_requires=[ 'cryptography', 'opcua', 'pydevmgr_core>=0.5.0'], 
    
    extras_require={
    },
    
    dependency_links=[],
    long_description_content_type='text/markdown',
    
    include_package_data=True, 
    package_data= {
    
    }, 
    entry_points = {
    }
)
