import setuptools
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.txt").read_text()

setuptools.setup(
    author="MohammadReza Barghi",
    author_email="info@genesiscube.ir",
    name='autooptimizer',
    license="MIT",
    description='AutoOptimizer is a python package for optimize ML algorithms.',
    version='v0.7.3',
    long_description= long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/mrb987/autooptimizer',
    packages=setuptools.find_packages(),
    python_requires=">=3",
    install_requires=['sklearn',
                      'numpy',
                      'matplotlib',
                      'mlxtend',],
    keyword=['python', 'machine learning', 'sklearn', 'data science','regression metrics','outlier removal'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',],
)
