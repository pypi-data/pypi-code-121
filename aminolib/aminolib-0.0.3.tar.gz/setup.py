import setuptools
with open("README.md", "r") as stream:
    long_description = stream.read()
setuptools.setup(name="aminolib",license = "MIT",version="0.0.3",author="@kingzero#6580",description="Library for Amino",long_description=long_description,long_description_content_type = "text/markdown",install_requires=["datetime","flask","requests","json-minify"],keywords=["amino","aminolib","Lord","AminoAPI"],python_requires=">=3.6",url="https://github.com/EpicSans002/aminolib",project_urls={"aminolib": "https://github.com/EpicSans002/aminolib/issues",},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
)