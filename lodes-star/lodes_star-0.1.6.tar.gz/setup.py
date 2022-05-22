from setuptools import setup

setup(
    name='lodes_star',
    version='0.1.6',
    description='For scraping Longitudinal Origin-Destination Employment Statistics (LODES) data from'
                ' the US Census as well as fetching Census Block GIS shapefiles.',
    url='https://github.com/nick-fournier/lodes-star',
    author='Nicholas Fournier',
    author_email='nichfournier@gmail.com',
    license='GNU',
    packages=['lodes_star'],
    install_requires=['beautifulsoup4==4.11.1',
                      'Fiona==1.8.21',
                      'geopandas==0.10.2',
                      'matplotlib==3.5.2',
                      'pandas==1.4.2',
                      'requests==2.27.1',
                      'scipy==1.8.1',
                      'setuptools==60.2.0',
                      'sparse==0.13.0',
                      'tqdm==4.64.0',
                      'urllib3==1.26.9'],
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 3.9',
    ],
)
