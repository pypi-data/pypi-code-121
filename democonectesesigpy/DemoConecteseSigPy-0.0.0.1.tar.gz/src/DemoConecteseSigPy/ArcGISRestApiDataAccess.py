import requests

from arcgis.gis import GIS

class ArcGISRestApiDataAccess :

    def __init__(self, espacioFuente) :
        self.espacioFuente = espacioFuente

    def __search_da(self, tabla_origen, campos, filtro = None ) :
        outFields = str.join(',', campos)
        if filtro == None  :
            queryString = "outFields={}&where=1%3D1".format(outFields)
        else :
            queryString = "outFields={}&where={}".format(outFields,filtro)

        url = "{}/query?f=json&{}".format(tabla_origen, queryString)

        response = requests.get(url)
        json = response.json()
        features_in = json["features"]
        features = []

        for f in features_in :
            feature = f["attributes"]
            features.append(feature)


        return features

    def query(self, table, fields, filter = None) :
        return self.__search_da(table, fields, filter)

