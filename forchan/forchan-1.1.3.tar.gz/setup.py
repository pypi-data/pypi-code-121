from setuptools import setup, find_packages

with open('README.md') as readme:
    long_description = readme.read()

REQUIREMENTS = ['argparse']

CLASSIFIERS = [
    "Development Status :: 4 - Beta",
    "Environment :: Console",
    "Intended Audience :: Other Audience",
    "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
    "Natural Language :: English",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3.10",
    "Topic :: Games/Entertainment :: Fortune Cookies"
]

setup(  name="forchan",
        version="1.1.3",
        description="Check your fortune as is tradition on [s4s].",
        long_description_content_type="text/markdown",
        long_description=long_description,
        url="https://github.com/ganelonhb/forchan",
        author="ganelon",
        license="GPLv3+",
        packages=find_packages(),
        entry_points = {
            'console_scripts' : [
                'forchan = esfores.forchan:main'
            ]
        },
        classifiers=CLASSIFIERS,
        install_requires=REQUIREMENTS,
        keywords="fortune forchan fourchan 4chan s4s esfores kek jej zozzle"
)
