from setuptools import setup
from pathlib import Path

this_dir = Path(__file__).parent
long_desc = (this_dir / 'README.md').read_text()

setup(
    name='ProtViewer',
    version='0.0.2',
    description='A web-based tool to visualize activities in proteins',
    long_description=long_desc,
    long_description_content_type='text/markdown',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Education',
        'Intended Audience :: Healthcare Industry',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Education',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Scientific/Engineering :: Visualization'
    ],
    keywords='python,visualization,protein,activity',
    author='Roman Joeres',
    license='MIT',
    author_email='romanjoeres@gmail.com',
    url='https://github.com/Old-Shatterhand/ProtViewer',
    platforms='any',
    python_requires='>=3.0',
)
