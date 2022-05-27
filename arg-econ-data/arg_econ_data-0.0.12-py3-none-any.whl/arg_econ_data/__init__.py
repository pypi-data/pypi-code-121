from logging import warning


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

class AdvertenciaRegion(Warning):
    pass


class EPH():

    @staticmethod
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
        

    @staticmethod
    def get_microdata(year, trimester_or_wave, type='hogar', advertencias=True, download=False):
        """Genera un DataFrame con los microdatos de la EPH.
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
        
        EPH.handle_exceptions_microdata(year, trimester_or_wave, type, advertencias)
        
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

    @staticmethod
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


class ENGHo():

    @staticmethod
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




    @staticmethod
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
        
        
        year = ENGHo.handle_exceptions_engho(year, type, region)
        
        
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
        
    @staticmethod
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
    
    
eph = EPH
ENGHO = ENGHo
engho = ENGHo



class Series():

    @staticmethod
    def get_metadata(organizacion):
        '''
        Devuelve las series disponibles para descargar de una organización.
        La lista de organizaciones disponibles se puede obtener con el método .get_organizations()
        Args:
            @organizacion (str): id de la organizacion (se pueden consultar con get_organizations())
        Returns:
            @df (pd.DataFrame): DataFrame con las series disponibles de la organizacion
        '''
        
        import pandas as pd
        df = pd.read_csv(f'https://apis.datos.gob.ar/series/api/dump/{organizacion}/series-tiempo-metadatos.csv')
        return df[['serie_id', 'serie_titulo', 'indice_tiempo_frecuencia', 'serie_descripcion', 'serie_unidades', 'serie_indice_inicio', 'serie_indice_final', 'serie_actualizada', 'serie_discontinuada', 'dataset_responsable', 'dataset_fuente']]
    
    @staticmethod
    def get_organizations():
        '''
        Devuelve la lista de ID de organizaciones que tienen datos en el datos.gob.ar/series.
        sspm = Subsecretaría de Programación Macroeconómica
        smn = Servicio Meteorológico Nacional
        '''
        import pandas as pd
        df = pd.read_json('https://apis.datos.gob.ar/series/api/search/catalog_id/')
        return df
        
    
    @staticmethod
    def search(texto, **kwargs):
        '''
        Busca series con el buscador de datos.gob.ar y devuelve un DataFrame con los primeros 10 resultados.
        Equivalente a buscar en https://datos.gob.ar/series/api/search/
        Args:
            @texto (str): texto a buscar (ej. "ipc", "mortalidad infantil", "bcra")
        Kwargs:
            @catalog_id (str): id de la organización (se pueden consultar con get_organizations())
            @limit (int): cantidad de resultados a devolver (máximo 1000)
            @dataset_source (str): fuente de los datos (se pueden consultar en get_sources())
            @units (str): unidad de medida de la serie (se pueden consultar las disponibles en https://apis.datos.gob.ar/series/api/search/field_units/)
            @sort_by (str): puede ser relevance (default), hits_90_days o frequency (periodicidad de la serie)
            '''
        
        
        import requests
        import urllib.parse
        import json
        import pandas as pd
        
        API_BASE_URL = "https://apis.datos.gob.ar/series/api/search/"
        query = "{}?q={}&{}".format(API_BASE_URL, texto, urllib.parse.urlencode(kwargs))
        response = requests.get(query)
        response = json.loads(response.text)
        
        df = pd.json_normalize(response, record_path=['data'], meta_prefix='field')
        return df


    @staticmethod
    def get_sources(organizacion=False):
        '''
        Devuelve las fuentes de los datos provistos por las organizaciones
        Sirve como punto de entrada para la busqueda.
        Args:
            @organizacion (str, optional): id de la organizacion'''
        import pandas as pd
        if organizacion:
            df = pd.read_csv(f'https://apis.datos.gob.ar/series/api/dump/{organizacion}/series-tiempo-fuentes.csv')
        else:
            df = pd.read_csv('https://apis.datos.gob.ar/series/api/dump/series-tiempo-fuentes.csv')
        return df

    @staticmethod
    def get_api_call(ids, **kwargs):
        import urllib.parse
        API_BASE_URL = "https://apis.datos.gob.ar/series/api/"
        try:
            kwargs["ids"] = ",".join(ids)
        except TypeError:
            query = ''
            n = 1
            for id in ids[0]:
                print(id)
                query += id
                n+=1
                if n == len(ids[0]):
                    query += ','
            kwargs['ids'] = query
                
        return "{}{}?{}".format(API_BASE_URL, "series", urllib.parse.urlencode(kwargs))

    @staticmethod
    def get_microdata(serie_id, **kwargs):
        '''
        Obtiene la serie correspondiente a serie_id. 
        Esta id puede buscarse desde Series.search(), Series.metadata() o directamente desde https://datos.gob.ar/series/api/search/.
        Se puede poner una lista con mas de un id y devuelve las series en un único DataFrame.
        Args:
            @serie_id (str o list): id de la serie a buscar o lista con ids
        Kwargs:
            @representation_mode (str): modo de representacion. Puede ser value (absoluto), change (variacion), percent_change (variación porcentual) y percent_change_a_year_ago (variación porcentual interanual)
            @collapse (str): frecuencia de la serie. Puede ser day, week, month, quarter, year. El default es la frecuencia máxima de la serie.
            @collapse_aggregation (str): dato que devuelve al agregar según frecuencia 
        Returns:
            @df (DataFrame): DataFrame con la serie'''
        
        import pandas as pd
        querys = Series.get_api_call([serie_id], format='csv', **kwargs)
        print(querys)
        df = pd.read_csv(querys)
        return df
    
    
series = Series
TimeSeries = Series
SeriesDeTiempo = Series
series_de_tiempo = Series
time_series = Series
timeseries = Series



class BancoMundial():
    
    class Indicadores():
        
        
        @staticmethod
        def get_sources():
            '''
            Devuelve un DataFrame con las fuentes disponibles en la base del BM.
            '''
            import wbgapi as wb
            
            return wb.source.info()
        
        
        @staticmethod
        def get_metadata(source_id=2):
            '''
            Devuelve un DataFrame con las Series disponibles para la fuente indicada. Se pueden consultar las fuentes con get_sources().
            Default: 2 (World Development Indicators)
            '''
            import wbgapi as wb
            wb.db = source_id
            return wb.series.info()
        
        @staticmethod
        def get_microdata(series_id, paises = 'ARG', source_id = 2, **kwargs):
            '''
            Devuelve un DataFrame con los datos de la serie indicada, para los países indicados. 
            Se pueden consultar las series con get_metadata().
            
            Args:
                @series_id (str o list): string o lista de strings con id de series. e.g., 'SP.POP.TOTL' o ['SP.POP.TOTL', 'EG.GDP.PUSE.KO.PP']
                @paises (str o list): string o lista de strings con id (3 letras) de países. Default: 'ARG', e.g., 'ARG' o ['ARG', 'BRA']
                @source_id (int): id de la fuente de datos. Se pueden consultar con get_sources(). Default: 2 (World Development Indicators)
            Kwargs:
                @time (str o range): año (con prefijo 'YR') o rango de años de la serie, e.g., 'YR2015' or range(2010,2020).
                @mrv (int): cantidad de años mas recientes a devolver. e.g. 5 devuelve los últimos 5 años.
                @mrnev (int): cantidad de años mas recientes a devolver, sin contar NaNs. e.g. 5 devuelve los últimos 5 años.
            '''
            import wbgapi as wb
                
            wb.db = source_id
            
            return wb.data.DataFrame(series_id, paises, **kwargs)
        
        
        
        
        
