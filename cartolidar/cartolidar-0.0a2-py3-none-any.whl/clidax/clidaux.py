#!/usr/bin/python
# -*- coding: UTF-8 -*-
'''
Created on 17/05/2017

@author: benmarjo
# -*- coding: latin-1 -*-
'''
from __future__ import division, print_function
from __future__ import unicode_literals

import os
import sys
import time
from datetime import datetime, timedelta
import math
import random
import struct
import platform, subprocess
import inspect
import collections
import types # Ver https://docs.python.org/2/library/types.html
import gc
import shutil
import pathlib
import socket
# Paquetes para progress:
from functools import partial
from collections import deque


# Paquetes de terceros
import psutil
import numpy as np
import numba
import scipy
from _ast import Or
# from scipy.spatial.distance import pdist

try:
    # print(os.path.abspath(os.curdir))
    # print(os.environ['PATH'])
    import gdal, ogr, osr
    gdalOk = True
except:
    # from osgeo import ogr, osr, gdal
    print('clidaux-> Error importando gdal directamente, se intenta from osgeo')
    gdalOk = False

if not gdalOk:
    try:
        from osgeo import gdal
        import ogr
        gdalOk = True
    except:
        gdalOk = False
        print('clidaux-> Error importando gdal from osgeo')
        print('clidaux-> No se ha podido cargar gdal directamente, se intente de la carpeta osgeo')


# ==============================================================================
# ============================== Variables MAIN ================================
# ==============================================================================
# Directorio que depende del entorno:
MAIN_HOME_DIR = str(pathlib.Path.home())
# DIrectorios de la aplicacion:
MAIN_FILE_DIR = os.path.dirname(os.path.abspath(__file__))
# Cuando estoy en un modulo principal (cartolidar.py o cartolider.py):
# MAIN_PROJ_DIR = MAIN_FILE_DIR
# Cuando estoy en un modulo dentro de un paquete (subdirectorio):
MAIN_PROJ_DIR = os.path.abspath(os.path.join(MAIN_FILE_DIR, '..')) # Equivale a MAIN_FILE_DIR = pathlib.Path(__file__).parent
MAIN_RAIZ_DIR = os.path.abspath(os.path.join(MAIN_PROJ_DIR, '..'))
MAIN_MDLS_DIR = os.path.join(MAIN_RAIZ_DIR, 'data')
# Directorio desde el que se lanza la app (estos dos coinciden):
MAIN_BASE_DIR = os.path.abspath('.')
MAIN_THIS_DIR = os.getcwd()
# ==============================================================================
# Unidad de disco si MAIN_ENTORNO = 'windows'
MAIN_DRIVE = os.path.splitdrive(MAIN_FILE_DIR)[0]  # 'D:' o 'C:'
# ==============================================================================
if MAIN_FILE_DIR[:12] == '/LUSTRE/HOME':
    MAIN_ENTORNO = 'calendula'
    MAIN_PC = 'calendula'
elif MAIN_FILE_DIR[:8] == '/content':
    MAIN_ENTORNO = 'colab'
    MAIN_PC = 'colab'
else:
    MAIN_ENTORNO = 'windows'
    try:
        if MAIN_DRIVE[0] == 'D':
            MAIN_PC = 'Casa'
        else:
            MAIN_PC = 'JCyL'
    except:
        MAIN_ENTORNO = 'calendula'
        MAIN_PC = 'calendula'
# ==============================================================================


# ==============================================================================
def showCallingModules(inspect_stack=inspect.stack(), verbose=True):
    # print('->->->inspect_stack  ', inspect_stack
    # print('->->->inspect.stack()', inspect.stack())
    if len(inspect_stack) > 1:
        try:
            esteModuloFile0 = inspect_stack[0][1]
            esteModuloNum0 = inspect_stack[0][2]
            esteModuloFile1 = inspect_stack[1][1]
            esteModuloNum1 = inspect_stack[1][2]
            esteModuloName0 = inspect.getmodulename(esteModuloFile0)
            esteModuloName1 = inspect.getmodulename(esteModuloFile1)
        except:
            print('\tclidaux-> Error identificando el modulo 1')
            return 'desconocido1', 'desconocido1'
    else:
        print('\tclidaux-> No hay modulos que identificar')
        return 'desconocido2', 'desconocido2'

    if not esteModuloName0 is None:
        esteModuloName = esteModuloName0
        esteModuloNum = esteModuloNum0
        stackSiguiente = 1
    else:
        esteModuloName = esteModuloName1
        esteModuloNum = esteModuloNum1
        stackSiguiente = 2

    callingModulePrevio = ''
    callingModuleInicial = ''
    if verbose:
        print('\tclidaux-> El modulo {} ({}) ha sido'.format(esteModuloName, esteModuloNum), end=' ')
    for llamada in inspect_stack[stackSiguiente:]:
        if 'cartolid' in llamada[1] or 'clid' in llamada[1] or 'qlid' in llamada[1]:
            callingModule = inspect.getmodulename(llamada[1])
            if callingModule != esteModuloName and callingModulePrevio == '':
                callingModulePrevio = callingModule
            callingModuleInicial = callingModule
            # if callingModule != 'clidaux' and callingModule != 'callingModule':
                # print('clidaux-> llamado por', llamada[1:3], end=' ')
            if verbose:
                print('importado desde: {} ({})'.format(callingModule, llamada[2]), end='; ')
    print()
    return callingModulePrevio, callingModuleInicial
# ==============================================================================

CONFIGverbose = False
if CONFIGverbose:
    print('clidaux-> Directorio desde el que se lanza la aplicacion-> os.getcwd():', os.getcwd())
    print('clidaux-> Cargando clidaux; reviso la pila de llamadas')
callingModulePrevio, callingModuleInicial = showCallingModules(inspect_stack=inspect.stack(), verbose=CONFIGverbose)
if CONFIGverbose:
    print('clidaux-> Pila de llamadas revisada-> callingModulePrevio:', callingModulePrevio, 'callingModuleInicial:', callingModuleInicial)

# print('\nclidaux-> Cargando clidaux desde callingModuleInicial:', callingModuleInicial)

# ==============================================================================
if (
    callingModuleInicial == 'generax'
    or os.getcwd().endswith('gens')
    or callingModuleInicial == 'qlidtwins' or callingModuleInicial == 'clidtwins'
    or callingModuleInicial == 'qlidmerge' or callingModuleInicial == 'clidmerge'
    or callingModuleInicial == 'cartolidar'
    or callingModuleInicial == 'runpy'
    or callingModuleInicial == '__init__'
    # or callingModuleInicial != 'clidtools'
):

    class Object(object):
        pass

    GLO = Object()
    GLO.MAINidProceso = 0
    GLO.GLBLficheroLasTemporal = ''
    GLO.GLBLverbose = True
    if GLO.GLBLverbose > 2:
        print(f'clidaux-> Modulo importado desde la ruta: {os.getcwd()} -> Modulo: {callingModuleInicial}')
        print('\t-> No se cargan las variables globales')

else:
    if __name__ == '__main__': # callingModuleInicial != 'clidaux'
        print('clidaux-> Modulo cargado directamente. os.getcwd():', os.getcwd(), time.asctime(time.localtime(time.time())))
        MAINidProceso = random.randint(1, 999998)
        sys.argv.append('idProceso')
        sys.argv.append(MAINidProceso)
        print('\t-> Se asigna idProceso: {} = {}'.format(MAINidProceso, sys.argv[-1]))
#         try:
        if True:
            # https://stackoverflow.com/questions/61234609/how-to-import-python-package-from-another-directory
            # https://realpython.com/python-import/
            # https://blog.ionelmc.ro/2014/05/25/python-packaging/
            # print('clidaux-> Pre sys.path:  {}'.format(sys.path))
            path = str(pathlib.Path(pathlib.Path(__file__).parent.absolute()).parent.absolute())
            # print('clidaux-> Incluyo el dir padre1 de este modulo en el path: {}'.format(os.path.abspath(path)))
            sys.path.insert(0, path)
            # Esto equivale a lo anterior:
            # print('clidaux-> Incluyo el dir padre2 de este modulo en el path: {}'.format(os.path.abspath('..')))
            # sys.path.insert(0, '..')
            # print('clidaux-> Post sys.path: {}'.format(sys.path))
            from clidax import clidconfig # No necesita ningun otro modulo de cartolid
            # print('clidaux-> clidconfig import ok')
            # from clidml import clidmachine # Necesita: clidconfig
            # print('clidaux-> clidmachine import ok')
            from clidio import clidhead # Necesita clidconfig, clidnaux, (clidndat si uso infoLasPoints<>)
            # print('clidaux-> clidhead import ok')
            from clidio import clidlax # Necesita clidconfig, clidnaux, clidhead, clidpoint (a su vez necesita clidconfig) 
            # print('clidaux-> clidlax import ok')
            # Modulos que se cargan con clidaux (directa o indirectamente): clidconfig, clidlax, clidnaux, clidhead, clidpoint (clidndat si uso infoLasPoints<>)
            # clidlax y clidnaux (si verbse) importan clidaux
            # print('clidaux-> clidconfig, clidmachine, clidhead & clidlax importados ok directamente desde clidaux')
            print('clidaux-> clidconfig, clidhead & clidlax importados ok directamente desde clidaux')
            print('\t-> clidnaux, clidpoint & clidndat importados ok desde modulos importados por clidaux')
#         except:
#             print('clidaux-> Error al importar modulos de otro subpackage. Se intenta con rutas referidas al directorio desde el que se ejecuta la app')
#             # Esta opcion es peor porque depende del directorio desde el que se llama a clidaux.py
#             print('clidaux-> Antes he incluido el dir padre1 de este modulo en el path:  {}'.format(os.path.abspath(path)))
#             print('clidaux-> Ahora incluyo el dir padre2 (..) de este modulo en el path: {}'.format(os.path.abspath('..')))
#             print('clidaux-> Tb incluyo este dir (./cartolid/clidax) en el path:         {}'.format(os.path.abspath('./cartolid/clidax')))
#             print('clidaux-> Post1 sys.path (antes): {}'.format(sys.path))
#             sys.path.insert(0, os.path.abspath('..'))
#             sys.path.insert(0, os.path.abspath('./cartolid/clidax'))
#             print('clidaux-> Post2 sys.path (ahora): {}'.format(sys.path))
#             from clidax import clidconfig # No necesita ningun otro modulo de cartolid
#             from clidml import clidmachine # Necesita: clidconfig
#             from clidio import clidhead # Necesita clidconfig, clidnaux, (clidndat si uso infoLasPoints<>)
#             from clidio import clidlax # Necesita clidconfig, clidnaux, clidhead, clidpoint (a su vez necesita clidconfig) 
#             # Modulos que se cargan con clidaux (directa o indirectamente): clidconfig, clidhead, clidlax, clidnaux, clidpoint (clidndat si uso infoLasPoints<>)
#             # clidlax y clidnaux (si verbse) importan clidaux

        # ==============================================================================
        MAINusuario = clidconfig.infoUsuario(False)
        # ==============================================================================
        nuevosParametroConfiguracion = {}
        #nuevosParametroConfiguracion['MAINversionLidas'] = [__version__, 'GrupoMAIN', '', 'str']
        nuevosParametroConfiguracion['MAINcopyright'] = ['2016-2021', 'GrupoMAIN', '', 'str']
        nuevosParametroConfiguracion['MAINusuario'] = [MAINusuario, 'GrupoMAIN', '', 'str']
        nuevosParametroConfiguracion['MAINmiRutaProyecto'] = [MAIN_PROJ_DIR, 'GrupoMAIN', '', 'str']
        nuevosParametroConfiguracion['MAINmiRutaRaiz'] = [MAIN_RAIZ_DIR, 'GrupoMAIN', '', 'str']
        nuevosParametroConfiguracion['MAINidProceso'] = [MAINidProceso, 'GrupoMAIN', '', 'str']
        nuevosParametroConfiguracion['MAIN_ENTORNO'] = [MAIN_ENTORNO, 'GrupoMAIN', '', 'str']
        nuevosParametroConfiguracion['MAIN_PC'] = [MAIN_PC, 'GrupoMAIN', '', 'str']
        nuevosParametroConfiguracion['MAIN_DRIVE'] = [MAIN_DRIVE, 'GrupoDirsFiles', '', 'str']
        nuevosParametroConfiguracion['MAIN_HOME_DIR'] = [MAIN_HOME_DIR, 'GrupoDirsFiles', '', 'str']
        nuevosParametroConfiguracion['MAIN_FILE_DIR'] = [MAIN_FILE_DIR, 'GrupoDirsFiles', '', 'str']
        nuevosParametroConfiguracion['MAIN_PROJ_DIR'] = [MAIN_PROJ_DIR, 'GrupoDirsFiles', '', 'str']
        nuevosParametroConfiguracion['MAIN_RAIZ_DIR'] = [MAIN_RAIZ_DIR, 'GrupoDirsFiles', '', 'str']
        nuevosParametroConfiguracion['MAIN_MDLS_DIR'] = [MAIN_MDLS_DIR, 'GrupoDirsFiles', '', 'str']
        nuevosParametroConfiguracion['MAIN_BASE_DIR'] = [MAIN_BASE_DIR, 'GrupoDirsFiles', '', 'str']
        nuevosParametroConfiguracion['MAIN_THIS_DIR'] = [MAIN_THIS_DIR, 'GrupoDirsFiles', '', 'str']

    else:
        MAINidProceso = sys.argv[-1]
        nuevosParametroConfiguracion = {}
        if callingModuleInicial != 'clidaux' and callingModuleInicial != 'clidtools' and callingModuleInicial != '__main__':
            if CONFIGverbose or True:
                print(f'clidaux-> Importando clidconfig desde clidaux, a su vez importado desde {callingModulePrevio} (modulo inicial: {callingModuleInicial})')
            try:
                import clidconfig
            except:
                from clidax import clidconfig
            # print('clidaux-> Ok clidmachine importado desde clidaux')
        elif callingModuleInicial == '__main__':
            try:
                from cartolidar.clidax import clidconfig
            except:
                from clidax import clidconfig
        else:
            try:
                from clidax import clidconfig
            except:
                import clidconfig
    # ==============================================================================


    if __name__ == '__main__' or (callingModuleInicial != 'clidaux' and callingModuleInicial != 'clidtools'):
        if CONFIGverbose:
            print('clidaux-> A Llamo a clidconfig.leerCambiarVariablesGlobales<> (con o sin nuevosParametroConfiguracion) para leer los parametros de configuracion del fichero cfg')
        GLOBALconfigDict = clidconfig.leerCambiarVariablesGlobales(
            nuevosParametroConfiguracion,
            idProceso=MAINidProceso,
            inspect_stack=inspect.stack(),
            verbose=CONFIGverbose,
        )
        if CONFIGverbose:
            print('clidaux-> B Cargando parametros de configuracion en GLO configVarsDict["GLBLverbose"]:', GLOBALconfigDict["GLBLverbose"])
        GLO = clidconfig.VariablesGlobales(GLOBALconfigDict)
        if CONFIGverbose:
            print('clidaux-> C ok. GLO.GLBLverbose:', GLO.GLBLverbose,)
        GLO.MAINidProceso = MAINidProceso


if callingModuleInicial == 'cartolider':
    printMsgToFile = False
else:
    printMsgToFile = True


# print('\nclidaux-> cargando clidaux. GLO:', GLO)
# ==============================================================================
# Dejo esto por si quiero ver como funciona la pila de llamadas segun desde donde se cargue este modulo
if False:
    mostrarModuloInicial = True
    mostrarPilaDeLlamadas = False
    if mostrarModuloInicial:
        import inspect
        callingModuleActual = inspect.getmodulename(inspect.stack()[0][1])
        try:
            if len(inspect.stack()) > 1:
                callingModuleInicial = inspect.getmodulename(inspect.stack()[-1][1])
                callingModulePrevio = 'desconocido'
                for nOrden, llamada in enumerate(inspect.stack()[1:]):
                    #print('\t->', nOrden, llamada[1])
                    if not llamada[1].startswith('<frozen'):
                        callingModulePrevio = inspect.getmodulename(llamada[1])
                        break
            else:
                callingModuleInicial = callingModuleActual
                callingModulePrevio = 'Modulo no importado desde otro modulo'
        except:
            callingModuleInicial = 'Desconocido'
            callingModulePrevio = 'Desconocido'
        print('clidaux-> Este modulo:                   ', callingModuleActual)
        print('clidaux-> Modulo desde el que se importa:', callingModulePrevio)
        print('clidaux-> Modulo ejecutado inicialmente: ', callingModuleInicial)
    if mostrarPilaDeLlamadas:
        print('clidaux-> Secuencia de llamadas:')
        for nOrden, llamada in enumerate(inspect.stack()):
            if not llamada[1].startswith('<frozen'):
                print('\t->', nOrden, llamada[1])
            if 'cartolid' in llamada[1]:
                callerFile = inspect.getmodulename(llamada[1])
                if callerFile != 'callingModule':
                    # print('llamado por', llamada[1:3], end=' ')
                    print('\t\t-> called from: %s (%i)' % (callerFile, llamada[2]))


# ==============================================================================
# Dejo esto por si quiero ver como funciona la pila de llamadas segun desde donde se cargue este modulo
if False:
    mostrarModuloInicial = True
    mostrarPilaDeLlamadas = False
    if mostrarModuloInicial:
        # import inspect
        if len(inspect.stack()) > 1:
            try:
                callingModuleActual = inspect.getmodulename(inspect.stack()[0][1])
                callingModuleInicial = inspect.getmodulename(inspect.stack()[-1][1])
                callingModulePrevio = 'desconocido'
                for nOrden, llamada in enumerate(inspect.stack()[1:]):
                    #print('\t->', nOrden, llamada[1])
                    if not llamada[1].startswith('<frozen'):
                        callingModulePrevio = inspect.getmodulename(llamada[1])
                        break
            except:
                print('Error al identificar el modulo')
        else:
            callingModuleActual = 'Este modulo'
            callingModuleInicial = 'Este modulo'
            callingModulePrevio = 'Modulo no importado desde otro modulo'
        print('clidaux-> Este modulo:                   ', callingModuleActual)
        print('clidaux-> Modulo desde el que se importa:', callingModulePrevio)
        print('clidaux-> Modulo ejecutado inicialmente: ', callingModuleInicial)
    if mostrarPilaDeLlamadas:
        print('clidaux-> Secuencia de llamadas:')
        for nOrden, llamada in enumerate(inspect.stack()):
            if not llamada[1].startswith('<frozen'):
                print('\t->', nOrden, llamada[1])
            if 'cartolid' in llamada[1]:
                callerFile = inspect.getmodulename(llamada[1])
                if callerFile != 'callingModule':
                    # print('llamado por', llamada[1:3], end=' ')
                    print('\t\t-> called from: %s (%i)' % (callerFile, llamada[2]))
else:
    callingModuleInicial = 'sinUso'
# ==============================================================================

# ==============================================================================
# print('os.getcwd():', os.getcwd())
if __name__ == '__main__':

    # ==============================================================================
    if MAIN_ENTORNO != 'calendula':
        # En casa tengo graphviz en esta ruta y necesito incluirla en el path
        rutaGraphviz = MAIN_DRIVE + '/_App/Graphviz/bin/'
        os.environ["PATH"] += os.pathsep + rutaGraphviz
        # En JCyL esto no es necesario porque graphiz lo tengo instalado desde anaconda
    # ==============================================================================
    # Con esta opcion elijo a donde se dirije la salida de matplotlib (backend):
    # Ver uso de los posibles backends en: https://matplotlib.org/3.3.3/api/matplotlib_configuration_api.html
    #  ->non-interactive backends: agg, cairo, pdf, pgf, ps, svg, template
    #  ->interactive backends: GTK3Agg, GTK3Cairo, MacOSX, nbAgg, Qt4Agg, Qt4Cairo, Qt5Agg, Qt5Cairo, TkAgg, TkCairo, WebAgg, WX, WXAgg, WXCairo
    # Ver detalles sobre los backends en: https://matplotlib.org/3.3.3/tutorials/introductory/usage.html#backends
    # Por ejemplo: -AGG     png     raster graphics -- high quality images using the Anti-Grain Geometry engine
    # Use non-interactive mode in scripts in which you want to generate one or more figures and display them before ending or generating a new set of figures. In that case, use show() to display the figure(s) and to block execution until you have manually destroyed them
    # ==============================================================================



# ooooooooooooooooooo Utilizacion de liblas (obsoleto) oooooooooooooooooooooooooo
'''
usar_liblas = False
if usar_liblas:
    #Para usar liblas hay que tener algunas variables de entorno apuntando a C:/OSGeo4W o C:/OSGeo4W64
    #Yo creo que la version de OSGeo4W debe ser la de 32 bits (no la de 64 bits)
    #Esto se puede hacer en un .bat:
    #    SET OSGEO4W_ROOT=C:/OSGeo4W
    #    SET GDAL_DATA=%OSGEO4W_ROOT%/share/gdal
    #    SET PROJ_LIB=%OSGEO4W_ROOT%/share/proj
    #    SET PYTHONPATH=%OSGEO4W_ROOT%/pymod;%PYTHONPATH%
    try:
        #import liblas
        from liblas import file as lasfile
        from liblas import header
        #from liblas import point
        importLiblas = True
        print( 'import liblas: Ok' )
    except:
        importLiblas = False
        print( 'import liblas: Error. liblas no disponible' )
else:
    importLiblas = False
if importLiblas:
    if usar_liblas:
        print( 'Libreria liblas no disponible. Procesar sin unsar esta libreria' )
        #quit()
        sys.exit()
else:
    #Clase ficticia (emula a la lasfile pero sin respuesta). Solo para que el eclipse no marque errores.
    class lasfile():
        def __init__(self):
            self.header =    None
            self.point =    None
        def File(self, outfile, mode='w', header='None'):
            pass
'''


# ==============================================================================o
def infoUsuario(verbose):
    try:
        USERusuario = psutil.users()[0].name
        if verbose:
            print('clidaux-> Usuario:', USERusuario)
    except:
        USERusuario = psutil.users()
        if verbose:
            print('clidaux-> Users:', USERusuario)
    if not isinstance(USERusuario, str) or USERusuario == '':
        USERusuario = 'PC1'
    return USERusuario


# ==============================================================================o
def mostrarVersionesDePythonEnElRegistro(verbose):
    import pytz

    epoch = datetime(1601, 1, 1, tzinfo=pytz.utc)
    # Ver: https://docs.python.org/2/library/winreg.html
    if sys.version_info[0] == 2:
        print('Consultando versiones de python en el registro (Python2)')
        import _winreg as winreg
    else:
        print('Consultando versiones de python en el registro (Python3)')
        import winreg

    # key = "HKEY_CURRENT_USER/Environment"
    keys = [winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER]
    for key1 in keys:
        key2 = winreg.OpenKey(key1, 'SOFTWARE')
        try:
            key3 = winreg.OpenKey(key2, 'Python')
        except:
            print('El registro no tiene la clave SOFTWARE/Python/PythonCore')

        key4txts = ['ContinuumAnalytics', 'PythonCore']
        for key4txt in key4txts:
            try:
                key4 = winreg.OpenKey(key3, key4txt)
                infoKey4 = winreg.QueryInfoKey(key4)
                print('Clave: HKEY_LOCAL_MACHINE.SOFTWARE.Python.' + key4txt)
                for indexValue4 in range(infoKey4[1]):
                    print('\tValor', indexValue4, winreg.EnumValue(key4, indexValue4))
                if infoKey4[0] > 0:
                    print('Versiones de python:')
                for indexKey4 in range(infoKey4[0]):
                    sub_key4 = winreg.EnumKey(key4, indexKey4)
                    key5 = winreg.OpenKey(key4, sub_key4)
                    infoKey5 = winreg.QueryInfoKey(key5)
                    installdatetime = epoch + timedelta(microseconds=infoKey5[2] / 10)
                    print('Version:', indexKey4, sub_key4, 'Instalado:', installdatetime, '->Claves:', infoKey5[0], 'Valores:', infoKey5[1])
                    if verbose:
                        if infoKey5[1] != 0:
                            for indexValue5 in range(infoKey5[1]):
                                print('\tValor', indexValue5, winreg.EnumValue(key5, indexValue5))
                        for indexKey5 in range(infoKey5[0]):
                            sub_key5 = winreg.EnumKey(key5, indexKey5)
                            key6 = winreg.OpenKey(key5, sub_key5)
                            infoKey6 = winreg.QueryInfoKey(key6)
                            installdatetime = epoch + timedelta(microseconds=infoKey6[2] / 10)
                            print('\tClave', indexKey5, sub_key5, 'Instalado:', installdatetime, '->Claves:', infoKey6[0], 'Valores:', infoKey6[1])
                            if infoKey6[1] >= 1:
                                for indexValue6 in range(infoKey6[1]):
                                    print('\t\tValor', indexValue6, winreg.EnumValue(key6, indexValue6))
                            if infoKey6[0] != 0:
                                for indexKey6 in range(infoKey6[0]):
                                    sub_key6 = winreg.EnumKey(key6, indexKey6)
                                    key7 = winreg.OpenKey(key6, sub_key6)
                                    infoKey7 = winreg.QueryInfoKey(key7)
                                    installdatetime = epoch + timedelta(microseconds=infoKey7[2] / 10)
                                    print('\t\tClave', indexKey6, sub_key6, 'Instalado:', installdatetime, '->Claves:', infoKey7[0], 'Valores:', infoKey7[1])

                                    if infoKey7[1] >= 1:
                                        for indexValue7 in range(infoKey7[1]):
                                            print('\t\t\tValor', indexValue7, winreg.EnumValue(key7, indexValue7))

            except:
                print('No hay', key4txt, 'en HKEY_LOCAL_MACHINE.SOFTWARE.Python')



# ==============================================================================o
def memoriaRam(marcador='-', verbose=True, swap=False, sangrado=''):
    ramMem = psutil.virtual_memory()
    if verbose:
        if marcador == '-':
            print(
                '%sTotal RAM: %0.2f Gb; usada: %0.2f Gb; disponible: %0.2f Gb'
                % (sangrado, ramMem.total / 1e9, ramMem.used / 1e9, ramMem.available / 1e9)
            )
        else:
            print(
                '%sTotal RAM (%s): %0.2f Gb; usada: %0.2f Gb; disponible: %0.2f Gb'
                % (sangrado, str(marcador), ramMem.total / 1e9, ramMem.used / 1e9, ramMem.available / 1e9)
            )
    if swap:
        swapMem = psutil.swap_memory()
        if verbose:
            print('Total SWAP memory: %0.2f Gb; usada: %0.2f Gb; disponible: %0.2f Gb' % (swapMem.total / 1e9, swapMem.used / 1e9, swapMem.free / 1e9))
    else:
        swapMem = None
    return ramMem, swapMem


# ==============================================================================o
def infoPC(verbosePlus=False):
    print('\n{:_^80}'.format(''))
    print('Sistema operativo:')
    print('  OS:      ', platform.system())
    print('  Version: ', platform.release())
    print('IP local:', socket.gethostbyname(socket.gethostname()))

    print('\nHardware:')
    print('  CPU totales %i (fisicas: %i)' % (psutil.cpu_count(), psutil.cpu_count(logical=False)))
    # print( 'CPU times - interrupt:', psutil.cpu_times(percpu=False) )
    # print( 'CPU times - interrupt:', psutil.cpu_times(percpu=True) )
    # print( 'CPU statistics:', psutil.cpu_stats() )
    # print( 'Addresses associated to each NIC (network interface card):' )
    # print( 'Ethernet', psutil.net_if_addrs()['Ethernet'] )
    # print( 'Wi-Fi', psutil.net_if_addrs()['Wi-Fi'] )
    # print( 'Conexion de area local* 11', psutil.net_if_addrs()['Conexi\xf3n de \xe1rea local* 11'] )

    # print( 'Procesos en ejecucion:' )
    # for proc in psutil.process_iter():
    #     try:
    #         pinfo = proc.as_dict(attrs=['pid', 'name'])
    #     except psutil.NoSuchProcess:
    #         pass
    #     else:
    #         print(pinfo)
    # import datetime
    # print( 'FechaHora de inicio:', datetime.datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S") )
    print('  Procesador:', platform.processor())
    info = 'No info'
    try:
        info = subprocess.check_output(["wmic", "cpu", "get", "name"])
        info = info.decode('utf-8')
        print('  Version:    %s' % info.split('Name')[1].split('@')[0].lstrip().replace('\r', '').replace('\n', ''))
        print('  Velocidad:  %s' % info.split('@')[1].replace(' ', '').replace('\r', '').replace('\n', ''))
    except:
        print('  subprocess->', info, '<-')

    print('\nMemoria RAM:')
    proc = psutil.Process(os.getpid())
    memoria = proc.memory_info().rss / 1e6
    print('  Memoria utilizada en este proceso (inicial) {:5.1f} [Mb]'.format(memoria))
    memoriaRam(sangrado='  ')
    if verbosePlus:
        print(' ', proc.memory_info())
    print('{:=^80}'.format(''))

    # import np.distutils.cpuinfo as cpuinfo
    # print( '1.', dir(cpuinfo) )
    # print( 'Procesador de 64 bits:', cpuinfo.CPUInfoBase()._is_64bit() )
    # print( 'Procesador de 32 bits:', cpuinfo.CPUInfoBase()._is_32bit() )
    # print( '3.', cpuinfo.Win32CPUInfo().info )
    # for inf in cpuinfo.Win32CPUInfo().info:
    #    print( inf )
    # print( '4.', cpuinfo.cpuinfo().info )
    # print( '5.', dir(cpuinfo.os) )
    # print( '5.', cpuinfo.os.path )
    # print( '5.', cpuinfo.os.system )
    # print( '6.', dir(cpuinfo.platform) )
    # print( '6.', cpuinfo.platform.version )
    # print( '7.', dir(cpuinfo.sys) )
    # print( '8.', cpuinfo.sys.version )

    if verbosePlus:
        try:
            # print( 'Usuario principal:', psutil.users()[0] )
            print('clidaux-> Nombre de usuario:', psutil.users()[0].name)
            print('  Info usuarios:', psutil.users())
            # print( type(psutil.users()[0]), dir(psutil.users()[0]) )
        except:
            print('clidaux-> Nombre de usuario:', psutil.users())



# ==============================================================================o
def mostrarEntornoDeTrabajo(verbosePlus=False):
    print('\n{:_^80}'.format(''))
    print('clidaux-> Info sobre Python:')
    print('\t-> Version:      %i.%i' % (sys.version_info[0], sys.version_info[1]))
    print('\t-> Ruta python:  %s' % sys.prefix)
    EXEC_DIR = os.path.dirname(os.path.abspath(sys.executable))
    print('\t-> Ruta binario: %s' % EXEC_DIR)
    print('\t-> Ejecutable:   %s' % sys.executable)

    if sys.version_info[0] == 2:
        pass
        # maximoEntero = sys.maxint
        # numBits = int( math.log(maximoEntero, 2) ) + 2
        # print( '\tNum bits (in python): %i (Max int: %i)' % (numBits, maximoEntero))
    else:
        # Esto solo funciona con python3
        numBits = int(math.log(sys.maxsize, 2)) + 1
        print('  Num bits:     %i (Max int: %i)' % (numBits, sys.maxsize))
        # python3 no tiene una maximo para los enteros
        # Ver: http://docs.python.org/3.1/whatsnew/3.0.html#integers
        # Ver: https://stackoverflow.com/questions/13795758/what-is-sys-maxint-in-python-3
    # Tres formas de leeer una variable de entorno
    # print('  PYTHONHOME (1) ->', os.environ.get('PYTHONHOME'))  # Si no existe devuelve None
    # print('  PYTHONHOME (2) ->', os.getenv('PYTHONHOME', 'PYTHONHOME Sin definir'))
    try:
        print('  PYTHONHOME:  ', os.environ['PYTHONHOME'])
    except:
        print('  PYTHONHOME:   no definida')
    try:
        print('  PYTHONPATH:  ', os.environ['PYTHONPATH'])
    except:
        print('  PYTHONPATH:   no definida')

    print('\nclidaux-> Versiones de algunos paquetes:')
    print('  Version de python:    ', platform.python_version())
    print('  Version de numpy:     ', np.__version__) # <=> np.version.version
    print('  Version de scipy:     ', scipy.__version__) # <=> scipy.version.version
    print('  Version de Numba:     ', numba.__version__)
    print('  Version de gdal:      ', gdal.VersionInfo())
    try:
        import pyproj
        print('  Version de pyproj:    ', pyproj.__version__)
        print('  Version de PROJ:      ', pyproj.__proj_version__)
        if verbosePlus:
            print('\nclidaux-> Mostrando info de pyproj:')
            print(pyproj.show_versions())
    except:
        print('  pyproj no disponible')
    print('{:=^80}'.format(''))


# ==============================================================================o
def mostrar_directorios():
    print('\n{:_^80}'.format(''))
    print('clidaux-> Modulos y directorios de la aplicacion:')
    print('\t-> Modulos de la aplicacion:')
    print('\t\t-> Modulo principal (sys.argv[0]) {}'.format(sys.argv[0]))
    print('\t\t-> Este modulo  (__file__):       {}'.format(__file__)) # MAIN_FILE_DIR
    print('\t-> Directorios de la aplicacion:')
    print('\t\t-> Proyecto     (MAIN_PROJ_DIR):  {}'.format(MAIN_PROJ_DIR))
    print('\t\t-> Raiz         (MAIN_RAIZ_DIR):  {}'.format(MAIN_RAIZ_DIR))
    print('\t-> Directorio desde el que se llama a la aplicacion:')
    print('\t\t-> Lanzadera    (MAIN_BASE_DIR):  {}'.format(MAIN_BASE_DIR))
    print('\t\t-> Actual       (MAIN_THIS_DIR):  {}'.format(MAIN_THIS_DIR))
    print('\t-> Directorio del usuario:')
    print('\t\t-> User-home    (MAIN_HOME_DIR):  {}'.format(MAIN_HOME_DIR))
    if len(sys.argv) > 3:
        print('\t-> Argumentos en linea de comandos:')
        print('\t\t-> Args: {}'.format(sys.argv[3:]))
    print('{:=^80}'.format(''))



# ==============================================================================o
def buscarDirectorioDeTrabajo():
    MAIN_FILE_DIR = os.path.dirname(os.path.abspath(__file__))
    directorioActual = os.path.abspath(os.path.join(MAIN_FILE_DIR, '..'))  # Equivale a MAIN_FILE_DIR = pathlib.Path(__file__).parent
    filenameAPP = os.path.join(directorioActual, 'cartolidar.py')
    if os.path.exists(filenameAPP):
        directorioDeTrabajo = directorioActual
    else:
        directorioPadre = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
        # directorioPadre = quitarContrabarrasAgregarBarraFinal(directorioPadre)
        directorioPadre = (directorioPadre).replace(os.sep, '/')

        filenameAPP = os.path.join(directorioPadre, 'cartolidar.py')
        if os.path.exists(filenameAPP):
            directorioDeTrabajo = directorioPadre
        else:
            directorioDeTrabajo = MAIN_FILE_DIR
    return directorioDeTrabajo


# ==============================================================================o


# ==============================================================================o
# ooooooooooooooooooooooooo Librerias para los ajustes oooooooooooooooooooooooooo
try:
    if GLO.GLBLusarSklearn:
        print('Importando sklearn')
        from sklearn import linear_model

        # from sklearn.metrics import mean_squared_error
        print('sklearn importado')
    else:

        class linear_model:
            def __init__(self):
                pass

            def LinearRegression(self):
                return None

        # def mean_squared_error(array1, array2):
        #    return 0
    # ==============================================================================o
    if GLO.GLBLusarSklearn:
        clf = linear_model.LinearRegression()
    else:
        clf = None
    if GLO.GLBLusarStatsmodels:
        print('Importando statsmodel.api')
        # import statsmodels.api as sm
        print('statsmodel importado')
    else:
        class Foo:
            def __init__(self):
                pass
            def fit(self):
                return None
        class sm:
            def __init__(self):
                pass
            def OLS(self, endog=None, exog=None):
                foo = Foo()
                return foo


except:
    pass
# ==============================================================================o
# El paquete scikit me da problemas para empaquetarlo con pyinstaller
# No se compila bien con numba
# ==============================================================================o
def ajustarPlanoSinNumba(listaCoordenadas, nX, nY):
    nPtosAjuste = len(listaCoordenadas)
    if nPtosAjuste < 3:
        return [0, 0, 0, -1]
    z_true = listaCoordenadas[:, 2]
    if GLO.GLBLusarSklearn:
        x_y_values = listaCoordenadas[:, 0:2]
        clf.fit(x_y_values, z_true)
        z_est = clf.intercept_ + (clf.coef_[0] * x_y_values[:, 0]) + (clf.coef_[1] * x_y_values[:, 1])
        print('-->z_est:', z_est)
        # mse = ( ((mean_squared_error(z_true, z_est))**0.5) *
        #                nPtosAjuste / (nPtosAjuste-1) )
        mse = (((np.square(z_true - z_est)).mean(axis=0)) ** 0.5) * nPtosAjuste / (nPtosAjuste - 1)
        coeficientes = [clf.intercept_, clf.coef_[0], clf.coef_[1], mse]
        return coeficientes

    if GLO.GLBLusarStatsmodels:
        # Ver:            http://stackoverflow.com/questions/11479064/multivariate-linear-regression-in-python
        # Paquete:    http://statsmodels.sourceforge.net/devel/
        # OLS:            http://statsmodels.sourceforge.net/devel/regression.html
        # Detalles: http://statsmodels.sourceforge.net/devel/generated/statsmodels.regression.linear_model.RegressionResults.html#statsmodels.regression.linear_model.RegressionResults
        x_y_values = [[1, punto[0], punto[1]] for punto in listaCoordenadas]
        results = sm.OLS(endog=z_true, exog=x_y_values).fit()
        z_est = [results.params[0] + (results.params[1] * punto[0]) + (results.params[2] * punto[1]) for punto in listaCoordenadas]
        coeficientes = results.params
        coeficientes.append.results.mse_resid ** 0.5
        # if nX == celdaX and nY == celdaY and mostrarAjuste:
        #    print( 'Coeficientes estimados con statsmodel (A0, A1, intercept):', results.params )
        #    print( 'Coordenadas:', nX, nY )
        #    print( 'Lista de valores x, y:                         ', x_y_values )
        #    print( 'Lista de valores z:                                ', z_true )
        #    print( 'Lista de valores ajustados:                ', results.fittedvalues )
        #    print( 'Lista de valores ajustados (z_est):', z_est )
        #    print( 'Lista de residuos (z_real-z_est):    ', results.resid )
        #    #Lo siguiente permitiria generar un fichero con los ajustes del plano-suelo de cada celda 10x10
        #    print( 'results.params[0], results.params[1], results.params[2]', results.params[0], results.params[1], results.params[2] )
        #    print( results.summary() )
        #    #print( results.summary2() )
        #    #print( 'Error cuadratico medio residual: %f (total: %f; R2: %f)' %\
        #    #             (results.mse_resid, results.mse_total, 100*results.mse_resid/results.mse_total) )
        #    #print( 'Error standar medio residual: %f m', (results.mse_resid**0.5) )
        #    #print( 'Suma de cuadrados (mse_resid x nobs)', results.ssr )
        #    #print( 'rsquared:', results.rsquared )
        return coeficientes


# ==============================================================================o
def leerPropiedadDePunto(ptoEnArray, txtPropiedad, miHead, lasPointFieldOrdenDict, lasPointFieldPropertiesDict):
    # Leer propiedades de los puntos guardados en el array aCeldasListaDePtosTlcAll[] o aCeldasListaDePtosTlcPralPF8[] y aCeldasListaDePtosAux[]
    # Por el momento lo guardo siempre como lista de propiedades sin interpretar (posiblemente implemente tb como string)
    if type(ptoEnArray) == np.ndarray or type(ptoEnArray) == list or type(ptoEnArray) == tuple or type(ptoEnArray) == np.void:
        if txtPropiedad == 'x':
            valorPropiedad = (ptoEnArray[lasPointFieldOrdenDict[txtPropiedad]] * miHead['xscale']) + miHead['xoffset']
        elif txtPropiedad == 'y':
            valorPropiedad = (ptoEnArray[lasPointFieldOrdenDict[txtPropiedad]] * miHead['yscale']) + miHead['yoffset']
        elif txtPropiedad == 'z':
            valorPropiedad = (ptoEnArray[lasPointFieldOrdenDict[txtPropiedad]] * miHead['zscale']) + miHead['zoffset']
        elif txtPropiedad in lasPointFieldOrdenDict.keys():
            valorPropiedad = ptoEnArray[lasPointFieldOrdenDict[txtPropiedad]]
        elif (
            txtPropiedad == 'scan_angle_rank'
            or txtPropiedad == 'user_data'
            or txtPropiedad == 'raw_time'
            or txtPropiedad == 'red'
            or txtPropiedad == 'green'
            or txtPropiedad == 'blue'
        ):
            # Propiedades que no se alacenan si GLBLalmacenarPuntosComoNumpyDtypeMini
            # TODO: ver si las consecuencias van mas alla de generar algunas salidas con todos los valores nulos
            valorPropiedad = 0
        else:
            if txtPropiedad == 'nRetorno' or txtPropiedad == 'totalRetornos' or txtPropiedad == 'scan_dir' or txtPropiedad == 'esPuntoEdge':
                return_grp = ptoEnArray[lasPointFieldOrdenDict['return_grp']]
            else:
                valorPropiedad = 0
                print('Propiedad no contemplada en el formato de punto usado:', txtPropiedad)
                print('ptoEnArray:', type(ptoEnArray), ptoEnArray)
                input('Implementar esto si ha lugar 2')
    elif type(ptoEnArray) == str or type(ptoEnArray) == bytes:
        if txtPropiedad in lasPointFieldPropertiesDict.keys():
            posIni = lasPointFieldPropertiesDict[txtPropiedad][3]
            posFin = lasPointFieldPropertiesDict[txtPropiedad][3] + lasPointFieldPropertiesDict[txtPropiedad][0]
            fmt = lasPointFieldPropertiesDict[txtPropiedad][1]
            valor = struct.unpack(fmt, ptoEnArray[posIni:posFin])[0]
            if txtPropiedad == 'x':
                valorPropiedad = (valor * miHead['xscale']) + miHead['xoffset']
            elif txtPropiedad == 'y':
                valorPropiedad = (valor * miHead['yscale']) + miHead['yoffset']
            elif txtPropiedad == 'z':
                valorPropiedad = (valor * miHead['zscale']) + miHead['zoffset']
            else:
                valorPropiedad = valor
        else:
            if txtPropiedad == 'nRetorno' or txtPropiedad == 'totalRetornos' or txtPropiedad == 'scan_dir' or txtPropiedad == 'esPuntoEdge':
                posIni = lasPointFieldPropertiesDict['return_grp'][3]
                posFin = lasPointFieldPropertiesDict['return_grp'][3] + lasPointFieldPropertiesDict['return_grp'][0]
                fmt = lasPointFieldPropertiesDict['return_grp'][1]
                return_grp = struct.unpack(fmt, ptoEnArray[posIni:posFin])[0]
            else:
                valorPropiedad = 0
                print('Propiedad no contemplada en el formato de punto usado:', txtPropiedad)
                print('ptoEnArray:', type(ptoEnArray), ptoEnArray)
                input('Implementar esto si ha lugar 3')
    else:
        print('Tipo de dato:', type(ptoEnArray))
        input('No contemplo otras opciones de guardar punto en el array -> revisar si hay que implementar esto')

    # Provisional: quitar el try cuando vea que funciona
    try:
        if txtPropiedad == 'nRetorno' or txtPropiedad == 'totalRetornos' or txtPropiedad == 'scan_dir' or txtPropiedad == 'esPuntoEdge':
            if txtPropiedad == 'esPuntoEdge':
                valorPropiedad = return_grp & 0b10000000
            elif txtPropiedad == 'scan_dir':
                valorPropiedad = return_grp & 0b01000000
            elif txtPropiedad == 'totalRetornos':
                valorPropiedad = return_grp & 0b00111000
            elif txtPropiedad == 'nRetorno':
                valorPropiedad = return_grp & 0b111
            else:
                valorPropiedad = 0
    except:
        print('clidaux-> ATENCION error: tipo de dato:', type(ptoEnArray))
    return valorPropiedad


# ==============================================================================o
def estaDentro(x, y, poly):
    n = len(poly)
    estaDentro = False
    p1x, p1y = poly[0]
    for i in range(n + 1):
        p2x, p2y = poly[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xints = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xints:
                        estaDentro = not estaDentro
        p1x, p1y = p2x, p2y
    return estaDentro


# # ==============================================================================o
# def quitarContrabarrasAgregarBarraFinal(ruta=''):
#     if not ruta:
#         return None
#     nuevaRuta = ruta.replace(os.sep, '/')
#     # nuevaRuta = ''
#     # for letra in ruta:
#     #     letraSinBackslash = letra if letra != '\\' else '/'
#     #     nuevaRuta += letraSinBackslash
#     # if nuevaRuta[-1:] != '/':
#     #     nuevaRuta += '/'
#     nuevaRuta = os.path.dirname(nuevaRuta.replace('//', '/'))
#     return nuevaRuta


# ==============================================================================o
def generar_tfw():
    # import gdal
    # path, gen_prj
    infile = 'O:/Sigmena/usuarios/COMUNES/Bengoa/SIC/cartolidar/JAEscudero/tif1/AltMdb95_LoteAsc.tif'
    src = gdal.Open(infile)
    xform = src.GetGeoTransform()

    #     if gen_prj == 'prj':
    #             src_srs = osr.SpatialReference()
    #             src_srs.ImportFromWkt(src.GetProjection())
    #             src_srs.MorphToESRI()
    #             src_wkt = src_srs.ExportToWkt()
    #
    #             prj = open(os.path.splitext(infile)[0] + '.prj', 'wt')
    #             prj.write(src_wkt)
    #             prj.close()

    src = None
    edit1 = xform[0] + xform[1] / 2
    edit2 = xform[3] + xform[5] / 2
    print('xform:', xform)
    print('edit1:', edit1)
    print('edit2:', edit2)
    print(os.path.splitext(infile)[0])

    tfw = open(os.path.splitext(infile)[0] + '.tfw', 'wt')
    tfw.write("%0.8f\n" % xform[1])
    tfw.write("%0.8f\n" % xform[2])
    tfw.write("%0.8f\n" % xform[4])
    tfw.write("%0.8f\n" % xform[5])
    tfw.write("%0.8f\n" % edit1)
    tfw.write("%0.8f\n" % edit2)
    tfw.close()


# ==============================================================================o
# https://code.tutsplus.com/tutorials/understand-how-much-memory-your-python-objects-use--cms-25609
# https://stackoverflow.com/questions/14372006/variables-memory-size-in-python
# getsizeof() function doesn't return the actual memory of the objects,
# but only the memory of the pointers to objects.
# En el caso de una lista: memory of the list and the pointers to its objects
def mostrarSizeof(x, level=0):
    print("\t" * level, x.__class__, sys.getsizeof(x), x)
    if hasattr(x, '__iter__'):
        if hasattr(x, 'items'):
            for xx in x.items():
                mostrarSizeof(xx, level + 1)
        else:
            for xx in x:
                mostrarSizeof(xx, level + 1)


# ==============================================================================o
# https://code.tutsplus.com/tutorials/understand-how-much-memory-your-python-objects-use--cms-25609
def deep_getsizeof(o, ids):
    """Find the memory footprint of a Python object
 
    This is a recursive function that drills down a Python object graph
    like a dictionary holding nested dictionaries with lists of lists
    and tuples and sets.
 
    The sys.getsizeof function does a shallow size of only. It counts each
    object inside a container as pointer only regardless of how big it
    really is.
 
    :param o: the object
    :param ids:
    :return:
    """
    d = deep_getsizeof
    if id(o) in ids:
        return 0
 
    r = sys.getsizeof(o)
    ids.add(id(o))
 
    if isinstance(o, str):
        return r
 
    if isinstance(o, collections.Mapping):
        try:
            return r + sum(d(k, ids) + d(v, ids) for k, v in o.iteritems())
        except:
            return 0
 
    if isinstance(o, collections.Container):
        return r + sum(d(x, ids) for x in o)
 
    return r 


# ==============================================================================o
def procesoActivo():
    return psutil.Process(os.getpid())


# ==============================================================================o
def printMsg(mensaje='', outputFileLas=True, verbose=True, newLine=True, end=None):
    if verbose:
        if not end is None:
            print(mensaje, end=end)
        elif not newLine:
            end=''
            print(mensaje, end=end)
        else:
            end=''
            print(mensaje)
    if printMsgToFile:
        try:
            if outputFileLas and clidconfig.controlFileLas:
                try:
                    clidconfig.controlFileLas.write(str(mensaje) + end + '\n' if newLine else ' ')
                except:
                    if clidconfig.controlFileGral:
                        clidconfig.controlFileGral.write('Error writing control file (1).\n')
            else:
                clidconfig.controlFileGral.write(str(mensaje) + end + '\n' if newLine else ' ')
        except:
            print('clidaux-> printMsg: no hay acceso a controlFileLas ni controlFileGral.')
            pass


# #Puedo usar esta funcion para mensajes individuales y globales
# def mostrarMensaje(mensaje, outputFileLas=True, verbose=True, newLine=True):
#     if verbose:
#         if newLine:
#             print( mensaje )
#         else:
#             print( mensaje, )
#     if outputFileLas and clidconfig.controlFileLas:
#         try:
#             clidconfig.controlFileLas.write(str(mensaje) + '\n' if newLine else ' ')
#         except:
#             if clidconfig.controlFileGral:
#                 clidconfig.controlFileGral.write('Error writing control file (1).\n')
#     else:
#         try:
#             clidconfig.controlFileGral.write(str(mensaje) + '\n' if newLine else ' ')
#         except:
#             print( 'Error writing control file (2).' )


# ==============================================================================o
def mostrarPropiedadesDeUnObjetoClase(
        myObjectClass,
        myClassObjectName='miObjeto',
        mostrarBuiltin=False,
        mostrarVariables=True,
        mostrarMetodos=False,
        sizeMaxKbParaMostrar=1.0):
    sumaBuiltinKb = 0
    sumaMetodosKb = 0
    sumaVariablesKb = 0
    printMsg('\nclidaux-> Mostrando propiedades del objeto/clase {}:'.format(myClassObjectName))
    for nombrePropiedad in dir(myObjectClass):
        valorPropiedad = getattr(myObjectClass, nombrePropiedad)
        sizePropiedadKb = deep_getsizeof(valorPropiedad, set()) / 1E3
        if nombrePropiedad[:2] == '__' and nombrePropiedad[-2:] == '__':
            esBuiltin = True
        else:
            esBuiltin = False

        if (
            isinstance(valorPropiedad, bool)
            or isinstance(valorPropiedad, str)
            or isinstance(valorPropiedad, int)
            or isinstance(valorPropiedad, float)
            or isinstance(valorPropiedad, complex)
            or isinstance(valorPropiedad, list)
            or isinstance(valorPropiedad, tuple)
            or isinstance(valorPropiedad, range)
            or isinstance(valorPropiedad, dict)
            or isinstance(valorPropiedad, bytes)
            or isinstance(valorPropiedad, bytearray)
            or isinstance(valorPropiedad, memoryview)
            or isinstance(valorPropiedad, set)
            or isinstance(valorPropiedad, frozenset)
            or isinstance(valorPropiedad, np.ndarray)
            # https://docs.python.org/3/library/stdtypes.html
        ):
            tipoPropiedad = 'variable'
        elif isinstance(valorPropiedad, types.FunctionType):
            tipoPropiedad = 'function'
        elif isinstance(valorPropiedad, types.MethodType):
            tipoPropiedad = 'method'
        elif isinstance(valorPropiedad, types.ModuleType):
            tipoPropiedad = 'modulo'
        elif isinstance(valorPropiedad, types.CodeType):
            tipoPropiedad = 'codeType'
        elif isinstance(valorPropiedad, types.BuiltinFunctionType):
            tipoPropiedad = 'builtinFun'
        elif isinstance(valorPropiedad, types.BuiltinMethodType):
            tipoPropiedad = 'builtinMet'
        elif isinstance(valorPropiedad, types.MethodWrapperType):
            tipoPropiedad = 'wrapper'
        elif (
            isinstance(valorPropiedad, types.MethodDescriptorType)
            or isinstance(valorPropiedad, types.WrapperDescriptorType)
            or isinstance(valorPropiedad, types.GetSetDescriptorType)
        ):
            tipoPropiedad = 'descriptor'
        else:
            tipoPropiedad = 'otros'

        if esBuiltin:
            sumaBuiltinKb += sizePropiedadKb
            if not mostrarBuiltin:
                continue

        if tipoPropiedad == 'variable':
            sumaVariablesKb += sizePropiedadKb
            if not mostrarVariables:
                continue
            try:
                variableShape = valorPropiedad.shape
            except:
                variableShape = [0]
            try:
                variableLen = len(valorPropiedad)
            except:
                variableLen = -1
        else:
            sumaMetodosKb += sizePropiedadKb
            if not mostrarMetodos:
                continue
            variableShape = None
            variableLen = None

        if nombrePropiedad == 'ficheroCompletoEnLaRAM':
            printMsg(
                '->memSize: {:08.1f} Kb {:>35} {:>10}->{:<30} --->No se muestra por incluir todo el fichero las. nElem: {}'.format(
                    sizePropiedadKb, nombrePropiedad, tipoPropiedad, str(type(valorPropiedad)), variableLen
                )
            )
            continue
        elif sizePropiedadKb > sizeMaxKbParaMostrar: 
            printMsg(
                '->memSize: {:08.1f} Kb {:>35} {:>10}->{:<30}--->Muy grande-> nElem: {} variableShape: {}'.format(
                    sizePropiedadKb, nombrePropiedad, tipoPropiedad, str(type(valorPropiedad)), variableLen, variableShape
                )
            )
            continue
        elif len(variableShape) > 1 and (variableShape[0] > 5 or variableShape[1] > 5):
            printMsg(
                '->memSize: {:08.1f} Kb {:>35} {:>10}->{:<30}--->Array de Shape: {}'.format(
                    sizePropiedadKb, nombrePropiedad, tipoPropiedad, str(type(valorPropiedad)), variableShape
                )
            )
            continue
        elif (isinstance(valorPropiedad, list) or isinstance(valorPropiedad, tuple)) and variableLen > 10:
            printMsg(
                '->memSize: {:08.1f} Kb {:>35} {:>10}->{:<30}--->Lista/tupla con {} elementos'.format(
                    sizePropiedadKb, nombrePropiedad, tipoPropiedad, str(type(valorPropiedad)), variableLen
                )
            )
            continue
        elif isinstance(valorPropiedad, dict) and variableLen > 10:
            printMsg(
                '->memSize: {:08.1f} Kb {:>35} {:>10}->{:<30}--->Diccionario con {} elementos'.format(
                    sizePropiedadKb, nombrePropiedad, tipoPropiedad, str(type(valorPropiedad)), variableLen
                )
            )
            continue

        try:
            printMsg(
                '->memSize: {:08.1f} Kb {:>35} {:>10}->{:<30}: {}'.format(
                    sizePropiedadKb,
                    nombrePropiedad,
                    tipoPropiedad,
                    str(type(valorPropiedad)),
                    str(valorPropiedad)
                )
            )
        except:
            printMsg(
                '->memSize: {:08.1f} Kb {:>35} {:>10}->{:<30}: ATENCION, no se puede mostrar'.format(
                    sizePropiedadKb,
                    nombrePropiedad,
                    tipoPropiedad,
                    str(type(valorPropiedad))
                )
            )

    printMsg('\n{:o^80}'.format(''))
    printMsg('clidaux-> Size suma de builtins  de la clase {}: {:05.1f} Mb'.format(myClassObjectName, sumaBuiltinKb / 1E3))
    printMsg('clidaux-> Size suma de metodos   de la clase {}: {:05.1f} Mb'.format(myClassObjectName, sumaMetodosKb / 1E3))
    printMsg('clidaux-> Size suma de variables de la clase {}: {:05.1f} Mb'.format(myClassObjectName, sumaVariablesKb / 1E3))
    printMsg('clidaux-> Size acum de b&m&v     de la clase {}: {:05.1f} Mb'.format(myClassObjectName, sumaVariablesKb / 1E3))
    printMsg('{:o^80}\n'.format(''))


# ==============================================================================o
def controlarAvance(contador, x=0, y=0, z=0, intervalo=1e6):
    if contador != 0 and contador % intervalo == 0:
        ramMem, _ = memoriaRam('0', False)
        if intervalo == 1e6:
            print(
                'clidaux-> %i %s x: %0.0f, y: %0.0f, z: %0.1f. Mem disp: %0.1f Mb'
                % (contador / intervalo, 'millon ptos.  ' if contador / intervalo == 1 else 'millones ptos.', x, y, z, ramMem.available / 1e6)
            )
        else:
            print('clidaux-> %i %s x: %0.0f, y: %0.0f, z: %0.1f. Mem disp: %0.1f Mb' % (contador, 'ptos.', x, y, z, ramMem.available / 1e6))

    if contador % (intervalo / 10) == 0:
        ramMem, _ = memoriaRam('99', False)
        if ramMem.available / 1e6 < GLO.GLBLminimoDeMemoriaRAM:
            print('clidaux-> Puede haber problemas de memoria:')
            memoriaRam('2', True)
            time.sleep(5)
            gc.collect()
            ramMem, _ = memoriaRam('99', False)
            if ramMem.available / 1e6 < GLO.GLBLminimoDeMemoriaRAM:
                print('clidaux-> Confirmado:')
                memoriaRam('3', True)
                return False
            else:
                print('clidaux-> Eran solo dificultades transitorias; memoria RAM disponible: %0.2f Mb' % (ramMem.available / 1e6))
    return True


# ==============================================================================o
def mostrarMemoriaOcupada(miLasClass):
    print('Memoria ocupada por miLasClass:')
    propiedades = [p for p in dir(miLasClass) if isinstance(getattr(miLasClass, p), property)]
    print('\nChequeo la memoria ocupada por las propiedades de miLasClass:', propiedades)
    for p in dir(miLasClass):
        try:
            if type(getattr(miLasClass, p)) in [bool, str, int, float]:
                # [types.NoneType, types.BooleanType, types.StringType, types.IntType, types.LongType, types.FloatType]:
                pass
            elif type(getattr(miLasClass, p)) in [type, dict]:
                # [types.TypeType, types.DictionaryType, types.ModuleType, types.ClassType, types.InstanceType, types.MethodType]:
                pass
            elif sys.getsizeof(getattr(miLasClass, p)) / 1e3 > 1:
                print('\s\t%0.2f MB\t' % (p, sys.getsizeof(getattr(miLasClass, p)) / 1e6), type(getattr(miLasClass, p)), '\t', getattr(miLasClass, p))
            else:
                print('\s\t%0.2f MB\t' % (p, sys.getsizeof(getattr(miLasClass, p)) / 1e6), type(getattr(miLasClass, p)), '\t', getattr(miLasClass, p))
            # elif getattr(miLasClass, p).nbytes / 1e3 > 1:
            #    print( '\s\t%0.2f MB\t' % (p, p.nbytes/1e6), type(getattr(miLasClass, p)), '\t', getattr(miLasClass, p) )
        except:
            print('Error al mostrar la memoria ocupada por', p, type(getattr(miLasClass, p)), getattr(miLasClass, p))
    print('\nVariables de miLasClass:')
    # for variableDeMiBloque in vars(miLasClass).keys():
    #    print( variableDeMiBloque, '\t', vars(miLasClass)[variableDeMiBloque] )


# ==============================================================================o
def interrumpoPorFaltaDeRAM(contador, totalPoints, miLasClass):
    elMensaje = '\nATENCION:\t\tInterrumpo el preprocesado para evitar problemas de memoria RAM (lectura de fichero completo).\n'
    clidconfig.controlFileGral.write(elMensaje)
    printMsg(elMensaje)
    if contador > totalPoints * 0.5:
        elMensaje = 'Puntos leidos:\t\t%i (<1/2). Continuo con los puntos ya procesados en primera vuelta.' % (contador)
        clidconfig.controlFileGral.write(elMensaje)
        printMsg(elMensaje)
    else:
        elMensaje = 'Puntos leidos:\t\t%i (<1/2). Interrumpo el procesado y reintento con distinta configuracion.\n' % (contador)
        clidconfig.controlFileGral.write(elMensaje)
        printMsg(elMensaje)
    printMsg(
        'Desactivar la opcion de cargar todos los puntos en array. Si tb falla: Lectura de registros individuales (en vez de leer el fichero completo cargandolo entero en la RAM).\n'
    )
    mostrarMemoriaOcupada(miLasClass)


# ==============================================================================o
def coordenadasDeBloque(miHead, metrosBloque, metrosCelda):
    xmin = miHead['xmin']
    ymin = miHead['ymin']
    xmax = miHead['xmax']
    ymax = miHead['ymax']
    xInfIzda = float(xmin)
    yInfIzda = float(ymin)
    xSupIzda = xInfIzda
    if metrosBloque == 1000 or metrosBloque == 2000:
        # print( 'Calculando las coordenadas de la esquina inferior del bloque' )
        if xInfIzda % metrosCelda != 0:
            print(
                'Corrigiendo xInfIzda. Antes:',
                xInfIzda,
            )
            #             (xInfIzda / metrosCelda), round((xInfIzda / metrosCelda), 0), metrosCelda * round((xInfIzda / metrosCelda), 0),
            xInfIzda = float(metrosCelda * round((xInfIzda / metrosCelda), 0))
            print('Despues:', xInfIzda)
        if yInfIzda % metrosCelda != 0:
            print(
                'Corrigiendo yInfIzda. Antes:',
                yInfIzda,
            )
            yInfIzda = float(metrosCelda * round((yInfIzda / metrosCelda), 0))
            print('Despues:', yInfIzda)
        # Esquina nominal del fichero las
        xSupDcha = xSupIzda + metrosBloque
        ySupIzda = yInfIzda + metrosBloque
    else:
        xSupDcha = float(xmax)
        ySupIzda = float(ymax)
    ySupDcha = ySupIzda

    return {'xInfIzda': xInfIzda, 'yInfIzda': yInfIzda, 'xSupIzda': xSupIzda, 'ySupIzda': ySupIzda, 'xSupDcha': xSupDcha, 'ySupDcha': ySupDcha}


def creaDirectorio(rutaDirectorio):
    # Parecido a os.makedirs(), pero que este no crea todo el arbol de directorios,
    # sino solo intenta crear el directorio y su padre.
    if not os.path.exists(rutaDirectorio):
        try:
            os.mkdir(rutaDirectorio)
        except:
            rutaPadre = os.path.abspath(os.path.join(rutaDirectorio, '..'))
            try:
                os.mkdir(rutaPadre)
                os.mkdir(rutaDirectorio)
                print('clidaux-> Se ha creado el directorio %s despues de crear su dir padre: %s' % (rutaDirectorio, rutaPadre))
            except:
                print('clidaux-> No se ha podido crear el directorio %s ni su dir padre %s' % (rutaDirectorio, rutaPadre))
            sys.exit(0)


def creaRutaDeFichero(rutaFichero):
    rutaDirectorio = os.path.dirname(os.path.realpath(rutaFichero))
    miFileNameSinPath = os.path.basename(os.path.realpath(rutaFichero))
    if not os.path.exists(rutaDirectorio):
        print(
            '\tclidaux-> Creando ruta {} para {}'.format(
                rutaDirectorio,
                miFileNameSinPath
            )
        )
        try:
            os.makedirs(rutaDirectorio)
        except:
            print('clidaux-> No se ha podido crear el directorio %s' % (rutaDirectorio))
            sys.exit()


def creaDirectorios(GLOBAL_rutaResultados, listaSubdirectorios=[]):
    if not os.path.exists(GLOBAL_rutaResultados):
        print('No existe el directorio %s -> Se crea automaticamente...' % (GLOBAL_rutaResultados))
    listaDirectorios = [
        GLOBAL_rutaResultados,
        GLOBAL_rutaResultados + 'Ajustes/',
        GLOBAL_rutaResultados + 'Ajustes/Basal/',
        GLOBAL_rutaResultados + 'Ajustes/Suelo/',
        GLOBAL_rutaResultados + 'Alt/',
        GLOBAL_rutaResultados + 'AltClases/',
        GLOBAL_rutaResultados + 'Clasificacion/',
        GLOBAL_rutaResultados + 'CobClases/',
        GLOBAL_rutaResultados + 'Fcc/',
        GLOBAL_rutaResultados + 'Fcc/RptoAzMin_MasDe/',
        GLOBAL_rutaResultados + 'Fcc/RptoAsuelo_MasDe/',
        GLOBAL_rutaResultados + 'Fcc/RptoAmds_MasDe/',
        GLOBAL_rutaResultados + 'Fcc/RptoAmds/',
        GLOBAL_rutaResultados + 'Fcc/RptoAmdb/',
        GLOBAL_rutaResultados + 'FormasUsos/',
        GLOBAL_rutaResultados + 'NumPtosPasadas/',
        GLOBAL_rutaResultados + 'NumPtosPasadas/PorRetornos/',
        GLOBAL_rutaResultados + 'NumPtosPasadas/PorClases/',
        GLOBAL_rutaResultados + 'OrientPte/',
        GLOBAL_rutaResultados + 'Varios/',
        GLOBAL_rutaResultados + 'z/',
    ]
    for directorio in listaDirectorios:
        if not os.path.exists(directorio):
            try:
                os.makedirs(directorio)
            except:
                print('No se ha podido crear el directorio %s' % (directorio))
                sys.exit()


def mostrarCabecera(header):
    if GLO.GLBLusarLiblas:
        # print( 'Propiedades y metodos de miHead:', dir(header) )
        """
        ['DeleteVLR', 'GetVLR', '__class__', '__del__', '__delattr__', '__dict__',
        '__doc__', '__format__', '__getattribute__', '__hash__', '__init__',
        '__len__', '__module__', '__new__', '__reduce__', '__reduce_ex__',
        '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__',
        'add_vlr', 'compressed', 'count', 'data_format_id', 'data_offset',
        'data_record_length', 'dataformat_id', 'date', 'delete_vlr', 'doc',
        'encoding', 'file_signature', 'file_source_id', 'filesource_id',
        'get_compressed', 'get_count', 'get_dataformatid', 'get_dataoffset',
        'get_datarecordlength', 'get_date', 'get_filesignature', 'get_filesourceid',
        'get_global_encoding', 'get_guid', 'get_headersize', 'get_majorversion',
        'get_max', 'get_min', 'get_minorversion', 'get_offset', 'get_padding',
        'get_pointrecordsbyreturncount', 'get_pointrecordscount', 'get_projectid',
        'get_recordscount', 'get_scale', 'get_schema', 'get_softwareid', 'get_srs',
        'get_systemid', 'get_version', 'get_vlr', 'get_vlrs', 'get_xml',
        'global_encoding', 'guid', 'handle', 'header_length', 'header_size',
        'major', 'major_version', 'max', 'min', 'minor', 'minor_version',
        'num_vlrs', 'offset', 'owned', 'padding', 'point_records_count',
        'point_return_count', 'project_id', 'records_count', 'return_count',
        'scale', 'schema', 'set_compressed', 'set_count', 'set_dataformatid',
        'set_dataoffset', 'set_date', 'set_filesourceid', 'set_global_encoding',
        'set_guid', 'set_majorversion', 'set_max', 'set_min', 'set_minorversion',
        'set_offset', 'set_padding', 'set_pointrecordsbyreturncount',
        'set_pointrecordscount', 'set_scale', 'set_schema', 'set_softwareid',
        'set_srs', 'set_systemid', 'set_version', 'set_vlrs', 'software_id',
        'srs', 'system_id', 'version', 'version_major', 'version_minor', 'vlrs', 'xml']
        """
        print('Version de formato LAS:', header.version)
        print('version:', header.version)
        print('data_format_id:', header.data_format_id)
        print('dataformat_id:', header.dataformat_id)
        print('data_record_length:', header.data_record_length)
        print('global_encoding:', header.global_encoding)
        print('header_length', header.header_length)
        print('header_size', header.header_size)
        print('major', header.major)
        print('major_version', header.major_version)
        print('max', header.max)
        print('min', header.min)
        print('minor', header.minor)
        print('minor_version', header.minor_version)
        print('num_vlrs')
        print('offset', header.offset)
        print('owned', header.owned)
        print('padding', header.padding)
        print('point_records_count', header.point_records_count)
        print('point_return_count', header.point_return_count)
        print('project_id', header.project_id)
        print('records_count', header.records_count)
        print('return_count', header.return_count)
        print('scale', header.scale)
        print('schema', header.schema)
        print('Numero total de puntos:', header.count)
        print('point_return_count:', header.point_return_count)
        print('data_offset:', header.data_offset)
        print('offset:', header.offset)
        print('srs:', header.srs)
        '''
        #Ejemplo:
        version: 1.2
        data_format_id: 3
        dataformat_id: 3
        data_record_length: 34
        global_encoding: 0
        header_length 227
        header_size 227
        major 1
        major_version 1
        max [343999.99, 4629999.99, 863.94]
        min [342058.62, 4628000.0, 845.6700000000001]
        minor 2
        minor_version 2
        num_vlrs
        offset [-0.0, -0.0, -0.0]
        owned False
        padding 2
        point_records_count 2397593
        point_return_count [2378079L, 19475L, 39L, 0L, 0L, 0L, 0L, 0L]
        project_id 00000000-0000-0000-0000-000000000000
        records_count 0
        return_count [2378079L, 19475L, 39L, 0L, 0L, 0L, 0L, 0L]
        scale [0.01, 0.01, 0.01]
        schema <liblas.schema.Schema object at 0x04E921B0>
        Numero total de puntos: 2397593
        point_return_count: [2378079L, 19475L, 39L, 0L, 0L, 0L, 0L, 0L]
        data_offset: 229
        offset: [-0.0, -0.0, -0.0]
        srs: <liblas.srs.SRS object at 0x04E921B0>
        '''
    else:  # Cabecera leida con file.read()
        print('Version de formato LAS: %i.%i' % (header['vermajor'], header['verminor']))
        print('Formato de puntos:', header['pointformat'])
        print('Numero total de puntos:', header['numptrecords'])
        print('pointreclen:', header['pointreclen'])
        print('xscale:', header['xscale'])
        print('yscale:', header['yscale'])
        print('xoffset, yoffset', header['xoffset'], header['yoffset'])
        '''
        #Ejemplo:
        pointreclen: 34
        xscale: 0.01
        yscale: 0.01
        xoffset, yoffset -0.0 -0.0
        '''


# def mostrarPunto(p):
#     if GLO.GLBLusarLiblas:
#         print( 'point_source_id', p.point_source_id )
#         print( 'handle', p.handle )
#         #print( 'header', p.header )
#         print( 'time', p.time )
#         print( 'raw_time', p.raw_time, time.asctime( time.localtime(p.raw_time) ) )
#         #print( 'xml', p.xml )
#         #print( 'x', p.x )
#         #print( 'y', p.y )
#         #print( 'z', p.z )
#         print( 'scan_angle', p.scan_angle )
#         print( 'scan_direction', p.scan_direction )
#         print( 'scan_flags', p.scan_flags )
#         #print( 'return_number', p.return_number )
#         #print( 'number_of_returns', p.number_of_returns )
#         #print( 'intensity', p.intensity )
#         #print( 'user_data', p.user_data )
#         #print( 'point_source_ID', p.point_source_ID )
#     else:
#         pass


# ==============================================================================o
def convertirMirecordEnDict(miRecord, listaTuplasPropPtoTodas):
    dctData = {}
    if GLO.GLBLalmacenarPuntosComoNumpyDtype:  # type(miPto) == np.void
        contador = 0
        for row in listaTuplasPropPtoTodas:
            dctData[row[0]] = miRecord[contador]
            contador += 1
    elif type(miRecord) == str or type(miRecord) == bytes:
        # Lectura del fichero .las con infile.read()
        puntero = 0
        for row in listaTuplasPropPtoTodas:
            # print( row[0], puntero, row[1], miRecord[puntero:puntero+row[1]], struct.unpack(row[2], miRecord[puntero:puntero+row[1]])[0] )
            dctData[row[0]] = struct.unpack(row[2], miRecord[puntero : puntero + row[1]])[0]
            puntero = puntero + row[1]
    elif type(miRecord) == list or type(miRecord) == tuple or type(miRecord) == np.ndarray:
        # Opcion no desarrollada, pero posible, igual que con
        if len(listaTuplasPropPtoTodas) != len(miRecord):
            print('Revisar problema de propiedades del punto:')
            print(listaTuplasPropPtoTodas)
            print(miRecord)
        contador = 0
        for row in listaTuplasPropPtoTodas:
            dctData[row[0]] = miRecord[contador]
            contador += 1
    else:
        print('Hay un error en el tipo de registro leido 1-> type(miRecord):', type(miRecord))
        print('type(miRecord) == np.ndarray', type(miRecord) == np.ndarray)
        print('Contenido del registro:', miRecord)
        print('Revisar este error de type()')
        quit()


# ==============================================================================o
def lasToolsDEM(infileConRuta):
    infile = os.path.basename(infileConRuta)
    rutaLazCompleta = os.path.dirname(infileConRuta)

    if MAIN_ENTORNO == 'calendula':
        las2dem_binary = 'las2dem'
    elif MAIN_ENTORNO == 'windows':
        # las2dem_binary = 'las2dem.exe'
        las2dem_binary = MAIN_DRIVE + '/_App/LAStools/bin/'
        if not os.path.isfile(las2dem_binary):
            las2dem_binary = 'C:/_app/LAStools/bin/'
            if not os.path.isfile(las2dem_binary):
                laszip_names = ('las2dem.exe')
                for binary in laszip_names:
                    in_path = [os.path.isfile(os.path.join(x, binary)) for x in os.environ["PATH"].split(os.pathsep)]
                    if any(in_path):
                        las2dem_binary = binary
                        break
                    else:
                        print('No se ha encontrado las2dem.exe en el path ni en D:/_App/LAStools/ ni C:/_app/LAStools/bin/')
                        sys.exit(0)

    # extensionDem = '.asc'
    extensionDem = '.tif'
    outfileDem = (infile.replace('.las', extensionDem)).replace('.laz', extensionDem)
    if outfileDem[-4:] != extensionDem:
        outfileDem = outfileDem + extensionDem
    outfileLasConRuta = os.path.join(rutaLazCompleta, outfileDem)
    print('\tSe crea el fichero dem %s' % outfileDem)
    # print('\t\t%s -i %s -o %s' % (las2dem_binary, infileConRuta, outfileLasConRuta))
    subprocess.call([las2dem_binary, '-i', infileConRuta, '-o', outfileLasConRuta, ' -keep_class 2 -step 2 -v -utm 30T'])


# ==============================================================================o
def comprimeLaz(
        infileConRuta,
        eliminarLasFile=False,
        LCLverbose=False,
        sobreEscribirOutFile=False,
    ):
    if LCLverbose:
        printMsg('\n{:_^80}'.format(''))

    if not os.path.exists(infileConRuta):
        printMsg(f'clidaux-> Fichero no disponible para comprimir: {infileConRuta}')
        return False

    infile = os.path.basename(infileConRuta)
    rutaLazCompleta = os.path.dirname(infileConRuta)
    if 'RGBI' in rutaLazCompleta:
        rutaLazCompleta = rutaLazCompleta.replace('RGBI', 'RGBI_laz')
    else:
        rutaLazCompleta = rutaLazCompleta.replace('RGB', 'RGB_laz')
    if not os.path.isdir(rutaLazCompleta):
        try:
            os.makedirs(rutaLazCompleta)
        except:
            print('clidaux-> ATENCION: no se ha podido crear la ruta:', rutaLazCompleta)
            sys.exit(0)

    #TRNSdescomprimirConlaszip = True
    #TRNSdescomprimirConlas2las = False
    if MAIN_ENTORNO == 'calendula':
        # laszip_binary = 'las2las'
        laszip_binary = 'laszip'
        outfileLaz = (infile.replace('.las', '.laz')).replace('.LAS', '.laz')
        outfileLazConRuta = (os.path.join(rutaLazCompleta, outfileLaz))
    elif MAIN_ENTORNO == 'windows':
        # laszip_binary = '{}/_clid/cartolid/laszip/laszip'.format(MAIN_PROJ_DIR)
        laszip_binary = os.path.join(MAIN_PROJ_DIR, 'laszip', 'laszip.exe')
        outfileLaz = (infile.replace('.las', '.laz')).replace('.LAS', '.laz')
        outfileLazConRuta = os.path.join(rutaLazCompleta, outfileLaz)
        # print('\t-> Compresor: {}'.format(laszip_binary))
        # print('\t-> infileConRuta:', infileConRuta)
        # print('\t-> outfileLazConRuta:', outfileLazConRuta)
        # print('\t\t%s -i %s -o %s' % (laszip_binary, infileConRuta, outfileLasConRuta))
    if os.path.exists(outfileLazConRuta) and not sobreEscribirOutFile:
        print('\t-> clidaux-> No se genera el fichero comprimido porque sobreEscribirOutFile={} y ya existe: {}'.format(sobreEscribirOutFile, outfileLazConRuta))
        return False

    if LCLverbose:
        print('\t-> clidaux-> Se comprime el fichero para generar: {}'.format(outfileLazConRuta))
        print('\t-> clidaux-> Compresor:', laszip_binary)
    subprocess.call([laszip_binary, '-i', infileConRuta, '-o', outfileLazConRuta])

    if eliminarLasFile and os.path.exists(infileConRuta):
        print('\tEliminando el fichero las despues de comprimir a laz:', infileConRuta)
        os.remove(infileConRuta)

    return True


# ==============================================================================o
def descomprimeLaz(
        infileConRuta,
        descomprimirLazEnMemoria=True,
        LCLverbose=False,
        sobreEscribirOutFile=False,
    ):
    if LCLverbose:
        printMsg('\n{:_^80}'.format(''))

    if not os.path.exists(infileConRuta):
        printMsg(f'clidaux-> Fichero no disponible para descomprimir: {infileConRuta}')
        return ''
    infileConRuta = infileConRuta.replace('.las', '.laz')

    infile = os.path.basename(infileConRuta)
    rutaLazCompleta = os.path.dirname(infileConRuta)

    # ATENCION: las2las no me funciona para descomprimir en memoria
    TRNSdescomprimirConlaszip = True
    TRNSdescomprimirConlas2las = False
    if MAIN_ENTORNO == 'calendula':
        laszip_binary_encontrado = True
        # laszip_binary = 'las2las'
        laszip_binary = 'laszip'
    elif MAIN_ENTORNO == 'windows':
        # ======================================================================
        # ======================================================================
        # Atencion: laszip.exe funciona con las 1.4 con todos los formatos de punto (las2las no)
        # ======================================================================
        # ======================================================================
        # 
        if TRNSdescomprimirConlaszip and TRNSdescomprimirConlas2las:
            laszip_names = ('laszip.exe', 'laszip', 'las2las.exe', 'las2las')
        elif TRNSdescomprimirConlaszip and not TRNSdescomprimirConlas2las:
            laszip_names = ('laszip.exe', 'laszip')
        elif TRNSdescomprimirConlas2las:
            laszip_names = ('las2las.exe', 'las2las')
        else:
            laszip_names = ('laszip-cli', 'laszip-cli.exe')

        laszip_binary = ''
        laszip_binary_encontrado = False
        for binary in laszip_names:
            in_path = [os.path.isfile(os.path.join(x, binary)) for x in os.environ["PATH"].split(os.pathsep)]
            # print('clidaux-> path: {}'.format(os.environ["PATH"].split(os.pathsep)))
            # print('clidaux-> Buscando {} {}'.format(any(in_path), in_path))
            if any(in_path):
                laszip_binary = binary
                laszip_binary_encontrado = True
                break
        if not laszip_binary_encontrado:
            if LCLverbose:
                print("clidaux-> No se ha encontrado ningun binario de laszip (%s) en el path; busco en mis directorios" % ", ".join(laszip_names))
            if TRNSdescomprimirConlaszip:
                if LCLverbose:
                    print('\t-> Buscando {}'.format(os.path.abspath('./laszip/laszip.exe')))

                if os.path.exists(os.path.abspath('./laszip/laszip.exe')):
                    laszip_binary_encontrado = True
                    if LCLverbose:
                        print('\t-> Utilizo  {}'.format(os.path.abspath('./laszip/laszip.exe')))
                    laszip_binary = os.path.abspath('./laszip/laszip')
                elif os.path.exists('C:/_app/LAStools/bin/laszip.exe'):
                    laszip_binary_encontrado = True
                    if LCLverbose:
                        print('\t-> Utilizo  {}'.format('C:/_app/LAStools/bin/laszip.exe'))
                    laszip_binary = os.path.abspath('C:/_app/LAStools/bin/laszip')
                elif os.path.exists(MAIN_DRIVE + '/_app/LAStools/bin/laszip.exe'):
                    laszip_binary_encontrado = True
                    if LCLverbose:
                        print('\t-> Utilizo  {}'.format(MAIN_DRIVE + '/_app/LAStools/bin/laszip.exe'))
                    laszip_binary = os.path.abspath(MAIN_DRIVE + '/_app/LAStools/bin/laszip')
            if not laszip_binary_encontrado and TRNSdescomprimirConlas2las:
                if (
                    os.path.exists('./laszip/las2las.exe')
                    and os.path.exists('./laszip/LASzip.dll')
                ):
                    laszip_binary_encontrado = True
                    laszip_binary = os.path.abspath('./laszip/las2las')
                elif (
                    os.path.exists('C:/_app/LAStools/bin/las2las.exe')
                    and os.path.exists('C:/_app/LAStools/laszip/dll/LASzip.dll')
                ):
                    laszip_binary_encontrado = True
                    laszip_binary ='C:/_app/LAStools/bin/las2las.exe'
                elif (
                    os.path.exists(MAIN_DRIVE + '/_app/LAStools/bin/las2las.exe')
                    and os.path.exists(MAIN_DRIVE + '/_app/LAStools/laszip/dll/LASzip.dll')
                ):
                    laszip_binary_encontrado = True
                    laszip_binary =MAIN_DRIVE + '/_app/LAStools/bin/las2las.exe'
                else:
                    print('No se encuentran los ficheros LDA2LAS.exe, LASzip.dll y/o relacionados. Solucionar el problema y empezar de nuevo')
                    sys.exit(0)
            elif False:
                # Esto es antiguo: miro si hay acceso a LDA2LAS.exe y las dll que necesita (laszip.dll y otros)
                if (
                    os.path.exists('LDA2LAS.exe')
                    and os.path.exists('LASzip.dll')
                    and os.path.exists('MSVCRTD.DLL')
                    and os.path.exists('MFC42D.DLL')
                    and os.path.exists('MSVCP60D.DLL')
                ):
                    laszip_binary = 'LDA2LAS'
                elif (
                    os.path.exists('./laszip/LDA2LAS.exe')
                    and os.path.exists('./laszip/LASzip.dll')
                    and os.path.exists('./laszip/MSVCRTD.DLL')
                    and os.path.exists('./laszip/MFC42D.DLL')
                    and os.path.exists('./laszip/MSVCP60D.DLL')
                ):
                    laszip_binary = os.path.abspath('./laszip/LDA2LAS')
                elif os.path.exists('C:/FUSION/LDA2LAS.exe') and os.path.exists('C:\FUSION\LASzip.dll'):
                    laszip_binary = 'c:/fusion/LDA2LAS'
                elif os.path.exists('C:/_app/FUSION/LDA2LAS.exe') and os.path.exists('C:/_app/FUSION/LASzip.dll'):
                    laszip_binary = 'c:/_app/fusion/LDA2LAS'
                elif os.path.exists(MAIN_DRIVE + '/_App/FUSION/LDA2LAS.exe') and os.path.exists(MAIN_DRIVE + '/_App/FUSION/LASzip.dll'):
                    laszip_binary = MAIN_DRIVE + '/_App/FUSION/LDA2LAS'
                else:
                    print('No se encuentran los ficheros LDA2LAS.exe, LASzip.dll y/o relacionados. Solucionar el problema y empezar de nuevo')
                    sys.exit(0)


    if not laszip_binary_encontrado:
        print('\nclidaux-> ATENCION: no se ha encontrado un binario para descomprimir')
        sys.exit(0)

    # outfileLas = infile.replace('.laz', '.las')
    if descomprimirLazEnMemoria:
        # laspy usa subprocess.Popen() (https://github.com/grantbrown/laspy/tree/master/laspy)
        # El fichero descomprimido no se guarda en un fichero, sino que se almacena en memoria (data)
        # Quito la opcion '-stdout' porque las2las.exe da error con esa opcion
        if LCLverbose:
            print('clidaux-> Descomprimiendo {} en memoria con {} '.format(infileConRuta, laszip_binary))
        if laszip_binary.endswith('laszip') or laszip_binary.endswith('laszip.exe'):
            prc = subprocess.Popen(
                [laszip_binary, '-olas', '-stdout', '-i', infileConRuta],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=-1
            )
        else:
            prc = subprocess.Popen(
                [laszip_binary, '-olas', '-i', infileConRuta],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=-1
            )
        lasDataMem, stderr = prc.communicate()
        if LCLverbose:
            print('clidaux-> subprocess ejecutado. type(lasDataMem): {} stderr: {}.'.format(type(lasDataMem), stderr))
        if not lasDataMem is None:
            if LCLverbose:
                print('\t-> len(lasDataMem): {}'.format(len(lasDataMem)))

        if prc.returncode != 0:
            print('clidaux-> Revisar este return code de %s: %d' % (laszip_binary, prc.returncode))
            # if stderr and len(stderr) < 2048:
            print(stderr)
            print('No se ha podido descomprimir el fichero laz en memoria, se prueba con fichero temporal')
            outfileLas = 'FicheroTemporal.las'
            outfileLasConRuta = os.path.join(rutaLazCompleta, outfileLas)
            print('\tSe crea el fichero las %s' % outfileLasConRuta)
            # print('\t\t%s -i %s -o %s' % (laszip_binary, infileConRuta, outfileLasConRuta))
            subprocess.call([laszip_binary, '-i', infileConRuta, '-o', outfileLasConRuta])
            # print('\tOk ejecutado laszip')
            lasDataMem = outfileLasConRuta
            # sys.exit(0)
    else:
        if GLO.GLBLficheroLasTemporal:
            outfileLas = 'FicheroTemporal.las'
        else:
            if infile[-4:] == '.las':
                outfileLas = infile.replace('.las', '.las_')
            elif infile[-4:] == '.laz':
                outfileLas = infile.replace('.laz', '.las')
            else:
                outfileLas = infile + '.las'
        outfileLasConRuta = os.path.join(rutaLazCompleta, outfileLas)
        if os.path.exists(outfileLasConRuta) and not sobreEscribirOutFile:
            printMsg(f'clidaux-> Fichero descomprimdo ya existe: {outfileLasConRuta}')
            return ''
        if LCLverbose:
            print('\tSe crea el fichero las %s' % outfileLasConRuta)
        # print('\t\t%s -i %s -o %s' % (laszip_binary, infileConRuta, outfileLasConRuta))
        subprocess.call([laszip_binary, '-i', infileConRuta, '-o', outfileLasConRuta])
        # print('\tOk ejecutado laszip')
        lasDataMem = outfileLasConRuta

        # #Ya no uso os.system() xq en linux no me funciona
        # if MAIN_ENTORNO == 'windows':
        #     ejecutar = laszip_binary + ' ' + infileConRuta + ' ' + outfileLasConRuta
        #     if GLO.GLBLverbose:
        #         print('\tcartolidar.%0.6i->' % GLO.MAINidProceso + 'Descomprimiendo con', laszip_binary)
        #         print('\t\t', ejecutar)
        #     os.system(ejecutar)

    if LCLverbose:
        printMsg('{:=^80}'.format(''))

    return lasDataMem


# ==============================================================================o
# ==============================================================================o
# ==============================================================================o
# Comodin
class Bloque2x2(object):
    def __init__(self, xInfIzda, yInfIzda, nCeldasX, nCeldasY, metrosPixel):
        self.xInfIzda = xInfIzda
        self.yInfIzda = yInfIzda
        self.nCeldasX = nCeldasX
        self.nCeldasY = nCeldasY
        self.xSupDcha = self.xInfIzda + (self.nCeldasX * metrosPixel)
        self.ySupDcha = self.yInfIzda + (self.nCeldasY * metrosPixel)
        self.numPuntosFueraDeBloque = 0
        self.hayPuntosDescartadosPorCotaAnomala = False
        self.hayPuntosConCotaExcesivaRptoAzMin = False
        self.numPuntosConCotaExcesivaRptoAzMin = 0
        self.cotaExcesivaMaximaRptoAzMin = 0
        self.hayPuntosConCotaExcesiva = False
        self.numPuntosConCotaExcesiva = 0
        self.cotaExcesivaMaxima = 0
        self.hayPuntosConCotaNegativa = False
        self.numPuntosConCotaNegativa = 0
        self.cotaNegativaMinima = 0
        self.primerIntento = True


class CeldaClass(object):
    def __init__(self, cX, cY, nCeldasX, nCeldasY, xInfIzda, yInfIzda, miHead, nBytesPorPunto):
        self.cX = cX
        self.cY = cY
        # self.xInfIzda = xInfIzda
        # self.yInfIzda = yInfIzda
        # self.nCeldasX = nCeldasX
        # self.nCeldasY = nCeldasY
        self.miHead = miHead
        self.nBytesPorPunto = nBytesPorPunto

    def celdaToBloc(self, cQ):
        bloc = np.zeros(10, dtype='int8')
        for nivel in range(10):
            bloc[nivel] = cQ % 2
            cQ = int(cQ / 2)
        return bloc

    def calculaOffsetDelIndice(self):
        # Offset desde el inicio del indice de blocs (despues del puntoIndiceGeneral)
        # print( 'Calculando offsets...', self.tipoIndice )
        self.offsetPtoFisicoPrimeroDesdeInicio = self.miHead['offset'] + (self.nBytesPorPunto * self.nPuntosIndice)

        if self.tipoIndice == 101:
            blocX = self.celdaToBloc(self.cX)
            blocY = self.celdaToBloc(self.cY)
            cX_ = sum([blocX[i] * (2 ** i) for i in range(0, len(blocX))])
            cY_ = sum([blocY[i] * (2 ** i) for i in range(0, len(blocY))])
            if cX_ != self.cX or cY_ != self.cY:
                print('\nCeldas mal calculadas', cX_, self.cX, cY_, self.cY)
            nCeldaSecuencial = 1
            for nivel in range(10):
                nCeldaSecuencial += blocX[nivel] * (2 ** (2 * nivel))
                nCeldaSecuencial += blocY[nivel] * (2 ** (2 * nivel)) * 2
            self.nCeldaSecuencial = nCeldaSecuencial
            print(blocX, blocY, 'Celda %i, %i -> Orden secuencial: %i' % (self.cX, self.cY, nCeldaSecuencial))
            self.offsetPtoIndiceBlocDesdeInicioIndice = self.nBytesPorPunto * (1 + self.nCeldaSecuencial)
        elif self.tipoIndice <= 0:
            # No hay indice
            self.offsetPtoIndiceBlocDesdeInicioIndice = 0  # Desconocido
            self.nCeldaSecuencial = 0
        elif self.tipoIndice < 100:
            # Indice matricial
            self.nCeldaSecuencial = (self.bY * self.nBlocsY) + self.bX
            self.offsetPtoIndiceBlocDesdeInicioIndice = self.nBytesPorPunto * (1 + self.nCeldaSecuencial)


# Sin uso
class BlocClass(object):
    def __init__(self, bX, bY, nBlocsX, nBlocsY, nCeldasX, nCeldasY, xInfIzda, yInfIzda, miHead, listaTuplasPropPtoTodas, nBytesPorPunto):
        self.bX = bX
        self.bY = bY
        self.nBlocsX = nBlocsX
        self.nBlocsY = nBlocsY

        self.xInfIzda = xInfIzda
        self.yInfIzda = yInfIzda
        self.nCeldasX = nCeldasX
        self.nCeldasY = nCeldasY
        self.miHead = miHead
        self.listaTuplasPropPtoTodas = listaTuplasPropPtoTodas
        self.nBytesPorPunto = nBytesPorPunto


# ==============================================================================#
def listarMetodos(object, spacing=10, collapse=1):
    'Listado de metodos del objeto "object" y doc strings. El objeto puede ser: modulo, clase, lista, dict o string'
    methodList = [method for method in dir(object) if callable(getattr(object, method))]
    processFunc = collapse and (lambda s: " ".join(s.split())) or (lambda s: s)
    print("\n".join(["%s %s" % (method.ljust(spacing), processFunc(str(getattr(object, method).__doc__))) for method in methodList]))


#!/usr/bin/env python
""" a small class for Principal Component Analysis
Usage:
        p = PCA( A, fraction=0.90 )
In:
        A: an array of e.g. 1000 observations x 20 variables, 1000 rows x 20 columns
        fraction: use principal components that account for e.g.
                90 % of the total variance

Out:
        p.U, p.d, p.Vt: from np.linalg.svd, A = U . d . Vt
        p.dinv: 1/d or 0, see NR
        p.eigen: the eigenvalues of A*A, in decreasing order (p.d**2).
                eigen[j] / eigen.sum() is variable j's fraction of the total variance;
                look at the first few eigen[] to see how many PCs get to 90 %, 95 % ...
        p.npc: number of principal components,
                e.g. 2 if the top 2 eigenvalues are >= `fraction` of the total.
                It's ok to change this; methods use the current value.

Methods:
        The methods of class PCA transform vectors or arrays of e.g.
        20 variables, 2 principal components and 1000 observations,
        using partial matrices U' d' Vt', parts of the full U d Vt:
        A ~ U' . d' . Vt' where e.g.
                U' is 1000 x 2
                d' is diag([ d0, d1 ]), the 2 largest singular values
                Vt' is 2 x 20.    Dropping the primes,

        d . Vt            2 principal vars = p.vars_pc( 20 vars )
        U                     1000 obs = p.pc_obs( 2 principal vars )
        U . d . Vt    1000 obs, p.obs( 20 vars ) = pc_obs( vars_pc( vars ))
                fast approximate A . vars, using the `npc` principal components

        Ut                            2 pcs = p.obs_pc( 1000 obs )
        V . dinv                20 vars = p.pc_vars( 2 principal vars )
        V . dinv . Ut     20 vars, p.vars( 1000 obs ) = pc_vars( obs_pc( obs )),
                fast approximate Ainverse . obs: vars that give ~ those obs.


Notes:
        PCA does not center or scale A; you usually want to first
                A -= A.mean(A, axis=0)
                A /= A.std(A, axis=0)
        with the little class Center or the like, below.

See also:
        http://en.wikipedia.org/wiki/Principal_component_analysis
        http://en.wikipedia.org/wiki/Singular_value_decomposition
        Press et al., Numerical Recipes (2 or 3 ed), SVD
        PCA micro-tutorial
        iris-pca .py .png

"""

# ...............................................................................
if __name__ == "__main__" and False:
    # ...............................................................................
    class PCA:
        def __init__(self, A, fraction=0.90):
            # __version__ = "2010-04-14 apr"
            # __author_email__ = "denis-bz-py at t-online dot de"
            assert 0 <= fraction <= 1
            # A = U . diag(d) . Vt, O( m n^2 ), lapack_lite --
            self.U, self.d, self.Vt = np.linalg.svd(A, full_matrices=False)
            assert np.all(self.d[:-1] >= self.d[1:])  # sorted
            self.eigen = self.d ** 2
            self.sumvariance = np.cumsum(self.eigen)
            self.sumvariance /= self.sumvariance[-1]
            self.npc = np.searchsorted(self.sumvariance, fraction) + 1
            self.dinv = np.array([1 / d if d > self.d[0] * 1e-6 else 0 for d in self.d])
    
            # dot = np.dot
            # import bz.numpyutil as nu
            # dot = nu.pdot
    
    
        def pc(self):
            """ e.g. 1000 x 2 U[:, :npc] * d[:npc], to plot etc. """
            n = self.npc
            return self.U[:, :n] * self.d[:n]
    
        # These 1-line methods may not be worth the bother;
        # then use U d Vt directly --
    
        def vars_pc(self, x):
            n = self.npc
            return self.d[:n] * np.dot(self.Vt[:n], x.T).T  # 20 vars -> 2 principal
    
        def pc_vars(self, p):
            n = self.npc
            return np.dot(self.Vt[:n].T, (self.dinv[:n] * p).T).T  # 2 PC -> 20 vars
    
        def pc_obs(self, p):
            n = self.npc
            return np.dot(self.U[:, :n], p.T)  # 2 principal -> 1000 obs
    
        def obs_pc(self, obs):
            n = self.npc
            return np.dot(self.U[:, :n].T, obs).T  # 1000 obs -> 2 principal
    
        def obs(self, x):
            return self.pc_obs(self.vars_pc(x))  # 20 vars -> 2 principal -> 1000 obs
    
        def vars(self, obs):
            return self.pc_vars(self.obs_pc(obs))  # 1000 obs -> 2 principal -> 20 vars
    
    
    class Center:
        """A -= A.mean() /= A.std(), inplace -- use A.copy() if need be
        uncenter(x) == original A . x
        """
    
        # mttiw
        def __init__(self, A, axis=0, scale=True, verbose=1):
            self.mean = A.mean(axis=axis)
            if verbose:
                print("Center -= A.mean:", self.mean)
            A -= self.mean
            if scale:
                std = A.std(axis=axis)
                self.std = np.where(std, std, 1.0)
                if verbose:
                    print("Center /= A.std:", self.std)
                A /= self.std
            else:
                self.std = np.ones(A.shape[-1])
            self.A = A
    
        def uncenter(self, x):
            return np.dot(self.A, x * self.std) + np.dot(x, self.mean)


    import sys

    csv = "iris4.csv"  # wikipedia Iris_flower_data_set
    # 5.1,3.5,1.4,0.2    # ,Iris-setosa ...
    N = 1000
    K = 20
    fraction = 0.90
    seed = 1
    ejecutable = "\n".join(sys.argv[1:])  # N= ...
    exec(ejecutable)
    np.random.seed(seed)
    np.set_printoptions(1, threshold=100, suppress=True)  # .1f
    try:
        A = np.genfromtxt(csv, delimiter=",")
        N, K = A.shape
    except IOError:
        A = np.random.normal(size=(N, K))  # gen correlated ?

    print("csv: %s    N: %d    K: %d    fraction: %.2g" % (csv, N, K, fraction))
    Center(A)
    print("A:", A)

    print(
        "PCA ...",
    )
    p = PCA(A, fraction=fraction)
    print("npc:", p.npc)
    print("% variance:", p.sumvariance * 100)

    print("Vt[0], weights that give PC 0:", p.Vt[0])
    print("A . Vt[0]:", np.dot(A, p.Vt[0]))
    print("pc:", p.pc())

    print("\nobs <-> pc <-> x: with fraction=1, diffs should be ~ 0")
    x = np.ones(K)
    # x = np.ones(( 3, K ))
    print("x:", x)
    pc = p.vars_pc(x)  # d' Vt' x
    print("vars_pc(x):", pc)
    print("back to ~ x:", p.pc_vars(pc))

    Ax = np.dot(A, x.T)
    pcx = p.obs(x)  # U' d' Vt' x
    print("Ax:", Ax)
    print("A'x:", pcx)
    print("max |Ax - A'x|: %.2g" % np.linalg.norm(Ax - pcx, np.inf))

    b = Ax  # ~ back to original x, Ainv A x
    back = p.vars(b)
    print("~ back again:", back)
    print("max |back - x|: %.2g" % np.linalg.norm(back - x, np.inf))


# ==============================================================================
def borrarFicheroDeConfiguracionTemporal():

    if GLO.GLBLeliminarTilesTrasProcesado:
        printMsg('\t-> clidaux-> Eliminando input images del entrenamiento del directorio {}'.format(GLO.GLBL_TRAIN_DIR))
        # Ver detalles en clidtry-> leerDirectoriosEnCalendula
        if os.path.isdir(GLO.GLBL_TRAIN_DIR):
            # Elimino el directorio y su contenido
            shutil.rmtree(GLO.GLBL_TRAIN_DIR)
    
            # Elimino fichero a fichero
            # for (thisPath1, filepaths, filenames) in os.walk(GLO.GLBL_TRAIN_DIR):
            #     for filename in filenames:
            #         print('\tBorrando: {}'.format(os.path.join(thisPath1, filename)))
            #     for filepath in filepaths:
            #         for (thisPath2, _, filenames) in os.walk(os.path.join(filepath, GLO.GLBL_TRAIN_DIR)):
            #             print('\tBorrando: {}'.format(os.path.join(thisPath2, filename)))


    configFileNameCfg = sys.argv[0].replace('.py', '%06i.cfg' % MAINidProceso)
    if os.path.exists(configFileNameCfg):
        print('clidaux-> Eliminando {}'.format(configFileNameCfg))
        os.remove(configFileNameCfg)
    #configFileNameXlsx = sys.argv[0].replace('.py', '%06i.xlsx' % MAINidProceso)
    configFileNameXlsx = sys.argv[0].replace('.py', '{:006}.xlsx'.format(MAINidProceso))
    if os.path.exists(configFileNameXlsx):
        print('clidaux-> Eliminando {}'.format(configFileNameXlsx))
        os.remove(configFileNameXlsx)


# ==============================================================================
# Progress bar copiado literal de: https://github.com/verigak/progress
HIDE_CURSOR = '\x1b[?25l'
SHOW_CURSOR = '\x1b[?25h'
# ==============================================================================
class Infinite(object):
    file = sys.stderr
    sma_window = 10         # Simple Moving Average window
    check_tty = True
    hide_cursor = True

    def __init__(self, message='', **kwargs):
        self.index = 0
        try:
            self.start_ts = time.monotonic()
        except:
            self.start_ts = time.time.monotonic()
        self.avg = 0
        self._avg_update_ts = self.start_ts
        self._ts = self.start_ts
        self._xput = deque(maxlen=self.sma_window)
        for key, val in kwargs.items():
            setattr(self, key, val)

        self._max_width = 0
        self._hidden_cursor = False
        self.message = message

        if self.file and self.is_tty():
            if self.hide_cursor:
                print(HIDE_CURSOR, end='', file=self.file)
                self._hidden_cursor = True
        self.writeln('')

    def __del__(self):
        if self._hidden_cursor:
            print(SHOW_CURSOR, end='', file=self.file)

    def __getitem__(self, key):
        if key.startswith('_'):
            return None
        return getattr(self, key, None)

    @property
    def elapsed(self):
        try:
            return int(time.monotonic() - self.start_ts)
        except:
            return int(time.time.monotonic() - self.start_ts)

    @property
    def elapsed_td(self):
        return timedelta(seconds=self.elapsed)

    def update_avg(self, n, dt):
        if n > 0:
            xput_len = len(self._xput)
            self._xput.append(dt / n)
            try:
                now = time.monotonic()
            except:
                now = time.time.monotonic()
            # update when we're still filling _xput, then after every second
            if (xput_len < self.sma_window or
                    now - self._avg_update_ts > 1):
                self.avg = sum(self._xput) / len(self._xput)
                self._avg_update_ts = now

    def update(self):
        pass

    def start(self):
        pass

    def writeln(self, line):
        if self.file and self.is_tty():
            width = len(line)
            if width < self._max_width:
                # Add padding to cover previous contents
                line += ' ' * (self._max_width - width)
            else:
                self._max_width = width
            print('\r' + line, end='', file=self.file)
            self.file.flush()

    def finish(self):
        if self.file and self.is_tty():
            print(file=self.file)
            if self._hidden_cursor:
                print(SHOW_CURSOR, end='', file=self.file)
                self._hidden_cursor = False

    def is_tty(self):
        try:
            return self.file.isatty() if self.check_tty else True
        except AttributeError:
            msg = "%s has no attribute 'isatty'. Try setting check_tty=False." % self
            raise AttributeError(msg)

    def next(self, n=1):
        try:
            now = time.monotonic()
        except:
            now = time.time.monotonic()
        dt = now - self._ts
        self.update_avg(n, dt)
        self._ts = now
        self.index = self.index + n
        self.update()

    def iter(self, it):
        self.iter_value = None
        with self:
            for x in it:
                self.iter_value = x
                yield x
                self.next()
        del self.iter_value

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.finish()


# ==============================================================================
class Progress(Infinite):
    def __init__(self, *args, **kwargs):
        super(Progress, self).__init__(*args, **kwargs)
        self.max = kwargs.get('max', 100)

    @property
    def eta(self):
        return int(math.ceil(self.avg * self.remaining))

    @property
    def eta_td(self):
        return timedelta(seconds=self.eta)

    @property
    def percent(self):
        return self.progress * 100

    @property
    def progress(self):
        if self.max == 0:
            return 0
        return min(1, self.index / self.max)

    @property
    def remaining(self):
        return max(self.max - self.index, 0)

    def start(self):
        self.update()

    def goto(self, index):
        incr = index - self.index
        self.next(incr)

    def iter(self, it):
        try:
            self.max = len(it)
        except TypeError:
            pass

        self.iter_value = None
        with self:
            for x in it:
                self.iter_value = x
                yield x
                self.next()
        del self.iter_value


# ==============================================================================
class Bar(Progress):
    width = 32
    suffix = '%(index)d/%(max)d'
    bar_prefix = ' |'
    bar_suffix = '| '
    empty_fill = ' '
    fill = '#'
    color = None

    def update(self):
        filled_length = int(self.width * self.progress)
        empty_length = self.width - filled_length

        message = self.message % self
        bar = color(self.fill * filled_length, fg=self.color)
        empty = self.empty_fill * empty_length
        suffix = self.suffix % self
        line = ''.join([message, self.bar_prefix, bar, empty, self.bar_suffix,
                        suffix])
        self.writeln(line)


class ChargingBar(Bar):
    suffix = '%(percent)d%%'
    bar_prefix = ' '
    bar_suffix = ' '
    empty_fill = '∙'
    fill = '█'


class FillingSquaresBar(ChargingBar):
    empty_fill = '▢'
    fill = '▣'


class FillingCirclesBar(ChargingBar):
    empty_fill = '◯'
    fill = '◉'


class IncrementalBar(Bar):
    if sys.platform.startswith('win'):
        phases = (u' ', u'▌', u'█')
    else:
        phases = (' ', '▏', '▎', '▍', '▌', '▋', '▊', '▉', '█')

    def update(self):
        nphases = len(self.phases)
        filled_len = self.width * self.progress
        nfull = int(filled_len)                      # Number of full chars
        phase = int((filled_len - nfull) * nphases)  # Phase of last char
        nempty = self.width - nfull                  # Number of empty chars

        message = self.message % self
        bar = color(self.phases[-1] * nfull, fg=self.color)
        current = self.phases[phase] if phase > 0 else ''
        empty = self.empty_fill * max(0, nempty - len(current))
        suffix = self.suffix % self
        line = ''.join([message, self.bar_prefix, bar, current, empty,
                        self.bar_suffix, suffix])
        self.writeln(line)


class PixelBar(IncrementalBar):
    phases = ('⡀', '⡄', '⡆', '⡇', '⣇', '⣧', '⣷', '⣿')


class ShadyBar(IncrementalBar):
    phases = (' ', '░', '▒', '▓', '█')


# ==============================================================================
def color(s, fg=None, bg=None, style=None):
    COLORS = ('black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan',
              'white')
    STYLES = ('bold', 'faint', 'italic', 'underline', 'blink', 'blink2',
              'negative', 'concealed', 'crossed')
    sgr = []

    if fg:
        if fg in COLORS:
            sgr.append(str(30 + COLORS.index(fg)))
        elif isinstance(fg, int) and 0 <= fg <= 255:
            sgr.append('38;5;%d' % int(fg))
        else:
            raise Exception('Invalid color "%s"' % fg)

    if bg:
        if bg in COLORS:
            sgr.append(str(40 + COLORS.index(bg)))
        elif isinstance(bg, int) and 0 <= bg <= 255:
            sgr.append('48;5;%d' % bg)
        else:
            raise Exception('Invalid color "%s"' % bg)

    if style:
        for st in style.split('+'):
            if st in STYLES:
                sgr.append(str(1 + STYLES.index(st)))
            else:
                raise Exception('Invalid style "%s"' % st)

    if sgr:
        prefix = '\x1b[' + ';'.join(sgr) + 'm'
        suffix = '\x1b[0m'
        return prefix + s + suffix
    else:
        return s


# ==============================================================================
# Foreground shortcuts
black = partial(color, fg='black')
red = partial(color, fg='red')
green = partial(color, fg='green')
yellow = partial(color, fg='yellow')
blue = partial(color, fg='blue')
magenta = partial(color, fg='magenta')
cyan = partial(color, fg='cyan')
white = partial(color, fg='white')

# Style shortcuts
bold = partial(color, style='bold')
faint = partial(color, style='faint')
italic = partial(color, style='italic')
underline = partial(color, style='underline')
blink = partial(color, style='blink')
blink2 = partial(color, style='blink2')
negative = partial(color, style='negative')
concealed = partial(color, style='concealed')
crossed = partial(color, style='crossed')


# ==============================================================================
def foo():
    pass



# Basura
# c:/fusion/gridsurfacecreate "338-4630_groundfilter.dtm" 10 M M 1 0 0 0 PNOA_2010_LOTE4_CYL_338-4630_ORT-CLA-COL.LAS
# funcion3+" "+str(parametros3_1)+" "+entrada3_1+" "+str(parametros3_2)+" "+salida3+" "+ entrada3_2
# c:/fusion/gridmetrics /minht:0.25 /nointensity 338-4630_groundfilter.dtm 0.25 10 338-4630_metric.csv PNOA_2010_LOTE4_CYL_338-4630_ORT-CLA-COL.LAS
# ==============================================================================
'''
from osgeo import ogr, osr, gdal
from gdalconst import *
import gdalnumeric

#Atencion al orden de carga:
#1. C:\\Python27\\Lib\\site-packages\\GDAL-1.11.2-py2.7.egg-info (este es el gdal con GEOS)
#2. C:\_app\gdal
#3. C:\_app\gdal\gdalplugins (para acceder a las dll:

# Si carga:
#     C:\Python27\lib\site-packages\osgeo\_gdal.pyd
# No tiene acceso a:
#     C:\_app\GDAL\gdalplugins\gdal_BAG.dll
#     C:\_app\GDAL\gdalplugins\gdal_BAG.dll
#     C:\_app\GDAL\gdalplugins\gdal_FITS.dll
#     C:\_app\GDAL\gdalplugins\gdal_FITS.dll
#     C:\_app\GDAL\gdalplugins\gdal_GMT.dll
#     C:\_app\GDAL\gdalplugins\gdal_GMT.dll
#     C:\_app\GDAL\gdalplugins\gdal_HDF4.dll
#     C:\_app\GDAL\gdalplugins\gdal_HDF4.dll
#     C:\_app\GDAL\gdalplugins\gdal_HDF4Image.dll
#     C:\_app\GDAL\gdalplugins\gdal_HDF4Image.dll
#     C:\_app\GDAL\gdalplugins\gdal_HDF5.dll
#     C:\_app\GDAL\gdalplugins\gdal_HDF5.dll
#     C:\_app\GDAL\gdalplugins\gdal_HDF5Image.dll
#     C:\_app\GDAL\gdalplugins\gdal_HDF5Image.dll
#     C:\_app\GDAL\gdalplugins\gdal_KEA.dll
#     C:\_app\GDAL\gdalplugins\gdal_KEA.dll
#     C:\_app\GDAL\gdalplugins\gdal_netCDF.dll
#     C:\_app\GDAL\gdalplugins\gdal_netCDF.dll


CAPA_CYL = r'O:/Sigmena/Carto/DIV_ADMI/GENERAL/auton_ign_e25_etrs89.shp'
inputDatasetVector = ogr.Open(CAPA_CYL, False)
for layer in inputDatasetVector:
    print( 'Layer: "%s"' % (layer.GetName()) )
ogrInputLayer = inputDatasetVector.GetLayer(0)
print( 'inputLayer.GetSpatialRef():', type(ogrInputLayer.GetSpatialRef()) #<class 'osgeo.osr.SpatialReference'>    )
print( ogrInputLayer.GetSpatialRef() #PROJCS["ETRS89_UTM_zone_30N_N_E", etc. )
print( 'Poligonos en la capa CyL', ogrInputLayer.GetFeatureCount() )
ogrInputLayer.ResetReading()
feature = ogrInputLayer.GetNextFeature()
if feature is None:
    print( 'Error de feature' )
fid = feature.GetFID()
print( 'First feature:', fid )
geom = feature.GetGeometryRef()
print( 'geom:', type(geom), dir(geom) )
#['AddGeometry', 'AddGeometryDirectly', 'AddPoint', 'AddPoint_2D', 'Area', 'AssignSpatialReference', 'Boundary', 'Buffer', 'Centroid', 'Clone', 'CloseRings', 'Contains', 'ConvexHull', 'Crosses', 'Destroy', 'Difference', 'Disjoint', 'Distance', 'Empty', 'Equal', 'Equals', 'ExportToGML', 'ExportToJson', 'ExportToKML', 'ExportToWkb', 'ExportToWkt', 'FlattenTo2D', 'GetArea', 'GetBoundary', 'GetCoordinateDimension', 'GetDimension', 'GetEnvelope', 'GetEnvelope3D', 'GetGeometryCount', 'GetGeometryName', 'GetGeometryRef', 'GetGeometryType', 'GetPoint', 'GetPointCount', 'GetPoint_2D', 'GetPoints', 'GetSpatialReference', 'GetX', 'GetY', 'GetZ', 'Intersect', 'Intersection', 'Intersects', 'IsEmpty', 'IsRing', 'IsSimple', 'IsValid', 'Length', 'Overlaps', 'PointOnSurface', 'Segmentize', 'SetCoordinateDimension', 'SetPoint', 'SetPoint_2D', 'Simplify', 'SimplifyPreserveTopology', 'SymDifference', 'SymmetricDifference', 'Touches', 'Transform', 'TransformTo', 'Union', 'UnionCascaded', 'Within', 'WkbSize', '__class__', '__del__', '__delattr__', '__dict__', '__doc__', '__format__', '__getattr__', '__getattribute__', '__hash__', '__init__', '__iter__', '__module__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__setstate__', '__sizeof__', '__str__', '__subclasshook__', '__swig_destroy__', '__swig_getmethods__', '__swig_setmethods__', '__weakref__', 'next', 'this']

print( '1.', 'geom.GetCoordinateDimension:', type(geom.GetCoordinateDimension()), geom.GetCoordinateDimension() #<type 'int'> 2 )
#print( '2.', 'geom.GetEnvelope:', type(geom.GetEnvelope()), geom.GetEnvelope() #<type 'tuple'> )
#print( '3.', 'geom.Boundary:', type(geom.Boundary()), geom.Boundary() #<class 'osgeo.ogr.Geometry'> )
#['AddGeometry', 'AddGeometryDirectly', 'AddPoint', 'AddPoint_2D', 'Area', 'AssignSpatialReference', 'Boundary', 'Buffer', 'Centroid', 'Clone', 'CloseRings', 'Contains', 'ConvexHull', 'Crosses', 'Destroy', 'Difference', 'Disjoint', 'Distance', 'Empty', 'Equal', 'Equals', 'ExportToGML', 'ExportToJson', 'ExportToKML', 'ExportToWkb', 'ExportToWkt', 'FlattenTo2D', 'GetArea', 'GetBoundary', 'GetCoordinateDimension', 'GetDimension', 'GetEnvelope', 'GetEnvelope3D', 'GetGeometryCount', 'GetGeometryName', 'GetGeometryRef', 'GetGeometryType', 'GetPoint', 'GetPointCount', 'GetPoint_2D', 'GetPoints', 'GetSpatialReference', 'GetX', 'GetY', 'GetZ', 'Intersect', 'Intersection', 'Intersects', 'IsEmpty', 'IsRing', 'IsSimple', 'IsValid', 'Length', 'Overlaps', 'PointOnSurface', 'Segmentize', 'SetCoordinateDimension', 'SetPoint', 'SetPoint_2D', 'Simplify', 'SimplifyPreserveTopology', 'SymDifference', 'SymmetricDifference', 'Touches', 'Transform', 'TransformTo', 'Union', 'UnionCascaded', 'Within', 'WkbSize', '__class__', '__del__', '__delattr__', '__dict__', '__doc__', '__format__', '__getattr__', '__getattribute__', '__hash__', '__init__', '__iter__', '__module__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__setstate__', '__sizeof__', '__str__', '__subclasshook__', '__swig_destroy__', '__swig_getmethods__', '__swig_setmethods__', '__weakref__', 'next', 'this']
#LINESTRING (460014.72542665247 4670908.0633002184,460267.40251024353 4670906.7403835505,460270.04834357958 4670672.5841333121,460013.40250998444 4670680.5216333196,460014.72542665247 4670908.0633002184)
#print( '4.', 'geom.GetBoundary:', type(geom.GetBoundary()), geom.GetBoundary() #<class 'osgeo.ogr.Geometry'> )
#['AddGeometry', 'AddGeometryDirectly', 'AddPoint', 'AddPoint_2D', 'Area', 'AssignSpatialReference', 'Boundary', 'Buffer', 'Centroid', 'Clone', 'CloseRings', 'Contains', 'ConvexHull', 'Crosses', 'Destroy', 'Difference', 'Disjoint', 'Distance', 'Empty', 'Equal', 'Equals', 'ExportToGML', 'ExportToJson', 'ExportToKML', 'ExportToWkb', 'ExportToWkt', 'FlattenTo2D', 'GetArea', 'GetBoundary', 'GetCoordinateDimension', 'GetDimension', 'GetEnvelope', 'GetEnvelope3D', 'GetGeometryCount', 'GetGeometryName', 'GetGeometryRef', 'GetGeometryType', 'GetPoint', 'GetPointCount', 'GetPoint_2D', 'GetPoints', 'GetSpatialReference', 'GetX', 'GetY', 'GetZ', 'Intersect', 'Intersection', 'Intersects', 'IsEmpty', 'IsRing', 'IsSimple', 'IsValid', 'Length', 'Overlaps', 'PointOnSurface', 'Segmentize', 'SetCoordinateDimension', 'SetPoint', 'SetPoint_2D', 'Simplify', 'SimplifyPreserveTopology', 'SymDifference', 'SymmetricDifference', 'Touches', 'Transform', 'TransformTo', 'Union', 'UnionCascaded', 'Within', 'WkbSize', '__class__', '__del__', '__delattr__', '__dict__', '__doc__', '__format__', '__getattr__', '__getattribute__', '__hash__', '__init__', '__iter__', '__module__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__setstate__', '__sizeof__', '__str__', '__subclasshook__', '__swig_destroy__', '__swig_getmethods__', '__swig_setmethods__', '__weakref__', 'next', 'this']
#LINESTRING (460014.72542665247 4670908.0633002184,460267.40251024353 4670906.7403835505,460270.04834357958 4670672.5841333121,460013.40250998444 4670680.5216333196,460014.72542665247 4670908.0633002184)
#print( '5.', 'geom.GetDimension:', type(geom.GetDimension()), geom.GetDimension() #<type 'int'> 2 )
#print( '6.', 'geom.GetGeometryRef:', type(geom.GetGeometryRef()), dir(geom.GetGeometryRef()) geom.GetGeometryRef() )
#print( '7.', 'geom.Length():', type(geom.Length()), geom.Length() )

pts = geom.GetGeometryRef(0)
print( 'pts:', type(pts), dir(pts) )
print( 'Numero de puntos del perimetro CyL:', pts.GetPointCount() )

#for miPto in range(pts.GetPointCount()):
#for miPto in range(pts.GetPointCount()):
#    #print( miPto, type(pts.GetX(miPto)), pts.GetX(miPto), pts.GetY(miPto) #<type 'float'> )
#    perimetro.append((pts.GetX(miPto), pts.GetY(miPto))) #Agrega una tupla de dos valores, X e Y
inputDatasetVector.Destroy()
#quit()'''


# Ver Reading Raster Data en: http://www.gdal.org/gdal_tutorial.html
# Ver la Class Dataset en: http://gdal.org/python/osgeo.gdal.Dataset-class.html
# Aqui se recoge el metodo ReadRaster() de esta clase:
#    ReadRaster(self, xoff, yoff, xsize, ysize, buf_xsize=None, buf_ysize=None, buf_type=None, band_list=None, buf_pixel_space=None, buf_line_space=None, buf_band_space=None)
'''
 786 -        def ReadRaster(self, xoff, yoff, xsize, ysize, 
 787                                         buf_xsize = None, buf_ysize = None, buf_type = None, 
 788                                         band_list = None, 
 789                                         buf_pixel_space = None, buf_line_space = None, buf_band_space = None ): 
 790     
 791                    if band_list is None: 
 792                            band_list = range(1,self.RasterCount+1) 
 793                    if buf_xsize is None: 
 794                            buf_xsize = xsize; 
 795                    if buf_ysize is None: 
 796                            buf_ysize = ysize; 
 797     
 798                    if buf_type is None: 
 799                            buf_type = self.GetRasterBand(1).DataType; 
 800     
 801                    return _gdal.Dataset_ReadRaster1(self, xoff, yoff, xsize, ysize, 
 802                                                                                            buf_xsize, buf_ysize, buf_type, 
 803                                                                                            band_list, buf_pixel_space, buf_line_space, buf_band_space ) 
'''
'''
 753 -        def ReadRaster1(self, *args, **kwargs): 
 754                    """ 
 755                    ReadRaster1(self, int xoff, int yoff, int xsize, int ysize, int buf_xsize = None,    
 756                            int buf_ysize = None, GDALDataType buf_type = None,    
 757                            int band_list = 0, int buf_pixel_space = None,    
 758                            int buf_line_space = None,    
 759                            int buf_band_space = None) -> CPLErr 
 760                    """ 
 761                    return _gdal.Dataset_ReadRaster1(self, *args, **kwargs) 
'''

# There are a few ways to read raster data, but the most common is via the GDALRasterBand::RasterIO() method.
# This method will automatically take care of data type conversion, up/down sampling and windowing.
# The following code will read the first scanline of data into a similarly sized buffer, converting it to floating point as part of the operation.
#    Rpta = band.ReadRaster(xoff, yoff, xsize, ysize, buf_xsize = None, buf_ysize = None, buf_type = None):
# Ejemplo para leer una linea:
#    scanline = band.ReadRaster( 0, 0, band.XSize, 1, \
#                                                            band.XSize, 1, GDT_Float32 )
# Note that the returned scanline is of type string, and contains xsize*4 bytes of raw binary floating point data.
# This can be converted to Python values using the struct module from the standard library:
#    import struct
#    tuple_of_floats = struct.unpack('f' * b2.XSize, scanline)
'''
The RasterIO call takes the following arguments.
CPLErr GDALRasterBand::RasterIO( GDALRWFlag eRWFlag,
                                                                 int nXOff, int nYOff, int nXSize, int nYSize,
                                                                 void * pData, int nBufXSize, int nBufYSize,
                                                                 GDALDataType eBufType,
                                                                 int nPixelSpace,
                                                                 int nLineSpace )
Note that the same RasterIO() call is used to read, or write based on the setting of eRWFlag (either GF_Read or GF_Write).
The nXOff, nYOff, nXSize, nYSize argument describe the window of raster data on disk to read (or write).
It doesn't have to fall on tile boundaries though access may be more efficient if it does.
The pData is the memory buffer the data is read into, or written from.
It's real type must be whatever is passed as eBufType, such as GDT_Float32, or GDT_Byte.
The RasterIO() call will take care of converting between the buffer's data type and the data type of the band.
Note that when converting floating point data to integer RasterIO() round down, 
and when converting source values outside the legal range of the output the nearest legal value is used. 
This implies, for instance, that 16bit data read into a GDT_Byte buffer will map all values greater than 255 to 255, the data is not scaled!
The nBufXSize and nBufYSize values describe the size of the buffer. 
When loading data at full resolution this would be the same as the window size. 
However, to load a reduced resolution overview this could be set to smaller than the window on disk. 
In this case the RasterIO() will utilize overviews to do the IO more efficiently if the overviews are suitable.
The nPixelSpace, and nLineSpace are normally zero indicating that default values should be used. 
However, they can be used to control access to the memory data buffer, 
allowing reading into a buffer containing other pixel interleaved data for instance
'''

'''
Se puede usar:
    ReadRaster() y struct.unpack()
    ReadAsArray() y numpy()


De: http://gis.stackexchange.com/questions/46893/how-do-i-get-the-pixel-value-of-a-gdal-raster-under-an-ogr-point-without-numpy
from osgeo import gdal,ogr
import struct

src_filename = '/tmp/test.tif'
shp_filename = '/tmp/test.shp'

src_ds=gdal.Open(src_filename) 
gt=src_ds.GetGeoTransform()
rb=src_ds.GetRasterBand(1)

ds=ogr.Open(shp_filename)
lyr=ds.GetLayer()
for feat in lyr:
        geom = feat.GetGeometryRef()
        mx,my=geom.GetX(), geom.GetY()    #coord in map units

        #Convert from map to pixel coordinates.
        #Only works for geotransforms with no rotation.
        pointX = int((mx - gt[0]) / gt[1]) #x pixel
        pointY = int((my - gt[3]) / gt[5]) #y pixel

        structval=rb.ReadRaster(pointX,pointY,1,1,buf_type=gdal.GDT_UInt16) #Assumes 16 bit int aka 'short'
        intval = struct.unpack('h' , structval) #use the 'short' format code (2 bytes) not int (4 bytes)

        print( intval[0] #intval is a tuple, length=1 as we only asked for 1 pixel value )



#Alternatively, since the reason you gave for not using numpy was to avoid reading the entire array in using ReadAsArray(), below is an example that uses numpy and does not read the entire raster in.

from osgeo import gdal,ogr
import struct

src_filename = '/tmp/test.tif'
shp_filename = '/tmp/test.shp'

src_ds=gdal.Open(src_filename) 
gt=src_ds.GetGeoTransform()
rb=src_ds.GetRasterBand(1)

ds=ogr.Open(shp_filename)
lyr=ds.GetLayer()
for feat in lyr:
        geom = feat.GetGeometryRef()
        mx,my=geom.GetX(), geom.GetY()    #coord in map units

        #Convert from map to pixel coordinates.
        #Only works for geotransforms with no rotation.
        pointX = int((mx - gt[0]) / gt[1]) #x pixel
        pointY = int((my - gt[3]) / gt[5]) #y pixel

        intval=rb.ReadAsArray(pointX,pointY,1,1)
        print intval[0] #intval is a numpy array, length=1 as we only asked for 1 pixel value
        
'''

'''
def mad_based_outlier(miLista, thresh=10):
    if type(miLista) != numpy.ndarray:
        miArray = numpy.array(miLista)
    print(type(miLista))
    print(type(miArray))
    if len(miArray.shape) == 1:
        miArray = miArray[:,None]
    median = numpy.median(miArray, axis=0)
    diff = numpy.sqrt(numpy.sum((miArray - median)**2, axis=-1))
    #Esto es una especie de desviacion tipica respecto a la mediana (en vez de rpto a la media):
    med_abs_deviation = numpy.median(diff)
    #Rango semi intercuartilar para la distribucion normal = 0.6745 * desviacion tipica = (Q3 - Q1) / 2
    #Considero outliers los que superan 10 veces ese rango
    modified_z_score = 0.6745 * diff / med_abs_deviation
    return modified_z_score > thresh

def mascara(data, selectors):
    # compress('ABCDEF', [1,0,1,0,1,1]) --> A C E F
    return (d for d, s in zip(data, selectors) if s)

for r in range(10):
    x = [1, 5, 6, 8, 9, 8, 7, 50]
    y = mad_based_outlier(x,r)
    print(x)
    #print(y)
    outliers = mascara(x, y)
    print(outliers)
'''
