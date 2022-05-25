import pathlib
import setuptools

HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setuptools.setup(
    name="cleandev-validator",
    version="0.3.1",
    author="Daniel Rodriguez Rodriguez",
    author_email="danielrodriguezrodriguez.pks@gmail.com",
    description="Module for handler dataclass more easy",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/cleansoftware/libs/public/cleandev-validator",
    project_urls={
        "Bug Tracker": "https://gitlab.com/cleansoftware/libs/public/cleandev-validator/-/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=[
        "cleandev_validator"
    ],
    install_requires=[
        'cleandev-config-loader==0.3.5'
    ],
    python_requires=">=3.9",
)
