import pathlib
from dataclasses import dataclass
from distutils.core import setup

HERE = pathlib.Path(__file__).parent

VERSION = (HERE / "VERSION.txt").read_text()

setup(name='faux-data',
      version=VERSION,
      description='Generate fake data from yaml templates',
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
