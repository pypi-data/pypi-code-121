import setuptools

with open("README.MD", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="kliffHenger",
    version="0.0.1",
    author="KliffHenger",
    author_email="my@mail.mail",
    description="Package for test",
    long_description=long_description ,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        ],
    python_requires= '>=3.8',  
)