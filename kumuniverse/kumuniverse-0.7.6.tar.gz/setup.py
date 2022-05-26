from setuptools import find_packages, setup


VERSION = "0.7.6"

DESCRIPTION = "Data team shared library for accessing services"

setup(
    name="kumuniverse",
    version=VERSION,
    description=DESCRIPTION,
    long_description="""Data team shared library for accessing services""",
    long_description_content_type="text/markdown",
    author="Renz Abergos",
    author_email="renz@kumu.ph",
    license="MIT",
    packages=find_packages(),
    install_requires=[
        "pymongo",
        "pymongo[srv]",
        "pymongo[aws]",
        "requests",
        "UnleashClient",
        "boto3",
        "pandas",
    ],
    extras_require={"databricks": ["pyspark"], "sagemaker": ["sagemaker", "redis"]},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ],
)
