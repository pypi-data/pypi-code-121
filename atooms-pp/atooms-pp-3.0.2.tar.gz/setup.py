#!/usr/bin/env python

import os
import glob

# We use numpy distutils to compile and wrap f90 code via f2py
import setuptools
    
with open('README.md', 'r') as fh:
    readme = fh.read()

with open('atooms/postprocessing/_version.py') as f:
    exec(f.read())

args = dict(name='atooms-pp',
            version=__version__,
            description='Post-processing tools for particle simulations',
            long_description=readme,
            long_description_content_type="text/markdown",
            author='Daniele Coslovich',
            author_email='daniele.coslovich@umontpellier.fr',
            url='http://www.coulomb.univ-montp2.fr/perso/daniele.coslovich/',
            packages=['atooms', 'atooms/postprocessing'],
            scripts=glob.glob(os.path.join('bin', '*.py')),
            install_requires=['atooms>=2', 'numpy', 'argh', 'tqdm'],
            license='GPLv3',
            setup_requires = ['numpy'],
            classifiers=[
                'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
                'Development Status :: 5 - Production/Stable',
                'Intended Audience :: Science/Research',
                'Programming Language :: Python :: 2',
                'Programming Language :: Python :: 2.7',
                'Programming Language :: Python :: 3',
                'Programming Language :: Python :: 3.4',
                'Topic :: Scientific/Engineering :: Physics',
            ]
)

try:
    from numpy.distutils.core import setup, Extension
    
    args["ext_modules"] = [Extension('atooms.postprocessing.realspace_wrap',
                                     sources=['atooms/postprocessing/realspace.f90'],
                                     extra_f90_compile_args=[]),
                           Extension('atooms.postprocessing.fourierspace_wrap', 
                                     sources=['atooms/postprocessing/fourierspace.f90'],
                                     extra_f90_compile_args=[])]

except (ModuleNotFoundError, ImportError):
    from distutils.core import setup

try:
    setup(**args)
except:
    args["ext_modules"] = []
    setup(**args)
