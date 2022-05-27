import setuptools

with open("README.md","r") as fh:
	long_description = fh.read()
	
setuptools.setup(
  name = "fuzzytest",
  version = "0.0.3",
  author = "Caio Souza",
  author_email = "caios@take.net",
  description = "Pacote para auxiliar no teste dos inputs na API de FuzzyMatch",
  long_description = long_description,
  long_description_content_type="text/markdown",
  keywords = [],
  install_requires=[
  'pandas',
  'ujson',
  'requests'
  ],
  classifiers=[  
    "Development Status :: 4 - Beta",
    "License :: OSI Approved :: MIT License",
	"Operating System :: OS Independent",
    "Programming Language :: Python :: 3"
  ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)