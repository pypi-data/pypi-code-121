from setuptools import find_packages, setup

with open("README.rst", "r") as fh:
    long_description = fh.read()


setup(
    name="go-retry",
    version='1.0.1',
    author="(samc0de) Sameer Mahabole",
    author_email="sssam.sam@gmail.com",
    description="Easy to use retry decorator, with fixes and updates.",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/samc0de/retry",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    python_requires='>=3.7',
)
