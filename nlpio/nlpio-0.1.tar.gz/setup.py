import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="nlpio",
    version="0.1",
    author="Mickaël Andrieu",
    author_email="mickael.andrieu@solvolabs.com",
    url="https://github.com/loveOSS/nlpio",
    description="Library to clean text data for NLP",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(exclude=["tests*"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    py_modules=["nlptools"],
    install_requires=[
        "beautifulsoup4>=4.11",
        "scikit-learn>=1.1",
        "nltk>=3.7",
        "spacy>=3.3.0",
    ],
)
