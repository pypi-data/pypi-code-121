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

name = 'ipyspeck'

# Get ipyspeck version
version = get_version(pjoin(name, '_version.py'))

js_dir = pjoin(here, 'js')
js_dir2 = pjoin(here, 'ipyspeck', 'stspeck', 'frontend')

# Representative files that should exist after a successful build
jstargets = [
    pjoin(js_dir, 'dist', 'index.js'),
]
jstargets2 = [
    pjoin(js_dir2, 'build', 'static'),
]
data_files_spec = [
    ('share/jupyter/nbextensions/ipyspeck', 'ipyspeck/static', '*.*'),
    ('share/streamlit/component/stspeck', 'ipyspeck/stspeck/frontend/build', '*.*'),
    ('share/streamlit/component/stspeck/static', 'ipyspeck/stspeck/frontend/build/static', '*.*'),
    ('share/streamlit/component/stspeck/static/js', 'ipyspeck/stspeck/frontend/build/static/js', '*.*'),
    ('etc/jupyter/nbconfig/notebook.d', '.', 'ipyspeck.json'),
]

cmdclass = create_cmdclass('jsdeps', data_files_spec=data_files_spec)
cmdclass['jsdeps'] = combine_commands(
    install_npm(js_dir, build_cmd='build'), ensure_targets(jstargets),
    install_npm(js_dir2, build_cmd='build'), ensure_targets(jstargets2),
)


LONG_DESCRIPTION = ""
with open("README.md", "r") as fh:
    LONG_DESCRIPTION = fh.read()

setup_args = dict(
    name=name,
    version=version,
    description='Speck Jupyter Widget',
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    include_package_data=True,
    install_requires=[
        'ipywidgets>=7.0.0',
        'jupyter_packaging>=0.3.0'    ],
    packages=find_packages(),
    zip_safe=False,
    cmdclass=cmdclass,
    author='Daniel Mejia (Denphi)',
    author_email='denphi@denphi.com',
    url='https://github.com/denphi/speck/tree/master/widget/ipyspeck',
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
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)

setup(**setup_args)
