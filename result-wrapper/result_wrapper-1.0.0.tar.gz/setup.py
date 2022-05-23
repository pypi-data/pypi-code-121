#!/usr/bin/env python

from setuptools import setup
import pathlib


here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(name='result_wrapper',
      version='1.0.0',
      description='Result Wrapper',
      long_description=long_description,
      long_description_content_type='text/markdown',
      author='Tibotix',
      author_email='tizian@seehaus.net',
      url='https://github.com/tibotix/result_wrapper',
      package_dir={"result_wrapper": "src"},
      packages=["result_wrapper"],
      keywords=["exception", "result", "wrapper"],
      extras_require={
        "test": ["pytest"]
      },
      python_requires=">=3.6, <4",
      )
