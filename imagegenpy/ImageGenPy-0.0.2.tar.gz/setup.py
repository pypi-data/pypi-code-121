import setuptools

# Reads the content of your README.md into a variable to be used in the setup below
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name='ImageGenPy',                           # should match the package folder
    packages=['ImageGenPy'],                     # should match the package folder
    version='0.0.2',                                # important for updates
    license='MIT',                                  # should match your chosen license
    description='Shitty python package for randomly generating images',
    long_description=long_description,              # loads your README.md
    long_description_content_type="text/markdown",  # README.md is of type 'markdown'
    author='Vladimir Poopin',
    author_email='real_vladdy_putin@pm.me',
    url='https://github.com/jclmnop/ImageGenPy', 
    project_urls = {                                # Optional
        "Bug Tracker": "https://github.com/jclmnop/ImageGenPy/issues"
    },
    install_requires=['Pillow'],                  # list all packages that your package uses
    keywords=[], #descriptive meta-data
    classifiers=[                                   # https://pypi.org/classifiers
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Documentation',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
    ],
    
    download_url="https://github.com/jclmnop/ImageGenPy/archive/refs/tags/v0.0.2.tar.gz",
)