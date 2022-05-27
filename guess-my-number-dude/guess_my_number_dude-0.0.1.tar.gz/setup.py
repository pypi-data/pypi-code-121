import setuptools

with open("README.md", "r") as f:
	long_description = f.read()

setuptools.setup(
	name="guess_my_number_dude",
	version="0.0.1",
	author="Yury Herasimau",
	author_email="dude@mail.ru",
	description="Package for test",
	long_description=long_description,
	long_description_content_type="text/markdown",
	url="http://bitbucket.org/dude/distribute/issues/",
	packages=setuptools.find_packages(),
	classifiers=[
		"Programming Language :: Python :: 3.8",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
	python_requires='>=3.8',
)