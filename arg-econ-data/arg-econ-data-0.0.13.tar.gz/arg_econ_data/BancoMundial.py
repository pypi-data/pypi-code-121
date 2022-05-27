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
    
    
class MicrodataLibrary():
        
    @staticmethod
    def get_collections():
        '''
        Devuelve la lista de colecciones disponibles en la librería de microdatos
        
        '''
        import pandas as pd
        import json
        import requests
        js = requests.get('https://microdata.worldbank.org/index.php/api/catalog/collections').json()
        
        df = pd.DataFrame(data=js['collections'])
        df = df[['id', 'repositoryid', 'title', 'short_text']]
        df = df.sort_values(by=['id'])
        df = df.reset_index(drop=True)
        return df
    
    def search_catalog(keywords, **kwargs):
        '''
        Busca catálogos disponibles en la librería de microdatos.
        
        Args:
            @keywords (str): Palabras clave para la búsqueda. Una o muchas separadas por coma
            
        Kwargs:
            @country (str): Nombre o código de el/los país/es que deben estar incluidos en el estudio (separados por '|', sin espacio)
            @from (int): Año desde el cual comenzó la recolección de datos
            @to (int): Año hasta el cual comenzó la recolección de datos
            @collection (str o list): Coleccion/es en las que buscar (separadas por ',')
            '''
        import pandas as pd
        import json
        import requests
        import urllib.parse
        
        API_BASE_URL = 'https://microdata.worldbank.org/index.php/api/catalog/search'
        query = f'{API_BASE_URL}?sk={keywords}{urllib.parse.urlencode(kwargs)}'
        
        js = requests.get(query).json()
        print(query)
        df = pd.DataFrame(data=js['result']['rows'])
        
        
        return df[['id', 'idno', 'title', 'nation', 'year_start', 'year_end', 'type', 'url', 'authoring_entity', 'repo_title', 'repositoryid', 'form_model']]
            
    