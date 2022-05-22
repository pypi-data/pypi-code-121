from setuptools import setup, find_packages
from pathlib import Path
long_description = (Path(__file__).parent / "README.md").read_text()
setup(
    name="ud-dist-meta",
    packages=find_packages(),
    version='1.0.2',
    description='Library to extract information from packages installed in current python environment',
    author='Umbriel Draken',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author_email='umbriel.draken@gmail.com',
    url='https://github.com/um-en/ud-dist-meta',
    license='MIT',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.9',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: Microsoft :: Windows :: Windows 10',
    ],
    keywords=['distribution', 'virtual environment', 'metadata'],
    install_requires=[
        'importlib-metadata',
        'pyyaml',
    ],
    entry_points={'console_scripts': ["gen_dist_info=dist_meta.scripts:gen_distinfo_cmd"]}
)
