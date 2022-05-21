import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="UDataLoader",
    version="0.0.2",
    author="kazgu",
    author_email="hasanjan@outlook.com",
    description="A small example package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kazgu/UDataLoader",
    packages=setuptools.find_packages(),
    package=['UDataLoader'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],

package_data={'': ['word2id']}
)