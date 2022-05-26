import os
import setuptools
from setuptools import find_packages


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name = "csmemo",
    version = "0.0.6",
    author = "Miguel Ponce-de-Leon",
    author_email = "miguelponcedeleon@gmail.com",
    maintainer = "Miguel Ponce-de-Leon",
    maintainer_email = "miguelponcedeleon@gmail.com",
    description = "A Library implementing constraint-based methods for context-specific metabolic modeling",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url = "https://github.com/bsc-life/csmemo",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires='>=3.6',
    setup_requires=['numpy', 'cobra>=0.25.0', 'corda', 'boolean.py', 'pyfastcore', 'networkx', 'pandas'],
    install_requires=['numpy', 'cobra>=0.25.0', 'corda', 'boolean.py', 'pyfastcore', 'networkx', 'pandas'],
    entry_points={
        'console_scripts': ['build-csm=csmemo.cmds.build_csm:main',
                            'run-experiment=csmemo.cmds.run_insilico_experiment:main',
                            'run-reachability=csmemo.cmds.run_reachability_analysis:main']
        
    }
)
