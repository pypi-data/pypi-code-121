import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ndnsimgraph",
    version="0.1.6",
    author="SunnyQjm",
    author_email="qjm253@pku.edu.cn",
    description="A small graph package used to draw image for ndnsim metrics",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/SunnyQjm/ndnsim-graph",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
