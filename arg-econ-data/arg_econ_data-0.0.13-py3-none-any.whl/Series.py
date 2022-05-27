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

def get_organizations():
    '''
    Devuelve la lista de ID de organizaciones que tienen datos en el datos.gob.ar/series.
    sspm = Subsecretaría de Programación Macroeconómica
    smn = Servicio Meteorológico Nacional
    '''
    import pandas as pd
    df = pd.read_json('https://apis.datos.gob.ar/series/api/search/catalog_id/')
    return df
    

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
    querys = get_api_call([serie_id], format='csv', **kwargs)
    print(querys)
    df = pd.read_csv(querys)
    return df
