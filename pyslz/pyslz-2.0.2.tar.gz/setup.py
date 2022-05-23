import os
from setuptools import setup, find_packages
here = os.path.abspath(os.path.dirname(__file__))

Version = '2.0.2'
Description = 'Pessoalize useful functions module'
LongDescription = "Functions that adjusts telephones, cpfs, cnpjs / postgres interaction functions"

setup(name="pyslz",
      version=Version,
      author="André Haffner",
      author_email="<andre.haffner@pessoalize.com>",
      description=Description,
      long_description_content_type="text/markdown",
      long_description=LongDescription,
      packages=find_packages(),
      install_requires=['pandas', 'numpy', 'sqlalchemy', 'psycopg2', 'tqdm', 'discord_webhook'],
      keywords=['python', 'pessoalize'],
      classifiers=["Development Status :: 1 - Planning",
                   "Intended Audience :: Developers",
                   "Programming Language :: Python :: 3",
                   "Operating System :: Microsoft :: Windows"])
