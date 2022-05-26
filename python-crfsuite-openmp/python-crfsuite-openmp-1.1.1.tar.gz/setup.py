#!/usr/bin/env python
import glob
import sys
from setuptools import setup, Extension
from distutils.command.build_ext import build_ext

sources = ['pycrfsuite/_pycrfsuite.cpp', 'pycrfsuite/trainer_wrapper.cpp']

# crfsuite
sources += glob.glob('crfsuite/lib/crf/src/*.c')
sources += glob.glob('crfsuite/swig/*.cpp')

sources += ['crfsuite/lib/cqdb/src/cqdb.c']
sources += ['crfsuite/lib/cqdb/src/lookup3.c']


includes = [
    'crfsuite/include/',
    'crfsuite/lib/cqdb/include',
    'pycrfsuite',
]

class build_ext_check_gcc(build_ext):
    def build_extensions(self):
        c = self.compiler
        print(self.compiler.compiler_type)
        if self.compiler.compiler_type == "unix":
            for e in self.extensions:
                e.extra_compile_args=['-std=c99', '-fopenmp', '-DUSE_SSE', '-DWITH_SSE2', '-DHAVE_EMMINTRIN_H', '-mms-bitfields', '-fno-strict-aliasing', '-march=westmere', '-msse2']
                # e.extra_link_args.append('-fopenmp')
        elif self.compiler.compiler_type == "msvc":
            for e in self.extensions:
                e.extra_compile_args=['/D', '"USE_SSE"']
                
        build_ext.build_extensions(self)


ext_modules = [Extension('pycrfsuite._pycrfsuite',
    include_dirs=includes,
    language='c++',
    sources=sources
)]


setup(
    name='python-crfsuite-openmp',
    version="1.1.1",
    description="Python binding for CRFsuite wih OpenMP build",
    long_description=open('README.rst').read(),
    author="Bruno Cabral, Terry Peng, Mikhail Korobov",
    author_email="bruno@potelo.com.br, pengtaoo@gmail.com, kmike84@gmail.com",
    license="MIT",
    url='https://github.com/bratao/python-crfsuite',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Cython",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Text Processing :: Linguistic",
    ],
    zip_safe=False,
    packages=['pycrfsuite'],
    ext_modules=ext_modules,
    cmdclass={'build_ext': build_ext_check_gcc}
)

