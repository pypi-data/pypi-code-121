from setuptools import setup

# Lee el contenido del fichero README
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README").read_text()

setup(
        name            = 'listas_anidadas',
        version         = '1.2.0',
        py_modules      = ['listas_anidadas'],
        author          = 'Fortinux',
        author_email    = 'info@fortinux.com',
        url             = 'https://fortinux.com',
        description     = 'Función que imprime listas anidadas',
        long_description=long_description,
        long_description_content_type='text/markdown'
    )
