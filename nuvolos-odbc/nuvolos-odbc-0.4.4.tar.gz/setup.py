from setuptools import setup, find_packages


def readme():
    with open("README.md") as f:
        return f.read()


exec(open("nuvolos/version.py").read())
setup(
    name="nuvolos-odbc",
    version=__version__,
    description="The Nuvolos python library for database connectivity, internal PyODBC-based version",
    long_description=readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/nuvolos-cloud/python-connector-odbc",
    author="Alphacruncher",
    author_email="support@nuvolos.cloud",
    license="MIT",
    packages=find_packages(exclude=("tests",)),
    include_package_data=True,
    install_requires=["keyring", "pyodbc", "pandas", "pyarrow!=8.0.0"],
    zip_safe=False,
    setup_requires=["pytest-runner"],
    tests_require=["pytest"],
)
