from setuptools import setup

name = "types-waitress"
description = "Typing stubs for waitress"
long_description = '''
## Typing stubs for waitress

This is a PEP 561 type stub package for the `waitress` package.
It can be used by type-checking tools like mypy, PyCharm, pytype etc. to check code
that uses `waitress`. The source for this package can be found at
https://github.com/python/typeshed/tree/master/stubs/waitress. All fixes for
types and metadata should be contributed there.

See https://github.com/python/typeshed/blob/master/README.md for more details.
This package was generated from typeshed commit `466f9c2ad7bb65702b268081bcc753778f43f6a0`.
'''.lstrip()

setup(name=name,
      version="2.0.9",
      description=description,
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://github.com/python/typeshed",
      project_urls={
          "GitHub": "https://github.com/python/typeshed",
          "Changes": "https://github.com/typeshed-internal/stub_uploader/blob/main/data/changelogs/waitress.md",
          "Issue tracker": "https://github.com/python/typeshed/issues",
          "Chat": "https://gitter.im/python/typing",
      },
      install_requires=[],
      packages=['waitress-stubs'],
      package_data={'waitress-stubs': ['__init__.pyi', 'adjustments.pyi', 'buffers.pyi', 'channel.pyi', 'compat.pyi', 'parser.pyi', 'proxy_headers.pyi', 'receiver.pyi', 'rfc7230.pyi', 'runner.pyi', 'server.pyi', 'task.pyi', 'trigger.pyi', 'utilities.pyi', 'wasyncore.pyi', 'METADATA.toml']},
      license="Apache-2.0 license",
      classifiers=[
          "License :: OSI Approved :: Apache Software License",
          "Programming Language :: Python :: 3",
          "Typing :: Stubs Only",
      ]
)
