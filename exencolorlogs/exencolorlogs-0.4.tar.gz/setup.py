import setuptools

with open("README.md") as readme_file:
    long_description = readme_file.read()


setuptools.setup(
    name="exencolorlogs",
    version="0.4",
    description="Package for colorlogs",
    long_description=long_description,
    author="Exenifix",
    url="https://github.com/Exenifix/exencolorlogs",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages("src"),
    python_requires=">=3.7",
    install_requires=["termcolor>=0.2"]
)
