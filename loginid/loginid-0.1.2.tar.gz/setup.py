import setuptools

with open("README.md", 'r', encoding="utf-8") as fh:
    long_description = fh.read()

INSTALL_REQUIRES = [
        "requests",
        "cryptography",
        "pyjwt"
    ]

setuptools.setup(
    name="loginid",
    version="0.1.2",
    author="Quang Hoang",
    author_email="quang@loginid.io",
    description="Interface SDK for LoginID infrastructure",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/loginid1/python-sdk",
    project_urls={
        "Bug Tracker": "https://github.com/loginid1/python-sdk/issues",
        "Documentation": "https://docs.loginid.io/Server-SDKs/Python/python-get-started"
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages("src"),
    python_requires=">=3.6",
    install_requires=INSTALL_REQUIRES
)
