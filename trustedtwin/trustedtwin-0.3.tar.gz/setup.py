from setuptools import setup, find_packages

setup(
    name='trustedtwin',
    version='0.3',
    url='https://gitlab.com/trustedtwinpublic/trustedtwin-python',
    long_description_content_type="text/markdown",
    license='MIT',
    author='TrustedTwin',
    author_email='api@trustedtwin.com',
    description='Python client for Trusted Twin API',
    packages=find_packages(exclude=['tests']),
    long_description=open('README.md').read(),
    zip_safe=False,
    install_requires=[
        'requests'
    ]
)
