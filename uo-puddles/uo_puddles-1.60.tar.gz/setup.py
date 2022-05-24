import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="uo_puddles",
    version="1.60",
    author="Stephen Fickas",
    author_email="stephenfickas@gmail.com",
    description="for cis423 class",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    #package_dir={"": "uo_puddles"},
    #packages=setuptools.find_packages(where="uo_puddles"),
    packages=['uo_puddles'],

    python_requires=">=3.6",
)
