from setuptools import setup, find_packages

VERSION = '0.0.2.1'
DESCRIPTION = "some basic tools for interacting with sms-it.ai's api"
LONG_DESCRIPTION = "just something I am working on to interact with sms-it.ai's api (should have everything soon)"

# Setting up
setup(
    # the name must match the folder name 'verysimplemodule'
    name="smsitai",
    version=VERSION,
    author="Jesse Love Ramsey",
    author_email="<jesse@ramsey.love>",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=[],  # add any additional packages that
    # needs to be installed along with your package. Eg: 'caer'

    keywords=['python', 'first package', 'sms-it', 'sms-it.ai', 'p2p sms'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
