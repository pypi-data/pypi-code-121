import setuptools
import pathlib

HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setuptools.setup(
    name="cleandev_config_loader",
    version="0.3.2",
    author="Daniel Rodriguez Rodriguez",
    author_email="danielrodriguezrodriguez.pks@gmail.com",
    description="Loader for properties.ini make more easy",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/cleansoftware/libs/public/config-loader",
    project_urls={
        "Bug Tracker": "https://gitlab.com/cleansoftware/libs/public/config-loader/-/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=["properties_loader"],
    install_requires=[
        'backports.strenum==1.1.1'
    ],
    python_requires=">=3.9",
)
