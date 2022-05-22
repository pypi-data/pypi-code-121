import setuptools

with open("README.md", "r") as fh:
	long_description = fh.read()

setuptools.setup(

	name="Work13less15",

	version="0.0.1",

	author="EgorDavydenko",

	author_email="egordavydenko1999@mail.ru",

	description="improved table from lesson 13",
	
	long_description=long_description,

	long_description_content_type="text/markdown",
	
	url="https://github.com/egordavyd/HOMEWORK15",

	packages=setuptools.find_packages(),
	
	classifiers=[
		"Programming Language :: Python :: 3.8",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
    
	python_requires='>=3.6',
)