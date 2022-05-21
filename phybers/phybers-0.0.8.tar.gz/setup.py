import setuptools
import os
import subprocess
from pathlib import Path

this_directory = Path(__file__).parent

long_description = (this_directory / "README.md").read_text()

setuptools.setup(name='phybers',
      version='0.0.8',
      description='Integration of multiple tractography and neural-fibers related tools and algorithms.',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='https://github.com/GonzaloSabat/MT',
      author='Gonzalo Sabat',
      author_email='gsabat@udec.cl',
      license='UdeC',
      package_dir={"": "src"},
      packages=setuptools.find_packages(where="src"),
      include_package_data=True,
      install_requires=[
          'numpy',
          'dipy',
          'joblib',
          'matplotlib',
          'sklearn',
          'networkx',
          'pandas',
          'PyQt5',
          'PyOpenGL',
          'PyOpenGL_accelerate'
      ]
)




