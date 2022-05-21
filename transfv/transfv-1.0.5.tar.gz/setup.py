import pathlib
from setuptools import setup, find_packages

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(

    name='transfv',
    version='1.0.5',
    description='Google translator for a terminal.',
    long_description=README,
    long_description_content_type="text/markdown",

    url='https://github.com/filipvrba/trans.git', 
    author='Filip Vrba',
    author_email='filipvrba@pm.me',
    license="MIT",
    classifiers=[
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Education',
    'Operating System :: OS Independent',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    ],
    keywords=['python', 'google', 'translator', 'fv', 'transfv'],

    packages=find_packages(),
    install_requires=["googletrans==4.0.0-rc1"],

    entry_points={
        "console_scripts": [
            "trans=transfv.__init__:main",
        ]
    },
)
