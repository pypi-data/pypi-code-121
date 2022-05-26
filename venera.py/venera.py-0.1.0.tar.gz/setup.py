import setuptools

__version__ = str('0.1.0')

requirements = []
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

packages = [
    'venera'
]


setuptools.setup(
    name='venera.py',
    version=__version__,
    packages=packages,
    url='https://github.com/veneralab/venera.py',
    license='MIT',
    author='Venera',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    install_requires=requirements,
    description='Asynchronous Venera API Wrapper',
    python_requires='>=3.9',
)
