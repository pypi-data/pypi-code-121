import setuptools

# read the contents of your README file
with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name = "napalm_aruba505",
    version = "0.0.56",
    author = "David Johnnes",
    author_email = "david.johnnes@gmail.com",
    description = ("Napaml Aruba driver for ArubaOs Wi-Fi devices '505' "),
    license = "BSD",
    keywords = "napalm drive",
    url="https://github.com/djohnnes/napalm-arubaOS",
    packages=['napalm_aruba505'],
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        "Topic :: Utilities",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: BSD License",
    ],
)