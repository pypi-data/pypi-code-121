import setuptools

with open("README.md", "r") as fh:
	long_description = fh.read()

setuptools.setup(
	name="ru_attacker",
	version="0.0.2",
	author="Julia Korotkova",
	author_email="koylenka15@gmail.com",
	description="A python package for attacking Russian NLP models",
	long_description=long_description,
	long_description_content_type="text/markdown",
	url="https://github.com/yuliya1324/ru_attacker",
	packages=setuptools.find_packages(),
	install_requires=open("requirements.txt").readlines(),
	classifiers=[
		"Programming Language :: Python :: 3.8",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
	python_requires='>=3.6',
)