import setuptools
import os

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="kubetpl",
    version=os.getenv('GITHUB_REF').replace('refs/tags/', ''),
    author="Grauer W01f",
    author_email="grauerwf@gmail.com",
    description="A template tool for kubernetes resources",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/grauerwf/kubetpl",
    # package_dir={"": "src"},
    packages=setuptools.find_packages(),
    entry_points={
        'console_scripts': [
            'kubetpl=kubetpl.kubetpl:main',
        ],
    },
    install_requires=[
        'Jinja2',
        'PyYAML',
        'boto3',
        'google-cloud-secret-manager'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
