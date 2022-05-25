import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="pyseismic",
    version="0.0.6",
    author="Xintao Chai",
    author_email="xtchai@126.com",
    description="A package for seismic data processing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/XintaoChai",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
