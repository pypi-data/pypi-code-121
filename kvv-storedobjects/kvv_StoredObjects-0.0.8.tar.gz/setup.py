import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="kvv_StoredObjects",
    version="0.0.8",
    author="Vladislav Kornilov",
    author_email="v.kornilovv@yandex.ru",
    description="StoredObjects is a helper package with University objects for the Publications Activity Module",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/VladKornilov/StoredObjects",
    project_urls={
        "Bug Tracker": "https://github.com/VladKornilov/StoredObjects/issues",
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
        'prettytable'
    ],
    python_requires=">=3.6",
)