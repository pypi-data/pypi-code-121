'''
Author     : knight_byte ( Abunachar )
File       : setup.py
'''
import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="lpulive",
    packages=["lpulive"],
    version="0.3.0",
    description="Lpulive api for searching, getting messages, getting user detail etc",
    long_description_content_type="text/markdown",
    long_description=long_description,
    url="https://github.com/knight-byte/lpulive",
    download_url="https://github.com/knight-byte/lpulive/archive/v0.3.0.tar.gz",
    author="Abunachar Yeahhia",
    author_email="abunachar1236@gmail.com",
    license="MIT",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
    keywords=["lpulive search", "lpulive api",
              "lpulive", "messaging", "lpu"],
    install_requires=["bs4", "requests", "lxml"],
)
