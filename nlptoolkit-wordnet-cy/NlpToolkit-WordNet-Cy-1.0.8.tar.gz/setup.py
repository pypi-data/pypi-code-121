from setuptools import setup

from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")
from Cython.Build import cythonize

setup(
    ext_modules=cythonize(["WordNet/*.pyx", "WordNet/Similarity/*.pyx"],
                          compiler_directives={'language_level': "3"}),
    name='NlpToolkit-WordNet-Cy',
    version='1.0.8',
    packages=['WordNet', 'WordNet.Similarity', 'WordNet.data'],
    package_data={'WordNet': ['*.pxd', '*.pyx', '*.c', '*.py'],
                  'WordNet.Similarity': ['*.pxd', '*.pyx', '*.c'],
                  'WordNet.data': ['*.xml']},
    url='https://github.com/StarlangSoftware/TurkishWordNet-Cy',
    license='',
    author='olcay',
    author_email='olcay.yildiz@ozyegin.edu.tr',
    description='Turkish WordNet KeNet',
    install_requires=['NlpToolkit-MorphologicalAnalysis-Cy'],
    long_description=long_description,
    long_description_content_type='text/markdown'
)
