import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="JPSLStudent",
    version="0.6.0",
    description="Install all student modules for Jupyter Physical Science Lab",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/JupyterPhysSciLab/JPSLStudent",
    author="Jonathan Gutow",
    author_email="gutow@uwosh.edu",
    license="GPL-3.0+",
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=[
        # 'python>=3.6',
        'jupyter>=1.0.0',
        'notebook>=6.4.10',
        'jupyterPiDAQ>=0.7.6',
        'Algebra_with_SymPy>=0.9.1',
        'jupyter_Pandas_GUI', # no version b/c should be imported by other pkg.
        'jupyter-datainputtable>=0.7.5',
        'JPSLUtils', # no version b/c should be imported by other pkgs.
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3',
        'Programming Language :: JavaScript',
        'Operating System :: OS Independent'
    ]
)
