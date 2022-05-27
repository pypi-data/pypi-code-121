import pathlib
import setuptools

HERE = pathlib.Path(__file__).parent

README = (HERE / "README.md").read_text()

setuptools.setup(
    name="cleandev-generic-utils",
    version="0.1.9",
    author="Daniel Rodriguez Rodriguez",
    author_email="danielrodriguezrodriguez.pks@gmail.com",
    description="Cleandev Generic Utils for other libs",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/cleansoftware/libs/public/cleandev-generic-utils",
    project_urls={
        "Bug Tracker": "https://gitlab.com/cleansoftware/libs/public/cleandev-generic-utils/-/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=["generic_utils"],
    install_requires=['cryptography==37.0.2'],
    python_requires=">=3.9",
)

