import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="FastOptDict",
    version="1.0.0",
    author="JulianZackWu",
    author_email="julianzackwu@gmail.com",
    description="A package for operating",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/JulianZackWu/FastOptDict",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]

)