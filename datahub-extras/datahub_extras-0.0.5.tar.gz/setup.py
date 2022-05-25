import setuptools

setuptools.setup(
    name="datahub_extras",
    version="0.0.5",
    author="Hugh Nguyen",
    description="This package extends datahub and makes it easier to interact with datahub APIs",
    packages=["datahub_extras"],
    install_requires=["acryl-datahub==0.8.34.1", "requests==2.27.1"]
)