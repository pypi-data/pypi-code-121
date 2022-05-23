import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="spyll",
    version="1.2.3",
    author="Dango Labs",
    author_email="info@dangolabs.com",
    description="Spyll is an open source Python package that aims to make text file handling more streamlined. Works with Python versions 3.6+",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://dangolabs.com",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
            ],
)
