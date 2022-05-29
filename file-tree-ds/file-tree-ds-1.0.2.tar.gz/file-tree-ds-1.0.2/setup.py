import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="file-tree-ds",
    version="1.0.2",
    author="Lawrence M",
    author_email="lm3263658@gmail.com",
    description="A tool to create directories for data science project",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/particlemontecarlo/FileTree",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
    install_requires=[
        "treelib==1.6.1"
    ]
)
