from setuptools import setup


with open("README.md") as f:
    README = f.read()

with open("version.txt") as f:
    VERSION = f.read()


setup(
    name="maxp",
    version=VERSION,
    description="3ds Max Python library",
    long_description=README,
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    url="https://github.com/thomascswalker/maxp",
    author="thomascswalker",
    author_email="thomascswalker@gmail.com",
    keywords="template",
    license="MIT",
    packages=[
        "maxp",
    ],
    install_requires=["pyside2"],
    include_package_data=True,
)