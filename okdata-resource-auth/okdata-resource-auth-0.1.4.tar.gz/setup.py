import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="okdata-resource-auth",
    version="0.1.4",
    author="Oslo Origo",
    author_email="dataplattform@oslo.kommune.no",
    description="Dataplatform resource authorizer",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/oslokommune/okdata-resource-auth",
    packages=setuptools.find_namespace_packages(
        include="origo.resource_auth.*", exclude=["tests*"]
    ),
    namespace_packages=["okdata"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
    ],
    install_requires=["requests"],
)
