from setuptools import setup

readme = open("./README.md", "r") # Abrir archivo Readme.md (No detecta acentos)

setup(
    name="SecuenciaAlfanumerica", # Nombre
    packages=['SecuenciaAlfanumerica'], # Nombre de la carpeta
    version="2022.05.28", # Version
    description="Convierte de un número o números a un grupo de caracteres y viceversa", # Descripcion corta
    long_description=readme.read(), # Leer archivo
    long_description_content_type='text/markdown',
    author="Xaival", # Autor
    author_email="xaival.dark@gmail.com", # Correo del autor
    url='https://github.com/Xaival/Libreria-Python-Secuencia-alfanumerica', # Usar la URL del repositorio de GitHub
    keywords=['conversions', 'sequence', 'alphanumeric', 'binary'], # Etiquetas
    classifiers=[ ],
    license='MIT', # Tipo de licencia
    include_package_data=True
)