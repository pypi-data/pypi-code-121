import setuptools
with open("version.py", encoding="utf8") as fp:
    exec(fp.read())

long_description = (
    open('README.md', encoding="utf8").read()
    + '\n\n' +
    open('CHANGELOG.md', encoding="utf8").read()
    + '\n')


setuptools.setup(
    name='jarvis-sdk-python',
    url='https://github.com/indykite/jarvis-sdk-python',
    version=__version__,
    author="Indykite",
    author_email="test@indykite.com",
    description='A python SDK package for Indykite\'s jarvis system (with protobuf)',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    license='Apache-2.0',
    install_requires=[
        'authlib',
        'certifi',
        'grpcio',
        'google-api-python-client',
        'google-cloud-storage',
        'protobuf',
    ],
    python_requires='~=3.8',
)
