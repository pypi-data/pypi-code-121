from setuptools import setup

from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")
from Cython.Build import cythonize

setup(
    ext_modules=cythonize(["PosTagger/*.pyx"],
                          compiler_directives={'language_level': "3"}),
    name='NlpToolkit-PosTagger-Cy',
    version='1.0.2',
    packages=['PosTagger'],
    package_data={'PosTagger': ['*.pxd', '*.pyx', '*.c']},
    url='https://github.com/StarlangSoftware/PosTagger-Cy',
    license='',
    author='olcaytaner',
    author_email='olcay.yildiz@ozyegin.edu.tr',
    description='English PosTagger Library',
    install_requires=['NlpToolkit-Corpus-Cy', 'NlpToolkit-Hmm-Cy'],
    long_description=long_description,
    long_description_content_type='text/markdown'
)
