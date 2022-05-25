from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup (
    name='templo',
    version='0.1.0',
    description='Generic template language.',
    py_modules=["templo"],
    package_dir={'': 'src'},
    packages=find_packages(where="src"),
    classifiers=[
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=[
        "ply ~= 3.11",
    ],
    extras_require={
        "dev": [
            "ply ~= 3.11",
            "twine",
        ]
    }
)