#see: https://setuptools.readthedocs.io/en/latest/userguide/package_discovery.html
from setuptools import setup, find_packages
import numpy as np
from Cython.Build import cythonize

setup(name="MaxFlowAeiu",
      version="0.1.3",
      description=u"Execution of the Fork Fulkerson method to find the maximum flow of a network",
      long_description=open("README.md", "r", encoding="utf-8").read(),
      url="https://github.com/optimizacion-2-2022-gh-classroom/practica-2-segunda-parte-EddOselotl",
      author="Team-2",
      author_email="",
      classifiers = ['License :: OSI Approved :: MIT License',
                     'Programming Language :: Python :: 3',
                     'Intended Audience :: Education'
                     ],
      license="MIT",
      keywords='max flow',
      packages=find_packages(),
      ext_modules = cythonize("MaxFlowAeiu/MaxFlowAeiu.pyx",compiler_directives={'language_level' : 3}),
      include_dirs=np.get_include(),
      install_requires=[
        'numpy>=1.21.5'
        ]
      )
