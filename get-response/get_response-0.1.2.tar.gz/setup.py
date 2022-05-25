import setuptools


VERSION = '0.1.2'
NAME = 'get_response'
AUTHOR = 'skv0zsneg'
DESCRIPTION = ("Parsing Tool for json-like, xml-like and etc Types of Response"
               "for Humans.")

with open("README.md", "r", encoding="utf-8") as fh:
    LONG_DESCRIPTION = fh.read()


setuptools.setup(
    name=NAME,
    version=VERSION,
    author=AUTHOR,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://github.com/skv0zsneg/get-response",
    project_urls={
        "Bug Tracker": "https://github.com/skv0zsneg/get-response/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.8",
)
