from setuptools import setup, find_packages

setup(
    name='RQMExcelImporter',
    version='0.1',
    license='MIT',
    author="Thiago Segato",
    author_email='thiagoosegato@gmail.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    url='https://github.com/ThiagoSegato/RQMExcelImporter',
    keywords='rqms excel convert extract',
    install_requires=[
        'et-xmlfile==1.1.0',
        'numpy==1.22.3',
        'openpyxl==3.0.10',
        'pandas==1.4.2',
        'python-dateutil==2.8.2',
        'pytz==2022.1',
        'six==1.16.0'
    ],

)