from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="dist-truncate",
    version="0.2.0",
    author="Sebastian Schönnenbeck",
    author_email="schoennenbeck@gmail.com",
    url="https://github.com/schoennenbeck/dist-truncate",
    description="Easily truncate scipy distributions.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=["tests"]),
    install_requires=["scipy >= 1"],
    license="MIT",
    python_requires=">=3.6",
    extras_require={
        "dev": [
            "black",
            "isort",
            "mypy",
            "pre-commit",
            "pytest",
            "pytest-cov",
            "coveralls",
            "coverage",
            "flake8",
        ],
    },
)
