from setuptools import setup

name = "types-emoji"
description = "Typing stubs for emoji"
long_description = '''
## Typing stubs for emoji

This is a PEP 561 type stub package for the `emoji` package.
It can be used by type-checking tools like mypy, PyCharm, pytype etc. to check code
that uses `emoji`. The source for this package can be found at
https://github.com/python/typeshed/tree/master/stubs/emoji. All fixes for
types and metadata should be contributed there.

See https://github.com/python/typeshed/blob/master/README.md for more details.
This package was generated from typeshed commit `6e18441a2c1e5836eca4e6763a9590d2b9270378`.
'''.lstrip()

setup(name=name,
      version="1.7.0",
      description=description,
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://github.com/python/typeshed",
      project_urls={
          "GitHub": "https://github.com/python/typeshed",
          "Changes": "https://github.com/typeshed-internal/stub_uploader/blob/main/data/changelogs/emoji.md",
          "Issue tracker": "https://github.com/python/typeshed/issues",
          "Chat": "https://gitter.im/python/typing",
      },
      install_requires=[],
      packages=['emoji-stubs'],
      package_data={'emoji-stubs': ['__init__.pyi', 'core.pyi', 'unicode_codes/__init__.pyi', 'METADATA.toml']},
      license="Apache-2.0 license",
      classifiers=[
          "License :: OSI Approved :: Apache Software License",
          "Programming Language :: Python :: 3",
          "Typing :: Stubs Only",
      ]
)
