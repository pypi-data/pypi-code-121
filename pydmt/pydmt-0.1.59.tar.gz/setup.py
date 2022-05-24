import setuptools


def get_readme():
    with open('README.rst') as f:
        return f.read()


setuptools.setup(
    # the first three fields are a must according to the documentation
    name="pydmt",
    version="0.1.59",
    packages=[
        'pydmt',
        'pydmt.api',
        'pydmt.builders',
        'pydmt.core',
        'pydmt.features',
        'pydmt.helpers',
        'pydmt.utils',
    ],
    # from here all is optional
    description="python dependency management tool",
    long_description=get_readme(),
    long_description_content_type="text/x-rst",
    author="Mark Veltzer",
    author_email="mark.veltzer@gmail.com",
    maintainer="Mark Veltzer",
    maintainer_email="mark.veltzer@gmail.com",
    keywords=[
        'pydmt',
        'cons',
        'scons',
        'software construction',
        'make',
        'cmake',
        'maven',
        'mvn',
    ],
    url="https://veltzer.github.io/pydmt",
    download_url="https://github.com/veltzer/pydmt",
    license="MIT",
    platforms=[
        'python3',
    ],
    install_requires=[
        'pyfakeuse',
        'pylogconf',
        'pytconf',
        'mako',
        'Sphinx',
        'pyyaml',
        'jsonschema',
        'venv-run',
        'gitpython',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License',
    ],
    entry_points={"console_scripts": [
        'pydmt=pydmt.main:main',
    ]},
)
