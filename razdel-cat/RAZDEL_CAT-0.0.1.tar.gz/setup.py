import setuptools

with open("README.md", "r") as fh:
	long_description = fh.read()

setuptools.setup(

	name="RAZDEL_CAT",

	version="0.0.1",

	author="NIKOLAEV",

	author_email="nic155k@gmail.com",

	description="This is work is bd",
	
	long_description=long_description,

	long_description_content_type="text/markdown",
	
	url="https://github.com/tamarskir/RAZDEL_CAT.git",

	packages=setuptools.find_packages(),
	
	classifiers=[
		"Programming Language :: Python :: 3.8",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
    
	python_requires='>=3.8',
)