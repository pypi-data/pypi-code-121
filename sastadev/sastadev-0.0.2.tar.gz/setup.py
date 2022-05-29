from setuptools import setup, find_packages

setup(
    name='sastadev',
    python_requires='>=3.5, <4',
    version='0.0.2',
    description='Linguistic functions for SASTA tool',
    author='Digital Humanities Lab, Utrecht University',
    author_email='digitalhumanities@uu.nl',
    url='https://github.com/UUDigitalHumanitieslab/sastadev',
    license='BSD-3-Clause',
    include_package_data=True,
    packages=['sastadev'],
    package_data={'sastadev': ['*.txt', 'LICENSE', 'py.typed']}
)
