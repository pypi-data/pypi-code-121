from setuptools import setup, find_packages


long_description = 'Script for Trickle'

setup(
    name ='shell_trickle',
    version ='1.0.5',
    author ='Lania Kea',
    author_email ='lania.dang@visionwx.com',
    url ='',
    description ='Demo Package for Shell Trickle.',
    long_description = long_description,
    long_description_content_type ="text/markdown",
    license ='MIT',
    packages = find_packages(),
    entry_points ={
        'console_scripts': [
            'trickle = src.main:main'
        ]
    },
    classifiers =(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
    keywords ='shell trickle',
    install_requires = [
        "requests"
    ],
    zip_safe = False
)