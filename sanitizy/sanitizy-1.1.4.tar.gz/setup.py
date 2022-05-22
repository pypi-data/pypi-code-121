import sys,setuptools
with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name="sanitizy",
    version="1.1.4",
    author="AlaBouali",
    author_email="trap.leader.123@gmail.com",
    description="Helpful module to secure flask apps",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AlaBouali/sanitizy",
    python_requires=">=2.7",
    install_requires=["pymysql","werkzeug"],
    packages=["sanitizy"],
    license="MIT License",
    classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: MIT License ",
    ],
)
