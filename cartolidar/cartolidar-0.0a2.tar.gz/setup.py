#!/usr/bin/env/python
# -*- coding: UTF-8 -*-
"""Installation script for cartolidar
"""

import os

import setuptools
# from setuptools import find_packages
# from setuptools import setup

# Ver https://bernat.tech/posts/pep-517-518/
# Ver https://packaging.python.org/guides/distributing-packages-using-setuptools/
# Ver https://github.com/pypa/sampleproject

packages=setuptools.find_packages()
print('packages encontrados:', packages)

# Ver https://docs.python.org/3/distutils/setupscript.html

# # Por ahora no uso versioneer
# #   Ver https://pypi.org/project/versioneer/
# # ensure the current directory is on sys.path so versioneer can be imported
# # when pip uses PEP 517/518 build rules.
# # https://github.com/python-versioneer/python-versioneer/issues/193
# sys.path.append(os.path.dirname(__file__))
# import versioneer

HERE = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(HERE, 'README.md')) as fid:
    README = fid.read()

INSTALL_REQUIRES = [
    'gdal >= 3.0.2',
    'numpy >= 1.19.1',
    'scipy >= 1.4.1',
    'psutil >= 5.7.0',
	'dbfread >= 2.0.7',
	# 'TensorFlow >= 2.3.0',
	# 'keras >= 2.4.3',
	# 'pandas>= 1.0.5',
	# 'h5py >= 2.10.0',
	# 'matplotlib >= 3.2.2',
	# 'PIL >= 7.2.0',
	# 'numba >= 0.50.1',
	# 'graphviz >= 0.11.1',
	# 'openpyxl >= 3.0.5',
]

datapath1 = os.path.abspath('data')
# print('Elementos en {}:\n\t{}'.format(HERE, os.listdir(HERE)))
# print('Elementos en {}:\n\t{}'.format(os.path.join(HERE, 'cartolidar'), os.listdir(os.path.join(HERE, 'cartolidar'))))
# print('Elementos en {}:\n\t{}'.format(os.path.abspath('cartolidar'), os.listdir('cartolidar')))
# print('NO se buscan los data_files en:', os.path.join(HERE, 'data'))
print('SI se buscan los data_files en: {}:\n\t {}'.format(datapath1, os.listdir(datapath1)))

# No creo directorio data dentro de la ruta del proyecto:
# datapath2 = os.path.join('cartolidar', 'data')
# try:
    # print('Data_files en {}: {}'.format(os.path.abspath('cartolidar/data'), os.listdir('cartolidar/data'))
# except OSError as my_error:
    # print('type(my_error):', type(my_error))    # the exception instance
    # print('my_error.args: ', my_error.args)     # arguments stored in .args
    # print('my_error:      ', my_error)
    # print('No existe la ruta: {}'.format(os.path.abspath('cartolidar/data'))

# get all data dirs in the datasets module
data_files = []
for item in os.listdir(datapath1):
    if not item.startswith('__'):
        if os.path.isdir(os.path.join('data', item)):
            data_files.append(os.path.join('data', item, '*'))
        elif item.endswith('.zip'):
            data_files.append(os.path.join('data', item))
# data_files.append('tests/data/*')


setuptools.setup(
    name='cartolidar',
	# Versions should comply with PEP 440:
    # 	https://www.python.org/dev/peps/pep-0440/
    # version=versioneer.get_version(),
    version='0.0a2',
    description='Lidar data processing tools focused on Spanish PNOA datasets',
    long_description=README,
    long_description_content_type='text/markdown',
    url='https://github.com/cartolid/cartolidar',
    project_urls={
        "Source": 'https://github.com/cartolid/cartolidar',
		"Bug Reports":  'https://github.com/cartolid/cartolidar/issues',
		"PNOA Lidar data":  'https://centrodedescargas.cnig.es',
    },
    author='Jose Bengoa',
    author_email='cartolidar@gmail.com',
    license='GNU GPLv3',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: Spanish',
        'Natural Language :: English',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.7',
        'Topic :: Scientific/Engineering :: GIS',
    ],
	keywords='lidar, forestry, dasometry, dasoLidar, DLV, PNOA, GIS, DEM, DTM, DSM',

    python_requires='>=3.7',
	# Ver https://docs.python.org/3/distutils/setupscript.html#listing-whole-packages
    # Esto da error (creo que solo se necesita si los modulos estan en un subdirectorio tipo "src":
    # packages=setuptools.find_packages(where='cartolidar'),
    # Alternativa (tambien da error):
    # package_dir={'': 'cartolidar'}
    packages=setuptools.find_packages(),
    # Otra alternativa es enumerar los paquetes explicitamente:
    # packages=[
        # 'cartolidar',
        # 'cartolidar.clidtools',
        # 'cartolidar.clidax',
    # ],
    install_requires=INSTALL_REQUIRES,

	# Para ficheros adicionales ver: http://docs.python.org/distutils/setupscript.html#installing-additional-files
    # package_data={"": data_files},
    # include_package_data=True,

	# Para entry_points ver:
	#	https://setuptools.pypa.io/en/latest/userguide/entry_point.html#dynamic-discovery-of-services-and-plugins
	#	https://docs.pytest.org/en/latest/how-to/writing_plugins.html
	#	https://docs.pytest.org/en/latest/how-to/plugins.html#using-plugins
	# 	https://stackoverflow.com/questions/774824/explain-python-entry-points
	# No lo uso porque no lo tengo bien configurado y me da error al instalar el paquete subido a pypi:
    # entry_points={'console_scripts': ['qlidtwins=cartolidar.qlidtwins']},
    # cmdclass=versioneer.get_cmdclass(),
)


#Para classifiers, ver https://pypi.org/pypi?%3Aaction=list_classifiers

#Aviso obsoleto: para incluir las carpetas auxiliares y otros ficheros uso el MANIFEST.in en lugar de la linea:
#    package_data={'': ['README.md', 'LICENSE', 'clidpar/clidax']},
#Aunque mantengo la linea:
#    include_package_data=True,
#Ver:
# https://stackoverflow.com/questions/1612733/including-non-python-files-with-setup-py
# https://stackoverflow.com/questions/1471994/what-is-setup-py