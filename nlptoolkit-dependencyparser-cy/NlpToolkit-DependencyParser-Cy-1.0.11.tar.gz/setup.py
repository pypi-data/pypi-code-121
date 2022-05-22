from setuptools import setup

from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")
from Cython.Build import cythonize

setup(
    ext_modules=cythonize(["DependencyParser/*.pyx", "DependencyParser/Stanford/*.pyx",
                           "DependencyParser/Turkish/*.pyx", "DependencyParser/Universal/*.pyx"],
                          compiler_directives={'language_level': "3"}),
    name='NlpToolkit-DependencyParser-Cy',
    version='1.0.11',
    packages=['DependencyParser', 'DependencyParser.Turkish', 'DependencyParser.Universal', 'DependencyParser.Stanford'],
    package_data={'DependencyParser': ['*.pxd', '*.pyx', '*.c', '*.py'],
                  'DependencyParser.Turkish': ['*.pxd', '*.pyx', '*.c', '*.py'],
                  'DependencyParser.Universal': ['*.pxd', '*.pyx', '*.c', '*.py'],
                  'DependencyParser.Stanford': ['*.pxd', '*.pyx', '*.c', '*.py']},
    url='https://github.com/StarlangSoftware/TurkishDependencyParser-Cy',
    license='',
    author='olcaytaner',
    author_email='olcay.yildiz@ozyegin.edu.tr',
    description='Turkish Dependency Parser',
    install_requires=['NlpToolkit-MorphologicalAnalysis-Cy'],
    long_description=long_description,
    long_description_content_type='text/markdown'
)
