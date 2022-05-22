from setuptools import setup

setup(
    name='projectal',
    version='2.0.1',
    description='Python bindings for the Projectal API',
    url='https://projectal.com/resources/developer',
    author='Projectal',
    author_email='support@projectal.com',
    license='MIT',
    packages=['projectal', 'projectal.entities', 'examples'],
    install_requires=['requests', 'packaging'],
    classifiers=[
        'Programming Language :: Python :: 3.9',
    ],
)
