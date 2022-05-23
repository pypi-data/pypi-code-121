import setuptools


with open("README.md", "r", encoding="utf-8") as readme:
  long_description = readme.read()


setuptools.setup(
  name="texplotlibx",
  version="0.6.0",
  author="D Hir",
  author_email="d_hir@outlook.com",
  description="A plot library for creating graphics using tikz/pgfplots",
  long_description=long_description,
  long_description_content_type="text/markdown",
  url="https://gitlab.com/d_hir/texplotlib",
  classifiers=[
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    "Operating System :: POSIX",
    "Development Status :: 3 - Alpha"
  ],
  package_dir={"": "src"},
  packages=setuptools.find_packages(where="src"),
  python_requires=">=3.6"
)

