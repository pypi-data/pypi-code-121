import os
from datetime import datetime
from fileinput import filename

from DemoConecteseSigPy.Utiles import FILE_HANDLER, STREAM_HANDLER, JsonFile, ToolboxLogger
from DemoConecteseSigPy.ArcGISPythonApiDataAccess import ArcGISPythonApiDataAccess

class Procesos :

    @staticmethod 
    def ActualizarFecha(
        portal = None, 
        usuario = None, 
        clave = None, 
        servicio = None, 
        nombreTabla = None,
        campoFecha = None,
        debug = False,
        rutaSalida = '', 
        salidaRelativa = False) :

        LOG_FILE = "__logActualizarFechaVSCode"
        alias = "LogActualizarFechaVSCode"

        folder_path = os.path.dirname(os.path.realpath(__file__))
        log_path = os.path.normpath(os.path.join(folder_path, rutaSalida)) if salidaRelativa else rutaSalida

        ToolboxLogger.initLogger(source=alias, log_path=log_path, log_file=LOG_FILE)
        ToolboxLogger.setDebugLevel() if debug else ToolboxLogger.setInfoLevel()

        ToolboxLogger.info("Iniciando {}".format(alias))
        ToolboxLogger.info("Ruta Salida: {}".format(log_path)) if rutaSalida != '' else None

        gis = ArcGISPythonApiDataAccess.getGIS(portal, usuario, clave)
        fuente_da = ArcGISPythonApiDataAccess(gis)
        fuente_da.setFeatureService(servicio)
        tabla  = fuente_da.getTable(nombreTabla)

        numRegistros = 0

        registros = fuente_da.query(tabla, "*")
        numRegistros += len(registros)

        for reg in registros:
            reg[campoFecha] = datetime.now()
            fuente_da.update(tabla, reg)


        ToolboxLogger.info("Total Actualizados: {}".format(numRegistros))

