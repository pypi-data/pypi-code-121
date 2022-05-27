#!/user/bin/env python3
"""
[Módulo con función que muestra los items de listas anidadas.]

Author: Fortinux
Email: info@fortinux.com
Web: https://fortinux.com
"""
def funcion(articulos, listas=0):
    """
    Esta función toma el argumento artículos (lista o listas 
    anidadas) e imprime los ítems separadamente en líneas.
    El segundo argumento, listas, inserta un tabulador cuando
    se encuentra una lista anidada.
    """ 
    for articulo in articulos:
        if isinstance(articulo, list):
            funcion(articulo, listas+1)
        else:
            for l in range(listas):
                print('\t', end='')    
            print(articulo)

