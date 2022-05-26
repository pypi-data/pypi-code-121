from setuptools import setup, find_packages
import pathlib


here = pathlib.Path(__file__).parent.resolve()

long_description = (here / 'README.md').read_text(encoding='utf-8')

setup(
    name='flask-sample-test',  # Required
    version='0.0.5',  # Required
    description='A sample test for project',  # Optional
    long_description=long_description,  # Optional
    long_description_content_type='text/markdown',  # Optional (see note above)
    url='https://github.com/December1208/flask_sample_test',  # Optional
    author='JiaLe.tan',  # Optional
    author_email='jiale.gfi@outlook.com',  # Optional
    keywords='flask, test, sqlalchemy',  # Optional
    packages=find_packages(),  # Required
    install_requires=['flask_sqlalchemy >= 2.0'],  # Optional
    python_requires='>=3.7',
    classifiers=[
      "Programming Language :: Python :: 3",
      "License :: OSI Approved :: MIT License",
      "Operating System :: OS Independent",
    ],
    include_package_data=True,
)

