import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="gornilo",
    version="0.9.3",
    author="rx00",
    author_email="rx00@hackerdom.com",
    description="AD CTFs checker wrapper",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Hackerdom/Gornilo",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
