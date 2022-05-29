from __future__ import print_function
from setuptools import setup, find_packages
import os
from os.path import join as pjoin
from distutils import log

from jupyter_packaging import (
    create_cmdclass,
    install_npm,
    ensure_targets,
    combine_commands,
    get_version,
)


here = os.path.dirname(os.path.abspath(__file__))

name = 'faerun_notebook'
LONG_DESCRIPTION = 'A widget for visualising *large* data sets.'

# Get faerun_notebook version
version = get_version(pjoin(name, '_version.py'))

js_dir = pjoin(here, 'js')

# Representative files that should exist after a successful build
jstargets = [
    pjoin(js_dir, 'dist', 'index.js'),
]

data_files_spec = [
    ('share/jupyter/nbextensions/faerun-notebook', 'faerun_notebook/nbextension', '*.*'),
    ('share/jupyter/labextensions/faerun-notebook', 'faerun_notebook/labextension', '**'),
    ('share/jupyter/labextensions/faerun-notebook', '.', 'install.json'),
    ('etc/jupyter/nbconfig/notebook.d', '.', 'faerun-notebook.json'),
]

cmdclass = create_cmdclass('jsdeps', data_files_spec=data_files_spec)
cmdclass['jsdeps'] = combine_commands(
    install_npm(js_dir, npm=['yarn'], build_cmd='build:prod'), ensure_targets(jstargets),
)

setup_args = dict(
    name=name,
    version=version,
    description='A widget for visualising *large* data sets.',
    long_description=LONG_DESCRIPTION,
    include_package_data=True,
    install_requires=[
        'ipywidgets>=7.6.0',
        'numpy',
        'matplotlib'
    ],
    packages=find_packages(),
    zip_safe=False,
    cmdclass=cmdclass,
    author='Daniel Probst',
    author_email='daenuprobst@gmail.com',
    url='https://github.com//faerun-notebook',
    keywords=[
        'ipython',
        'jupyter',
        'widgets',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: IPython',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Multimedia :: Graphics',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)

setup(**setup_args)
