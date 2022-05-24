# -*- coding: utf-8 -*-
from re import findall
from datetime import datetime

REQUIRED_CONTRATO_KEYS = [
    'comercializadora', 'tensionConexion', 'tarifaAcceso', 'discriminacionHoraria', 'tipoPunto', 'modoControlPotencia',
    'fechaInicioContrato', 'nif', 'nombre', 'cups', 'distribuidora', 'codigoPostal', 'provincia', 'municipio', 'CNAE'
]
REQUIRED_MAXIMAS_POTENCIA_KEYS = [
    'medida', 'fecha', 'periodo'
]

REQUIRED_AUTOCONSUMO_KEYS = [
    'cau', 'tipoAutoConsumo', 'seccion', 'subseccion'
]

def adaptar_contrato(data):
    for key in REQUIRED_CONTRATO_KEYS:
        if key not in data:
            raise KeyError("Clave requerida {} no encontrada!".format(key))
    if len(str(data['municipio'])) != 3:
        data['municipio'] = str(data['municipio'])[-3:]
    if not data['CNAE']:
        data.update({'CNAE': ""})
    else:
        data.update({'CNAE': str(data['CNAE']).zfill(4)})
    data.update({
        'comercializadora': str(data['comercializadora'].zfill(4)),
        'distribuidora': str(data['distribuidora'].zfill(4)),
        'tarifaAcceso': str(data['tarifaAcceso'].upper()),
        'tensionConexion': str(data['tensionConexion'].upper()),
        'discriminacionHoraria': str(data['discriminacionHoraria'].upper()),
        'municipio': str(data['municipio']).zfill(3),
        'provincia': str(data['provincia']).zfill(2),
        'codigoPostal': str(data['codigoPostal']).zfill(5),
        'tipoPunto': int(data['tipoPunto']),
        'nif': str(data['nif']).replace('ES', '')
    })
    if not isinstance(data['modoControlPotencia'], int):
        control_potencia = 1 if 'max' in data['modoControlPotencia'] else 2
        data.update({'modoControlPotencia': control_potencia})
    if 'potenciasContratadas' in data:
        if isinstance(data['potenciasContratadas'], (dict)):
            potencias = []
            for val in data['potenciasContratadas'].values():
                potencias.append(float(val))
            data['potenciasContratadas'] = potencias
        elif not isinstance(data['potenciasContratadas'], (list, dict)):
            potencias = data['potenciasContratadas']
            potencias_keys = findall('P\d', potencias)
            for pot_key in potencias_keys:
                potencias = potencias.replace('{}: '.format(pot_key), '')
            potencias = potencias.split(' ')
            for i, pot in enumerate(potencias):
                potencias[i] = float(potencias[i])
            data['potenciasContratadas'] = potencias
    if 'cau' in data:
        data.update({'coeficienteReparto': float(data['coeficienteReparto'])})
    return data

def adaptar_maximas_potencia(data):
    for key in REQUIRED_MAXIMAS_POTENCIA_KEYS:
        if key not in data:
            raise KeyError("Clave requerida {} no encontrada!".format(key))

    hour_mask = "%H:%M"
    date_mask = "%Y-%m-%d"
    try:
        ts = datetime.strptime(data['fecha'], date_mask + ' ' + hour_mask + ":%S")
    except (ValueError, TypeError):
        try:
            ts = datetime.strptime(data['fecha'], date_mask + ' ' + hour_mask)
        except (ValueError, TypeError):
            try:
                ts = datetime.strptime(data['fecha'], date_mask)
            except:
                raise Exception("Formato {} fecha incorrecto -> AAAA/mm/dd o AAAA/mm/dd HH:MM o AAAA/mm/dd HH:MM:SS".format(data['fecha']))
    fecha = ts.strftime(date_mask)
    hora = ts.strftime(hour_mask)
    medida = "%.3f" % round(data['medida'], 3)
    medida = float(medida)
    periodo = int(data['periodo'])
    if periodo not in [1, 2, 3, 4, 5, 6]:
        raise Exception("Periodo {} incorrecto. Valores permitidos 1, 2, 3, 4, 5, 6".format(periodo))
    data.update({'medida': medida, 'fecha': fecha, 'hora': hora, 'periodo': periodo})
    return data

def adaptar_estado(data):
    if not isinstance(data['timestamp'], int):
        data['timestamp'] = int(data['timestamp'])
    return data

def adaptar_autoconsumo(data):
    for key in REQUIRED_AUTOCONSUMO_KEYS:
        if key not in data:
            raise KeyError("Clave requerida {} no encontrada!".format(key))
    data.update({
        'tipoAutoConsumo': str(data['tipoAutoConsumo']),
        'seccion': str(data['seccion']),
        'subseccion': str(data['subseccion'].lower()),
        'potenciaInstaladaGeneracion': float(data['potenciaInstaladaGeneracion'])
    })
    return data
