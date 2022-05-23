import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="stringunitconverter",
    version="0.2b",
    author="abaeyens",
    author_email="2arne.baeyens@gmail.com",
    description="Returns multiplier for unit conversion, with units defined as strings.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/abaeyens/stringunitconverter",
    keywords='unit conversion, conversion',
    package_dir={'': 'src'},
    packages=setuptools.find_packages(where='src'),
    package_data={'': ['*.json']},
    install_requires=[],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Education",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
