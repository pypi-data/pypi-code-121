from setuptools import find_packages, setup

setup(
    name="davesci",
    version="0.0.1",
    install_requires=[
        "Jinja2>=2.0.0",
        "smart-open>=3.0.0",
        "snowflake-connector-python>=1.0.0",
    ],
    extras_require={"test": ["pytest==6.2.2", "pytest_mock>=3.7.0"]},
    packages=find_packages(include=["davesci", "davesci.**"]),
)
