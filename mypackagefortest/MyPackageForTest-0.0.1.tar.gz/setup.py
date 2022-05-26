# pip install setuptools
import setuptools

with open("README.MD", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="MyPackageForTest",
    version="0.0.1",
    author="Me",
    author_email="lapin.kirill45@gmail.com",
    description="Package for test",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License"
    ],
    python_requires='>=3.6'
)