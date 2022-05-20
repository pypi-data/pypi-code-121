from setuptools import find_packages, setup

info = open("README.md").read()

setup(
    name='ttrs_quicfire',
    version='1.0.1',
    description='ttrs_quicfire is a Python library to easily configure burn models for plots of land defined using shape files for the quicfire model.',
    long_description=info,
    long_description_content_type='text/markdown',
    url='https://github.com/QUIC-Fire-TT/ttrs_quicfire',
    license='MIT', # Verify License Before Upload
    author='Zachary Cope',
    author_email='zcope@talltimbers.org',
    packages=find_packages(),
    install_requires=['numpy',
                      'scipy',
                      'geopandas',
                      'pandas',
                      'gdal',
                      'rasterio',
                      'fastfuels',
                      'shapely'],
    classifiers=[
        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering :: GIS',
        'Topic :: Scientific/Engineering :: Visualization',
        'License :: OSI Approved :: MIT License', # Verify license before upload
    ],
    project_urls={
        #'Documentation': 'https://github.com/QUIC-Fire-TT/ttrs_quicfire/wiki', # Github Wiki?
        'Source': 'https://github.com/QUIC-Fire-TT/ttrs_quicfire', # Github Repo
        'Tracker': 'https://github.com/QUIC-Fire-TT/ttrs_quicfireissues', # Github Issues
    }
)