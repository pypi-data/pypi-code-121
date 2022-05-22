from setuptools import setup, find_packages

VERSION = '1.1.0'

with open("README.md") as f:
    long_description = f.read()

setup(
    name='generate_elan',
    version=VERSION,
    description='Automatic ELAN generation package.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Md. Shahad Mahmud Chowdhury',
    author_email='shahad9381@gmail.com',
    packages=find_packages(),
    url='',
    keywords=['STT', 'ASR', 'TTS', 'ELAN', 'annotation'],
    python_requires='>=3.6',
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    install_requires=["pympi-ling", "tqdm"]
) 