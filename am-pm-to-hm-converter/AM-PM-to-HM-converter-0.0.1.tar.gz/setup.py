from setuptools import setup

def readme():
    with open('README.md') as f:
        README = f.read()
    return README


setup(
    name="AM-PM-to-HM-converter",
    version="0.0.001",
    description="A Python package to convert AM PM time mode to 24 hours mode.",
    long_description=readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/aniket-coder-arch/AM-PM-to-HM-converter",
    author="Aniket Dubey",
    author_email="daniket182@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["AM_PM_to_HM_converter"],
    include_package_data=True,
    install_requires=["nltk"],
    entry_points={
        "console_scripts": [
            "AM-PM-to-HM-converter=AM_PM_to_HM_converter.AM_PM_to_24",
        ]
    },
)