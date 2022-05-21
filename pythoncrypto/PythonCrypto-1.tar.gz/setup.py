from setuptools import setup
with open("README.md","r") as fh:
    long_description = fh.read()
setup(
    name='PythonCrypto',
    version='1',
    description='NORMAL TEXT TO CIPHER TEXT',
    py_modules=["PythonCrypto"],
    package_dir={'':'src'},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)",
        "Operating System :: OS Independent",
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[
        "blessings ~= 1.7"
    ],
    extra_require ={
        "dev":[
            "pytest>=3.7",

        ],
    },
    author="Akshay",
    author_email="akshaysavanoor@gmail.com",
    url="https://github.com/WIZARD00007/PyCrypto.git",
)
