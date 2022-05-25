import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="tfdata",
    version="0.2.8",
    author="DrEdw",
    author_email="ed@topfintech.org",
    description="NA",
    long_description="NA",
    long_description_content_type="text/markdown",
    url="https://github.com/edwincca/tfdata/blob/master/README.md",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    include_package_data=True
)