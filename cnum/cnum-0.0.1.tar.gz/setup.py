import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cnum",
    version="0.0.1",
    author="town_paddy",
    author_email="town_paddy@yahoo.com",
    description="Change int and float value to Chinese numeral format string",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    project_urls={
        "website": "https://sites.google.com/view/kumake/english",
        "twitter": "https://twitter.com/tweet_paddy"
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=['cnum'],
    python_requires=">=3.6",
)