import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="altvmasterlist",
    version="2.0.9",
    author="Nickwasused",
    author_email="contact.nickwasused.fa6c8@simplelogin.co",
    description="A package to use the alt:V Masterlist api",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Nickwasused/altv-python-masterlist",
    project_urls={
        "Bug Tracker": "https://github.com/Nickwasused/altv-python-masterlist/issues",
        "Documentation": "https://nickwasused.github.io/altv-python-masterlist/"
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.7",
)