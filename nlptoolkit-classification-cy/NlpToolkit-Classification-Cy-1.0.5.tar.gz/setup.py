from setuptools import setup

from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")
from Cython.Build import cythonize

setup(
    ext_modules=cythonize(["Classification/Parameter/*.pyx",
                           "Classification/Attribute/*.pyx",
                           "Classification/FeatureSelection/*.pyx",
                           "Classification/Instance/*.pyx",
                           "Classification/DataSet/*.pyx",
                           "Classification/Performance/*.pyx",
                           "Classification/StatisticalTest/*.pyx",
                           "Classification/DistanceMetric/*.pyx",
                           "Classification/Model/*.pyx",
                           "Classification/InstanceList/*.pyx",
                           "Classification/Filter/*.pyx",
                           "Classification/Model/DecisionTree/*.pyx",
                           "Classification/Classifier/*.pyx",
                           "Classification/Experiment/*.pyx"],
                          compiler_directives={'language_level': "3"}),
    name='NlpToolkit-Classification-Cy',
    version='1.0.5',
    packages=['Classification', 'Classification.Model', 'Classification.Model.DecisionTree', 'Classification.Filter',
              'Classification.DataSet', 'Classification.Instance', 'Classification.Attribute',
              'Classification.Parameter', 'Classification.Classifier', 'Classification.Experiment',
              'Classification.Performance', 'Classification.InstanceList', 'Classification.DistanceMetric',
              'Classification.StatisticalTest', 'Classification.FeatureSelection'],
    package_data={'Classification.Model': ['*.pxd', '*.pyx', '*.c', '*.py'],
                  'Classification.Model.DecisionTree': ['*.pxd', '*.pyx', '*.c', '*.py'],
                  'Classification.Filter': ['*.pxd', '*.pyx', '*.c', '*.py'],
                  'Classification.DataSet': ['*.pxd', '*.pyx', '*.c', '*.py'],
                  'Classification.Instance': ['*.pxd', '*.pyx', '*.c', '*.py'],
                  'Classification.Attribute': ['*.pxd', '*.pyx', '*.c', '*.py'],
                  'Classification.Parameter': ['*.pxd', '*.pyx', '*.c', '*.py'],
                  'Classification.Classifier': ['*.pxd', '*.pyx', '*.c', '*.py'],
                  'Classification.Experiment': ['*.pxd', '*.pyx', '*.c', '*.py'],
                  'Classification.Performance': ['*.pxd', '*.pyx', '*.c', '*.py'],
                  'Classification.InstanceList': ['*.pxd', '*.pyx', '*.c', '*.py'],
                  'Classification.DistanceMetric': ['*.pxd', '*.pyx', '*.c', '*.py'],
                  'Classification.StatisticalTest': ['*.pxd', '*.pyx', '*.c', '*.py'],
                  'Classification.FeatureSelection': ['*.pxd', '*.pyx', '*.c', '*.py']},
    url='https://github.com/StarlangSoftware/Classification-Cy',
    license='',
    author='olcaytaner',
    author_email='olcay.yildiz@ozyegin.edu.tr',
    description='Classification library',
    install_requires=['NlpToolkit-Math-Cy', 'NlpToolkit-DataStructure-Cy', 'NlpToolkit-Sampling-Cy'],
    long_description=long_description,
    long_description_content_type='text/markdown'
)
