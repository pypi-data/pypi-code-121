import setuptools

with open("README.rst", "r",encoding = "UTF-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="swift-module-copiseded",
    version="0.6.2",
    author="Monkey Hammer Copiseded",
    author_email="Wf6350177@163.com",
    description="this is swift-module-copiseded 0.6.2，kill some bug",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://pypi.org/project/swift-module-copiseded/",
    project_urls={
        "Bug Tracker": "https://github.com/monkeyhammercopiseded/swift-module-copiseded-0.6.1/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "swift apple"},
    packages=setuptools.find_packages(where="swift apple"),
    python_requires=">=3.6",
)
