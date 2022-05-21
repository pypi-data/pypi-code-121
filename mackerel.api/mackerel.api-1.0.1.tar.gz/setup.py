from setuptools import find_packages, setup

setup(
    name="mackerel.api",
    version="1.0.1",
    description="mackerel.api is a python client library for mackerel api \
        on Python 3.7 and above.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    license="MIT",
    author="10mohi6",
    author_email="10.mohi.6.y@gmail.com",
    url="https://github.com/10mohi6/mackerel-api-python",
    keywords="mackerel rest api rest-api python client",
    packages=find_packages(),
    install_requires=["requests"],
    python_requires=">=3.7.0",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: System :: Networking",
        "Topic :: Office/Business",
        "License :: OSI Approved :: MIT License",
    ],
)
