from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

with open('requirements/requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name="arm64_tester",
    version="1.2.3",
    author="Luis Tavares",
    python_requires='>=3.6',
    long_description_content_type='text/markdown',
    long_description=long_description,
    install_requires=required,
    packages=find_packages(exclude=['test']),
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
)
