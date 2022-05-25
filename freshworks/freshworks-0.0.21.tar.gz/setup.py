import setuptools


with open("README.md", "r") as fin:
    long_description = fin.read()


setuptools.setup(
    name="freshworks",
    version="0.0.21",
    author="Kyle L. Davis",
    author_email="AceofSpades5757.github@gmail.com",
    url="https://github.com/AceofSpades5757/freshworks",
    license="MIT",
    description="Python client library for interacting with Freshworks products.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages("src"),
    project_urls={
        "Documentation": "https://fzflib.readthedocs.io/en/latest/",
        "Author": "https://github.com/AceofSpades5757",
    },
    package_dir={
        "": "src",
        "freshdesk": "src/freshdesk",
        "freshcaller": "src/freshcaller",
    },
    test_suite="tests",
    python_requires=">=3.6",
    install_requires=["requests", "python-dateutil"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 2 - Pre-Alpha",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
