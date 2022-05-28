from .class_tiplsb import tiplsb
from .function_additional import *


def tip_decode(path_original, path_modified):
    recorrido = {}

    # Abrir imagen modificada
    tip_modified = tiplsb(path_modified)

    # Inicializamos imagen
    tip_original = tiplsb(path_original, hash=tip_modified.init['Hash'], version=tip_modified.init['Version'], redundancy=tip_modified.init['Redundancy'])

    max_ring = int(min(tip_modified.width, tip_modified.height) / 2) - 1
    j = list(range(0, max_ring + 1, tip_modified.init['Redundancy']))
    l_rings = [j[i]+1 for i in range(0, len(j) - 1)]

    index_read = int((tip_original.init['Line']-1)/tip_original.init['Redundancy'])

    # Recorremos anillos
    for ring in l_rings[index_read:]:
        # Leer linea con redundancia
        read_count = {}
        read = read_ring_redundancy(tip_modified.img_array, ring, tip_original.hash_image, tip_modified.init['Redundancy'], tip_modified.width, tip_modified.height)
        # Comprobar si son iguales
        for r in read:
            if r[0] in read_count.keys():
                read_count[r[0]] += 1
            elif r[0] != "":
                read_count[r[0]] = 1

        # Si solo hay una clave significa que no hace falta aplicar redundancia
        if len(read_count.keys()) == 1:
            # No hay redundancia
            # Se escribe en imagen original
            text = list(read_count.keys())[0]
            recorrido[index_read] = text
            index_read += 1
            text = text.split("|")
            tip_original.add(text[1], text[2], text[3])
        elif len(read_count.keys()) > 1:
            # Aplicar redundancia
            read_count = list(read_count.items())
            read_count.sort(key=lambda x: x[1], reverse=True)
            text = read_count[0][0]
            recorrido[index_read] = text
            index_read += 1
            text = text.split("|")
            tip_original.add(text[1], text[2], text[3])
            # Paramos el proceso ya que nos hemos encontrado con errores
            break
        else:
            # No se encuentran resultados
            break

    return recorrido