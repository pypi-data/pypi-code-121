import setuptools

setuptools.setup(
    name="convenient-datascience-tools",
    version="0.0.2",
    author="Guilherme Turtera",
    long_description="Useful tools for handling data, using many known data science packages.",
    long_description_content_type='text/markdown',
    description="DataScience Tools",
    packages=["tools"],
    python_requires = ">=3.9.12",
    install_requires=["pandas"],
    package_dir={'tools': 'src/tools'},
)