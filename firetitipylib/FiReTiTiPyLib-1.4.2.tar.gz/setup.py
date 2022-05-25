import os
import sys

from pathlib import Path
from setuptools import find_packages, setup

import FiReTiTiPyLib



def AllFiles():
	files = []
	for file_path in Path('cycIFAAP/FiReTiTiPyLib').glob('**/*.py'):
		path = str(file_path)
		if not "PyTorch_Models" in path:
			files.append(path[9:])
	return files



setup(
	name=FiReTiTiPyLib.__name__,
	packages=find_packages(),
	version=FiReTiTiPyLib.__version__,
	author="Guillaume THIBAULT",
	author_email="thibaulg@ohsu.org",
	maintainer="Guillaume THIBAULT",
	maintainer_email="thibaulg@ohsu.edu",
	#url = "https://www.thibault.biz/Research/cycIFAAP/cycIFAAP.html",
	download_url="https://www.thibault.biz/Doc/FiReTiTiPyLib/FiReTiTiPyLib-" + FiReTiTiPyLib.__version__ + ".tar.gz",
	license="MIT",
	plateforms='ALL',
	#package_data={'cycIFAAP':AllFiles()},
	#data_files=[('',['cycIFAAP/FiReTiTiLiB.jar'])],
	keywords=["cyclic Immunofluorescence", "cycif", "immunofluorescence",
				"registration", "segmentation", "features", "features extraction",
				"nuclei", "nucleus", "cells", "cell", "cell analysis"],
	classifiers=["Development Status :: 5 - Production/Stable",
					"Environment :: Console",
					"Environment :: GPU",
					"Environment :: GPU :: NVIDIA CUDA :: 10.2",
					"Environment :: Other Environment",
					"Intended Audience :: Developers",
					"Intended Audience :: Healthcare Industry",
					"Intended Audience :: Science/Research",
					"License :: OSI Approved :: MIT License",
					"Operating System :: OS Independent",
					"Programming Language :: Java",
					"Programming Language :: Python :: 3",
					"Programming Language :: Python :: 3.8",
					"Programming Language :: Python :: 3.9",
					"Topic :: Scientific/Engineering",
					"Topic :: Scientific/Engineering :: Artificial Intelligence",
					"Topic :: Scientific/Engineering :: Bio-Informatics",
					"Topic :: Scientific/Engineering :: Image Processing",
					"Topic :: Scientific/Engineering :: Image Recognition"],
	install_requires=[#"bleach~=3.3.0",
						#"certifi>=2020.12.5",
						"glob2>=0.7",
						"graphviz>=0.8",
						"horology>=1.1.0",
						"imagecodecs>=2021.5.20",
						"imageio>=2.9.0",
						"matplotlib>=3.4.2",
						"natsort>=7.1.0",
						"numpy>=1.21.5",
						"opencv-contrib-python-headless>=4.5.5",
						"opencv-python-headless>=4.5.5",
						"pandas>=1.2.4",
						"Pillow>=8.2.0",
						"psutil>=5.8.0",
						"qtconsole>=5.1.0",
						"QtPy>=1.9.0",
						"scikit-image>=0.18.3,<0.19",
						"scikit-learn>=0.24.2",
						"scipy>=1.6.3",
						"seaborn>=0.11.1",
						#"six>=1.15.0",
						"sklearn>=0.0",
						"spams>=2.6.2.5",
						"tifffile>=2021.4.8",
						"torch>=1.7.1,<1.8",
						"torchvision>=0.8.2,<0.9",
						"tornado>=6.1",
						"wheel>=0.37.0"],
	python_requires=">=3.8,<3.10",
	description="Python libraries used as support/tools.",
	long_description=open(os.path.join(os.path.dirname(__file__), 'FiReTiTiPyLib/README.md')).read()
	)
