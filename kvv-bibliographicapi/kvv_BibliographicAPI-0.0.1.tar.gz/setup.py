import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="kvv_BibliographicAPI",
    version="0.0.1",
    author="Vladislav Kornilov",
    author_email="v.kornilovv@yandex.ru",
    description="BibliographicAPI is used to access official APIs of several bibliographic databases",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/VladKornilov/BibliographicAPI",
    project_urls={
        "Bug Tracker": "https://github.com/VladKornilov/BibliographicAPI/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(),
    install_requires=[
        'requests',
        'beautifulsoup4',
        'transliterate',
        'prettytable',
        'kvv_StoredObjects'
    ],
    python_requires=">=3.6",
)
