from setuptools import setup, find_namespace_packages


def _read(f) -> bytes:
    """
    Reads in the content of the file.
    :param f: the file to read
    :type f: str
    :return: the content
    :rtype: str
    """
    return open(f, 'rb').read()


setup(
    name="wai.common",
    description="Python library with common functionality for other Waikato projects.",
    long_description=(
        _read('DESCRIPTION.rst') + b'\n' +
        _read('CHANGES.rst')).decode('utf-8'),
    url="https://github.com/waikato-datamining/wai-common",
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Programming Language :: Python :: 3',
    ],
    license='MIT',
    package_dir={
        '': 'src'
    },
    packages=find_namespace_packages(where="src"),
    namespace_packages=[
        "wai"
    ],
    version="0.0.38",
    author='Corey Sterling',
    author_email='coreytsterling@gmail.com',
    install_requires=[
        "typing-inspect",
        "javaproperties"
    ],
    include_package_data=True
)
