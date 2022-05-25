import os.path
from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), "README.md")) as fp:
    long_description = fp.read()

setup(
    name="wsgirpc",
    description="Tiny implementation of a WSGI-based RPC server and client",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/luismsgomes/wsgirpc",
    author="Luís Gomes",
    author_email="luismsgomes@gmail.com",
    version="2.0.0",
    package_dir={"": "src"},
    py_modules=["wsgirpc"],
    install_requires=["requests", "tblib"],
    license='MIT',
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
)
