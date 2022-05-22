from setuptools import setup

from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")
from Cython.Build import cythonize

setup(
    ext_modules=cythonize(["ParseTree/*.pyx", "ParseTree/NodeCondition/*.pyx"],
                          compiler_directives={'language_level': "3"}),
    name='NlpToolkit-ParseTree-Cy',
    version='1.0.8',
    packages=['ParseTree', 'ParseTree.NodeCondition'],
    package_data={'ParseTree': ['*.pxd', '*.pyx', '*.c', '*.py'],
                  'ParseTree.NodeCondition': ['*.pxd', '*.pyx', '*.c', '*.py']},
    url='https://github.com/StarlangSoftware/ParseTree-Cy',
    license='',
    author='olcaytaner',
    author_email='olcay.yildiz@ozyegin.edu.tr',
    description='Constituency Parse Tree Library',
    install_requires = ['NlpToolkit-Dictionary-Cy'],
    long_description=long_description,
    long_description_content_type='text/markdown'
)
