import setuptools

with open("README.md", "r") as fh:
	long_description = fh.read()

setuptools.setup(

	name="hw15",

	version="0.0.1",

	author="vemelyanov",

	author_email="vemelyanov@mail.ru",

	description="Doing homework 15",
	
	long_description=long_description,

	long_description_content_type="text/markdown",
	
	url="https://github.com/vemelyanov07/hw15.git",

	packages=setuptools.find_packages(),
	
	classifiers=[
		"Programming Language :: Python :: 3.8",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
    
	python_requires='>=3.8',
)