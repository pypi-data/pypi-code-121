import io

from setuptools import setup

with open('requirements.txt') as f:
    required = f.readlines()

setup(
    name='hivebox',
    version='1.0.2',
    description='HiveBox is a toolset helping in AI/ML/CV and other tasks',
    long_description=io.open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url='https://gitlab.com/hivecv/hivebox',
    keywords="hive box",
    author='HiveCV',
    author_email='lukasz@hivecv.com',
    license_files = ('LICENSE',),
    packages=['hivebox'],
    package_dir={"": "src"},  # https://stackoverflow.com/a/67238346/5494277
    install_requires=required,
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)
