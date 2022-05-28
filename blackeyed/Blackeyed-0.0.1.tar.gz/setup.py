import setuptools

with open("README.md", "r") as f:
	long_description = f.read()

setuptools.setup(

	name="Blackeyed",

	version="0.0.1",

	author="Evgeniy Chernookiy",

	author_email="ChernookiyEvgeniy@gmil.com",

	description="Best TV series package",
	
	long_description=long_description,

	long_description_content_type="text/markdown",
	
	url="https://gitlab.com/Chernookiy19",

	packages=setuptools.find_packages(),
	
	classifiers=[
		"Programming Language :: Python :: 3.8",
		"License :: OSI Approved :: MIT License",
	],
    
	python_requires='>=3.8',
)