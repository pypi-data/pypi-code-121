from setuptools import setup

setup(
    name='projectal',
    version='2.0.2',
    description='Python bindings for the Projectal API',
    long_description="The Python library allows developers to write Python-based apps that talk directly with Projectal. This gives developers immense freedom to access all data points in Projectal and to integrate Projectal with their workflow.",
    long_description_content_type="text/plain",
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
