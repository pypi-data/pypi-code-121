from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '0.0.5'
DESCRIPTION = 'FlaskPostgresSequelize'

# Setting up
setup(
    name="pgsequelize",
    version=VERSION,
    author="Rahil Patel (TechAddict)",
    author_email="<rahil.geek21@outlook.com>",
    description=DESCRIPTION,
    packages=find_packages(),
    install_requires=["psycopg2"],
    keywords=['python', 'flask', 'postgres', 'database', 'sql', 'sequelize'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
