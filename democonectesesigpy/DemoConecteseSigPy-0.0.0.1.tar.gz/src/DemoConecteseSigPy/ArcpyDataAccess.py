# -*- coding: utf-8 -*-

import os

from arcpy import da
from DemoConecteseSigPy.Utiles import ToolboxLogger
from DemoConecteseSigPy.DataAccess import DataAccess

class ArcpyDataAccess(DataAccess) :
    def __init__(self, ruta_espacio) :
        DataAccess.__init__(self)
        self.ruta_espacio = ruta_espacio

    def _getValue(self, cursor, row, fieldName):
        fields = tuple(f.lower() for f in cursor.fields)
        index = fields.index(fieldName.lower())
        if index > -1:
            return row[index]

    def _setValue(self, cursor, row, fieldName, value):
        fields = tuple(f.lower() for f in cursor.fields)
        index = fields.index(fieldName.lower())
        if index > -1:
            row[index] = value

    def _search_da(self, tabla_origen, campos, filtro=None) :
        ToolboxLogger.debug("--> ArcpyDataAccess._search_da")
        tabla_origen = os.path.join(self.ruta_espacio, tabla_origen)
        try:
            if filtro == None:
                cursor_origen = da.SearchCursor(tabla_origen, campos)
            else:
                cursor_origen = da.SearchCursor(tabla_origen, campos, filtro)

            registros_salida = []
            fields = tuple(f for f in cursor_origen.fields)

            for registro_origen in cursor_origen:
                registro_salida = {}
                for f in cursor_origen.fields:
                    index = fields.index(f)
                    registro_salida[f] = registro_origen[index]
                registros_salida.append(registro_salida)

            return registros_salida
        except Exception as e:
            ToolboxLogger.debug("ERROR: ---->{}".format(e))

    def query(self, table, fields, filter = None) :
        return self._search_da(table, fields, filter)
