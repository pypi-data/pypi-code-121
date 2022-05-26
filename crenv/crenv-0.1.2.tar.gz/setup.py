from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

VERSION = '0.1.2'
DESCRIPTION = 'RL Environment for Cryptocurrency Research'
LONG_DESCRIPTION = long_description

# Setting up
setup(
    name='crenv',
    version=VERSION,
    author='Crinstaniev',
    author_email='zhuangzesen@gmail.com',
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=['plotly', 'numpy', 'pandas', 'scipy', 'tqdm', 'matplotlib', 'gym'],
    license='MIT',
    keywords=['RL', 'Machine Learning'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "Programming Language :: Python :: 3",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)