"""Setup module for Robot Framework Docker Library package."""

from setuptools import setup

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Testing',
    'License :: OSI Approved :: Apache Software License',
    'Programming Language :: Python :: 3.8',
    'Framework :: Robot Framework :: Library',
]

setup(
    name='robotframework-dockerlibrary',
    version='1.0.0',
    description='A Robot Framework Docker Library',
    long_description=open('README_EN.md').read(),
    long_description_content_type="text/markdown",
    url='',
    author='Oliver Uhlar',
    author_email='oliverkolombo@gmail.com',
    license='Apache License 2.0',
    classifiers=classifiers,
    keywords='testing testautomation robotframework docker dind containerization',
    package_dir={'': 'src'},
    py_modules=['DockerLibrary', 'Utils'],
    data_files=[('images/centos',['src/images/centos/Dockerfile']),
                ('images/ubuntu',['src/images/ubuntu/Dockerfile']),
                ('images/alpine',['src/images/alpine/Dockerfile'])],
    install_requires=[
        'robotframework==4.1.2',
        'packaging',
    ],
)
