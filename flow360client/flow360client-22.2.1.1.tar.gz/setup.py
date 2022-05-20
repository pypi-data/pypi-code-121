from setuptools import setup
 
version = {}
with open("flow360client/version.py") as fp:
    exec(fp.read(), version)

setup(
    name='flow360client',
    version=version['__version__'],
    description='A Python API for Flow360 CFD solver',
    author='FlexCompute, Inc.',
    author_email='john@simulation.cloud',
    packages=['flow360client', 'flow360client.generator'],
    install_requires=['requests>=2.13.0', 'aws-requests-auth', 'bcrypt', 'boto3', 'numpy'],
    dependency_links=['http://github.com/flexcompute/warrant/tarball/master#egg=warrant-0.6.4'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.5'
)
