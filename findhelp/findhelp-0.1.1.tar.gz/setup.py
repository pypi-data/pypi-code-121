from setuptools import setup


# Load the README file.
with open(file="README.md", mode="r") as readme_handle:
    long_description = readme_handle.read()

setup(
    name='findhelp',
    py_modules=["findhelp"],
    package_dir={"findhelp": "src/findhelp"},
    packages=["findhelp"],
    #package_dir={"": "src"},
    package_data={"src": ["config.yaml"]},
    include_package_data=True,
    author='Miguel Ángel Rendón García',
    author_email='miguerendongarcia@gmail.com',
    #   - MAJOR VERSION 0
    #   - MINOR VERSION 1
    #   - MAINTENANCE VERSION 0
    version='0.1.1',
    description='Helps finding files / directories using custom parameters',

    long_description=long_description,
    long_description_content_type="text/markdown",

    url='https://github.com/rendongarcia/findhelp',

    install_requires=[
        'PyYaml',
        'pandas>=1.0.0',
        'Unidecode>=1.0.22',
    ],

    # Here are the keywords of my library.
    keywords='find, search, file, folder',

    python_requires='>=3.7',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Education',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Topic :: Education',
    ]
)
