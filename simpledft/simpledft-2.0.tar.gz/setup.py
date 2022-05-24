from setuptools import find_packages, setup

with open('README.md', 'r') as fh:
    long_description = fh.read()

setup(
    name='simpledft',
    version='2.0',
    description='A simple density functional theory code.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Wanja Timm Schulze',
    author_email='wangenau@protonmail.com',
    url='https://gitlab.com/nextdft/simpledft',
    packages=find_packages(),
    license='APACHE2.0',
    install_requires=['numpy'],
    keywords=['NextDFT'],
    include_package_data=True,
    zip_safe=False,
    python_requires='>=3',
    project_urls={
        'Bug Tracker': 'https://gitlab.com/nextdft/simpledft/-/issues'
    }
)
