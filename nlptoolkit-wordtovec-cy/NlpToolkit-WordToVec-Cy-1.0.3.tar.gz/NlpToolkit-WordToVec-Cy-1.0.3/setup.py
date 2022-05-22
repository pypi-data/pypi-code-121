from setuptools import setup

from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")
from Cython.Build import cythonize

setup(
    ext_modules=cythonize(["WordToVec/*.pyx"],
                          compiler_directives={'language_level': "3"}),
    name='NlpToolkit-WordToVec-Cy',
    version='1.0.3',
    packages=['WordToVec'],
    package_data={'WordToVec': ['*.pxd', '*.pyx', '*.c']},
    url='https://github.com/StarlangSoftware/WordToVec-Cy',
    license='',
    author='olcay',
    author_email='olcay.yildiz@ozyegin.edu.tr',
    description='Word2Vec Library',
    install_requires=['NlpToolkit-Corpus-Cy'],
    long_description=long_description,
    long_description_content_type='text/markdown'
)
