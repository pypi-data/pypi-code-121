import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="fchroot",
    version="0.4.1",
    author="Daniel Robbins",
    author_email="drobbins@funtoo.org",
    description="Funtoo franken-chroot tool.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://code.funtoo.org/bitbucket/users/drobbins/repos/fchroot/browse",
    scripts=['bin/fchroot'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires='>=3.7',
    packages=setuptools.find_packages()
)
