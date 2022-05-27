import json
import yaml
import os
import sys

#from PDFWriter import PDFWriter
from fpdf import FPDF


def merge_dicts(dictionary):
    """ TODO translate to english 
    
    Recebe um dicionario de dicionarios e retorna um dicionario unico com chave valor, 
    onde valor nao e dicionario.
    
    Recebe:
            dictionary - dicionario de dicionarios.

    Retorna:
            merged_dict - dicionario com chave valor, onde valor nao e dicionario"""
    merged_dict = {}

    for key in dictionary:
        if type(dictionary[key]) is dict:
            merged_dict = {**merged_dict, **merge_dicts(dictionary[key])}
        else:
            merged_dict = {**merged_dict, **{key: dictionary[key]}}
    
    return merged_dict


def remove_item_list(list, item):
    """TODO translate to english
    
    Recebe uma lista e um item a ser retirado da lista e retorna a lista sem o item.
    
    Recebe:
            list - lista

    Retorna:
            list - lista sem o item de entrada"""
    list.remove(item)
    return list


def print_json(input, file_path=None, mode='w'):
    """TODO translate to english
    
    Recebe um dicionario de entrada (input var) e o caminho do arquivo JSON a ser gravado e printa
    o conteudo da entrada no arquivo caso exista. Em caso negativo printa em std_out.
    
    Recebe:
            input - dicionario a ser gravado no arquivo file_path caso exista
            file_path - caminho do arquivo a ser realizado o print do conteudo do dicionario de entrada"""

    if file_path is None:
        print(json.dumps(input, indent=4))
    else:
        print(
            json.dumps(input, indent=4), 
            file=open(file_path, mode)
        )

    return


def print_yaml(input, file_path=None):
    """TODO write docstring"""
    if file_path is None:
        print(yaml.dump(input))
    else:
        print(yaml.dump(input), file=open(file_path, "w"))

    return


def remove_empty_lines(filename):
    """TODO translate to english
    
    Recebe o path de um arquivo e remove as linhas vazias
    
    Recebe:
            filename - path de um arquivo"""
    if not os.path.isfile(filename):
        print("{} does not exist ".format(filename))
        return
    with open(filename) as filehandle:
        lines = filehandle.readlines()

    with open(filename, 'w') as filehandle:
        lines = filter(lambda x: x.strip(), lines)
        filehandle.writelines(lines)  

    return

def text_to_pdf(txt_data):
    # save FPDF() class into 
    # a pdf object
    pdf = FPDF()   
    # Add a page
    pdf.add_page()
    
    # Set style and size of font 
    pdf.set_font(
        txt_data['font_name'], 
        size=txt_data['font_size']
    )
    
    # Insert the texts in pdf
    for x in txt_data['lines']:
        pdf.cell(200, 10, txt = x, ln = 1, align = 'J')
    
    # Save the pdf with name
    pdf.output(txt_data['pdf_filename'])

    return

def convert_txt_to_pdf(file_path):
    """TODO write docstring"""
    ori_filename = file_path.split('/')[-1]
    filename = f"{ori_filename.split('.')[0]}"
    file_header = filename.replace("_", " ").upper()
    pdf_filename = f"{filename}.pdf"
    with open(file_path, 'r') as file:
        lines = file.readlines()
        data = {
            'pdf_filename': pdf_filename,
            'font_name': 'Courier',
            'font_size': 9,
            'header': file_header,
            'lines': lines
        }
        text_to_pdf(data)
    print(f"PDF file converted from {ori_filename} to {pdf_filename}")
    
    return pdf_filename


def elem2dict(node):
    """
    Convert an xml.ElementTree node tree into a dict.
    """
    result = {}

    for element in node:
        key = element.tag
        if '}' in key:
            # Remove namespace prefix
            key = key.split('}')[1]

        if node.attrib:
            result['@attribs'] = dict(node.items())

        # Process element as tree element if the inner XML contains non-whitespace content
        if element.text and element.text.strip():
            value = element.text
        else:
            value = elem2dict(element)
        
        # Check if a node with this name at this depth was already found
        if key in result:
            if type(result[key]) is not list:
                # We've seen it before, but only once, we need to convert it to a list
                try:
                    tempvalue = result[key].copy()
                    result[key] = [tempvalue, value]
                except Exception:
                    pass
            else:
                # We've seen it at least once, it's already a list, just append the node's inner XML
                result[key].append(value)
        else:
            # First time we've seen it
            result[key] = value

    return result