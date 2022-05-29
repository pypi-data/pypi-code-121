import setuptools

with open("Library.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="xmlApiParse",
    version="1.2.6",
    author="azatbek.t",
    author_email="azatbek.t@itfox-web.com",
    description="Python module for xml parse",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    download_url='https://gitlab.com/itfox-web/foodbox20/food-box-rk-xml-interface/archive/data.zip'
)
