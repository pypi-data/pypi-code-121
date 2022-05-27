class INDECError(Exception):
    pass

class WaveError(Exception):
    pass

class TrimesterError(Exception):
    pass

class YearError(Exception):
    pass

class AdvertenciaINDEC(Warning):
    pass
    
def disponibles(year=False):
    '''
    Devuelve la lista de EPHs disponibles para descargar.
    Se puede especificar un año o un rango de años [desde, hasta]'''
    import pandas as pd
    import warnings
    warnings.warn('La lista de EPH disponibles se actualizó el 29/4/22. Seguramente se pueda acceder a bases posteriores si INDEC no cambió el formato de los nombres, pero no está verificado. Probar si andan\n-------------------------------------------------------------------------------------------------', stacklevel=3)
    
    df = pd.DataFrame(data={'año': {0: 2021, 1: 2021,  2: 2021,  3: 2020,  4: 2020,  5: 2020,  6: 2020,  7: 2019,  8: 2019,  9: 2019,  10: 2019,  11: 2018,  12: 2018,  13: 2018,  14: 2018,  15: 2017,  16: 2017,  17: 2017,  18: 2017,  19: 2016,  20: 2016,  21: 2016,  22: 2016,  23: 2015,  24: 2015,  25: 2015,  26: 2015,  27: 2014,  28: 2014,  29: 2014,  30: 2014,  31: 2013,  32: 2013,  33: 2013,  34: 2013,  35: 2012,  36: 2012,  37: 2012,  38: 2012,  39: 2011,  40: 2011,  41: 2011,  42: 2011,  43: 2010,  44: 2010,  45: 2010,  46: 2010,  47: 2009,  48: 2009,  49: 2009,  50: 2009,  51: 2008,  52: 2008,  53: 2008,  54: 2008,  55: 2007,  56: 2007,  57: 2007,  58: 2007,  59: 2006,  60: 2006,  61: 2006,  62: 2006,  63: 2005,  64: 2005,  65: 2005,  66: 2005,  67: 2004,  68: 2004,  69: 2004,  70: 2004,  71: 2003,  72: 2003,  73: 2003,  74: 2003,  75: 2002,  76: 2002,  77: 2001,  78: 2001,  79: 2000,  80: 2000,  81: 1999,  82: 1999,  83: 1998,  84: 1998,  85: 1997,  86: 1997,  87: 1996,  88: 1996}, 
                            'trimestre_u_onda': {0: 3,  1: 2,  2: 1,  3: 4,  4: 3,  5: 2,  6: 1,  7: 4,  8: 3,  9: 2,  10: 1,  11: 4,  12: 3,  13: 2,  14: 1,  15: 4,  16: 3,  17: 2,  18: 1,  19: 4,  20: 3,  21: 2,  22: 1,  23: 4,  24: 3,  25: 2,  26: 1,  27: 4,  28: 3,  29: 2,  30: 1,  31: 4,  32: 3,  33: 2,  34: 1,  35: 4,  36: 3,  37: 2,  38: 1,  39: 4,  40: 3,  41: 2,  42: 1,  43: 4,  44: 3,  45: 2,  46: 1,  47: 4,  48: 3,  49: 2,  50: 1,  51: 4,  52: 3,  53: 2,  54: 1,  55: 4,  56: 3,  57: 2,  58: 1,  59: 4,  60: 3,  61: 2,  62: 1,  63: 4,  64: 3,  65: 2,  66: 1,  67: 4,  68: 3,  69: 2,  70: 1,  71: 4,  72: 3,  73: 2,  74: 1,  75: 2,  76: 1,  77: 2,  78: 1,  79: 2,  80: 1,  81: 2,  82: 1,  83: 2,  84: 1,  85: 2,  86: 1,  87: 2,  88: 1}})
    
    # No data:
    df = df[~((df['año'] == 2007) &(df['trimestre_u_onda'] == 3))]
    df = df[~((df['año'] == 2003) &(df['trimestre_u_onda'] == 2))]
    # Cambio para trimestre/onda de 2003:
    df.loc[(df['año'] == 2003) &(df['trimestre_u_onda'] == 1), 'trimestre_u_onda'] = 'O1'
    df.loc[(df['año'] == 2003) &(df['trimestre_u_onda'] == 3), 'trimestre_u_onda'] = 'T3'
    df.loc[(df['año'] == 2003) &(df['trimestre_u_onda'] == 4), 'trimestre_u_onda'] = 'T4'
    if year:
        try:
            df = df[df['año'].between(year[0], year[1])]
        except:
            df = df[df['año'] == year]    
    
    return df
    


def get_microdata(year, trimester_or_wave, type='hogar', advertencias=True, download=False):
    """Genera un DataFrame con los microdatos de la 
    Hasta 2018, usa los datos desde la página de Humai (ihum.ai).
    Desde 2019, los descarga desde la página de INDEC (salvo que cambie el formato del nombre de los archivos y links, debería andar para años posteriores, pero se probó hasta 2021)

    Args:
        @year (int): Año de la EPH
        @trimester_or_wave (int): Trimestre (si año >= 2003) u onda (si año < 2003)
        @type (str, optional): Tipo de base (hogar o individual). Default: 'hogar'.
        @advertencias (bool, optional): Mostrar advertencias metodológicas de INDEC. Defaults to True.
        @download (bool, optional): Descargar los csv de las EPH (en vez de cargarlos directamente a la RAM). Defaults to False.

    Returns:
        pandas.DataFrame: DataFrame con los microdatos de la EPH
    """
    
    from zipfile import ZipFile
    from io import BytesIO
    import os
    import wget
    import fnmatch
    import requests
    import pandas as pd
    
    handle_exceptions_microdata(year, trimester_or_wave, type, advertencias)
    
    if year < 2019:
        if year >= 2003 and trimester_or_wave is not None:
            url = f'https://datasets-humai.s3.amazonaws.com/eph/{type}/base_{type}_{year}T{trimester_or_wave}.csv'
            link = url
        
        elif year < 2003  and trimester_or_wave is not None:
            url = f'https://datasets-humai.s3.amazonaws.com/eph/{type}/base_{type}_{year}O{trimester_or_wave}.csv'
            link = url
        if download:
            filename = url.split('/')[-1]
            
            if os.path.exists(filename):
                os.remove(filename)
                
            filename = wget.download(url)
            df = pd.read_csv(filename, low_memory=False, encoding='unicode_escape')
        else:
            df = pd.read_csv(url, low_memory=False, encoding='unicode_escape')
    elif year >= 2019:
        if trimester_or_wave == 1:
            suffix = 'er' 
        elif trimester_or_wave == 2:
            suffix = 'do'
        elif trimester_or_wave == 3:
            suffix = 'er'
        elif trimester_or_wave == 4:
            suffix = 'to'
            
        try:
            query_str = f"https://www.indec.gob.ar/ftp/cuadros/menusuperior/eph/EPH_usu_{trimester_or_wave}_Trim_{year}_txt.zip"
            print('Descomprimiendo...(si tarda mas de 1 min reintentar, seguramente la página de INDEC esté caída)', end='\r')
            r = requests.get(query_str)
            files = ZipFile(BytesIO(r.content))
            link = query_str
        except:
            try:
                query_str = f'https://www.indec.gob.ar/ftp/cuadros/menusuperior/eph/EPH_usu_{trimester_or_wave}{suffix}_Trim_{year}_txt.zip'
                print('Descomprimiendo...(si tarda mas de 1 min reintentar, seguramente la página de INDEC esté caída)', flush=True, end='\r')
                r = requests.get(query_str)
                files = ZipFile(BytesIO(r.content))
                link = query_str
            except:
                try:
                    query_str = f'https://www.indec.gob.ar/ftp/cuadros/menusuperior/eph/EPH_usu_{trimester_or_wave}{suffix}Trim_{year}_txt.zip'
                    print('Descomprimiendo...(si tarda mas de 1 min reintentar, seguramente la página de INDEC esté caída)', flush=True, sep='', end='\r')
                    r = requests.get(query_str)
                    files = ZipFile(BytesIO(r.content))
                    link = query_str
                except:
                    raise ValueError(f'No se encontró el archivo de microdatos de la EPH para el año {year} y el trimestre {trimester_or_wave}')	
        try:
            df = pd.read_csv(files.open(f"EPH_usu_{trimester_or_wave}{suffix}_Trim_{year}_txt/usu_{type}_T{trimester_or_wave}{str(year)[-2:]}.txt.txt"), delimiter=';')
            print(f'Se descargó la EPH desde {link}')
            return df
        except:
            try:
                for file in files.namelist():
                    if fnmatch.fnmatch(file, f'*{type}*.txt'):
                        df = pd.read_csv(files.open(file), low_memory=False, delimiter=';')
                        print(f'Se descargó la EPH desde {link}')
                        return df
            except:
                raise ValueError('No se encontró el archivo de microdatos en la base de INDEC')
    print(f'Se descargó la EPH desde {link}')
    return df


def handle_exceptions_microdata(year, trimester_or_wave, type, advertencias):
    
    import warnings
    
    if not isinstance(year,int):
        raise YearError("El año tiene que ser un numero")
    
    if not isinstance(trimester_or_wave,int) and not isinstance(trimester_or_wave,int) :
        raise TrimesterError("Debe haber trimestre desde 2003 en adelante (1, 2, 3 o 4) \
                        u onda si es antes de 2003 (1 o 2)")
    
    if (isinstance(trimester_or_wave,int) and trimester_or_wave not in [1,2,3,4]) and (year >= 2003):
        raise TrimesterError("Trimestre/Onda inválido (debe ser entre 1 y 4)")
    
    # if (isinstance(trimester_or_wave,int) and trimester_or_wave not in [1,2]) and (year <= 2003):
    #     raise WaveError("Onda inválida (debe ser 1 o 2)")
    
    if type not in ['individual','hogar']:
        raise TypeError("Seleccione un tipo de base válido: individual u hogar")
    
    if year==2007 and trimester_or_wave==3:
        raise INDECError("\nLa informacion correspondiente al tercer trimestre \
2007 no está disponible ya que los aglomerados Mar del Plata-Batan, \
Bahia Blanca-Cerri y Gran La Plata no fueron relevados por causas \
de orden administrativo, mientras que los datos correspondientes al \
Aglomerado Gran Buenos Aires no fueron relevados por paro del \
personal de la EPH")
        
    if (year == 2015 and trimester_or_wave in [3,4]) |  (year ==2016 and trimester_or_wave==3):
        raise INDECError("En el marco de la emergencia estadistica, el INDEC no publicó la base solicitada. \
                mas información en: https://www.indec.gob.ar/ftp/cuadros/sociedad/anexo_informe_eph_23_08_16.pdf")
    
    if (year == 2003 and trimester_or_wave in [2]):
        raise INDECError('Debido al cambio metodológico en la EPH, en 2003 la encuesta se realizó para el primer semestre y los dos últimos trimestres')
    
    if advertencias:
        if year >= 2007 and year <= 2015:
            warnings.warn('''\n
Las series estadisticas publicadas con posterioridad a enero 2007 y hasta diciembre \
2015 deben ser consideradas con reservas, excepto las que ya hayan sido revisadas en \
2016 y su difusion lo consigne expresamente. El INDEC, en el marco de las atribuciones \
conferidas por los decretos 181/15 y 55/16, dispuso las investigaciones requeridas para \
establecer la regularidad de procedimientos de obtencion de datos, su procesamiento, \
elaboracion de indicadores y difusion.
Más información en: https://www.indec.gob.ar/ftp/cuadros/sociedad/anexo_informe_eph_23_08_16.pdf 
(Se puede desactivar este mensaje con advertencias=False)\n-------------------------------------------------------------------------------------------------'''
, AdvertenciaINDEC, stacklevel=3)
