# -*- coding: utf-8 -*-
from os import path

CODIGOS_TARIFA = ['30', '31', '62', '63', '64', '65', '21', '2A', '6A', '2T', '3T', '3V', '6V']
CODIGOS_TENSION = ['E0', 'E1', 'E2', 'E3', 'E4', 'E5', 'E6']
CODIGOS_DH = ['G0', 'E3', 'E2', 'E1']
CODIGOS_AUTOCONSUMO = ['31', '32', '33', '41', '42', '51', '52', '53', '54', '55', '56', '61', '62', '63', '64', '71', '72', '73', '74']

def validar_contrato(data):
    if not isinstance(data, dict):
        raise Exception("El formato de datos debe ser un diccionario")

    validar_provincia(data['provincia'])
    validar_municipio(data['municipio'])
    validar_cups(data['cups'])
    validar_tension(data['tensionConexion'])
    validar_tarifa(data['tarifaAcceso'])
    validar_dh(data['discriminacionHoraria'])
    validar_tipo_punto(data['tipoPunto'])
    validar_control_potencia(data['modoControlPotencia'])
    validar_nif(data['nif'])
    validar_cnae(data['CNAE'])
    if 'potenciasContratadas' in data:
        validar_potencias_contratadas(data['potenciasContratadas'])
    if 'cau' in data:
        validar_cau(data['cau'])
        validar_coeficiente_reparto(data['coeficienteReparto'])

def validar_autoconsumo(data):
    if not isinstance(data, dict):
        raise Exception("El formato de datos debe ser un diccionario")

    validar_cau(data['cau'])
    validar_tipo_autoconsumo(data['tipoAutoConsumo'])
    validar_seccion(data['seccion'])

def validar_provincia(provincia):
    provincias, municipios = read_provincias_municipios()
    if provincia not in provincias:
        raise Exception('El codigo provincia {} no existe en el INE'.format(provincia))

def validar_municipio(municipio):
    provincias, municipios = read_provincias_municipios()
    if municipio not in municipios:
        raise Exception('El codigo municipio {} no existe en el INE'.format(municipio))

def validar_cups(cups):
    if len(cups) != 22:
        raise Exception('El cups debe tener 22 caracteres')

def validar_tension(tension):
    if not isinstance(tension, str):
        raise TypeError("Tension {} incorrecta".format(tension))
    if tension.upper() not in CODIGOS_TENSION:
        raise Exception("Codigo tension {} no catalogada en las tablas de tension".format(tension))

def validar_tarifa(tarifa):
    if not isinstance(tarifa, str):
        raise TypeError("Tarifa {} incorrecta".format(tarifa))
    if tarifa.upper() not in CODIGOS_TARIFA:
        raise Exception("Codigo tarifa {} no catalogada en las tablas de tarifa".format(tarifa))

def validar_dh(dh):
    if not isinstance(dh, str):
        raise TypeError("Discriminacion horaria {} incorrecta".format(dh))
    if dh.upper() not in CODIGOS_DH:
        raise Exception("Codigo discriminacion horaria {} no catalogada en las tablas de discriminacion horaria -> {}".format(dh, CODIGOS_DH))

def validar_tipo_punto(tipo_punto):
    if int(tipo_punto) > 5 or int(tipo_punto) < 1:
        raise Exception("Codigo tipo de punto {} incorrecto -> 1, 2, 3, 4, 5".format(tipo_punto))

def validar_control_potencia(control_potencia):
    if not isinstance(control_potencia, int):
        raise TypeError("Modo control potencia {} incorrecto".format(control_potencia))
    if control_potencia not in (1, 2):
        raise Exception("Modo control potencia {} incorrecto -> 1: Maximetro, 2: ICP")

def validar_nif(nif):
    if len(nif) < 9:
        raise Exception("Longitud NIF/CIF {} incorrecto".format(nif))

def validar_potencias_contratadas(potencias_contratadas):
    if not isinstance(potencias_contratadas, (list, tuple)):
        raise Exception("Las potencias contratadas deben enviarse en formato lista")
    for pot in potencias_contratadas:
        if not isinstance(pot, float):
            raise Exception("Las potencias contratadas deben enviarse en kWh y en decimales")

def validar_cnae(cnae):
    if cnae and len(cnae) != 4:
        raise Exception("Longitud CNAE {} incorrecta".format(cnae))

def validar_cau(cau):
    if len(cau) != 26:
        raise Exception('El CAU debe tener 26 caracteres')

def validar_tipo_autoconsumo(tipo_autoconsumo):
    if not isinstance(tipo_autoconsumo, str):
        raise TypeError("Tipo autoconsumo {} incorrecto, debe ser un string".format(tipo_autoconsumo))
    if tipo_autoconsumo.upper() not in CODIGOS_AUTOCONSUMO:
        raise Exception(
            "Tipo autoconsumo {} no catalogado en las tablas -> {}".format(tipo_autoconsumo, CODIGOS_AUTOCONSUMO))

def validar_seccion(seccion):
    if not int(seccion) in (1, 2):
        raise Exception(
            "Seccion incorrecta {}: Solo se permite seccion 1 Sin excedentes o 2 Con excedentes".format(seccion))

def validar_coeficiente_reparto(coeficiente_reparto):
    if not isinstance(coeficiente_reparto, (int, float)):
        raise TypeError("El formato de Coeficiente de reparto {} es incorrecto.".format(coeficiente_reparto))

def read_provincias_municipios():
    import csv
    municipios = []
    provincias = []
    abs_route_fname = path.join(
        path.dirname(path.realpath(__file__)), 'data/20codmun.csv'
    )
    with open(abs_route_fname) as csvfile:
        for CODAUTO, CPRO, CMUN, DC, NOMBRE in csv.reader(csvfile, delimiter=';'):
            provincias.append(CPRO)
            municipios.append(CMUN)
    return provincias, municipios
