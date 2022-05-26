import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="examplebtu41",
    version="0.0.1",
    author="dabrunda45",
    author_email="nino.dabrundashvili.1@btu.edu.ge",
    description="test project",
    long_description=long_description,
    long_description_content_type="text/markdown",

    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "btu41"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)