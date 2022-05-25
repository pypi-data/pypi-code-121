import setuptools

with open("version.txt", "r") as version_file:
    version = version_file.read().strip()

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="smartdiagnostics-sdk", # Replace with your own username
    version=version,
    author="KCF Technologies, Inc",
    author_email="python-packages@kcftech.com",
    description="Python SDK for executing the SMARTdiagnostics API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="http://www.kcftech.com",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)