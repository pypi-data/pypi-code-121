import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="fileSimpleTokenizer",
    version="1.1",
    author="joseph forest",
    author_email="josephforestcoder@gmail.com",
    description="A small example package for tokenizing text documents",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/serdarildercaglar/simple-tokenizer",
    project_urls={
        "Bug Tracker": "https://github.com/serdarildercaglar/simple-tokenizer/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)
