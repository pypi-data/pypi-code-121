import os
from setuptools import setup
from setuptools import find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

current_folder = os.path.dirname(os.path.realpath(__file__))
requirement_path = current_folder + '/requirements.txt'
install_requires = []
if os.path.isfile(requirement_path):
    with open(requirement_path) as f:
        install_requires = f.read().splitlines()

setup(
	name = 'java_features',
	version = '0.1.1',
	description = 'This package contains java code similarity features calculation',
	long_description=long_description,
	long_description_content_type="text/markdown",
	author = 'Tomy Widjaja',
	author_email = 'tomywid77@gmail.com',
	url = 'https://github.com/tomytw/java-features',
	packages = find_packages(exclude=('tests*', 'testing*')),
	python_requires='>=3.7',
	install_requires=install_requires,
	classifiers=[
        "Programming Language :: Python :: 3.7",
		"Programming Language :: Java",
        "License :: OSI Approved :: MIT License",
		"Topic :: Scientific/Engineering :: Artificial Intelligence",
		"Topic :: Text Processing :: General",
		"Topic :: Utilities"
	],
)