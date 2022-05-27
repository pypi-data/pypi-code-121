#!/user/bin/env python3
"""
[Módulo con función que muestra los items de listas anidadas.]

Author: Fortinux
Email: info@fortinux.com
Web: https://fortinux.com
"""
def funcion(articulos):
    """
    Esta función toma la lista artículos (y si hubiera, 
    anidadas) e imprime los items separadamente en líneas.
    """ 
    for articulo in articulos:
        if isinstance(articulo, list):
            funcion(articulo)
        else:
            print(articulo)

