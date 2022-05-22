from setuptools import setup

from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")
from Cython.Build import cythonize

setup(
    ext_modules=cythonize(["NER/AutoProcessor/ParseTree/*.pyx",
                           "NER/AutoProcessor/Sentence/*.pyx"],
                          compiler_directives={'language_level': "3"}),
    name='NlpToolkit-NER-Cy',
    version='1.0.4',
    packages=['NER', 'NER.AutoProcessor', 'NER.AutoProcessor.Sentence', 'NER.AutoProcessor.ParseTree'],
    package_data={'NER.AutoProcessor.ParseTree': ['*.pxd', '*.pyx', '*.c', '*.py'],
                  'NER.AutoProcessor.Sentence': ['*.pxd', '*.pyx', '*.c', '*.py']},
    url='https://github.com/StarlangSoftware/NER-Cy',
    license='',
    author='olcaytaner',
    author_email='olcay.yildiz@ozyegin.edu.tr',
    description='NER library',
    install_requires = ['NlpToolkit-AnnotatedTree-Cy'],
    long_description=long_description,
    long_description_content_type='text/markdown'
)
