from setuptools import find_packages, setup

# read the contents of your README file
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()
c_dict = {}
with open(this_directory / "tiyaro/version.py") as ver_file:
    exec(ver_file.read(), c_dict)

# https://packaging.python.org/en/latest/guides/making-a-pypi-friendly-readme/
setup(
    name='tiyaro',
    version=c_dict['__version__'],
    description='Tiyaro Python Package Index',
    long_description=long_description,
    long_description_content_type='text/markdown',

    author='Venkat Raman, I-Jong Lin',
    author_email='venkat@tiyaro.ai, ijonglin@tiyaro.ai',

    url='https://github.com/pypa/sampleproject',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent'],
    license='Apache License 2.0',
    license_files=('LICENSE',),
    platforms='any',

    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click==8.0.4',
        'requests',
        'PyYAML',
        'marshmallow',
        'validators'
    ],
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'tiyaro = tiyaro.main:cli',
        ],
    },
)
