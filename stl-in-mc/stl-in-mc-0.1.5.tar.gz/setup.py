import os
from setuptools import setup

with open("README.md", "r", encoding="utf-8") as f:
    LONG_DESCRIPTION = f.read()

# get github workflow env vars
try:
    version = (os.environ['GIT_TAG_NAME']).replace('v', '')
except KeyError:
    print('Defaulting to 0.0.0')
    version = '0.0.0'

setup(
    name='stl-in-mc',
    version=version,
    description='Import STL into Minecraft',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    license='MIT',
    keywords='stl python minecraft',
    author='Martin Miglio',
    url='https://github.com/marmig0404/stl-in-mc',
    download_url='https://github.com/marmig0404/stl-in-mc/releases',
    install_requires=['numpy', 'numpy-stl',
                      'validators', 'mcpi', 'stl-to-voxel', 'joblib'],
    packages=['stlinmc'],
    python_requires='>=3',
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'stlinmc = stlinmc.__main__:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
)
