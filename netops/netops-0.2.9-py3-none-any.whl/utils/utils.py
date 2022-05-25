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
    Convert an lxml.etree node tree into a dict.
    """
    result = {}

    for element in node.iterchildren():
        # Remove namespace prefix
        key = element.tag.split('}')[1] if '}' in element.tag else element.tag

        # Process element as tree element if the inner XML contains non-whitespace content
        if element.text and element.text.strip():
            value = element.text
        else:
            value = elem2dict(element)
        if key in result:


            if type(result[key]) is list:
                result[key].append(value)
            else:
                tempvalue = result[key].copy()
                result[key] = [tempvalue, value]
        else:
            result[key] = value
    return result