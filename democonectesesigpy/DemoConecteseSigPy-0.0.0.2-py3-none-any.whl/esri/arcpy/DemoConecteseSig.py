# -*- coding: utf-8 -*-
r""""""
__all__ = ['ActualizarFechas']
__alias__ = 'DemoConecteseSigPy'
from arcpy.geoprocessing._base import gptooldoc, gp, gp_fixargs
from arcpy.arcobjects.arcobjectconversion import convertArcObjectToPythonObject

# Tools
@gptooldoc('ActualizarFechas_DemoConecteseSigPy', None)
def ActualizarFechas(portal=None, usuario=None, clave=None, servicio=None, tabla=None, campo=None):
    """ActualizarFechas_DemoConecteseSigPy(portal, usuario, clave, servicio, tabla, campo)

     INPUTS:
      portal (Cadena):
          URL del Portal
      usuario (Cadena):
          Usuario
      clave (Cadena de caracteres oculta):
          Clave
      servicio (Cadena):
          Servicio
      tabla (Cadena):
          Tabla
      campo (Cadena):
          Campo"""
    from arcpy.geoprocessing._base import gp, gp_fixargs
    from arcpy.arcobjects.arcobjectconversion import convertArcObjectToPythonObject
    try:
        retval = convertArcObjectToPythonObject(gp.ActualizarFechas_DemoConecteseSigPy(*gp_fixargs((portal, usuario, clave, servicio, tabla, campo), True)))
        return retval
    except Exception as e:
        raise e


# End of generated toolbox code
del gptooldoc, gp, gp_fixargs, convertArcObjectToPythonObject