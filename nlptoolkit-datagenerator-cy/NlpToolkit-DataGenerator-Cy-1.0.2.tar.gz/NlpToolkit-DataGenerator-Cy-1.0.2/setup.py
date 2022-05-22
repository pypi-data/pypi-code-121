from setuptools import setup

from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")
from Cython.Build import cythonize

setup(
    ext_modules=cythonize(["DataGenerator/Attribute/*.pyx",
                           "DataGenerator/CorpusGenerator/*.pyx",
                           "DataGenerator/InstanceGenerator/*.pyx",
                           "DataGenerator/DatasetGenerator/*.pyx"],
                          compiler_directives={'language_level': "3"}),
    name='NlpToolkit-DataGenerator-Cy',
    version='1.0.2',
    packages=['DataGenerator', 'DataGenerator.Attribute', 'DataGenerator.CorpusGenerator',
              'DataGenerator.DatasetGenerator', 'DataGenerator.InstanceGenerator'],
    package_data={'DataGenerator.Attribute': ['*.pxd', '*.pyx', '*.c'],
                  'DataGenerator.CorpusGenerator': ['*.pxd', '*.pyx', '*.c'],
                  'DataGenerator.DatasetGenerator': ['*.pxd', '*.pyx', '*.c'],
                  'DataGenerator.InstanceGenerator': ['*.pxd', '*.pyx', '*.c']},
    url='https://github.com/StarlangSoftware/DataGenerator-Cy',
    license='',
    author='olcaytaner',
    author_email='olcay.yildiz@ozyegin.edu.tr',
    description='Classification dataset generator library for high level Nlp tasks',
    install_requires=['NlpToolkit-AnnotatedTree-Cy', 'NlpToolkit-Classification-Cy', 'NlpToolkit-MorphologicalDisambiguation-Cy'],
    long_description=long_description,
    long_description_content_type='text/markdown'
)
