from ctypes.wintypes import LONG
import pathlib
from setuptools import setup

HERE = pathlib.Path(__file__).parent

VERSION = (HERE / "VERSION.txt").read_text()

LONG_DESCRIPTION = """\
# Faux Data

Faux Data is a library for generating data using configuration files.

See the project on github for more info - https://github.com/jack-tee/faux-data

"""

setup(name='faux-data',
      version=VERSION,
      description='Generate fake data from yaml templates',
      long_description=LONG_DESCRIPTION,
      long_description_content_type='text/markdown',
      author='jack-tee',
      author_email='10283360+jack-tee@users.noreply.github.com',
      packages=['faux_data'],
      install_requires=[
          "pandas==1.4.2",
          "google-cloud-bigquery",
          "google-cloud-pubsub",
          "pyarrow",
          "pyyaml",
          "jinja2",
          "tabulate",
          "fsspec",
          "gcsfs",
      ],
      entry_points={'console_scripts': ['faux=faux_data.cmd:main']})
