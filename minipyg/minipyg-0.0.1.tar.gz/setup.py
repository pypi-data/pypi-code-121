from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='minipyg',
    version='0.0.1',
    packages=['minipyg'],
    install_requires=[
    ],
    entry_points={
        'console_scripts': [
            'minipyg = minipyg.minipyg:entry',
        ]
    },
    description="A simple(st) python dependency manager",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
