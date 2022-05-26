import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="hscan",
    version="1.4.6",
    author="jyanghe",
    author_email="jyanghe1023@gmail.com",
    description="A python framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jyangHe/hscan",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8.11',
)