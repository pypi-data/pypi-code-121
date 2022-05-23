"""
McUtils
A simple package for working with common McCoy group problems
"""

# pulled from Ryan's stuff, lightly modified
import glob

from setuptools import setup, find_packages

short_description = __doc__.split("\n")

try:
    with open("README.md", "r") as handle:
        long_description = handle.read()
except:
    long_description = "\n".join(short_description[2:])

def get_version():
    import subprocess
    run_out = subprocess.run(['git', 'describe', '--tags', '--abbrev=0'], capture_output=True)
    return run_out.stdout.decode().strip().strip("v")

setup(
    # Self-descriptive entries which should always be present
    name='mccoygroup-mcutils',
    author='Mark Boyer',
    author_email='b3m2a1@uw.edu',
    description=short_description[0],
    long_description=long_description,
    long_description_content_type="text/markdown",
    version=get_version(),
    license='MIT',

    # Which Python importable modules should be included when your package is installed
    # Handled automatically by setuptools. Use 'exclude' to prevent some specific
    # subpackage(s) from being added, if needed
    packages=find_packages(),

    # Optional include package data to ship with your package
    # Customize MANIFEST.in if the general case does not suit your needs
    # Comment out this line to prevent the files from being packaged with your software
    # include_package_data=True

    install_requires=[
        "numpy>=1.8,<=1.21",
        "scipy>=1.7.0",
        "h5py>=2.10.0",
        "numba>=0.53.1",
        "matplotlib>=3.3.4",
        "jupyterlab>=3.3.2",
        "ipywidgets>=7.6.3",
        "sympy>=1.9",
        "nglview>=3.0.1"
    ],

    include_package_data=True,
    # data_files=[
    #     # like `jupyter nbextension install --sys-prefix`
    #     ("share/jupyter/labextensions/ActiveHTMLWidget", [
    #         "my_fancy_module/static/index.js",
    #     ]),
    #     # like `jupyter nbextension enable --sys-prefix`
    #     ("etc/jupyter/nbconfig/notebook.d", [
    #         "jupyter-config/nbconfig/notebook.d/my_fancy_module.json"
    #     ]),
    #     # like `jupyter serverextension enable --sys-prefix`
    #     ("etc/jupyter/jupyter_notebook_config.d", [
    #         "jupyter-config/jupyter_notebook_config.d/my_fancy_module.json"
    #     ])
    # ],
    data_files=[
        ('share/jupyter/nbextensions/ActiveHTMLWidget', glob.glob('McUtils/Jupyter/JHTML/ActiveHTMLWidget/nbextension/*')),
        ('share/jupyter/labextensions/ActiveHTMLWidget/static', glob.glob('McUtils/Jupyter/JHTML/ActiveHTMLWidget/labextension/static/*.js')),
        ('share/jupyter/labextensions/ActiveHTMLWidget', glob.glob('McUtils/Jupyter/JHTML/ActiveHTMLWidget/labextension/*.json')),
        ('share/jupyter/labextensions/ActiveHTMLWidget', ['McUtils/Jupyter/JHTML/ActiveHTMLWidget/install.json']),
        ('etc/jupyter/nbconfig/notebook.d', ['McUtils/Jupyter/JHTML/ActiveHTMLWidget/ActiveHTMLWidget.json']),
    ]

)