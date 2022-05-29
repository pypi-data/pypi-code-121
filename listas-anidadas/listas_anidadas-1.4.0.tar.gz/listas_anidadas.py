#!/user/bin/env python3
"""
[Módulo con función que muestra los items de listas anidadas.]

Author: Fortinux
Email: info@fortinux.com
Web: https://fortinux.com
"""
import sys

def funcion(articulos, tabular=False, listas=0, fichero=sys.stdout):
    """
    Esta función toma el argumento artículos (lista o listas 
    anidadas) e imprime los ítems separadamente en líneas.
    El argumento {listas} inserta un tabulador cuando  se 
    encuentra una lista anidada. Finalmente {fichero} imprime
    el contenido a un nuevo fichero.
    """ 
    for articulo in articulos:
        if isinstance(articulo, list):
            funcion(articulo, tabular, listas+1, fichero)
        else:
            if tabular:
                for l in range(listas):
                    print('\t', end='', file=fichero)    
            print(articulo, file=fichero)


