from setuptools import setup, find_packages, Extension

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='softpotato',
    version="1.0.12",
    license='GPL3',
    author='Oliver Rodriguez',
    author_email='oliver.rdz@softpotato.xyz',
    description='Open source electrochemistry toolkit',
    #long_description=long_description,
    #long_description_content_type='text/markdown',
    packages=find_packages('src'),
    package_dir={'':'src'},
    url='https://softpotato.xyz',
    keywords='Electrochemistry',
    python_requires=">=3.6",
    install_requires=[
        'numpy',
        'matplotlib',
        'scipy',
    ],
)
