# coding: utf-8
"""Setup script for IVA TPU."""
# import os
from setuptools import setup

with open('README.md', 'r') as fh:
    long_description = fh.read()

# with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, 'VERSION'), 'r') as f:
#     VERSION = f.readline()
#     print(f'Install version: {VERSION}')

setup(
    name='pytpu',
    packages=['pytpu', 'pytpu.tools', 'pytpu.pytpu', 'pytpu.scripts'],
    # packages=find_packages(),
    # version=VERSION,
    version="14.2.1",
    author="Alexey Antipin",
    author_email="a.antipin@iva-tech.ru",
    description="TPU Python API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="http://git.mmp.iva-tech.ru/tpu_sw/iva_tpu_sdk",
    install_requires=[
        'asyncio',
        'numpy',
        'tpu_tlm_is~=0.2.0,>=0.2.0.2',
    ],
    extras_require={
        'test': [
            # Tests
            'pytest',
            'pytest-xdist',
            'pytest-cov',
            'Pillow',
            'tpu_tlm[test]~=0.2.0',
            'iva_applications',
            # Code Quality
            'flake8',
            'mypy',
            'pycodestyle',
            'pydocstyle',
            'pylint',
        ],
    },
    zip_safe=False,
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'run_get_fps = pytpu.scripts.run_get_fps:main',
            'pyrun_tpu = pytpu.scripts.pyrun_tpu_cli:main'
        ]
    },
)
