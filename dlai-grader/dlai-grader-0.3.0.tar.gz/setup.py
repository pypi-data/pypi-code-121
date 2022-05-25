from setuptools import setup, find_packages

setup(
    name='dlai-grader',
    version='0.3.0',    
    description='Grading utilities for DLAI courses',
    url='https://github.com/https-deeplearning-ai/grader',
    author='Andres Zarta',
    author_email='andrezb5@gmail.com',
    license='MIT License',
    packages=find_packages(),
    entry_points={"console_scripts": ["dlai_grader = dlai_grader.cli:parse_dlai_grader_args"]},
    install_requires=['nbformat>=5.1.3',
                      'jupytext>=1.13.0',                     
                      ],

    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)