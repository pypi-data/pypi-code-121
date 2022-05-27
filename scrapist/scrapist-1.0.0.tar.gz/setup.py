import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="scrapist",
    version="1.0.0",
    author="Areen-Rath",
    description="A fast web scraper for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    py_modules=["scraping"],
    package_dir={'':'.'},
    install_requires=["requests", "beautifulsoup4", "lxml"]
)