import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name = "Ageas",
    version = "v0.0.1-alpha5",
    author = "nkmtmsys and JackSSK",
    author_email = "gyu17@alumni.jh.edu",
    description = "AutoML-based Genomic fEatrue extrAction System",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = "https://github.com/nkmtmsys/Ageas",
    project_urls = {"Bug Tracker": "https://github.com/nkmtmsys/Ageas/issues",},
    packages = setuptools.find_packages(),
    package_data = {'': ['data/config/*', 'data/human/*', 'data/mouse/*']},
    classifiers = [
                    'Programming Language :: Python :: 3',
                    'License :: OSI Approved :: MIT License',
                    'Operating System :: OS Independent',
                    ],
    python_requires = ">=3.6",
    include_package_data = True
)
