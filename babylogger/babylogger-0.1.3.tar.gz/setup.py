from setuptools import setup, find_packages
import os

VERSION = "0.1.3"
DESCRIPTION  = "Minimilastic logger"
LONG_DESCRIPTION = ""

setup(
    name = "babylogger",
    version = VERSION,
    author = "VISHAL KUMAR",
    author_email = "vishalku@iiitd.ac.in",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages= find_packages(),
    install_requires = [],
    keywords = ["python", "logger", "mini", "checkpoint-track"],
    classifiers=[
    	"Development Status :: 4 - Beta",
    	"Intended Audience :: Developers",
    	"Intended Audience :: Science/Research",
    	"License :: Free For Educational Use",
    	"Operating System :: MacOS",
    	"Operating System :: Microsoft",
    	"Operating System :: POSIX",
    	"Programming Language :: Python :: 3 :: Only",
    	
    	]

)
