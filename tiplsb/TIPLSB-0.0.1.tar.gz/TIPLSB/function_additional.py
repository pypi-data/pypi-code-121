import random
import hashlib


def max_index_element_ring(ring, width, height):
    size_width = width - (ring + 1) * 2 + 2
    size_height = height - (ring + 1) * 2 + 2
    return (size_width * 2 + size_height * 2 - 4) * 3


def index_element_ring(element, ring, width, height):
    size_width = (width - (ring + 1) * 2 + 2)
    size_height = (height - (ring + 1) * 2 + 2)

    size_width_color = size_width * 3
    size_height_color = size_height * 3

    side_a = width * ring + ring
    side_b = side_a + size_width - 1
    side_c = side_b + width * (size_height - 1)
    side_d = side_a + width * (size_height - 1)

    if element < size_width_color:
        bit_corresponde = element // 3
        color_corresponde = element % 3
        return (side_a + bit_corresponde, color_corresponde)
    elif element < (size_width_color + size_height_color - 3):
        element = element - size_width_color
        bit_corresponde = element // 3 + 1
        color_corresponde = element % 3
        return (side_b + bit_corresponde * width, color_corresponde)
    elif element < (size_width_color * 2 + size_height_color - 6):
        element = element - size_width_color - size_height_color
        bit_corresponde = element // 3 + 1
        color_corresponde = element % 3
        return (side_d + (size_width - bit_corresponde) - 2, color_corresponde)
    else:
        element = element - size_width_color * 2 - size_height_color
        bit_corresponde = element // 3 + 3
        color_corresponde = element % 3
        return (side_d - bit_corresponde * width, color_corresponde)


def txt_to_bin(text):
    return ''.join([format(ord(i), "08b") for i in text])


def bin_to_txt(bits):
    text = ''
    bits = [bits[i:i + 8] for i in range(0, len(bits), 8)]
    for i in range(len(bits)):
        text += chr(int(bits[i], 2))
    return text


# Le das una lista de index de colores [(pixel, color)] y el array y te devuelve los bits
def read_bits_index(array, list_index):
    bits = ''
    for (pixel, color) in list_index:
        bits += bin(array[pixel][color])[2:][-1]
    return bits


def read_ring(array, ring, actual_hash, width, height):
    elements = max_index_element_ring(ring, width, height)
    random.seed(actual_hash)
    l_elements = random.sample(range(0, elements), k=520)
    list_index = []
    for i in l_elements[:48]:
        list_index.append(index_element_ring(i, ring, width, height))
    txt_bits = read_bits_index(array, list_index)
    txt = bin_to_txt(txt_bits)
    list_index_read = list(zip(list_index, txt_bits))
    if txt == "TIPLSB":
        cont = 0
        list_index = []
        for i in l_elements[48:]:
            index_ele = index_element_ring(i, ring, width, height)
            list_index.append(index_ele)
            cont += 1
            if cont == 8:
                txt_bits = read_bits_index(array, list_index)
                list_index_read.extend(list(zip(list_index, txt_bits)))
                character = bin_to_txt(txt_bits)
                if character == "#":
                    break
                else:
                    txt += character
                    list_index = []
                    cont = 0
        return txt, list_index_read
    else:
        return "", ""


def read_ring_redundancy(array, ring, actual_hash, redundancy, width, height):
    res = []
    for i in range(0, redundancy):
        new_hash = hex(int(actual_hash, 16) + int(str(i), 16))[2:]
        res.append(read_ring(array, ring, new_hash, width, height))
        ring += 1
    return res


def switch_hash(hash):
    if hash == 'sha1':
        return hashlib.sha1
    elif hash == 'sha224':
        return hashlib.sha224
    elif hash == 'sha256':
        return hashlib.sha256
    elif hash == 'sha384':
        return hashlib.sha384
    elif hash == 'sha512':
        return hashlib.sha512
    else:
        return hashlib.sha256
