import setuptools

with open("README.md", "r") as fh:
	long_description = fh.read()

setuptools.setup(

	name="MySqlTable",

	version="0.0.1",

	author="KukharenkaDzmitry",

	author_email="dimsiko@gmail.com",

	description="This is SqlTable",
	
	long_description=long_description,

	long_description_content_type="text/markdown",
	
	url="https://github.com/DzmitryKukharenka/MySqlTable",

	packages=setuptools.find_packages(),
	
	classifiers=[
		"Programming Language :: Python :: 3.8",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
    
	python_requires='>=3.8',
)