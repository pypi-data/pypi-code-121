class TrimesterError(Exception):
    pass

class YearError(Exception):
    pass

class AdvertenciaINDEC(Warning):
    pass

class AdvertenciaRegion(Warning):
    pass
  
def disponibles(edicion=False):
    '''
    Devuelve la lista de ENGHo disponibles.
    Se puede definir una edicion para ver todas las bases de esa edicion.'''
    import pandas as pd
    import warnings
    import numpy as np
    nan = np.nan
    
    df = pd.DataFrame(data={'edicion': {0: '17-18',  1: '17-18',  2: '17-18',  3: '17-18',  4: '17-18',  5: '12-13',  6: '12-13',  7: '12-13',  8: '12-13',  9: '12-13',  10: '12-13',  11: '04-05',  12: '04-05',  13: '04-05',  14: '04-05',  15: '04-05',  16: '04-05',  17: '96-97',  18: '96-97',  19: '96-97',  20: '96-97',  21: '96-97',  22: '96-97',  23: '96-97',  24: '96-97',  25: '96-97',  26: '96-97',  27: '96-97',  28: '96-97',  29: '96-97',  30: '96-97',  31: '96-97',  32: '96-97',  33: '96-97',  34: '96-97',  35: '96-97',  36: '96-97',  37: '96-97',  38: '96-97',  39: '96-97',  40: '96-97',  41: '96-97',  42: '96-97',  43: '96-97',  44: '96-97',  45: '96-97',  46: '96-97',  47: '96-97',  48: '96-97',  49: '96-97',  50: '96-97',  51: '96-97',  52: '85-86',  53: '85-86',  54: '85-86',  55: '85-86',  56: '85-86',  57: '85-86',  58: '85-86'}, 
                            'base': {0: 'personas',  1: 'hogares',  2: 'habitos',  3: 'gastos',  4: 'equipamiento',  5: 'personas',  6: 'hogares',  7: 'gtnfp (gastos segun tipo de negocio y forma de pago)',  8: 'ingresos',  9: 'equipamiento',  10: 'gastos',  11: 'personas',  12: 'ingresos',  13: 'hogares',  14: 'gastos',  15: 'gtnfp (gastos por forma de pago, tipo de negocio y lugar de compra)',  16: 'equipamiento',  17: 'gtnfp (gastos por forma de pago y lugar de adquisicion)',  18: 'personas',  19: 'ingresos',  20: 'hogares',  21: 'gastos',  22: 'equipamiento',  23: 'cantidades',  24: 'gtnfp (gastos por forma de pago y lugar de adquisicion)',  25: 'personas',  26: 'ingresos',  27: 'hogares',  28: 'gastos',  29: 'equipamiento',  30: 'cantidades',  31: 'gtnfp (gastos por forma de pago y lugar de adquisicion)',  32: 'personas',  33: 'ingresos',  34: 'hogares',  35: 'gastos',  36: 'equipamiento',  37: 'cantidades',  38: 'gtnfp (gastos por forma de pago y lugar de adquisicion)',  39: 'personas',  40: 'ingresos',  41: 'hogares',  42: 'gastos',  43: 'equipamiento',  44: 'cantidades',  45: 'gtnfp (gastos por forma de pago y lugar de adquisicion)',  46: 'personas',  47: 'ingresos',  48: 'hogares',  49: 'gastos',  50: 'equipamiento',  51: 'cantidades',  52: 'personas',  53: 'hogares',  54: 'grupos',  55: 'gastos',  56: 'capitulos',  57: 'cantidades',  58: 'articulo'}, 
                            'region': {0: nan,  1: nan,  2: nan,  3: nan,  4: nan,  5: nan,  6: nan,  7: nan,  8: nan,  9: nan,  10: nan,  11: nan,  12: nan,  13: nan,  14: nan,  15: nan,  16: nan,  17: 'pampeana',  18: 'pampeana',  19: 'pampeana',  20: 'pampeana',  21: 'pampeana',  22: 'pampeana',  23: 'pampeana',  24: 'noroeste',  25: 'noroeste',  26: 'noroeste',  27: 'noroeste',  28: 'noroeste',  29: 'noroeste',  30: 'noroeste',  31: 'noreste',  32: 'noreste',  33: 'noreste',  34: 'noreste',  35: 'noreste',  36: 'noreste',  37: 'noreste',  38: 'metropolitana',  39: 'metropolitana',  40: 'metropolitana',  41: 'metropolitana',  42: 'metropolitana',  43: 'metropolitana',  44: 'metropolitana',  45: 'cuyo',  46: 'cuyo',  47: 'cuyo',  48: 'cuyo',  49: 'cuyo',  50: 'cuyo',  51: 'cuyo',  52: nan,  53: nan,  54: nan,  55: nan,  56: nan,  57: nan,  58: nan}})
    if edicion:
        if edicion in [2017, 2018, 17, 18, '17-18', '17/18', '2017/2018', '2017-2018']:
            edicion = '17-18'
        elif edicion in [2012, 2013, 12, 13, '12-13', '12/13', '2012-2013', '2012/2012']: 
            edicion = '12-13'
        elif edicion in [2004, 2005, 4, 5, '04-05', '04/05', '2004-2005', '2004/2005']:
            edicion = '04-05'
        elif edicion in [1996, 1997, 96, 97, '96-97', '96/97', '1996/1997', '1996-1997']:
            edicion = '96-97'
        elif edicion in [1985, 1986, 85, 86, '85-86', '85/86', '1985-1986', '1985/1986']:
            edicion = '85-86'
        else:
            raise YearError("La ENGHo solo se realizó en 17-18, 12-13, 04-05, 96-97 y 85-86. Usar alguno de esos años")
        df = df[df['edicion'] == edicion]
        
    return df





def get_microdata(year, type, region=False, download=False):
    '''
    Genera un DataFrame con los microdatos de la ENGHo (Encuesta Nacional de Gastos de los Hogares).
    Utiliza las bases de la página de INDEC (al 27/4/22), resubidas a un Github con los nombres de archivo estandarizados.
    Args:
        @year (int): Año de la ENGHo. Acepta varias alternativas para una misma ENGHo (ej. "17-18", "17/18", 17, 18, 2017, 2018, etc.)
        @type (str, optional): Base a acceder. Varía con el año. Se pueden consultar en el mensaje de error al correr con un type incorrecto.
        @region (str, optional): Usado solo en ENGHo 96-97 
        @download (bool, optional): Descargar los csv de las EPH (en vez de cargarlos directamente a la RAM). Defaults to False.

    Returns:
        pandas.DataFrame: DataFrame con los microdatos de la EPH
    '''
    import pandas as pd
    import zipfile
    import warnings
    
    
    year = handle_exceptions_engho(year, type, region)
    
    
    if year != 1997:
        if region:
            warnings.warn('Las ENGHo están por región solo para la edición 96-97. Región ignorado')
        
        df = pd.read_table(f'https://github.com/lucas-abbate/engho/blob/main/engho/engho{year}_{type}.zip?raw=true', low_memory=False, compression='zip', sep='|', encoding='latin-1')
        link = f'https://github.com/lucas-abbate/engho/blob/main/engho/engho{year}_{type}.zip'
        print(f'Se descargó la ENGHo desde {link} (bases oficiales de INDEC, actualizadas al 27/4/22)')
        return df
    elif year == 1997:
        df = pd.read_table(f'https://github.com/lucas-abbate/engho/blob/main/engho/engho{year}_{region}_{type}.zip?raw=true', compression='zip', sep='|', encoding='latin-1', header=None)
        link = f'https://github.com/lucas-abbate/engho/blob/main/engho/engho{year}_{region}_{type}.zip'
        print(f'Se descargó la ENGHo desde {link} (bases oficiales de INDEC, actualizadas al 27/4/22)')
        return df
    

def handle_exceptions_engho(year, type, region):
    import warnings
    
    if year in [2017, 2018, 17, 18, '17-18', '17/18', '2017/2018', '2017-2018']:
        year = 2018
    elif year in [2012, 2013, 12, 13, '12-13', '12/13', '2012-2013', '2012/2012']: 
        year = 2012
    elif year in [2004, 2005, 4, 5, '04-05', '04/05', '2004-2005', '2004/2005']:
        year = 2005
    elif year in [1996, 1997, 96, 97, '96-97', '96/97', '1996/1997', '1996-1997']:
        year = 1997
        if region not in ['metropolitana', 'cuyo', 'noreste', 'noroeste', 'pampeana']:
            raise TypeError('La ENGHo 96-97 está publicada por regiones para: metropolitana, cuyo, noreste, noroeste y pampeana')
        link_variables = 'https://www.indec.gob.ar/ftp/cuadros/menusuperior/engho/engh9697_dise%C3%B1o_registro.zip'
        warnings.warn(f'Los archivos de ENGHo 96-97 proporcionados por INDEC no tienen nombres de variable. Se pueden consultar para cada base en {link_variables}', AdvertenciaINDEC, stacklevel=3)
    elif year in [1985, 1986, 85, 86, '85-86', '85/86', '1985-1986', '1985/1986']:
        year = 1986
    else:
        raise YearError("La ENGHo solo se realizó en 17-18, 12-13, 04-05, 96-97 y 85-86. Usar alguno de esos años")

    if year != 1997 and region != False:
        warnings.warn('La única base regionalizada es la de 96-97 (y la 85-86, solo para CABA y conurbano). Se omitirá la region', AdvertenciaINDEC, stacklevel=3)
    

    if year == 2018 and type not in ['personas', 'hogares', 'equipamiento', 'gastos', 'habitos']:
        raise TypeError('En la ENGHo 17-18, las bases son: personas, hogares, equipamiento, gastos y habitos')
    
    elif year == 2012 and type not in ['personas', 'hogares', 'equipamiento', 'gastos', 'ingresos', 'gtnfp']:
        raise TypeError('En la ENGHo 12-13, las bases son: personas, hogares, equipamiento, gastos y gtnfp (gastos segun tipo de negocio y forma de pago)')
    
    elif year == 2005 and type not in ['personas', 'hogares', 'equipamiento', 'gastos', 'ingresos', 'gtnfp']:
        raise TypeError('En la ENGHo 04-05, las bases son: personas, hogares, equipamiento, gastos, ingresos y gtnfp (gastos segun tipo de negocio y forma de pago)')
    
    elif year == 1997 and type not in ['personas', 'hogares', 'equipamiento', 'ingresos', 'gastos', 'gtnfp', 'cantidades']:
        raise TypeError('En la ENGHo 96-97, las bases son: personas, hogares, equipamiento, gastos, cantidades, ingresos y gtnfp (gastos segun tipo de negocio y forma de pago)')
    
    elif year == 1986 and type not in ['personas', 'hogares', 'articulo', 'ingresos', 'capitulo', 'gastos', 'grupo']:
        raise TypeError('En la ENGHo 85-86, las bases son: personas, hogares, articulo, gastos, ingresos, capitulo y grupo')
    
    return year    
