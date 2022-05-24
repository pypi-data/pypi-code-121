from setuptools import setup


def readme():
    with open("README.md") as f:
        return f.read()


setup(
    name="maxp",
    version="0.1.0",
    description="3ds Max Python library",
    long_description=readme(),
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