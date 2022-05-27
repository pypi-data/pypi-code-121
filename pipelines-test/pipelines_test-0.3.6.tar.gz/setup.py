from setuptools import setup

setup(
    name='pipelines_test',
    version='0.3.6',
    description='Test Pipelines',
    author='Julia Patacz',
    author_email='julia.patacz@skillcorner.com',
    packages=['pipelines'],
    python_requires='>=3.6',
    install_requires=[
        'Sphinx>=4.0.0',
        'sphinx-rtd-theme==1.0.0',
    ],
)