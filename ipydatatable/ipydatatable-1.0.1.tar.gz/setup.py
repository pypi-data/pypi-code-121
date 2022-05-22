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

log.set_verbosity(log.DEBUG)
log.info('setup.py entered')
log.info('$PATH=%s' % os.environ['PATH'])

name = 'ipydatatable'
LONG_DESCRIPTION = '''Library to wrap jQuery DataTables to use inside Jupyter.

ipydatatable is a library build using the Jupyter Widget cookiecutter in order to have jQuery DataTable inside a Jupyter Environment.'''

# Get ipydatatable version
version = get_version(pjoin(name, '_version.py'))

js_dir = pjoin(here, 'js')

# Representative files that should exist after a successful build
jstargets = [
    pjoin(js_dir, 'dist', 'index.js'),
]

data_files_spec = [
    ('share/jupyter/nbextensions/ipydatatable', 'ipydatatable/nbextension', '*.*'),
    ('share/jupyter/labextensions/ipydatatable', 'ipydatatable/labextension', '**'),
    ('share/jupyter/labextensions/ipydatatable', '.', 'install.json'),
    ('etc/jupyter/nbconfig/notebook.d', '.', 'ipydatatable.json'),
]

cmdclass = create_cmdclass('jsdeps', data_files_spec=data_files_spec)
cmdclass['jsdeps'] = combine_commands(
    install_npm(js_dir, npm=['yarn'], build_cmd='build:prod'), ensure_targets(jstargets),
)

setup_args = dict(
    name=name,
    version=version,
    description='Library to wrap interactive datatables js into a library that helps pandas dataframes inside JupyerLab',
    long_description=LONG_DESCRIPTION,
    include_package_data=True,
    install_requires=[
        'ipywidgets>=7.6.0',
    ],
    packages=find_packages(),
    zip_safe=False,
    cmdclass=cmdclass,
    author='David Fernandez',
    author_email='teia.eng.14@gmail.com',
    url='https://gitlab.com/teia_engineering/ipydatatable',
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
