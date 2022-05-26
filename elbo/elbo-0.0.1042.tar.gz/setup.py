import os

import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open('requirements.txt') as f:
    requirements = f.readlines()

version = os.popen('git --git-dir ~/projects/elbo-client/.git log | wc -l').read().strip()
__version__ = f"0.0.{version}"

print(f"Using version {version}")
setuptools.setup(
    name='elbo',
    description='ELBO.AI CLI and API - https://elbo.ai',
    long_description=long_description,
    long_description_content_type="text/markdown",
    version=f"0.0.{version}",
    url='https://elbo.ai',
    project_urls={
        "Bug Tracker": "https://github.com/elbo-ai/elbo-client/issues"
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': [
            'elbo = elbo.main:cli'
        ]
    },
    packages=setuptools.find_packages(),
    python_requires=">=3.6",
    author='ELBO AI, Inc.',
    author_email='hi@elbo.ai',
    install_requires=requirements,
    keywords=['pip', 'elbo', 'training']
)
