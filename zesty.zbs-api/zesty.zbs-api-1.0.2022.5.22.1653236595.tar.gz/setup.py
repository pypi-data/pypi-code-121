import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='zesty.zbs-api',
    install_requires=['requests',
                      'zesty.zesty-id'],
    version='1.0',
    include_package_data=True,
    author="Zesty.co",
    author_email="rnd@cloudvisor.co",
    description="Zesty Disk API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/javatechy/dokr",
    packages=[
        "zesty",
        "zesty.models"
    ],
    package_dir={
        "zesty": "src",
        "zesty.models": "src/models"
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
