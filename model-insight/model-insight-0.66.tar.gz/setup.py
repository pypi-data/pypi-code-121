from setuptools import setup, find_packages

with open('README.md') as f:
    LONG_DESCRIPTION = f.read()

setup(
    name='model-insight',
    version='0.66',
    license='MIT',
    author="Wang Haihua",
    author_email='reformship@gmail.com',
    description='A package for learning and teaching mathematical modeling',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    url= "https://reformship.github.io/pages(en)/134modelinsight.html",
    project_urls={
    "Documentation(Chinese)": "https://reformship.github.io/pages/134modelinsight.html",
    "Code": "https://github.com/reformship/model-insight",
    "Issue tracker": "https://github.com/reformship/model-insight/issues",},
    keywords='mathematical modeling',
    install_requires=[
          'numpy','pandas','matplotlib','seaborn','scipy','pulp'
      ],
    include_package_data=False,
    #package_data={'': ['src/model_insight/datasets/*.csv','src/model_insight/datasets/*.xls','src/model_insight/datasets/*.xlsx']},

)
