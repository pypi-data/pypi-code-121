import setuptools

# Reads the content of your README.md into a variable to be used in the setup below
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name='v3wrapper',  # should match the package folder
    packages=['v3wrapper'],  # should match the package folder
    version='v0.0.8',  # important for updates
    license='GNU2L',  # should match your chosen license
    description='wrapper for easy download of data from Metrikus v3 API',
    long_description=long_description,  # loads your README.md
    long_description_content_type="text/markdown",  # README.md is of type 'markdown'
    author='JQ',
    author_email='juan.f.quintas@gmail.com',
    url='https://github.com/lupit0/Metrikus',
    install_requires=['requests','pandas','pytz','holidays'],  # list all packages that your package uses
    keywords=["metrikus"],  # descriptive meta-data
    classifiers=[  # https://pypi.org/classifiers
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Documentation',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ]
)