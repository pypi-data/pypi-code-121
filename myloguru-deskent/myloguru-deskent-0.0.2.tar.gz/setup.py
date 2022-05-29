from setuptools import setup, find_packages

setup(
    name='myloguru-deskent',
    version='0.0.2',
    author='Deskent',
    author_email='battenetciz@gmail.com',
    description='My loguru config',
    install_requires=[
        'loguru==0.5.3',
        'pytest==7.1.2 ',
    ],
    scripts=['src/myloguru/my_loguru.py'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    url="https://github.com/Deskent/my_loguru",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.8",
)
