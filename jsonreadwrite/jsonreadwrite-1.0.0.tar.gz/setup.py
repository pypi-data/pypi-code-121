"""
    seting up the package
"""
import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="jsonreadwrite",
    version="1.0.0",
    author="Sumiza",
    author_email="sumiza@gmail.com",
    description="A package to read and write json files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Sumiza/jsonreadwrite/",
    project_urls={
        "Bug Tracker": "https://github.com/Sumiza/jsonreadwrite/issues",
    },
    classifiers=[
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.9",
)
