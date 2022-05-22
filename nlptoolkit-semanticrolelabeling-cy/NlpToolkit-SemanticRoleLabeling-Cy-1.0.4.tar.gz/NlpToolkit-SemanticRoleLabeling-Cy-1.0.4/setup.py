from setuptools import setup

from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")
from Cython.Build import cythonize

setup(
    ext_modules=cythonize(["SemanticRoleLabeling/AutoProcessor/ParseTree/Propbank/*.pyx",
                           "SemanticRoleLabeling/AutoProcessor/Sentence/Propbank/*.pyx",
                           "SemanticRoleLabeling/AutoProcessor/Sentence/FrameNet/*.pyx"],
                          compiler_directives={'language_level': "3"}),
    name='NlpToolkit-SemanticRoleLabeling-Cy',
    version='1.0.4',
    packages=['SemanticRoleLabeling', 'SemanticRoleLabeling.AutoProcessor',
              'SemanticRoleLabeling.AutoProcessor.Sentence', 'SemanticRoleLabeling.AutoProcessor.Sentence.FrameNet',
              'SemanticRoleLabeling.AutoProcessor.Sentence.Propbank', 'SemanticRoleLabeling.AutoProcessor.ParseTree',
              'SemanticRoleLabeling.AutoProcessor.ParseTree.Propbank'],
    package_data={'SemanticRoleLabeling.AutoProcessor.ParseTree.Propbank': ['*.pxd', '*.pyx', '*.c', '*.py'],
                  'SemanticRoleLabeling.AutoProcessor.Sentence.FrameNet': ['*.pxd', '*.pyx', '*.c', '*.py'],
                  'SemanticRoleLabeling.AutoProcessor.Sentence.Propbank': ['*.pxd', '*.pyx', '*.c', '*.py']},
    url='https://github.com/StarlangSoftware/SemanticRoleLabeling-Cy',
    license='',
    author='olcaytaner',
    author_email='olcay.yildiz@ozyegin.edu.tr',
    description='Semantic Role Labeling Library',
    install_requires = ['NlpToolkit-AnnotatedTree-Cy'],
    long_description=long_description,
    long_description_content_type='text/markdown'
)
