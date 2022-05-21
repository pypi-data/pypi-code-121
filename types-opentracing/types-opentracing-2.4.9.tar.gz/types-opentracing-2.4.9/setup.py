from setuptools import setup

name = "types-opentracing"
description = "Typing stubs for opentracing"
long_description = '''
## Typing stubs for opentracing

This is a PEP 561 type stub package for the `opentracing` package.
It can be used by type-checking tools like mypy, PyCharm, pytype etc. to check code
that uses `opentracing`. The source for this package can be found at
https://github.com/python/typeshed/tree/master/stubs/opentracing. All fixes for
types and metadata should be contributed there.

See https://github.com/python/typeshed/blob/master/README.md for more details.
This package was generated from typeshed commit `8b58371278078d50c85128d74b1fc10c24029d21`.
'''.lstrip()

setup(name=name,
      version="2.4.9",
      description=description,
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://github.com/python/typeshed",
      project_urls={
          "GitHub": "https://github.com/python/typeshed",
          "Changes": "https://github.com/typeshed-internal/stub_uploader/blob/main/data/changelogs/opentracing.md",
          "Issue tracker": "https://github.com/python/typeshed/issues",
          "Chat": "https://gitter.im/python/typing",
      },
      install_requires=[],
      packages=['opentracing-stubs'],
      package_data={'opentracing-stubs': ['__init__.pyi', 'ext/__init__.pyi', 'ext/tags.pyi', 'harness/__init__.pyi', 'harness/api_check.pyi', 'harness/scope_check.pyi', 'logs.pyi', 'mocktracer/__init__.pyi', 'mocktracer/binary_propagator.pyi', 'mocktracer/context.pyi', 'mocktracer/propagator.pyi', 'mocktracer/span.pyi', 'mocktracer/text_propagator.pyi', 'mocktracer/tracer.pyi', 'propagation.pyi', 'scope.pyi', 'scope_manager.pyi', 'scope_managers/__init__.pyi', 'scope_managers/asyncio.pyi', 'scope_managers/constants.pyi', 'scope_managers/contextvars.pyi', 'scope_managers/gevent.pyi', 'scope_managers/tornado.pyi', 'span.pyi', 'tags.pyi', 'tracer.pyi', 'METADATA.toml']},
      license="Apache-2.0 license",
      classifiers=[
          "License :: OSI Approved :: Apache Software License",
          "Programming Language :: Python :: 3",
          "Typing :: Stubs Only",
      ]
)
