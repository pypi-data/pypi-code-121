import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="quadro",
    version="1.0.0",
    author="2vin2vin",
    author_email="sohithvulpie@gmail.com",
    description="A quad package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/2vin2vin/quadro.git",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)

