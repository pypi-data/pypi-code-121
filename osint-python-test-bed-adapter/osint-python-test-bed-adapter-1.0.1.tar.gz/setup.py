import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="osint-python-test-bed-adapter",
    version="1.0.1",
    author="TimovdK",
    author_email="timo_kuil@hotmail.com",
    description="Python adapter for Kafka",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/OSINT-VDU-TNO/python-adapter",
    include_package_data=True,
    data_files=[('default_schema', ['test_bed_adapter/registry/default_schema.json'])],
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)