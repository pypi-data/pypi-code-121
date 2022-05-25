#!/usr/bin/python
# -*- coding: UTF-8 -*-
'''
Module included in cartolidar project (clidtools package)
cartolidar: tools for Lidar processing focused on Spanish PNOA datasets

clidtwins provides classes and functions that can be used to search for
areas similar to a reference one in terms of dasometric Lidar variables (DLVs).
DLVs (Daso Lidar Vars): vars that characterize forest or land cover structure.

@author:     Jose Bengoa
@copyright:  2022 @clid
@license:    GNU General Public License v3 (GPLv3)
@contact:    cartolidar@gmail.com
'''
# -*- coding: latin-1 -*-

import os
import sys
import unicodedata
import warnings
import pathlib
# import random

import numpy as np
import numpy.ma as ma
from scipy.spatial import distance_matrix
# from scipy.spatial import KDTree
import matplotlib.pyplot as plt
from configparser import RawConfigParser
try:
    import psutil
    psutilOk = True
except:
    psutilOk = False
try:
    import gdal, ogr, gdalconst
    # import osr, gdalnumeric
    gdalOk = True
except:
    gdalOk = False

# ==============================================================================
# Verbose provisional para la version alpha
if '-vvv' in sys.argv:
    __verbose__ = 3
elif '-vv' in sys.argv:
    __verbose__ = 2
elif '-v' in sys.argv or '--verbose' in sys.argv:
    __verbose__ = 1
else:
    __verbose__ = 0
if __verbose__ > 2:
    print(f'clidtwins-> __name__:     <{__name__}>')
    print(f'clidtwins-> __package__ : <{__package__ }>')
# ==============================================================================

# ==============================================================================
try:
    from cartolidar.clidax import clidconfig
    from cartolidar.clidax import clidraster
    from cartolidar.clidtools.clidtwins_config import GLO
except:
    if __verbose__ > 2:
        print(f'qlidtwins-> Se importan clidconfig y clidraster desde clidtwins del directorio local {os.getcwd()}/clidtools')
        print('\tNo hay vesion de cartolidar instalada en site-packages.')
    from clidax import clidconfig
    from clidax import clidraster
    from clidtools.clidtwins_config import GLO
# Alternativa, si necesitara algun otro infreciente de clidtwins_config:
# from cartolidar.clidtools import clidtwins_config as CNFG
# ==============================================================================
# Nota: en clidtwins_config se asignan algunos parametros de configuracion que
# no se usan en clidtwins: pero se mantienen porque se usan en otros modulos
# de cartolidar, como son las funciones compartidas con clidmerge.py
# ==============================================================================

# ==============================================================================
TRNS_buscarBloquesSoloDentroDelMarcoUTM = False
# TRNSmostrarClusterMatch = False # Se define mas adelante
MINIMO_PIXELS_POR_CLUSTER = 5
# TB = '\t'
TB = ' ' * 12
TV = ' ' * 2
# ==============================================================================


# ==============================================================================
class DasoLidarSource:
    """Main Class of clidtwins module with the methods needed to search source
files, analyze Dasolidar Variables (DLVs) and check o locate similar areas to
the reference one(s) in terms of DLVs."""

    # ==========================================================================
    # Se leen los argumentos y se convierte la listLstDasoVars en listas individuales:
    # FileTypes, NickNames, RangoLinf, RangoLsup, NumClases, Movilidad, Ponderado,
    def __init__(
            self,
            LCL_leer_extra_args=0,  # optional
            LCL_menuInteractivo=GLO.GLBLmenuInteractivoPorDefecto,  # extra: 0
            LCL_outRasterDriver=GLO.GLBLoutRasterDriverPorDefecto,  # extra: 'GTiff'
            LCL_outputSubdirNew=GLO.GLBLoutputSubdirNewPorDefecto,  # extra: 'dasoLayers'
            LCL_cartoMFErecorte=GLO.GLBLcartoMFErecortePorDefecto,  # extra: 'mfe50rec'
            LCL_varsTxtFileName=GLO.GLBLvarsTxtFileNamePorDefecto,  # extra: 'rangosDeDeferencia.txt'
            LCL_ambitoTiffNuevo=GLO.GLBLambitoTiffNuevoPorDefecto,  # extra: 'loteAsc'
            LCL_noDataTiffProvi=GLO.GLBLnoDataTiffProviPorDefecto,  # extra: -8888
            LCL_noDataTiffFiles=GLO.GLBLnoDataTiffFilesPorDefecto,  # extra: -9999
            LCL_noDataTipoDMasa=GLO.GLBLnoDataTipoDMasaPorDefecto,  # extra: 255
            LCL_umbralMatriDist=GLO.GLBLumbralMatriDistPorDefecto,  # extra: 20
            LCL_verbose=__verbose__,  # optional
        ):
        """Instantiation of DasoLidarSource Class with asignation of some optional extra arguments
that usually take the default values (from configuration file or clidtwins_config.py module
    Attributes
    ----------
    LCL_leer_extra_args : bool
        Default: False (optional)
    LCL_menuInteractivo
        Default: param GLBLmenuInteractivoPorDefecto from cfg file (0)
    LCL_outRasterDriver : str
        Default: param GLBLoutRasterDriverPorDefecto from cfg file ('GTiff')
    LCL_outputSubdirNew : str
        Default: param GLBLoutputSubdirNewPorDefecto from cfg file ('dasoLayers')
    LCL_cartoMFErecorte : str
        Default: param GLBLcartoMFErecortePorDefecto from cfg file ('mfe50rec')
    LCL_varsTxtFileName : str
        Default: param GLBLvarsTxtFileNamePorDefecto from cfg file ('rangosDeDeferencia.txt')
    LCL_ambitoTiffNuevo : str
        Default: param GLBLambitoTiffNuevoPorDefecto from cfg file ('loteAsc')
    LCL_noDataTiffProvi : int
        Default: param GLBLnoDataTiffProviPorDefecto from cfg file (-8888)
    LCL_noDataTiffFiles : int
        Default: param GLBLnoDataTiffFilesPorDefecto from cfg file (-9999)
    LCL_noDataTipoDMasa : int
        Default: param GLBLnoDataTipoDMasaPorDefecto from cfg file (255)
    LCL_umbralMatriDist : int
        Default: param GLBLumbralMatriDistPorDefecto from cfg file (20)
    LCL_verbose : bool
        Default: __verbose__ (optional)
"""
        self.LOCLverbose = LCL_verbose

        # Esto parece redundante con el valor por defecto de estos parametros.
        # Sin embargo, no lo es porque el argumento LCL_leer_extra_args,
        # fuerza, si es True, a usar los parametros por defecto. Uso esta modalidad
        # a pesar de que la forma canonica de python para argumentos por defecto es
        # usar None y asignar despues el valor que corresponda si el parametro es None.
        if LCL_leer_extra_args:
            self.GLBLmenuInteractivo = LCL_menuInteractivo
            self.GLBLoutRasterDriver = LCL_outRasterDriver
            self.GLBLoutputSubdirNew = LCL_outputSubdirNew
            self.GLBLcartoMFErecorte = LCL_cartoMFErecorte
            self.GLBLvarsTxtFileName = LCL_varsTxtFileName
            self.GLBLambitoTiffNuevo = LCL_ambitoTiffNuevo
            self.GLBLnoDataTiffProvi = LCL_noDataTiffProvi
            self.GLBLnoDataTiffFiles = LCL_noDataTiffFiles
            self.GLBLnoDataTipoDMasa = LCL_noDataTipoDMasa
            self.GLBLumbralMatriDist = LCL_umbralMatriDist
        else:
            self.GLBLmenuInteractivo = GLO.GLBLmenuInteractivoPorDefecto  # p.ej.: 0
            self.GLBLoutRasterDriver = GLO.GLBLoutRasterDriverPorDefecto  # p.ej.: 'GTiff'
            self.GLBLoutputSubdirNew = GLO.GLBLoutputSubdirNewPorDefecto  # p.ej.: 'dasoLayers'
            self.GLBLcartoMFErecorte = GLO.GLBLcartoMFErecortePorDefecto  # p.ej.: 'mfe50rec'
            self.GLBLvarsTxtFileName = GLO.GLBLvarsTxtFileNamePorDefecto  # p.ej.: 'rangosDeDeferencia.txt'
            self.GLBLambitoTiffNuevo = GLO.GLBLambitoTiffNuevoPorDefecto  # p.ej.: 'loteAsc'
            self.GLBLnoDataTiffProvi = GLO.GLBLnoDataTiffProviPorDefecto  # p.ej.: -8888
            self.GLBLnoDataTiffFiles = GLO.GLBLnoDataTiffFilesPorDefecto  # p.ej.: -9999
            self.GLBLnoDataTipoDMasa = GLO.GLBLnoDataTipoDMasaPorDefecto  # p.ej.: 255
            self.GLBLumbralMatriDist = GLO.GLBLumbralMatriDistPorDefecto  # p.ej.: 20

        # Se inician estos atributos por si no se ejecuta el metodo setRangeUTM<>
        self.LOCLmarcoCoordMiniX = 0
        self.LOCLmarcoCoordMaxiX = 0
        self.LOCLmarcoCoordMiniY = 0
        self.LOCLmarcoCoordMaxiY = 0
        self.marcoCoordEjecutado = False
        self.marcoCoordDisponible = False
        self.usarVectorFileParaDelimitarZona = False
        self.GLBLmarcoPatronTest = GLO.GLBLmarcoPatronTestPorDefecto

    # ==========================================================================
    def setRangeUTM(
            self,
            LCL_marcoCoordMiniX=None,  # opcional
            LCL_marcoCoordMaxiX=None,  # opcional
            LCL_marcoCoordMiniY=None,  # opcional
            LCL_marcoCoordMaxiY=None,  # opcional
            LCL_marcoPatronTest=None,  # extra: 0
            LCL_rutaAscRaizBase=None,  # opcional
            LCL_patronVectrName=None,  # opcional
            LCL_patronLayerName=None,  # opcional
            LCL_testeoVectrName=None,  # opcional
            LCL_testeoLayerName=None,  # opcional
            LCL_verbose=None,
        ):
        """Method for seting UTM range for analysis area
        Attributes
        ----------
        LCL_marcoCoordMiniX : int
            Default: None
        LCL_marcoCoordMaxiX : int
            Default: None
        LCL_marcoCoordMiniY : int
            Default: None
        LCL_marcoCoordMaxiY : int
            Default: None
        LCL_marcoPatronTest = bool
            Default: parameter GLBLmarcoPatronTestPorDefecto from cfg file or clidtwins_config.py module
        LCL_rutaAscRaizBase : str
            Default: None (optional)
        LCL_patronVectrName : str
            Default: None (optional)
        LCL_patronLayerName : str
            Default: None (optional)
        LCL_testeoVectrName : str
            Default: None (optional)
        LCL_testeoLayerName : str
            Default: None (optional)
        """

        if not LCL_verbose is None:
            self.LOCLverbose = LCL_verbose

        self.marcoCoordEjecutado = True

        if LCL_marcoPatronTest is None:
            self.GLBLmarcoPatronTest = GLO.GLBLmarcoPatronTestPorDefecto
        else:
            self.GLBLmarcoPatronTest = LCL_marcoPatronTest

        if LCL_marcoCoordMiniX is None:
            self.LOCLmarcoCoordMiniX = GLO.GLBLmarcoCoordMiniXPorDefecto
        else:
            self.LOCLmarcoCoordMiniX = LCL_marcoCoordMiniX
        if LCL_marcoCoordMaxiX is None:
            self.LOCLmarcoCoordMaxiX = GLO.GLBLmarcoCoordMaxiXPorDefecto
        else:
            self.LOCLmarcoCoordMaxiX = LCL_marcoCoordMaxiX
        if LCL_marcoCoordMiniY is None:
            self.LOCLmarcoCoordMiniY = GLO.GLBLmarcoCoordMiniYPorDefecto
        else:
            self.LOCLmarcoCoordMiniY = LCL_marcoCoordMiniY
        if LCL_marcoCoordMaxiY is None:
            self.LOCLmarcoCoordMaxiY = GLO.GLBLmarcoCoordMaxiYPorDefecto
        else:
            self.LOCLmarcoCoordMaxiY = LCL_marcoCoordMaxiY

        if self.LOCLmarcoCoordMiniX > 0:
            self.marcoCoordDisponible = True
            self.LOCLmarcoLibreMiniX = False
        else:
            self.LOCLmarcoCoordMiniX = 0
            self.LOCLmarcoLibreMiniX = True
        if self.LOCLmarcoCoordMaxiX > 0:
            self.marcoCoordDisponible = True
            self.LOCLmarcoLibreMaxiX = False
        else:
            self.LOCLmarcoCoordMaxiX = 0
            self.LOCLmarcoLibreMaxiX = True
        if self.LOCLmarcoCoordMiniY > 0:
            self.marcoCoordDisponible = True
            self.LOCLmarcoLibreMiniY = False
        else:
            self.LOCLmarcoCoordMiniY = 0
            self.LOCLmarcoLibreMiniY = True
        if self.LOCLmarcoCoordMaxiY > 0:
            self.marcoCoordDisponible = True
            self.LOCLmarcoLibreMaxiY = False
        else:
            self.LOCLmarcoCoordMaxiY = 0
            self.LOCLmarcoLibreMaxiY = True

        if self.GLBLmarcoPatronTest:
            if LCL_rutaAscRaizBase is None:
                self.LOCLrutaAscRaizBase = GLO.GLBLrutaAscRaizBasePorDefecto
            else:
                self.LOCLrutaAscRaizBase = LCL_rutaAscRaizBase
            if LCL_patronVectrName is None:
                self.LOCLpatronVectrName = GLO.GLBLpatronVectrNamePorDefecto
            else:
                self.LOCLpatronVectrName = LCL_patronVectrName
            if LCL_patronLayerName is None:
                self.LOCLpatronLayerName = GLO.GLBLpatronLayerNamePorDefecto
            else:
                self.LOCLpatronLayerName = LCL_patronLayerName
            if LCL_testeoVectrName is None:
                self.LOCLtesteoVectrName = GLO.GLBLtesteoVectrNamePorDefecto
            else:
                self.LOCLtesteoVectrName = LCL_testeoVectrName
            if LCL_testeoLayerName is None:
                self.LOCLtesteoLayerName = GLO.GLBLtesteoLayerNamePorDefecto
            else:
                self.LOCLtesteoLayerName = LCL_testeoLayerName

#ññ
            # if hasattr(self, 'LOCLpatronVectrName') and hasattr(self, 'LOCLpatronLayerName'):
            #     (usarVectorFileParaDelimitarZona, patronVectrNameConPath) = verificarExistencia(self.LOCLpatronVectrName)
            # else:
            #     (usarVectorFileParaDelimitarZona, patronVectrNameConPath) = verificarExistencia(GLO.GLBLpatronVectrNamePorDefecto)
            #     if usarVectorFileParaDelimitarZona:
            #         self.LOCLpatronVectrName = GLO.GLBLpatronVectrNamePorDefecto
            #         self.LOCLpatronLayerName = GLO.GLBLpatronLayerNamePorDefecto

            envolventePatron = obtenerExtensionDeCapaVectorial(
                self.LOCLrutaAscRaizBase,
                self.LOCLpatronVectrName,
                LOCLlayerName=self.LOCLpatronLayerName,
                LOCLverbose=self.LOCLverbose,
            )
            if not envolventePatron is None:
                self.LOCLmarcoCoordMiniX = envolventePatron[0]
                self.LOCLmarcoCoordMaxiX = envolventePatron[1]
                self.LOCLmarcoCoordMiniY = envolventePatron[2]
                self.LOCLmarcoCoordMaxiY = envolventePatron[3]
                self.usarVectorFileParaDelimitarZona = True
            else:
                print('\nclidtwins-> ATENCION: no esta disponible el fichero {}'.format(self.LOCLpatronVectrName))
                print('{}-> Ruta base: {}'.format(TB, self.LOCLrutaAscRaizBase))
                # sys.exit(0)
            envolventeTesteo = obtenerExtensionDeCapaVectorial(
                self.LOCLrutaAscRaizBase,
                self.LOCLtesteoVectrName,
                LOCLlayerName=self.LOCLtesteoLayerName,
                LOCLverbose=self.LOCLverbose,
            )
            if not envolventeTesteo is None:
                self.LOCLmarcoCoordMiniX = min(self.LOCLmarcoCoordMiniX, envolventeTesteo[0])
                self.LOCLmarcoCoordMaxiX = max(self.LOCLmarcoCoordMaxiX, envolventeTesteo[1])
                self.LOCLmarcoCoordMiniY = min(self.LOCLmarcoCoordMiniY, envolventeTesteo[2])
                self.LOCLmarcoCoordMaxiY = max(self.LOCLmarcoCoordMaxiY, envolventeTesteo[3])
                self.usarVectorFileParaDelimitarZona = True

            if self.LOCLverbose:
                if envolventeTesteo is None:
                    print('clidtwins-> Se adopta la envolvente del shapes de referenia (patron) -no se dispone de shape de chequeo (testeo)-:')
                else:
                    print('clidtwins-> Se adopta la envolvente de los shapes de referenia (patron) y chequeo (testeo):')
                print(
                    '{}-> X: {:10.2f} {:10.2f} -> {:4.0f} m'.format(
                        TB,
                        self.LOCLmarcoCoordMiniX, self.LOCLmarcoCoordMaxiX,
                        self.LOCLmarcoCoordMaxiX - self.LOCLmarcoCoordMiniX
                    )
                )
                print(
                    '{}-> Y: {:10.2f} {:10.2f} -> {:4.0f} m'.format(
                        TB,
                        self.LOCLmarcoCoordMiniY, self.LOCLmarcoCoordMaxiY,
                        self.LOCLmarcoCoordMaxiY - self.LOCLmarcoCoordMiniY
                    )
                )
        elif not self.marcoCoordDisponible:
            if self.LOCLverbose:
                print('clidtwins-> AVISO: tras ejecutar el metodo .setRangeUTM\n'
                      f'{TB}no se han establecido coordenadas para la zona de estudio.')

    # ==========================================================================
    def searchSourceFiles(
            self,
            LCL_listLstDasoVars=None,  # optional (si existe, prevalece sobre el siguiente)
            LCL_listaTxtDasoVarsFileTypes=None,  # optional (alternativa simplificada al anterior en formato str o list)
            LCL_nClasesDasoVars=None,  # optional
            LCL_trasferDasoVars=None,  # optional
            LCL_nPatronDasoVars=None,  # optional

            LCL_rutaAscRaizBase=None,  # opcional
            LCL_nivelSubdirExpl=0,  # opcional
            LCL_outputSubdirNew=None,  # opcional
            LCL_verbose=None,
        ):
        """Search asc files with dasoLidar variables
        Attributes
        ----------
        LCL_listLstDasoVars : list
            Default: None (optional)
        LCL_listaTxtDasoVarsFileTypes : list or str
            Default: None (optional)
        LCL_nClasesDasoVars : int
            Default: None (optional)
        LCL_trasferDasoVars : int
            Default: None (optional)
        LCL_nPatronDasoVars : int
            Default: None (optional)

        LCL_rutaAscRaizBase : str
            Default: None,
        LCL_nivelSubdirExpl : str
            Default: 0 (optional)
        LCL_outputSubdirNew : str
            Default: None (optional)
        """

        if not LCL_verbose is None:
            self.LOCLverbose = LCL_verbose

        # ======================================================================
        self.verificarlistaDasoVars(
            LCL_listLstDasoVars=LCL_listLstDasoVars,
            LCL_listaTxtDasoVarsFileTypes=LCL_listaTxtDasoVarsFileTypes,
            LCL_nClasesDasoVars=LCL_nClasesDasoVars,
            LCL_trasferDasoVars=LCL_trasferDasoVars,
            LCL_nPatronDasoVars=LCL_nPatronDasoVars,
        )
        self.verificarRutaAscRaiz(
            LCL_rutaAscRaizBase=LCL_rutaAscRaizBase,
            LCL_nivelSubdirExpl=LCL_nivelSubdirExpl,
            LCL_outputSubdirNew=LCL_outputSubdirNew,
        )
        self.verificarMarcoCoord()
        # ======================================================================

        # ======================================================================
        self.LOCLnivelSubdirExpl = LCL_nivelSubdirExpl
        if LCL_outputSubdirNew is None:
            self.LOCLoutputSubdirNew = GLO.GLBLoutputSubdirNewPorDefecto
        else:
            self.LOCLoutputSubdirNew = LCL_outputSubdirNew

        self.idInputDir = os.path.basename(self.LOCLrutaAscRaizBase)

        if self.LOCLverbose:
            print('\n{:_^80}'.format(''))
            print('clidtwins-> Explorando directorios...')
            print(f'{TB}-> Directorio raiz para los ficheros dasolidar (asc):')
            print('{}{}{}'.format(TB, TV, self.LOCLrutaAscRaizBase))
            # print(f'{TB}-> Identificador de este lote de ficheros -> IdDir: {}'.format(self.idInputDir))
            if self.LOCLnivelSubdirExpl:
                print(f'{TB}{TV}-> Se van a explorar subdirectorios hasta nivel:    {self.LOCLnivelSubdirExpl}')
            else:
                print(f'{TB}{TV}-> Se van a explorar subdirectorios hasta el ultimo nivel')

        listaDirsExcluidos = [self.LOCLoutputSubdirNew]
        if self.LOCLverbose:
            print(f'{TB}-> Directorios excluidos:')
            for dirExcluido in listaDirsExcluidos:
                print(f'{TB}{TV}{os.path.join(self.LOCLrutaAscRaizBase, dirExcluido)}')
            print('{:=^80}'.format(''))

        if self.LOCLverbose:
            print('\n{:_^80}'.format(''))
            print('clidtwins-> Buscando ficheros de cada tipo en todos los directorios previstos:')
            if not self.marcoCoordDisponible:
                print(f'{TB}-> Sin restricciones de coordendas porque no se han pre-establecido coordenadas para la zona de estudio.')
            elif not TRNS_buscarBloquesSoloDentroDelMarcoUTM and not self.GLBLmarcoPatronTest:
                print(f'{TB}-> Sin restricciones de coordendas porque se ha desabilitado temporalmente esta opcion.')
            else:
                if self.GLBLmarcoPatronTest:
                    print(f'{TB}-> Que solapen con la envolvente de los shapes de referenia (patron) y chequeo (testeo):')
                else:
                    print(f'{TB}-> Dentro de las coordenadas establecidas en linea de comandos o configuracion por defecto:')
                print(
                    '{}{}X {:10.2f} - {:10.2f} -> {:4.0f} m:'.format(
                        TB, TV,
                        self.LOCLmarcoCoordMiniX, self.LOCLmarcoCoordMaxiX,
                        self.LOCLmarcoCoordMaxiX - self.LOCLmarcoCoordMiniX
                    )
                )
                print(
                    '{}{}Y {:10.2f} - {:10.2f} -> {:4.0f} m:'.format(
                        TB, TV,
                        self.LOCLmarcoCoordMiniY, self.LOCLmarcoCoordMaxiY,
                        self.LOCLmarcoCoordMaxiY - self.LOCLmarcoCoordMiniY
                    )
                )

        # ======================================================================
        # print('clidtwins-> self.LOCLlistaDasoVarsFileTypes:', self.LOCLlistaDasoVarsFileTypes)
        # quit()
        # Listas de ficheros reunidas por tipoDeFichero
        self.inFilesListAllTypes = []
        for nInputVar, miTipoDeFicheroDasoLayer in enumerate(self.LOCLlistaDasoVarsFileTypes):
            if self.LOCLnPatronDasoVars != 0 and nInputVar >= self.LOCLnPatronDasoVars:
                break
            miDasoVarNickName = self.LOCLlistaDasoVarsNickNames[nInputVar]
            if self.LOCLverbose:
                print('-> Tipo {}: > Variable: {} - Identificador del tipo de fichero: {}'.format(nInputVar, miDasoVarNickName, miTipoDeFicheroDasoLayer))
            if miDasoVarNickName == 'MFE25' or miDasoVarNickName == 'TMasa':
                if self.LOCLverbose > 1:
                    print(f'{TB}{TV}-> No requiere explorar directorios')
                continue

            dirIterator = iter(os.walk(self.LOCLrutaAscRaizBase))
            # dirpath, dirnames, filenames = next(dirIterator)
            # dirpathPrevio = os.path.abspath(os.path.join(self.LOCLrutaAscRaizBase, '..'))
            # dirpathPrevio = self.LOCLrutaAscRaizBase
            infilesX = []
            for dirpathOk, dirnames, filenames in dirIterator:
                if miDasoVarNickName == 'MFE' or miDasoVarNickName == 'TipoMasa':
                    # El MFE se obtiene de una capa vectorial y el tipo de masa por ahoraa no lo uso (se generaria en esta aplicacion)
                    continue
                if dirpathOk.endswith(self.LOCLoutputSubdirNew):
                    if self.LOCLverbose > 1:
                        print(f'{TB}{TV}-> Saltando el directorio {dirpathOk}')
                    continue

                subDirExplorado = dirpathOk.replace(self.LOCLrutaAscRaizBase, '')
                if dirpathOk == self.LOCLrutaAscRaizBase:
                    nivelDeSubdir = 0
                elif not '/' in subDirExplorado and not '\\' in subDirExplorado:
                    nivelDeSubdir = 0
                else:
                    nivelDeSubdir = subDirExplorado.count('/') + subDirExplorado.count('\\')
                if self.LOCLnivelSubdirExpl and nivelDeSubdir > self.LOCLnivelSubdirExpl:
                    if self.LOCLverbose > 2:
                        print(f'{TB}{TV}Se ha alcanzado el nivel de directorios maximo ({self.LOCLnivelSubdirExpl})\n')
                    continue
                else:
                    pass
                    # print(f'Explorando nivel de subdirectorios {nivelDeSubdir} de {self.LOCLnivelSubdirExpl}')

                excluirDirectorio = False
                for dirExcluido in listaDirsExcluidos:
                    if dirpathOk == os.path.join(self.LOCLrutaAscRaizBase, dirExcluido):
                        excluirDirectorio = True
                        break
                if excluirDirectorio:
                    if self.LOCLverbose > 1:
                        print(f'\n{TB}-> Directorio excluido: {dirpathOk}')
                    continue
                if self.LOCLverbose > 1:
                    print(f'{TB}-> Explorando directorio: {dirpathOk}')
                if len(filenames) == 0:
                    if self.LOCLverbose > 1:
                        print(f'{TB}{TV}-> No hay ficheros; se pasa al siguiente directorio')
                    continue

                #===================================================================
                try:
                    # Si se ha establecido marco UTM se incorporan los bloques
                    # que esten dentro del marco; en caso contrario, todos.
                    # Siempre y cuando tengan todas las variables dasoLidar.
                    if (
                        self.marcoCoordDisponible
                        and TRNS_buscarBloquesSoloDentroDelMarcoUTM
                    ):
                        filenamesSeleccionadosX = [
                            filename for filename in filenames
                            if (
                                miTipoDeFicheroDasoLayer.upper() in filename.upper()
                                and filename[-4:].upper() == '.ASC'
                                and (self.LOCLmarcoLibreMiniX or (int(filename[:3]) * 1000) + 2000 >= self.LOCLmarcoCoordMiniX)
                                and (self.LOCLmarcoLibreMaxiX or int(filename[:3]) * 1000 < self.LOCLmarcoCoordMaxiX)
                                and (self.LOCLmarcoLibreMiniY or int(filename[4:8]) * 1000 >= self.LOCLmarcoCoordMiniY)
                                and (self.LOCLmarcoLibreMaxiY or (int(filename[4:8]) * 1000) - 2000 < self.LOCLmarcoCoordMaxiY)
                            )
                        ]
                    else:
                        filenamesSeleccionadosX = [
                            filename for filename in filenames
                            if (
                                miTipoDeFicheroDasoLayer.upper() in filename.upper()
                                and filename[-4:].upper() == '.ASC'
                            )
                        ]
                except:
                    print('\nAVISO: no se han podido filtrar los ficheros por coordenadas debido a que no siguen el patron XXX_YYYY...asc.')
                    filenamesSeleccionadosX = [
                        filename for filename in filenames
                        if (
                            miTipoDeFicheroDasoLayer.upper() in filename.upper()
                            and filename[-4:].upper() == '.ASC'
                        )
                    ]

                if filenamesSeleccionadosX:
                    if self.LOCLverbose > 2:
                        print(f'{TB}{TV}{TV}AscRaiz => subDir: {self.LOCLrutaAscRaizBase} => {subDirExplorado}')
                        print(f'{TB}{TV}{TV}nivelDeSubdir:     {nivelDeSubdir}')
                        print(f'{TB}{TV}{TV}dirnames:          {dirnames}')
                        print(f'{TB}{TV}{TV}numFiles:          {len(filenames)}')
                        print(f'{TB}{TV}{TV}Algunos files:     {filenames[:2]}, etc.')
                        # print(f'{TB}{TV}{TV}dirpathPrevio:     {}'.format(dirpathPrevio))
                        # dirpathPadre1 = os.path.abspath(os.path.join(dirpathOk, '..'))
                        # print(f'{TB}{TV}{TV}dirpathPadre1:     {}'.format(dirpathPadre1))
                        # dirpathPrevio = dirpathPadre1
                    for filenameSel in filenamesSeleccionadosX:
                        infilesX.append([dirpathOk, filenameSel])
                    if self.LOCLverbose > 1:
                        print(f'{TB}{TV}-> Encontrados: {len(filenamesSeleccionadosX)} ficheros.')
                        print(f'{TB}{TV}-> Primeros {min(len(filenamesSeleccionadosX), 5)} ficheros:')
                        for nFile, pathAndfilename in enumerate(filenamesSeleccionadosX[:5]):
                            print(f'{TB}{TV}{TV}', nFile, pathAndfilename)
                else:
                    if self.LOCLverbose > 2:
                        print(f'{TB}{TV}dirpathOk:         {dirpathOk}')
                        print(f'{TB}{TV}numFiles:          {len(filenames)}')
                    if self.LOCLverbose > 1:
                        if self.marcoCoordDisponible and TRNS_buscarBloquesSoloDentroDelMarcoUTM:
                            print(
                                '{}{}{}No se ha localizado ningun fichero con el patron: <{}> que solape con el marco de coordenadas X: {} {} Y: {} {}'.format(
                                    TB, TV, TV,
                                    miTipoDeFicheroDasoLayer,
                                    self.LOCLmarcoCoordMiniX,
                                    self.LOCLmarcoCoordMaxiX,
                                    self.LOCLmarcoCoordMiniY,
                                    self.LOCLmarcoCoordMaxiY,
                                )
                            )
                        else:
                            print(
                                '{}No se ha localizado ningun fichero con el patron: <{}>'.format(
                                    TB,
                                    miTipoDeFicheroDasoLayer,
                                )
                            )
                #===================================================================

            self.inFilesListAllTypes.append(infilesX)
        # ======================================================================

        # Despues de buscar todos los ficheros disponibles de cada tipo (cada variable)
        # Elimino los ficheros de bloques que no tengan todos los tipos (todas las variables)

        # print('\nNumero de ficheros en {}: {} {}'.format(self.LOCLrutaAscRaizBase, len(self.inFilesListAllTypes), len(self.LOCLlistaDasoVarsFileTypes)))
        # print('Numero de tipos de fichero: {}'.format(min(self.LOCLnPatronDasoVars, len(self.LOCLlistLstDasoVars) - 2)))
        self.numFicherosVariablesPorBloque = {}
        if self.LOCLverbose > 2:
            print('\nclidtwins-> Listas de bloques/ficheros seleccionados:')
        hayAlgunBloqueCompleto = False
        for nLista in range(len(self.inFilesListAllTypes)):
            if (
                self.LOCLlistLstDasoVars[nLista][1] == 'MFE25'
                or self.LOCLlistLstDasoVars[nLista][1] == 'TMasa'
            ):
                continue
            # print('------------>', self.inFilesListAllTypes[nLista])
            # print('------------>', self.numFicherosVariablesPorBloque.keys())
            for numFile, [pathFile, nameFile] in enumerate(self.inFilesListAllTypes[nLista]):
                # print('------------>', nameFile)
                codigoBloque = nameFile[:8]
                if codigoBloque in self.numFicherosVariablesPorBloque.keys():
                    self.numFicherosVariablesPorBloque[codigoBloque] += 1
                else:
                    self.numFicherosVariablesPorBloque[codigoBloque] = 1
                    if self.LOCLverbose > 1:
                        print(f'{TB}-> Nuevo codigoBloque encontrado:', codigoBloque)
            if self.LOCLverbose > 2:
                if len(self.inFilesListAllTypes[nLista]) == 0:
                    print(
                        '{}{} -> {} => fileType: {:<35} ATENCION: no hay ficheros'.format(
                            TB,
                            nLista,
                            self.LOCLlistLstDasoVars[nLista][1],
                            self.LOCLlistLstDasoVars[nLista][0],
                        )
                    )
                else:
                    print(
                        '{}{:<2} -> {} => fileType: {:<35} ({:<2} files):'.format(
                            TB,
                            nLista,
                            self.LOCLlistLstDasoVars[nLista][1],
                            self.LOCLlistLstDasoVars[nLista][0],
                            len(self.inFilesListAllTypes[nLista]),
                        )
                    )
                    print(f'{TB}{TV}{self.inFilesListAllTypes[nLista][:2]}, etc.')

        if self.LOCLverbose > 1:
            print('\nclidtwins-> Lista de bloques encontrados (completos e incompletos): {}'.format(self.numFicherosVariablesPorBloque))
            for bloqueKey in self.numFicherosVariablesPorBloque:
                print(f'{TB}-> Bloque {bloqueKey}: {self.numFicherosVariablesPorBloque[bloqueKey]} ficheros')

        for nLista in range(len(self.inFilesListAllTypes)):
            if (
                self.LOCLlistLstDasoVars[nLista][1] == 'MFE25'
                or self.LOCLlistLstDasoVars[nLista][1] == 'TMasa'
            ):
                continue
            # Si no se han localizado los N ficheros del bloque, se elimina todos los ficheros de ese bloque
            for numFile, [pathFile, nameFile] in enumerate(self.inFilesListAllTypes[nLista]):
                codigoBloque = nameFile[:8]
                # print('---------->', codigoBloque, '->>', self.numFicherosVariablesPorBloque[codigoBloque], 'ficheros (variables)')
                if self.numFicherosVariablesPorBloque[codigoBloque] < self.nInputVars:
                    if nameFile[:8] == codigoBloque:
                        # (self.inFilesListAllTypes[nLista]).remove([pathFile, nameFile])
                        del self.inFilesListAllTypes[nLista][numFile]
                        if self.LOCLverbose > 1:
                            print('clidtwins-> Eliminando codigoBloque por no tener todas las dasoVars:', codigoBloque, 'nameFile', nameFile)
                else:
                    hayAlgunBloqueCompleto = True

        if not hayAlgunBloqueCompleto:
            print('\nATENCION: No hay ningun bloque con todas las variables (todos los tipos de fichero).')
            print(f'{TB}-> Ruta de busqueda de ficheros: {self.LOCLrutaAscRaizBase}')
            sys.exit(0)

        # Actualizo el marco de coordenadas de la zona de estudio con los bloques encontrados y admitidos
        if self.LOCLverbose > 1:
            if not TRNS_buscarBloquesSoloDentroDelMarcoUTM or (
                self.LOCLmarcoLibreMiniX
                or self.LOCLmarcoLibreMaxiX
                or self.LOCLmarcoLibreMiniY
                or self.LOCLmarcoLibreMaxiY
            ):
                print('\nclidtwuins-> Actualizando marco de analisis:')
        for codigoBloque in self.numFicherosVariablesPorBloque.keys():
            if (
                self.LOCLmarcoLibreMiniX
                or (
                    not TRNS_buscarBloquesSoloDentroDelMarcoUTM
                    and int(codigoBloque[:3]) * 1000 < self.LOCLmarcoCoordMiniX
                )
            ):
                if self.LOCLverbose > 1:
                    print(
                        '{}-> Actualizando marcoCoordMiniX de {:0.2f} a {}'.format(
                            TB,
                            self.LOCLmarcoCoordMiniX,
                            int(codigoBloque[:3]) * 1000
                        )
                    )
                self.LOCLmarcoCoordMiniX = int(codigoBloque[:3]) * 1000
            if (
                self.LOCLmarcoLibreMaxiX
                or (
                    not TRNS_buscarBloquesSoloDentroDelMarcoUTM
                    and (int(codigoBloque[:3]) * 1000) + 2000 > self.LOCLmarcoCoordMaxiX
                )
            ):
                if self.LOCLverbose > 1:
                    print(
                        '{}-> Actualizando marcoCoordMaxiX de {:0.2f} a {:0.2f}'.format(
                            TB,
                            self.LOCLmarcoCoordMaxiX,
                            (int(codigoBloque[:3]) * 1000) + 2000
                        )
                    )
                self.LOCLmarcoCoordMaxiX = (int(codigoBloque[:3]) * 1000) + 1999.99
            if (
                self.LOCLmarcoLibreMaxiY
                or (
                    not TRNS_buscarBloquesSoloDentroDelMarcoUTM
                    and int(codigoBloque[4:8]) * 1000 > self.LOCLmarcoCoordMaxiY
                )
            ):
                if self.LOCLverbose > 1:
                    print(
                        '{}-> Actualizando marcoCoordMaxiY de {:0.2f} a {:0.2f}'.format(
                            TB,
                            self.LOCLmarcoCoordMaxiY,
                            int(codigoBloque[4:8]) * 1000
                        )
                    )
                self.LOCLmarcoCoordMaxiY = int(codigoBloque[4:8]) * 1000
            if (
                self.LOCLmarcoLibreMiniY
                or (
                    not TRNS_buscarBloquesSoloDentroDelMarcoUTM
                    and (int(codigoBloque[4:8]) * 1000) - 2000 < self.LOCLmarcoCoordMiniY
                )
            ):
                if self.LOCLverbose > 1:
                    print(
                        '{}-> Actualizando marcoCoordMiniY de {:0.2f} a {:0.2f}'.format(
                            TB,
                        self.LOCLmarcoCoordMiniY,
                        (int(codigoBloque[4:8]) * 1000) - 2000
                        )
                    )
                self.LOCLmarcoCoordMiniY = (int(codigoBloque[4:8]) * 1000) - 2000

        # print('Resultado tras eliminar los que procedan:')
        # for nLista in range(len(self.inFilesListAllTypes)):
        #     print('Variable num', nLista, 'Files ->', self.inFilesListAllTypes[nLista])

    # ==========================================================================
    def verificarlistaDasoVars(
            self,
            LCL_listLstDasoVars=None,  # optional (si existe, prevalece sobre el siguiente)
            LCL_listaTxtDasoVarsFileTypes=None,  # optional (alternativa simplificada al anterior)
            LCL_nClasesDasoVars=None,  # optional
            LCL_trasferDasoVars=None,  # optional
            LCL_nPatronDasoVars=None,  # optional
        ):
        # ======================================================================
        if self.LOCLverbose:
            print('\n{:_^80}'.format(''))
        if not LCL_listLstDasoVars is None:
            self.LOCLlistLstDasoVars = LCL_listLstDasoVars
            if self.LOCLverbose:
                print('clidtwins-> Se crea un objeto de la clase DasoLidarSource con las listas\n'
                      f'{TB}de identificadores de tipo de fichero y demas propiedades de cada\n'
                      f'{TB}variable pasadas oomo argumento (LCL_listLstDasoVars): nickName, rango\n'
                      f'{TB}de valores, numero de clases, movilidad inter-clases y peso relativo.')
            self.calcularRangoVariables = False
        elif not LCL_listaTxtDasoVarsFileTypes is None:
            if self.LOCLverbose > 1:
                print('clidtwins-> Se crea un objeto de la clase DasoLidarSource con la lista de\n'
                      f'{TB}identificadores de tipo de fichero (LCL_listaTxtDasoVarsFileTypes).\n'
                      f'{TB}Cada tipo de fichero corresponde a una variable dasoLidar..\n'
                      f'{TB}Ficheros: XXX_YYYY_*IdFileType*.asc; XXX, YYYY: coord. UTM /1000 m;\n'
                      f'{TB}*IdFileType*: cadena que incluye el identificador de tipo de fichero.\n'
                      f'{TB}Para cada variable se establecen clases dividiendo su rango absoluto\n'
                      f'{TB}entre el num de clases. El numero de clases, la movilidad inter-clases,\n'
                      f'{TB}y el peso relativo son iguales para todas las variables:')
            if LCL_nClasesDasoVars is None:
                self.LOCLnClasesDasoVars = GLO.GLBLnClasesDasoVarsPorDefecto
                if self.LOCLverbose > 1:
                    print(f'{TB}{TV}Numero de clases: {self.LOCLnClasesDasoVars} clases (valor por defecto).')
            else:
                self.LOCLnClasesDasoVars = LCL_nClasesDasoVars
                if self.LOCLverbose > 1:
                    print(f'{TB}{TV}Numero de clases: {self.LOCLnClasesDasoVars} clases (argumeto LCL_nClasesDasoVars).')
            if LCL_trasferDasoVars is None:
                self.LOCLtrasferDasoVars = GLO.GLBLtrasferDasoVarsPorDefecto
                if self.LOCLverbose > 1:
                    print(f'{TB}{TV}Movilidad inter-clases: {self.LOCLtrasferDasoVars} % (valor por defecto).')
            else:
                self.LOCLtrasferDasoVars = LCL_trasferDasoVars
                if self.LOCLverbose > 1:
                    print(f'{TB}{TV}Movilidad inter-clases: {self.LOCLnClasesDasoVars} % (argumeto LCL_nClasesDasoVars).')
            self.LOCLponderaDasoVars = 1
            if self.LOCLverbose > 1:
                    print(f'{TB}{TV}Todas las variables se poderan igual.')

            self.calcularRangoVariables = True
            if type(LCL_listaTxtDasoVarsFileTypes) == str:
                self.LOCLlistaDasoVarsFileTypes = [item.strip() for item in LCL_listaTxtDasoVarsFileTypes.split(',')]
            elif type(LCL_listaTxtDasoVarsFileTypes) == list:
                self.LOCLlistaDasoVarsFileTypes = LCL_listaTxtDasoVarsFileTypes
            elif type(LCL_listaTxtDasoVarsFileTypes) == tuple:
                self.LOCLlistaDasoVarsFileTypes = list(LCL_listaTxtDasoVarsFileTypes)
            else:
                print(f'\nclidtwins-> ATENCION: el argumento LCL_listaTxtDasoVarsFileTypes es de tipo {type(LCL_listaTxtDasoVarsFileTypes)}, y debe ser str o list.')
                print('Se interrumpe la ejecucion.')
                sys.exit(0)

            self.LOCLlistaDasoVarsNickNames = [
                'alt95' if ('alt' in item.lower() and '95' in item) else
                'fcc3m' if ('fcc' in item.lower() and '03' in item) else
                'fcc5m' if ('fcc' in item.lower() and '05' in item) else
                item[:5]
                for item in self.LOCLlistaDasoVarsFileTypes
            ]
            self.LOCLlistaDasoVarsRangoLinf = [0] * len(self.LOCLlistaDasoVarsFileTypes)  # Se calcula al leer los ficheros
            self.LOCLlistaDasoVarsRangoLsup = [100] * len(self.LOCLlistaDasoVarsFileTypes)  # Se calcula al leer los ficheros
            self.LOCLlistaDasoVarsNumClases = [self.LOCLnClasesDasoVars] * len(self.LOCLlistaDasoVarsFileTypes)
            self.LOCLlistaDasoVarsMovilidad = [self.LOCLtrasferDasoVars] * len(self.LOCLlistaDasoVarsFileTypes)
            self.LOCLlistaDasoVarsPonderado = [self.LOCLponderaDasoVars] * len(self.LOCLlistaDasoVarsFileTypes)

            self.LOCLlistLstDasoVars = []
            for nVar in range(len(self.LOCLlistaDasoVarsFileTypes)):
                self.LOCLlistLstDasoVars.append(
                    [
                        self.LOCLlistaDasoVarsFileTypes[nVar],
                        self.LOCLlistaDasoVarsNickNames[nVar],
                        self.LOCLlistaDasoVarsRangoLinf[nVar],
                        self.LOCLlistaDasoVarsRangoLsup[nVar],
                        self.LOCLlistaDasoVarsNumClases[nVar],
                        self.LOCLlistaDasoVarsMovilidad[nVar],
                        self.LOCLlistaDasoVarsPonderado[nVar],
                    ]
                )
        else:
            # LCL_listLstDasoVars is None and LCL_listaTxtDasoVarsFileTypes is None:
            self.LOCLlistLstDasoVars = GLO.GLBLlistLstDasoVarsPorDefecto
            self.calcularRangoVariables = False
            if self.LOCLverbose:
                print('clidtwins-> AVISO:')
                if os.path.exists(GLO.configFileNameCfg):
                    print(f'{TB}Se lee la lista de DasoVars del fichero de configuracion ({GLO.configFileNameCfg})')
                else:
                    print(f'{TB}Se usa la lista de DasoVars por defecto (incluida en clidtwins._config.py)')
                print(f'{TB}por no haberse especificado LCL_listLstDasoVars de forma explicita')
                print(f'{TB}al instanciar la clase DasoLidarSource.')
                if self.LOCLverbose > 1:
                    print(f'listaDasoVars: {self.LOCLlistLstDasoVars}')

        if self.LOCLverbose:
            print('{:=^80}'.format(''))

        if not hasattr(self, 'LOCLlistaDasoVarsFileTypes'):
            self.LOCLlistaDasoVarsFileTypes = []
            self.LOCLlistaDasoVarsNickNames = []
            self.LOCLlistaDasoVarsRangoLinf = []
            self.LOCLlistaDasoVarsRangoLsup = []
            self.LOCLlistaDasoVarsNumClases = []
            self.LOCLlistaDasoVarsMovilidad = []
            self.LOCLlistaDasoVarsPonderado = []
            for thisListLstDasoVar in self.LOCLlistLstDasoVars:
                self.LOCLlistaDasoVarsFileTypes.append(thisListLstDasoVar[0])
                self.LOCLlistaDasoVarsNickNames.append(thisListLstDasoVar[1])
                self.LOCLlistaDasoVarsRangoLinf.append(thisListLstDasoVar[2])
                self.LOCLlistaDasoVarsRangoLsup.append(thisListLstDasoVar[3])
                self.LOCLlistaDasoVarsNumClases.append(thisListLstDasoVar[4])
                self.LOCLlistaDasoVarsMovilidad.append(thisListLstDasoVar[5])
                if len(thisListLstDasoVar) > 6:
                    self.LOCLlistaDasoVarsPonderado.append(thisListLstDasoVar[6])
                else:
                    self.LOCLlistaDasoVarsPonderado.append(10)

        if (
            not (self.LOCLlistLstDasoVars[-2][0]).upper().startswith('MFE')
            and not (self.LOCLlistLstDasoVars[-2][0]).upper().startswith('LAND')
        ):
            dasoVarTipoBosquePorDefecto = ['MFE25', 'MFE25', 0, 255, 255, 0, 0]
            dasoVarTipoDeMasaPorDefecto = ['TMasa', 'TMasa', 0, 255, 255, 0, 0]
            if self.LOCLverbose:
                print('\n{:_^80}'.format(''))
                print('clidtwins-> AVISO: la lista de variables dasolidar no incluye las dos adicionales')
                print(f'{TB}que deben ser tipo de bosque (MFE**) y tipo de masa (TMasa).')
                print(f'{TB}Se agregan a la lista con esta configuracion:')
                print(f'{TB}Tipos de bosque: {dasoVarTipoBosquePorDefecto}')
                print(f'{TB}Tipos de masa:   {dasoVarTipoDeMasaPorDefecto}')
                if self.LOCLverbose > 3:
                    rpta = input('Agregar estas dos variables? (S/n) ')
                    if rpta.upper() == 'N':
                        print('Se ha elegido no agregar las variables TipoBosque y TipoDeMasa.')
                        print('\nDefinir las variables de entrada con TipoBosque y TipoDeMasa como argumento'
                              'en linea de comandos el fichero de configuracion o en codigo por defecto')
                        print('Se interrumpe la ejecucion')
                        sys.exit(0)
                else:
                    print(f'{TB}Se agregan estas dos variables.')
                print('{:=^80}'.format(''))
            self.LOCLlistLstDasoVars.append(dasoVarTipoBosquePorDefecto)
            self.LOCLlistLstDasoVars.append(dasoVarTipoDeMasaPorDefecto)
            for dasoVarMFE25TMasaPorDefecto in [dasoVarTipoBosquePorDefecto, dasoVarTipoDeMasaPorDefecto]:
                self.LOCLlistaDasoVarsFileTypes.append(dasoVarMFE25TMasaPorDefecto[0])
                self.LOCLlistaDasoVarsNickNames.append(dasoVarMFE25TMasaPorDefecto[1])
                self.LOCLlistaDasoVarsRangoLinf.append(dasoVarMFE25TMasaPorDefecto[2])
                self.LOCLlistaDasoVarsRangoLsup.append(dasoVarMFE25TMasaPorDefecto[3])
                self.LOCLlistaDasoVarsNumClases.append(dasoVarMFE25TMasaPorDefecto[4])
                self.LOCLlistaDasoVarsMovilidad.append(dasoVarMFE25TMasaPorDefecto[5])
                self.LOCLlistaDasoVarsPonderado.append(dasoVarMFE25TMasaPorDefecto[6])
        # ======================================================================

        # ======================================================================
        if LCL_nPatronDasoVars is None:
            self.LOCLnPatronDasoVars = GLO.GLBLnPatronDasoVarsPorDefecto
        else:
            self.LOCLnPatronDasoVars = LCL_nPatronDasoVars

        if self.LOCLnPatronDasoVars == 0:
            self.nBandasPrevistasOutput = len(self.LOCLlistLstDasoVars)
        else:
            self.nBandasPrevistasOutput = self.LOCLnPatronDasoVars + 2
        self.nInputVars = self.nBandasPrevistasOutput - 2
        # ======================================================================

        # ======================================================================
        if self.LOCLverbose:
            print('\n{:_^80}'.format(''))
            print('clidtwins-> Lista de variables DasoLidar con indicacion para cada una de:')
            print(f'{TB}-> codigoFichero             -> para buscar ficheros con ese codigo')
            print(f'{TB}-> (nickName)                -> sin uso interno, unicamente para identificacion rapida')
            print(f'{TB}-> rango y numero de clases  -> para crear histograma') 
            print(f'{TB}-> movilidad inter-clases    -> para buscar zonas similares')
            print(f'{TB}-> peso relativo             -> para ponderar al comparar con el patron')

        # Esto es reiterativo:
        # self.LOCLlistaDasoVarsFileTypes = []
        # self.LOCLlistaDasoVarsNickNames = []
        # self.LOCLlistaDasoVarsRangoLinf = []
        # self.LOCLlistaDasoVarsRangoLsup = []
        # self.LOCLlistaDasoVarsNumClases = []
        # self.LOCLlistaDasoVarsMovilidad = []
        # self.LOCLlistaDasoVarsPonderado = []
        for nVar, thisListLstDasoVar in enumerate(self.LOCLlistLstDasoVars):
            # self.LOCLlistaDasoVarsFileTypes.append(thisListLstDasoVar[0])
            # self.LOCLlistaDasoVarsNickNames.append(thisListLstDasoVar[1])
            # self.LOCLlistaDasoVarsRangoLinf.append(thisListLstDasoVar[2])
            # self.LOCLlistaDasoVarsRangoLsup.append(thisListLstDasoVar[3])
            # self.LOCLlistaDasoVarsNumClases.append(thisListLstDasoVar[4])
            # self.LOCLlistaDasoVarsMovilidad.append(thisListLstDasoVar[5])
            # if len(thisListLstDasoVar) > 6:
            #     self.LOCLlistaDasoVarsPonderado.append(thisListLstDasoVar[6])
            # else:
            #     self.LOCLlistaDasoVarsPonderado.append(10)
            if self.LOCLverbose:
                if thisListLstDasoVar[0] == 'MFE25':
                    pesoPonderado = 'Excluyente'
                elif thisListLstDasoVar[6] == 0:
                    pesoPonderado = '--'
                else:
                    pesoPonderado = '{:>2} (/10)'.format(thisListLstDasoVar[6])
                print(
                    '{}-> variable {}-> codigoFichero: {:<35}'.format(TB, nVar, thisListLstDasoVar[0]),
                    '({}) ->'.format(thisListLstDasoVar[1]),
                    'rango: {} - {:>3};'.format(thisListLstDasoVar[2], thisListLstDasoVar[3]),
                    'clases: {:>3};'.format(thisListLstDasoVar[4]),
                    'movilidad: {:>3} %'.format(thisListLstDasoVar[5]),
                    'peso: {}'.format(pesoPonderado)
                )

        if self.LOCLverbose:
            print('{:=^80}'.format(''))
        # ======================================================================

    # ==========================================================================
    def verificarRutaAscRaiz(
            self,
            LCL_rutaAscRaizBase=None,  # opcional
            LCL_nivelSubdirExpl=0,  # opcional
            LCL_outputSubdirNew=None,  # opcional
        ):
        # ======================================================================
        # Si no se ha especificado LCL_rutaAscRaizBase, se elige una que exista:
        if type(LCL_rutaAscRaizBase) == str:
            LCL_rutaAscRaizBase = os.path.abspath(LCL_rutaAscRaizBase)
            if 'site-packages' in LCL_rutaAscRaizBase:
                LCL_rutaAscRaizBase = str(pathlib.Path.home())
            if not os.path.isdir(LCL_rutaAscRaizBase):
                print(f'\nclidtwins-> ATENCION: ruta {LCL_rutaAscRaizBase} no disponible, se interrumpe la ejecucion.')
                sys.exit(0)
        else:
            LCL_rutaAscRaizBase = None

        if LCL_rutaAscRaizBase is None:
            print('\n{:_^80}'.format(''))
            print(f'clidtwins-> AVISO: no se ha indicado ruta para los ficheros asc con las variables dasoLidar de entrada.')
            if self.LOCLverbose:
                print(f'{TB}Ruta: {LCL_rutaAscRaizBase}')
            if os.path.isdir(GLO.GLBLrutaAscRaizBasePorDefecto):
                if os.path.exists(GLO.configFileNameCfg):
                    print(f'{TB}-> Se adopta el valor del fichero de configuracion ({GLO.configFileNameCfg})')
                else:
                    print(f'{TB}-> Se adopta el valor por defecto (incluida en clidtwins._config.py)')
                LCL_rutaAscRaizBase = GLO.GLBLrutaAscRaizBasePorDefecto
            else:
                # Directorio que depende del entorno:
                MAIN_HOME_DIR = str(pathlib.Path.home())
                listaRutasDisponibles = [MAIN_HOME_DIR]
                # Directorio desde el que se lanza la app (estos dos coinciden):
                MAIN_THIS_DIR = os.getcwd()
                if not 'site-packages' in MAIN_THIS_DIR and not MAIN_THIS_DIR in listaRutasDisponibles:
                    listaRutasDisponibles.append(MAIN_THIS_DIR)
                MAIN_BASE_DIR = os.path.abspath('.')
                if not 'site-packages' in MAIN_BASE_DIR and not MAIN_BASE_DIR in listaRutasDisponibles:
                    listaRutasDisponibles.append(MAIN_BASE_DIR)
                # Directorios de la aplicacion:
                try:
                    MAIN_FILE_DIR = os.path.dirname(os.path.abspath(__file__))
                except:
                    MAIN_FILE_DIR = MAIN_BASE_DIR
                if not 'site-packages' in MAIN_FILE_DIR and not MAIN_FILE_DIR in listaRutasDisponibles:
                    listaRutasDisponibles.append(MAIN_FILE_DIR)
                # Cuando estoy en un modulo dentro de un paquete (subdirectorio):
                MAIN_RAIZ_DIR = os.path.abspath(os.path.join(MAIN_FILE_DIR, '..'))
                if not 'site-packages' in MAIN_RAIZ_DIR and not MAIN_RAIZ_DIR in listaRutasDisponibles:
                    listaRutasDisponibles.append(MAIN_RAIZ_DIR)

                if self.LOCLverbose > 3:
                    print(f'{TB}-> Elegir ruta: ')
                    for numRuta, txtRutaDisponible in enumerate(listaRutasDisponibles):
                        print(f'{TB}   {numRuta + 1}. {txtRutaDisponible}')
                    print(f'{TB}   9. Interrumpir la ejecucion y especificar una ruta') # (como argumento en el codigo o en cmd, o en el fichero de configuracion)
                    txtNumRuta = input(f'{TB}-> Ruta elegida: ')
                    try:
                        numRuta = int(txtNumRuta)
                    except:
                        numRuta = 9
                    if numRuta < len(listaRutasDisponibles) + 1:
                        LCL_rutaAscRaizBase = listaRutasDisponibles[numRuta - 1]
                        print(
                            f'Opcion selecionada: {numRuta} -> {LCL_rutaAscRaizBase}'
                        )
                    else:
                        if numRuta != 9:
                            print(
                                f'Opcion selecionada ({numRuta}) no disponible.'
                            )
                        print('\nSe interrumpe la ejecucion')
                        sys.exit(0)
                else:
                    if len(listaRutasDisponibles) >= 2:
                        LCL_rutaAscRaizBase = listaRutasDisponibles[1]
                    else:
                        LCL_rutaAscRaizBase = listaRutasDisponibles[0]
            print('{:=^80}'.format(''))
        # ======================================================================
        self.LOCLrutaAscRaizBase = LCL_rutaAscRaizBase
        # ======================================================================

    # ==========================================================================
    def verificarMarcoCoord(self):
        # ======================================================================
        # Si no se ha ejecutado setRangeUTM<> se usan todos los asc disponibles.
        if not self.marcoCoordEjecutado:
            TRNS_verbose = self.LOCLverbose
            self.setRangeUTM(
                LCL_marcoCoordMiniX=0,
                LCL_marcoCoordMaxiX=0,
                LCL_marcoCoordMiniY=0,
                LCL_marcoCoordMaxiY=0,
                LCL_marcoPatronTest=False,
                LCL_verbose=False,
            )
            self.marcoCoordEjecutado = False
            self.LOCLverbose = TRNS_verbose
            
            self.LOCLpatronVectrName = None
            self.LOCLpatronLayerName = None
            self.LOCLtesteoVectrName = None
            self.LOCLtesteoLayerName = None

        if self.LOCLverbose:
            if not self.marcoCoordEjecutado:
                print('clidtwins-> AVISO: no se ha ejecurtado el metodo .setRangeUTM para delimitar la zona de estudio.\n'
                      f'{TB}-> Se adopta la envolvente de los ficheros ASC que se encuentren en {self.LOCLrutaAscRaizBase}\n'
                      f'{TB}con dasoLidarVars (siempre que se esten los ficheros correspondientes a todas las dasoLidarVars).')
            elif not self.marcoCoordDisponible and not self.GLBLmarcoPatronTest:
                print('clidtwins-> AVISO: no se dispone de coordenadas para delimitar la zona de estudio.\n'
                      f'{TB}-> Se adopta la envolvente de los ficheros ASC que se encuentren en {self.LOCLrutaAscRaizBase}\n'
                      f'{TB}con dasoLidarVars (siempre que se esten los ficheros correspondientes a todas las dasoLidarVars).')
            elif self.marcoCoordDisponible and self.GLBLmarcoPatronTest and self.usarVectorFileParaDelimitarZona:
                print('clidtwins-> AVISO: se delimita la zona de estudio que abarca tanto las coordenadas indicadas expresamente\n'
                      f'{TB}como la envolvente de los ficheros de referencia y chequeo para las variables dasoLidar (patron y testeo).')
            elif self.GLBLmarcoPatronTest and self.usarVectorFileParaDelimitarZona:
                print('clidtwins-> Se delimita la zona de estudio con la envolvente de los ficheros\n'
                      f'{TB}de referencia y chequeo para las variables dasoLidar (patron y testeo).')
            else:
                print('clidtwins-> Se delimita la zona de estudio con las coordenadas indicadas expresamente.')
        # ======================================================================

    # ==========================================================================
    def createMultiDasoLayerRasterFile(
            self,
            LCL_rutaCompletaMFE=None,
            LCL_cartoMFEcampoSp=None,
            LCL_rasterPixelSize=None,  # opcional
            LCL_outRasterDriver=None,  # opcional
            LCL_cartoMFErecorte=None,  # opcional
            LCL_varsTxtFileName=None,  # opcional
        ):
        f"""Create a new raster file with one layer for every dasoLidar Variable
and two more layers for forest type (land cover) and stand type.
        Attributes
        ----------
        LCL_rutaCompletaMFE : str
            Default: None (optional)
        LCL_cartoMFEcampoSp : str
            Default: None (optional)
        LCL_rasterPixelSize : int
            Default: {GLO.GLBLrasterPixelSizePorDefecto} (optional)
        LCL_outRasterDriver : str
            Default: '{GLO.GLBLoutRasterDriverPorDefecto}' (optional)
        LCL_cartoMFErecorte : str
            Default: '{GLO.GLBLcartoMFErecortePorDefecto}' (optional)
        LCL_varsTxtFileName : str
            Default: '{GLO.GLBLvarsTxtFileNamePorDefecto}' (optional)
        """

        if hasattr(self, 'inFilesListAllTypes'):
            if len((self.inFilesListAllTypes)[0]) == 0:
                print(f'clidtwins-> AVISO: no se han encontrado ficheros con las variables dasoLidar.')
                print(f'{TB}-> Se interrume el metodo createMultiDasoLayerRasterFile')
                return
        else:
            if self.LOCLverbose:
                print(f'clidtwins-> AVISO: antes de generar y analizar el nuevo raster con las variables dasoLidar')
                print(f'{TB}-> hay que buscar ficheros con dichas variables (metodo searchSourceFiles)')
                print(f'{TB}-> Se interrume el metodo createMultiDasoLayerRasterFile')
                return

        if LCL_rutaCompletaMFE is None:
            self.LOCLrutaCompletaMFE = GLO.GLBLrutaCompletaMFEPorDefecto
        else:
            self.LOCLrutaCompletaMFE = LCL_rutaCompletaMFE
        if LCL_cartoMFEcampoSp is None:
            self.LOCLcartoMFEcampoSp = GLO.GLBLcartoMFEcampoSpPorDefecto
        else:
            self.LOCLcartoMFEcampoSp = LCL_cartoMFEcampoSp

        if LCL_rasterPixelSize is None:
            self.LOCLrasterPixelSize = GLO.GLBLrasterPixelSizePorDefecto
        else:
            self.LOCLrasterPixelSize = LCL_outRasterDriver

        if LCL_outRasterDriver is None:
            self.LOCLoutRasterDriver = self.GLBLoutRasterDriver
        else:
            self.LOCLoutRasterDriver = LCL_outRasterDriver
        if LCL_cartoMFErecorte is None:
            self.LOCLcartoMFErecorte = self.GLBLcartoMFErecorte
        else:
            self.LOCLcartoMFErecorte = LCL_cartoMFErecorte
        if LCL_varsTxtFileName is None:
            self.LOCLvarsTxtFileName = self.GLBLvarsTxtFileName
        else:
            self.LOCLvarsTxtFileName = LCL_varsTxtFileName

        self.LOCLcartoMFEpathName = os.path.dirname(self.LOCLrutaCompletaMFE)
        self.LOCLcartoMFEfileName = os.path.basename(self.LOCLrutaCompletaMFE)
        self.LOCLcartoMFEfileNSinExt, self.LOCLcartoMFEfileSoloExt = os.path.splitext(self.LOCLcartoMFEfileName)

        #===========================================================================
        # En teoria no pasa por aqui si antes no se ha ejecutado el metodo .searchSourceFiles<>
        # que, a su vez llama al metodo .setRangeUTM<> para establecer los limites de la zona de analisis.
        # Con esto, los limites quedan establecidos con setRangeUTM<> o, en su defecto, al leer los ficheros.
        # Al ejecutar estos metodos, ningun limite del marco puede quedar a 0. No obstante,
        # si se llega aqui sin pasar por esos metodos (creando manualmente la propiedad inFilesListAllTypes) 
        # se verifica de nuevo que haya limites de coordenadas por los cuatro costados.
        if hasattr(self, 'LOCLpatronVectrName') and not self.LOCLpatronVectrName is None:
            if (
                self.LOCLmarcoCoordMiniX <= 0
                or self.LOCLmarcoCoordMaxiX <= 0
                or self.LOCLmarcoCoordMiniY <= 0
                or self.LOCLmarcoCoordMaxiY <= 0
            ):
                if self.LOCLverbose:
                    print('\n{:_^80}'.format(''))
                    print(f'clidtwins-> AVISO: no se han establecido previamente los limites de la zona de analisis.')
                    if self.LOCLpatronLayerName == '' or self.LOCLpatronLayerName is None or (self.LOCLpatronVectrName.lower()).endswith('.shp'):
                        print(f'{TB}-> Se adopta como rango de coordenadas la extension de la capa {self.LOCLpatronVectrName}')
                    else:
                        print(f'{TB}-> Se adopta como rango de coordenadas la extension de la capa {self.LOCLpatronVectrName} layer {self.LOCLpatronLayerName}')
                    print('{:=^80}'.format(''))
                self.setRangeUTM(
                    LCL_marcoPatronTest=True,
                    LCL_rutaAscRaizBase=self.LOCLrutaAscRaizBase,
                    LCL_patronVectrName=self.LOCLpatronVectrName,
                    LCL_patronLayerName=self.LOCLpatronLayerName,
                )
                if (
                    self.LOCLmarcoCoordMiniX == 0
                    or self.LOCLmarcoCoordMaxiX == 0
                    or self.LOCLmarcoCoordMiniY == 0
                    or self.LOCLmarcoCoordMaxiY == 0
                ):
                    self.marcoCoordDisponible = False
        #===========================================================================

        #===========================================================================
        # Formatos raster alternativos a GTiff:
        # self.GLBLoutRasterDriver = "JP2ECW"
        #     https://gdal.org/drivers/raster/jp2ecw.html#raster-jp2ecw
        #     Requiere descargar:
        #         https://download.hexagongeospatial.com/en/downloads/ecw/erdas-ecw-jp2-sdk-v5-4
        # self.GLBLoutRasterDriver = 'JP2OpenJPEG' # Solo permite copiar y editar, no crear
        #     https://gdal.org/drivers/raster/jp2openjpeg.html
        # self.GLBLoutRasterDriver = 'KEA'
        #     https://gdal.org/drivers/raster/kea.html#raster-kea
        # self.GLBLoutRasterDriver = 'HDF5'
        #     https://gdal.org/drivers/raster/hdf5.html#raster-hdf5
        # self.GLBLoutRasterDriver = 'SENTINEL2'
        #     https://gdal.org/drivers/raster/sentinel2.html#raster-sentinel2
        # self.GLBLoutRasterDriver = 'netCDF'
        #     https://gdal.org/drivers/raster/netcdf.html#raster-netcdf
        # self.GLBLoutRasterDriver = "GTiff"
        #     https://gdal.org/drivers/raster/gtiff.html#raster-gtiff
        if self.GLBLoutRasterDriver == 'GTiff':
            self.driverExtension = 'tif'
        elif self.GLBLoutRasterDriver == 'JP2ECW':
            self.driverExtension = 'jp2'
        elif self.GLBLoutRasterDriver == 'JP2OpenJPEG':
            self.driverExtension = 'jp2'
        elif self.GLBLoutRasterDriver == 'KEA':
            self.driverExtension = 'KEA'
        elif self.GLBLoutRasterDriver == 'HDF5':
            self.driverExtension = 'H5'
        else:
            self.driverExtension = 'xxx'
        if self.GLBLoutRasterDriver == "GTiff":
            self.outputOptions = ['COMPRESS=LZW']
            self.outputOptions.append('BIGTIFF=YES')
        else:
            self.outputOptions = []
        #===========================================================================

        self.LOCLoutFileNameWExt_mergedUniCellAllDasoVars = '{}_{}_Global.{}'.format('uniCellAllDasoVars', self.idInputDir, self.driverExtension)
        self.LOCLoutPathNameRuta = os.path.join(self.LOCLrutaAscRaizBase, self.LOCLoutputSubdirNew)

        if self.LOCLverbose:
            print('\n{:_^80}'.format(''))
            print(f'clidtwins-> Outputs:')
            print(f'{TB}-> Ruta para los ficheros de salida:')
            print(f'{TB}{TV}{self.LOCLoutPathNameRuta}')
            print(f'{TB}-> Se crea un fichero merge con todas las variables dasoLidar:')
            print(f'{TB}{TV}{self.LOCLoutFileNameWExt_mergedUniCellAllDasoVars}')

            if self.marcoCoordDisponible and TRNS_buscarBloquesSoloDentroDelMarcoUTM:
                    print(f'{TB}{TV}-> Integra todos los bloques localizados dentro del rango de coordenadas: '
                          f'X: {self.LOCLmarcoCoordMiniX}-{self.LOCLmarcoCoordMaxiX}; '
                          f'Y: {self.LOCLmarcoCoordMiniY}-{self.LOCLmarcoCoordMaxiY}')
            else:
                print(f'{TB}{TV}-> Integra todos los bloques localizados ')
            print(f'{TB}{TV}-> Una variable en cada banda mas dos bandas adicionales con tipo de bosque (MFE) y tipo de masa (ad-hoc)')

        if not os.path.exists(self.LOCLoutPathNameRuta):
            if self.LOCLverbose:
                print(f'{TB}-> No existe directorio %s -> Se crea automaticamente' % (self.LOCLoutPathNameRuta))
            try:
                os.makedirs(self.LOCLoutPathNameRuta)
            except:
                print('\nATENCION: No se ha podido crear el directorio {}'.format(self.LOCLoutPathNameRuta))
                print(f'{TB}Revisar derechos de escritura en esa ruta')
                sys.exit(0)
        else:
            if self.LOCLverbose:
                print(f'{TB}-> Ya existe el directorio {self.LOCLoutPathNameRuta}')
                print(f'{TB}{TV}-> Se agregan los outputs (tif, txt, npz, ...) a este directorio')
        if self.LOCLverbose:
            print('{:=^80}'.format(''))
        # ======================================================================

        # ======================================================================
        # Primer tipo de fichero (y de variable) de la lista:
        (
            self.noDataDasoVarAll,
            self.outputGdalDatatypeAll,
            self.outputNpDatatypeAll,
            self.nCeldasX_Destino,
            self.nCeldasY_Destino,
            self.metrosPixelX_Destino,
            self.metrosPixelY_Destino,
            self.nMinX_tif,
            self.nMaxY_tif,
            self.nFicherosDisponiblesPorTipoVariable,
            self.arrayMinVariables,
            self.arrayMaxVariables,
            self.nMinTipoMasa,
            self.nMaxTipoMasa,
        ) = clidraster.crearRasterTiff(
            # self.LOCLrutaAscRaizBase,
            self_inFilesListAllTypes=self.inFilesListAllTypes,
            self_LOCLoutPathNameRuta=self.LOCLoutPathNameRuta,
            self_LOCLoutFileNameWExt=self.LOCLoutFileNameWExt_mergedUniCellAllDasoVars,
            self_LOCLlistaDasoVarsFileTypes=self.LOCLlistaDasoVarsFileTypes,

            PAR_rasterPixelSize=self.LOCLrasterPixelSize,
            PAR_outRasterDriver=self.GLBLoutRasterDriver,
            PAR_noDataTiffProvi=self.GLBLnoDataTiffProvi,
            PAR_noDataMergeTiff=self.GLBLnoDataTiffFiles,
            PAR_outputOptions=self.outputOptions,
            PAR_nInputVars=self.nInputVars,
            PAR_outputGdalDatatype=None,
            PAR_outputNpDatatype=None,

            PAR_cartoMFEpathName=self.LOCLcartoMFEpathName,
            PAR_cartoMFEfileName=self.LOCLcartoMFEfileName,
            PAR_cartoMFEfileSoloExt=self.LOCLcartoMFEfileSoloExt,
            PAR_cartoMFEfileNSinExt=self.LOCLcartoMFEfileNSinExt,

            PAR_cartoMFEcampoSp=self.LOCLcartoMFEcampoSp,
            PAR_cartoMFErecorte=self.GLBLcartoMFErecorte,

            PAR_generarDasoLayers=True,
            PAR_ambitoTiffNuevo=self.GLBLambitoTiffNuevo,
            PAR_verbose=self.LOCLverbose,
        )


    # ==========================================================================
    def analyzeMultiDasoLayerRasterFile(
            self,
            LCL_patronVectrName=None,
            LCL_patronLayerName=None,
        ):
        f"""Analize the dasoLidar Variables included in the created raster file (with one band for every DLV).
        ----------
        LCL_patronVectrName : str
            Default: None (optional)
        LCL_patronLayerName : str
            Default: None (optional)
        """
        #===========================================================================
        # DistanciaEuclideaMedia
        # PorcentajeDeProximidad
        # CoeficienteParidad
        # Proximidad
        # Semejanza
        # Similitud
        # Analogia
        # Homogeneidad
        #===========================================================================

        if LCL_patronVectrName is None:
            self.LOCLpatronVectrName = GLO.GLBLpatronVectrNamePorDefecto
        else:
            self.LOCLpatronVectrName = LCL_patronVectrName
        if LCL_patronLayerName is None:
            self.LOCLpatronLayerName = GLO.GLBLpatronLayerNamePorDefecto
        else:
            self.LOCLpatronLayerName = LCL_patronLayerName

        #===========================================================================
        (
            self.outputRangosFileNpzSinPath,
            self.nBandasRasterOutput,
            self.rasterDatasetAll,
            self.listaCeldasConDasoVarsPatron,
            self.dictHistProb01,
            self.myNBins,
            self.myRange,
            self.pctjTipoBosquePatronMasFrecuente1,
            self.codeTipoBosquePatronMasFrecuente1,
            self.pctjTipoBosquePatronMasFrecuente2,
            self.codeTipoBosquePatronMasFrecuente2,
            self.histProb01Patron,
        ) = recortarRasterTiffPatronDasoLidar(
            self.LOCLrutaAscRaizBase,
            self.LOCLoutPathNameRuta,
            self.LOCLoutFileNameWExt_mergedUniCellAllDasoVars,
            self.noDataDasoVarAll,
            self.outputNpDatatypeAll,
            self.nMinTipoMasa,
            self.nMaxTipoMasa,
            self.nInputVars,
            self.nFicherosDisponiblesPorTipoVariable,
            self_LOCLlistaDasoVarsMovilidad=self.LOCLlistaDasoVarsMovilidad,
            # self_LOCLlistaDasoVarsPonderado=self.LOCLlistaDasoVarsPonderado,
            self_LOCLvarsTxtFileName=self.GLBLvarsTxtFileName,
            self_LOCLpatronVectrName=self.LOCLpatronVectrName,
            self_LOCLpatronLayerName=self.LOCLpatronLayerName,
            self_LOCLlistLstDasoVars=self.LOCLlistLstDasoVars,

            self_nCeldasX_Destino=self.nCeldasX_Destino,
            self_nCeldasY_Destino=self.nCeldasY_Destino,
            self_metrosPixelX_Destino=self.metrosPixelX_Destino,
            self_metrosPixelY_Destino=self.metrosPixelY_Destino,
            self_nMinX_tif=self.nMinX_tif,
            self_nMaxY_tif=self.nMaxY_tif,

            self_LOCLverbose=self.LOCLverbose,
        )
        # ======================================================================
        if self.nBandasRasterOutput != self.nBandasPrevistasOutput:
            print('clidtwins-> ATENCION: la capa creada con las dasoVars en la zona de referencia (patron) no niene el numero previsto de bandas')
            print(f'{TB}-> Numero previsto: {self.nBandasPrevistasOutput}; numero de bandas en la capa creada {self.nBandasRasterOutput}')
            sys.exit(0)

        mostrarExportarRangos(
            self.LOCLoutPathNameRuta,
            self.outputRangosFileNpzSinPath,
            self.dictHistProb01,
            self.nInputVars,
            self.myRange,
            self.myNBins,
            self.nFicherosDisponiblesPorTipoVariable,
            self_LOCLvarsTxtFileName=self.GLBLvarsTxtFileName,
            self_LOCLlistLstDasoVars=self.LOCLlistLstDasoVars,
        )
        # ======================================================================


    # ==========================================================================
    def chequearCompatibilidadConTesteoVector(
            self,
            LCL_testeoVectrName=None,
            LCL_testeoLayerName=None,
        ):
        # Variables de clase (previamente definidas) que se usan en esta funcion:
        # self.LOCLrutaAscRaizBase,
        # self.LOCLoutPathNameRuta,
        # self.LOCLoutFileNameWExt_mergedUniCellAllDasoVars,
        # self.noDataDasoVarAll,
        # self.outputNpDatatypeAll,
        # self.nBandasPrevistasOutput,
        # self.nInputVars,
        # self.nFicherosDisponiblesPorTipoVariable,
        # self.listaCeldasConDasoVarsPatron,
        # self.dictHistProb01,
        # self.myNBins,
        # self.myRange,
        # self.ññ
        # self.pctjTipoBosquePatronMasFrecuente1,
        # self.codeTipoBosquePatronMasFrecuente1,
        # self.pctjTipoBosquePatronMasFrecuente2,
        # self.codeTipoBosquePatronMasFrecuente2,
        # self.histProb01Patron,
        # self.GLBLumbralMatriDist,
        # self.LOCLlistLstDasoVars,
        self.LOCLtesteoVectrName = LCL_testeoVectrName
        self.LOCLtesteoLayerName = LCL_testeoLayerName

        if ':/' in self.LOCLtesteoVectrName or ':\\' in self.LOCLtesteoVectrName:
            testeoVectrNameConPath = self.LOCLtesteoVectrName
        else:
            testeoVectrNameConPath = os.path.join(self.LOCLrutaAscRaizBase, self.LOCLtesteoVectrName)
        mergedUniCellAllDasoVarsFileNameConPath = os.path.join(self.LOCLoutPathNameRuta, self.LOCLoutFileNameWExt_mergedUniCellAllDasoVars)
        outputRasterNameClip = mergedUniCellAllDasoVarsFileNameConPath.replace('Global.', 'Testeo.')
        print('\n{:_^80}'.format(''))
        print(f'Recortando testeoArea {mergedUniCellAllDasoVarsFileNameConPath} con {testeoVectrNameConPath}')
        rasterDataset = gdal.Open(mergedUniCellAllDasoVarsFileNameConPath, gdalconst.GA_ReadOnly)

        # outputBand1 = rasterDataset.GetRasterBand(1)
        # arrayBanda1 = outputBand1.ReadAsArray().astype(self.outputNpDatatypeAll)
        # Ver: https://gdal.org/python/osgeo.gdal-module.html
        try:
            rasterDatasetClip = gdal.Warp(
                outputRasterNameClip,
                rasterDataset,
                cutlineDSName=testeoVectrNameConPath,
                cutlineLayer=self.LOCLtesteoLayerName,
                cropToCutline=True,
                # dstNodata=np.nan,
                dstNodata=self.noDataDasoVarAll,
            )
        except:
            print(f'\nclidtwins-> No se ha podido recortar el raster generado con {testeoVectrNameConPath}, cutlineLayer: {self.LOCLtesteoLayerName}, {type(self.LOCLtesteoLayerName)}')
            print(f'{TB}Revisar si se ha generado adecuadamente el raster {mergedUniCellAllDasoVarsFileNameConPath}')
            print(f'{TB}Revisar si la capa vectorial de recorte es correcta, no esta bloqueada y (tiene un poligono) {testeoVectrNameConPath}')
            sys.exit(0)

        rasterDatasetClip = gdal.Open(outputRasterNameClip, gdalconst.GA_ReadOnly)
        nBandasRasterOutput = rasterDatasetClip.RasterCount
        if nBandasRasterOutput != self.nBandasPrevistasOutput:
            print(f'\nAVISO: el numero de bandas del raster generado ({nBandasRasterOutput}) no es igual al previsto ({self.nBandasPrevistasOutput}), es decir num. de variables + 2 (num variables: {self.nInputVars})')

        outputBand1Clip = rasterDatasetClip.GetRasterBand(1)
        arrayBanda1Clip = outputBand1Clip.ReadAsArray().astype(self.outputNpDatatypeAll)
        # Mascara con ceros en celdas con alguna variable noData
        arrayBandaXMaskTesteo = np.full_like(arrayBanda1Clip, 0, dtype=np.uint8)
        for nBanda in range(1, nBandasRasterOutput + 1):
            outputBandXClip = rasterDatasetClip.GetRasterBand(nBanda)
            arrayBandaXClip = outputBandXClip.ReadAsArray().astype(self.outputNpDatatypeAll)
            arrayBandaXMaskTesteo[arrayBandaXClip == self.noDataDasoVarAll] = 1

        nCeldasConDasoVarsOk = np.count_nonzero(arrayBandaXMaskTesteo == 0)
        listaCeldasConDasoVarsTesteo = np.zeros(nCeldasConDasoVarsOk * nBandasRasterOutput, dtype=self.outputNpDatatypeAll).reshape(nCeldasConDasoVarsOk, nBandasRasterOutput)
        print(f'Numero de celdas Testeo con dasoVars ok: {nCeldasConDasoVarsOk}')

        # Las self.nInputVars primeras bandas corresponden a las variables utilizadas (self_LOCLlistaDasoVarsFileTypes)
        # La penultima corresponde al tipo de bosque o cobertura MFE
        # La ultima corresponde al tipo de masa.
        # La numeracion de las bandas empieza en 1 y la de variables empieza en 0.
        nVariablesNoOk = 0
        tipoBosqueOk = 0
        for nBanda in range(1, nBandasRasterOutput + 1):
            # Si para esa variable estan todos los bloques:
            nInputVar = nBanda - 1
            if nInputVar >= 0 and nInputVar < self.nInputVars:
                if self.nFicherosDisponiblesPorTipoVariable[nInputVar] != self.nFicherosDisponiblesPorTipoVariable[0]:
                    # print(f'\nHistograma para banda {nBanda} (variable {nInputVar}: {self.LOCLlistLstDasoVars[nInputVar][1]})')
                    claveDef = f'{str(nInputVar)}_{self.LOCLlistLstDasoVars[nInputVar][1]}_ref'
                    print(f'\n(2) Chequeando rangos admisibles para: {claveDef}')
                    print(f'{TB}AVISO: La banda {nBanda} (variable {nInputVar}) no cuenta con fichero para todos los bloques ({self.nFicherosDisponiblesPorTipoVariable[nInputVar]} de {self.nFicherosDisponiblesPorTipoVariable[0]})')
                    continue
            outputBandXClip = rasterDatasetClip.GetRasterBand(nBanda)
            arrayBandaXClip = outputBandXClip.ReadAsArray().astype(self.outputNpDatatypeAll)
            # hist = histogram(arrayBandaXClip)
            # hist = np.histogram(arrayBandaXClip, bins=5, range=(0, arrayBandaXClip.max()))

            # https://numpy.org/doc/stable/reference/maskedarray.html
            # https://numpy.org/doc/stable/reference/routines.ma.html#conversion-operations
            arrayBandaXClipMasked = ma.masked_array(
                arrayBandaXClip,
                mask=arrayBandaXMaskTesteo,
                dtype=self.outputNpDatatypeAll
                )
            # print(f'Numero de puntos Testeo con dasoVars ok (banda {nBanda}):', len(ma.compressed(arrayBandaXClipMasked)))
            listaCeldasConDasoVarsTesteo[:, nInputVar] = ma.compressed(arrayBandaXClipMasked)

            histNumberTesteo = np.histogram(arrayBandaXClip, bins=self.myNBins[nBanda], range=self.myRange[nBanda])
            histProbabTesteo = np.histogram(arrayBandaXClip, bins=self.myNBins[nBanda], range=self.myRange[nBanda], density=True)
            # print(f'\nhistProbabTesteo[0]: {type(histProbabTesteo[0])}')
            histProb01Testeo = np.array(histProbabTesteo[0]) * ((self.myRange[nBanda][1] - self.myRange[nBanda][0]) / self.myNBins[nBanda])

            # print('-->> histProbabTesteo:', histProbabTesteo)
            # print('-->> histProb01Testeo:', histProb01Testeo)

            # if nBanda == nBandasRasterOutput:
            #     print(f'\nHistograma para tipos de masa (banda {nBanda})')
            # elif nBanda == nBandasRasterOutput - 1:
            #     print(f'\nHistograma para tipos de bosque (banda {nBanda})')
            # else:
            #     if nInputVar < len(self.LOCLlistLstDasoVars):
            #         print(f'\nHistograma para banda {nBanda} (variable {nInputVar}: {self.LOCLlistLstDasoVars[nInputVar][1]})')
            #     else:
            #         print(f'\nHistograma para banda {nBanda} (variable {nInputVar} de {self.LOCLlistLstDasoVars})')
            # print(f'{TB}-> Numero puntos: {(histNumberTesteo[0]).sum()}-> {histNumberTesteo}')
            # # print(f'{TB}-> Suma frecuencias: {round(histProb01Testeo.sum(), 2)}')

            if nBanda == nBandasRasterOutput - 1:
                print(f'\nChequeando Tipos de bosque (banda {nBanda}):')
                try:
                    tipoBosqueUltimoNumero = np.max(np.nonzero(histNumberTesteo[0]))
                except:
                    tipoBosqueUltimoNumero = 0
                histogramaTemp = (histNumberTesteo[0]).copy()
                histogramaTemp.sort()
                codeTipoBosqueTesteoMasFrecuente1 = (histNumberTesteo[0]).argmax(axis=0)
                arrayPosicionTipoBosqueTesteo1 = np.where(histNumberTesteo[0] == histogramaTemp[-1])
                arrayPosicionTipoBosqueTesteo2 = np.where(histNumberTesteo[0] == histogramaTemp[-2])
                print(f'{TB}-> Tipo de bosque principal (testeo): {codeTipoBosqueTesteoMasFrecuente1}; frecuencia: {int(round(100 * histProb01Testeo[codeTipoBosqueTesteoMasFrecuente1], 0))} %')
                # print(f'{TB}-> {arrayPosicionTipoBosqueTesteo1}')
                for contadorTB1, numPosicionTipoBosqueTesteo1 in enumerate(arrayPosicionTipoBosqueTesteo1[0]):
                    # print(f'{TB}-> {numPosicionTipoBosqueTesteo1}')
                    print(f'{TB}-> {contadorTB1} Tipo de bosque primero (testeo): {numPosicionTipoBosqueTesteo1}; frecuencia: {int(round(100 * histProb01Testeo[numPosicionTipoBosqueTesteo1], 0))} %')
                if self.histProb01Patron[arrayPosicionTipoBosqueTesteo2[0][0]] != 0:
                    for contadorTB2, numPosicionTipoBosqueTesteo2 in enumerate(arrayPosicionTipoBosqueTesteo2[0]):
                        # print(f'{TB}-> {numPosicionTipoBosqueTesteo2}')
                        if histProb01Testeo[numPosicionTipoBosqueTesteo2] != 0:
                            print(f'{TB}-> {contadorTB2} Tipo de bosque segundo (testeo): {numPosicionTipoBosqueTesteo2}; frecuencia: {int(round(100 * histProb01Testeo[numPosicionTipoBosqueTesteo2], 0))} %')
                else:
                    print(f'{TB}-> Solo hay tipo de bosque princial')

                if codeTipoBosqueTesteoMasFrecuente1 != arrayPosicionTipoBosqueTesteo1[0][0]:
                    print(f'{TB}-> ATENCION: revisar esto porque debe haber algun error: {codeTipoBosqueTesteoMasFrecuente1} != {arrayPosicionTipoBosqueTesteo1[0][0]}')
                if len(arrayPosicionTipoBosqueTesteo1[0]) == 1:
                    codeTipoBosqueTesteoMasFrecuente2 = arrayPosicionTipoBosqueTesteo2[0][0]
                else:
                    codeTipoBosqueTesteoMasFrecuente2 = arrayPosicionTipoBosqueTesteo1[0][1]

                pctjTipoBosqueTesteoMasFrecuente1 = int(round(100 * histProb01Testeo[codeTipoBosqueTesteoMasFrecuente1], 0))
                pctjTipoBosqueTesteoMasFrecuente2 = int(round(100 * histProb01Testeo[codeTipoBosqueTesteoMasFrecuente2], 0))

                print(f'{TB}-> Tipos de bosque mas frecuentes (testeo): 1-> {codeTipoBosqueTesteoMasFrecuente1} ({pctjTipoBosqueTesteoMasFrecuente1} %); 2-> {codeTipoBosqueTesteoMasFrecuente2} ({pctjTipoBosqueTesteoMasFrecuente2} %)')

                # print(f'{TB}-> Numero pixeles de cada tipo de bosque (testeo) ({(histNumberTesteo[0]).sum()}):\n{histNumberTesteo[0][:tipoBosqueUltimoNumero + 1]}')
                print(f'{TB}-> Numero pixeles de cada tipo de bosque (testeo) ({(histNumberTesteo[0]).sum()}):')
                for numTipoBosque in range(len(histNumberTesteo[0])):
                    if histNumberTesteo[0][numTipoBosque] != 0:
                        print(f'tipoBosque: {numTipoBosque} -> nPixeles: {histNumberTesteo[0][numTipoBosque]}')

                if self.pctjTipoBosquePatronMasFrecuente1 >= 70 and pctjTipoBosqueTesteoMasFrecuente1 >= 70:
                    if (codeTipoBosqueTesteoMasFrecuente1 == self.codeTipoBosquePatronMasFrecuente1):
                        print(f'{TB}-> Tipo de bosque principal con mas del 70 de ocupacion SI ok:')
                        print(f'{TB}{TV}-> Tipo mas frecuente (patron): 1-> {self.codeTipoBosquePatronMasFrecuente1} ({self.pctjTipoBosquePatronMasFrecuente1} %)')
                        print(f'{TB}{TV}-> Tipo mas frecuente (testeo): 1-> {codeTipoBosqueTesteoMasFrecuente1} ({pctjTipoBosqueTesteoMasFrecuente1} %)')
                        tipoBosqueOk = 10
                    else:
                        binomioEspecies = f'{codeTipoBosqueTesteoMasFrecuente1}_{self.codeTipoBosquePatronMasFrecuente1}'
                        if binomioEspecies in (GLO.GLBLdictProximidadInterEspecies).keys():
                            tipoBosqueOk = GLO.GLBLdictProximidadInterEspecies[binomioEspecies]
                        else:
                            tipoBosqueOk = 0
                        print(f'{TB}-> Tipo de bosque principal con mas del 70 de ocupacion NO ok: {tipoBosqueOk}')
                else:
                    if (
                        codeTipoBosqueTesteoMasFrecuente1 == self.codeTipoBosquePatronMasFrecuente1
                        and codeTipoBosqueTesteoMasFrecuente2 == self.codeTipoBosquePatronMasFrecuente2
                    ):
                        print(f'{TB}-> Tipo de bosque principal (menos del 70 de ocupacion) y segundo SI ok:')
                        tipoBosqueOk = 10
                    elif (
                        codeTipoBosqueTesteoMasFrecuente1 == self.codeTipoBosquePatronMasFrecuente2
                        and codeTipoBosqueTesteoMasFrecuente2 == self.codeTipoBosquePatronMasFrecuente1
                    ):
                        print(f'{TB}-> Tipo de bosque principal (menos del 70 de ocupacion) y segundo XX ok:')
                        tipoBosqueOk = 10
                    else:
                        binomioEspecies = f'{codeTipoBosqueTesteoMasFrecuente1}_{self.codeTipoBosquePatronMasFrecuente1}'
                        if binomioEspecies in (GLO.GLBLdictProximidadInterEspecies).keys():
                            tipoBosqueOk = GLO.GLBLdictProximidadInterEspecies[binomioEspecies] - 1
                        else:
                            tipoBosqueOk = 0
                        print(f'{TB}-> Tipos de bosque principal (menos del 70 de ocupacion) y segundo NO ok: {tipoBosqueOk}')
                    print(f'{TB}{TV}-> Tipo mas frecuente (patron): 1-> {self.codeTipoBosquePatronMasFrecuente1} ({self.pctjTipoBosquePatronMasFrecuente1} %)')
                    print(f'{TB}{TV}-> Tipo mas frecuente (testeo): 1-> {codeTipoBosqueTesteoMasFrecuente1} ({pctjTipoBosqueTesteoMasFrecuente1} %)')
                    print(f'{TB}{TV}-> Tipo mas frecuente (patron): 2-> {self.codeTipoBosquePatronMasFrecuente2} ({self.pctjTipoBosquePatronMasFrecuente2} %)')
                    print(f'{TB}{TV}-> Tipo mas frecuente (testeo): 2-> {codeTipoBosqueTesteoMasFrecuente2} ({pctjTipoBosqueTesteoMasFrecuente2} %)')

            elif nInputVar >= 0 and nInputVar < self.nInputVars:
                claveDef = f'{str(nInputVar)}_{self.LOCLlistLstDasoVars[nInputVar][1]}_ref'
                claveMin = f'{str(nInputVar)}_{self.LOCLlistLstDasoVars[nInputVar][1]}_min'
                claveMax = f'{str(nInputVar)}_{self.LOCLlistLstDasoVars[nInputVar][1]}_max'
                # self.dictHistProb01[claveDef] = histProb01Testeo



                if self.calcularRangoVariables:
                    print('\n{:_^80}'.format(''))
                    print('\n\n\nclidtwins-> ATENCION: calcular rangos aqui.\n\n\n')
                    print('{:=^80}'.format(''))


                print(f'\n(3) Chequeando rangos admisibles para: {claveDef}')
                # print(f'{TB}Valores de referencia:')
                # print(f'{TB}{TV}-> self.dictHistProb01[claveDef]:', self.dictHistProb01[claveDef])
                todosLosRangosOk = True
                nTramosFueraDeRango = 0
                # for nRango in range(len(histProb01Testeo)):
                for nRango in range(self.myNBins[nBanda]):
                    histProb01Testeo[nRango] = round(histProb01Testeo[nRango], 3)
                    limInf = nRango * (self.myRange[nBanda][1] - self.myRange[nBanda][0]) / self.myNBins[nBanda]
                    limSup = (nRango + 1) * (self.myRange[nBanda][1] - self.myRange[nBanda][0]) / self.myNBins[nBanda]
                    miRango = f'{limInf}-{limSup}'
                    if histProb01Testeo[nRango] < self.dictHistProb01[claveMin][nRango]:
                        print(f'{TB}-> {claveDef}-> nRango {nRango} de {self.myNBins[nBanda]} ({miRango}): {histProb01Testeo[nRango]} debajo del rango {self.dictHistProb01[claveMin][nRango]} - {self.dictHistProb01[claveMax][nRango]}; Valor de referencia: {self.dictHistProb01[claveDef][nRango]}')
                        todosLosRangosOk = False
                        nTramosFueraDeRango += 1
                    if histProb01Testeo[nRango] > self.dictHistProb01[claveMax][nRango]:
                        print(f'{TB}-> {claveDef}-> nRango {nRango} ({miRango}): {histProb01Testeo[nRango]} encima del rango {self.dictHistProb01[claveMin][nRango]} - {self.dictHistProb01[claveMax][nRango]}; Valor de referencia: {self.dictHistProb01[claveDef][nRango]}')
                        todosLosRangosOk = False
                        nTramosFueraDeRango += 1
                if todosLosRangosOk:
                    print(f'{TB}-> Todos los tramos ok.')
                else:
                    print(f'{TB}-> TestShape-> Numero de tramos fuera de rango: {nTramosFueraDeRango}')
                    if nTramosFueraDeRango >= 1:
                        nVariablesNoOk += 1

        matrizDeDistancias = distance_matrix(self.listaCeldasConDasoVarsPatron, listaCeldasConDasoVarsTesteo)
        distanciaEuclideaMedia = np.average(matrizDeDistancias)
        pctjPorcentajeDeProximidad = 100 * (
            np.count_nonzero(matrizDeDistancias < self.GLBLumbralMatriDist)
            / np.ma.count(matrizDeDistancias)
        )
        print('\n{:_^80}'.format(''))
        # print('clidtwins-> Matriz de distancias:')
        # print(matrizDeDistancias[:5,:5])
        print(f'Resumen del match:')
        print(f'{TB}-> tipoBosqueOk:             {tipoBosqueOk}')
        print(f'{TB}-> nVariablesNoOk:           {nVariablesNoOk}')
        print(f'{TB}-> matrizDeDistancias.shape: {matrizDeDistancias.shape}') 
        print(f'{TB}-> Distancia media:          {distanciaEuclideaMedia}')
        print(f'{TB}-> Factor de proximidad:     {pctjPorcentajeDeProximidad}')
        print('{:=^80}'.format(''))


    # ==========================================================================
    def generarRasterCluster(
            self,
            LCL_radioClusterPix=0,
        ):
        # Variables de clase (previamente definidas) que se usan en esta funcion:
        # self.nBandasRasterOutput,
        # self.rasterDatasetAll,
        # self.outputNpDatatypeAll,
        # self.LOCLoutPathNameRuta,
        # self.outputClusterAllDasoVarsFileNameSinPath,
        # self.outputClusterTiposDeMasaFileNameSinPath,
        # self.outputClusterFactorProxiFileNameSinPath,
        # self.outputClusterDistanciaEuFileNameSinPath,
        # self.LOCLrasterPixelSize,
        # self.nMinX_tif,
        # self.nMaxY_tif,
        # self.nCeldasX_Destino,
        # self.nCeldasY_Destino,
        # self.metrosPixelX_Destino,
        # self.metrosPixelY_Destino,
        # self.LOCLoutRasterDriver,
        # self.outputOptions,
        # self.nInputVars,
        # self.noDataDasoVarAll,
        # self.GLBLnoDataTipoDMasa,
        # self.GLBLnoDataTiffFiles,
        # self.nBandasPrevistasOutput,
        # self.listaCeldasConDasoVarsPatron,
        # self.myNBins,
        # self.myRange,
        # self.pctjTipoBosquePatronMasFrecuente1,
        # self.codeTipoBosquePatronMasFrecuente1,
        # self.pctjTipoBosquePatronMasFrecuente2,
        # self.codeTipoBosquePatronMasFrecuente2,
        # self.dictHistProb01,
        # self.GLBLumbralMatriDist,
        # self.LOCLlistLstDasoVars,

        if LCL_radioClusterPix == 0:
            self.LOCLradioClusterPix = GLO.GLBLradioClusterPixPorDefecto
        elif LCL_radioClusterPix > 10:
            if self.LOCLverbose:
                print('\n{:_^80}'.format(''))
                print(f'clidtwins-> AVISO: radio de cluster excesivo ({LCL_radioClusterPix} pixeles); se reduce a 10 pixeles.')
                print('{:=^80}'.format(''))
            self.LOCLradioClusterPix = 10
        else:
            self.LOCLradioClusterPix = LCL_radioClusterPix

        self.outputClusterAllDasoVarsFileNameSinPath = '{}_{}.{}'.format('clusterAllDasoVars', self.idInputDir, self.driverExtension)
        self.outputClusterTiposDeMasaFileNameSinPath = '{}_{}.{}'.format('clusterTiposDeMasa', self.idInputDir, self.driverExtension)
        self.outputClusterDistanciaEuFileNameSinPath = '{}_{}.{}'.format('clusterDistanciaEu', self.idInputDir, self.driverExtension)
        self.outputClusterFactorProxiFileNameSinPath = '{}_{}.{}'.format('clusterFactorProxi', self.idInputDir, self.driverExtension)
        if self.LOCLverbose:
            print('\n{:_^80}'.format(''))
            print('clidtwins-> Ficheros que se generan:')
            print(f'{TB} Fichero multibanda* con las variables dasoLidar clusterizadas (radio de {self.LOCLradioClusterPix} pixeles): {self.outputClusterAllDasoVarsFileNameSinPath}')
            print(f'{TB}{TV} * Con todas las variables dasoLidar (una en cada banda) y dos bandas adicionales con tipo de bosque y tipo de masa.')
            print(f'{TB} Fichero biBanda con presencia del tipo de masa patron y proximidad a especie principal:')
            print(f'{TB}{TV} {self.outputClusterTiposDeMasaFileNameSinPath}')
            print(f'{TB}{TV} * Segunda banda: MFE')
            print(f'{TB} Fichero biBanda con la distancia euclidea al patron y especie principal clusterizados:')
            print(f'{TB}{TV} {self.outputClusterDistanciaEuFileNameSinPath}')
            print(f'{TB}{TV} * Segunda banda: MFE')
            print(f'{TB} Fichero monoBanda con el factor de proximidad al patron y proximidad a especie principal:')
            print(f'{TB}{TV} {self.outputClusterFactorProxiFileNameSinPath}')

        # ======================================================================
        # Lectura del raster con todas las variables en distintas bandas,
        # mas el tipo de bosque y el tipo de masa, por el momento sin asignar.
        # Requiere haver ejecutado antes createMultiDasoLayerRasterFile<>
        # Para generar el dict rasterDatasetAll con los datos de todas las bandas.
        # ======================================================================
        arrayBandaXinputMonoPixelAll = {}
        # arrayBandaFlip = {}
        for nBanda in range(1, self.nBandasRasterOutput + 1):
            selecBandaXinputMonoPixelAll = self.rasterDatasetAll.GetRasterBand(nBanda)
            arrayBandaXinputMonoPixelAll[nBanda - 1] = selecBandaXinputMonoPixelAll.ReadAsArray().astype(self.outputNpDatatypeAll)

            # arrayBandaFlip[nBanda - 1] = np.flipud(arrayBandaXinputMonoPixelAll[nBanda - 1])
            # arrayBandaFlip[nBanda - 1] = arrayBandaXinputMonoPixelAll[nBanda - 1].copy()
            # print('\nnBanda', nBanda)
            # print('--->>> selecBandaXinputMonoPixelAll (2):', selecBandaXinputMonoPixelAll, dir(selecBandaXinputMonoPixelAll))
            # print('--->>> shape:', arrayBandaXinputMonoPixelAll[nBanda - 1].shape)
            # print('-->>', arrayBandaXinputMonoPixelAll[nBanda - 1][0:5, 2200:2210])
            # print('-->>', arrayBandaXinputMonoPixelAll[nBanda - 1][195:199, 2200:2210])
        # ======================================================================

        # ======================================================================
        ladoCluster = (self.LOCLradioClusterPix * 2) + 1
        # ======================================================================

        # ======================================================================
        nBandasOutputMonoBanda = 1
        nBandasOutputBiBanda = 2
        nBandasOutputCluster = self.nInputVars + 2

        if self.GLBLnoDataTipoDMasa == 255 or self.GLBLnoDataTipoDMasa == 0:
            self.outputGdalDatatypeTipoMasa = gdal.GDT_Byte
            self.outputNpDatatypeTipoMasa = np.uint8
        else:
            self.outputGdalDatatypeTipoMasa = gdal.GDT_Float32
            self.outputNpDatatypeTipoMasa = np.float32
        if self.noDataDasoVarAll == 255 or self.noDataDasoVarAll == 0:
            self.outputGdalDatatypeAll = gdal.GDT_Byte
            self.outputNpDatatypeAll = np.uint8
        else:
            self.outputGdalDatatypeAll = gdal.GDT_Float32
            self.outputNpDatatypeAll = np.float32
        self.outputGdalDatatypeFloat32 = gdal.GDT_Float32
        self.outputNpDatatypeFloat32 = np.float32
        # ======================================================================

        # ======================================================================
        # Creacion de los raster, que albergaran (pixelesCluster):
        # 1. Monolayer con tipo de masa similar al de referencia (patron)
        # 2. Bilayer con DistanciaEu y MFE
        # 3. Bilayer con factorProxi y MFE
        # 4. MultiLayer clusterAllDasoVars
        # ======================================================================
        # 1. El tipo de masa similar al de referencia (patron)
        # ======================================================================
        if self.LOCLverbose:
            print('\n{:_^80}'.format(''))
            print(f'clidtwins-> Creando fichero para el layer tipoMasa {self.outputClusterTiposDeMasaFileNameSinPath}')
        outputDatasetTipoMasa, outputBandaTipoMasa = clidraster.CrearOutputRaster(
            self.LOCLoutPathNameRuta,
            self.outputClusterTiposDeMasaFileNameSinPath,
            self.nMinX_tif,
            self.nMaxY_tif,
            self.nCeldasX_Destino,
            self.nCeldasY_Destino,
            self.metrosPixelX_Destino,
            self.metrosPixelY_Destino,
            self.LOCLoutRasterDriver,
            self.outputOptions,
            nBandasOutputMonoBanda,
            self.outputGdalDatatypeTipoMasa,
            self.outputNpDatatypeTipoMasa,
            self.GLBLnoDataTipoDMasa,
            self.GLBLnoDataTipoDMasa,
            self.GLBLnoDataTiffFiles,
            generarMetaPixeles=True,
        )

        # ======================================================================
        # 2. Bilayer con DistanciaEu y MFE
        # ======================================================================
        if self.LOCLverbose:
            print('\n{:_^80}'.format(''))
            print(f'clidtwins-> Creando fichero para el layer distanciaEu {self.outputClusterDistanciaEuFileNameSinPath}')
        outputDatasetDistanciaEuclideaMedia, outputBandaDistanciaEuclideaMedia = clidraster.CrearOutputRaster(
            self.LOCLoutPathNameRuta,
            self.outputClusterDistanciaEuFileNameSinPath,
            self.nMinX_tif,
            self.nMaxY_tif,
            self.nCeldasX_Destino,
            self.nCeldasY_Destino,
            self.metrosPixelX_Destino,
            self.metrosPixelY_Destino,
            self.LOCLoutRasterDriver,
            self.outputOptions,
            nBandasOutputBiBanda,
            self.outputGdalDatatypeFloat32,
            self.outputNpDatatypeFloat32,
            self.GLBLnoDataTiffFiles,
            self.GLBLnoDataTiffFiles,
            self.GLBLnoDataTiffFiles,
            generarMetaPixeles=True,
        )
        outputBandaProximidadInterEspecies1 = outputDatasetDistanciaEuclideaMedia.GetRasterBand(2)

        # ======================================================================
        # 3. Bilayer con factorProxi y MFE
        # ======================================================================
        if self.LOCLverbose:
            print('\n{:_^80}'.format(''))
            print(f'clidtwins-> Creando fichero para el layer factorProxi {self.outputClusterFactorProxiFileNameSinPath}')
        outputDatasetPorcentajeDeProximidad, outputBandaPorcentajeDeProximidad = clidraster.CrearOutputRaster(
            self.LOCLoutPathNameRuta,
            self.outputClusterFactorProxiFileNameSinPath,
            self.nMinX_tif,
            self.nMaxY_tif,
            self.nCeldasX_Destino,
            self.nCeldasY_Destino,
            self.metrosPixelX_Destino,
            self.metrosPixelY_Destino,
            self.LOCLoutRasterDriver,
            self.outputOptions,
            nBandasOutputBiBanda,
            self.outputGdalDatatypeFloat32,
            self.outputNpDatatypeFloat32,
            self.GLBLnoDataTiffFiles,
            self.GLBLnoDataTiffFiles,
            self.GLBLnoDataTiffFiles,
            generarMetaPixeles=True,
        )
        outputBandaProximidadInterEspecies2 = outputDatasetPorcentajeDeProximidad.GetRasterBand(2)

        # ======================================================================
        # 4. MultiLayer clusterAllDasoVars
        # ======================================================================
        # Creacion del raster, con las variables y tipo de bosque clusterizados
        if self.LOCLverbose:
            print('\n{:_^80}'.format(''))
            print(f'clidtwins-> Creando fichero para el multiLayer clusterAllDasoVars {self.outputClusterAllDasoVarsFileNameSinPath}')
        outputDatasetClusterDasoVarMultiple, outputBandaClusterDasoVarBanda1 = clidraster.CrearOutputRaster(
            self.LOCLoutPathNameRuta,
            self.outputClusterAllDasoVarsFileNameSinPath,
            self.nMinX_tif,
            self.nMaxY_tif,
            self.nCeldasX_Destino,
            self.nCeldasY_Destino,
            self.metrosPixelX_Destino,
            self.metrosPixelY_Destino,
            self.LOCLoutRasterDriver,
            self.outputOptions,
            nBandasOutputCluster,
            self.outputGdalDatatypeAll,
            self.outputNpDatatypeAll,
            self.noDataDasoVarAll,
            self.noDataDasoVarAll,
            self.GLBLnoDataTiffFiles,
            generarMetaPixeles=True,
        )
        # ======================================================================

        # ======================================================================
        # Compruebo si puedo cargar la banda 1 en memoria
        print('\n{:_^80}'.format(''))
        print('clidtwins-> Comprobando memoria RAM disponible:')
        nBytesPorBanda = 4
        if psutilOk:
            ramMem = psutil.virtual_memory()
            megasLibres = ramMem.available / 1048576 # ~1E6
            megasReservados = 1000 if megasLibres > 2000 else megasLibres / 2
            print('{}-> Megas libres: {:0.2f} MB'.format(TB, megasLibres))
            numMaximoPixeles = (megasLibres - megasReservados) * 1e6 / (self.nBandasRasterOutput * nBytesPorBanda)
            print(
                '{}-> Num max. Pixeles: {:0.2f} MegaPixeles ({} bandas, {} bytes por pixel)'.format(
                    TB,
                    numMaximoPixeles / 1e6,
                    self.nBandasRasterOutput,
                    nBytesPorBanda
                )
            )
        else:
            numMaximoPixeles = 1e9
        nMegaPixeles = self.nCeldasX_Destino * self.nCeldasY_Destino / 1e6
        nMegaBytes = nMegaPixeles * self.nBandasRasterOutput * nBytesPorBanda
        print(
            '{}-> nCeldas previstas:  {} x {} = {:0.2f} MegaPixeles = {:0.2f} MegaBytes'.format(
                TB,
                self.nCeldasX_Destino,
                self.nCeldasY_Destino,
                nMegaPixeles,
                nMegaBytes,
            )
        )
        if nMegaPixeles < numMaximoPixeles * 0.5:
            # Se puede cargar toda la banda1 en memoria
            cargarRasterEnMemoria = True
            # Creo un ndarray con el contenido de la banda 1 del raster dataset creado
            print(f'{TB}-> SI se carga toda la banda en memoria.')
        else:
            cargarRasterEnMemoria = False
            print(f'{TB}-> NO se carga toda la banda en memoria.')
            print(f'{TB}{TV} OPCION PARCIALMENTE IMPLEMENTADA: seguir el procedimiento usado en mergeBloques<>')
            sys.exit(0)
        print('{:=^80}'.format(''))
        # ======================================================================

        # ======================================================================
        arrayBandaTipoMasa = outputBandaTipoMasa.ReadAsArray().astype(self.outputNpDatatypeTipoMasa)
        arrayBandaDistanciaEuclideaMedia = outputBandaDistanciaEuclideaMedia.ReadAsArray().astype(self.outputNpDatatypeFloat32)
        arrayBandaPorcentajeDeProximidad = outputBandaPorcentajeDeProximidad.ReadAsArray().astype(self.outputNpDatatypeFloat32)
        arrayBandaClusterDasoVarBanda1 = outputBandaClusterDasoVarBanda1.ReadAsArray().astype(self.outputNpDatatypeAll)
        # ======================================================================

        # Convertir esto a uint8 (los arrays y el rasterDataset
        # ======================================================================
        arrayProximidadInterEspecies = np.full_like(arrayBandaTipoMasa, self.GLBLnoDataTiffFiles, dtype=np.float32)
        arrayDistanciaEuclideaMedia = np.full_like(arrayBandaTipoMasa, self.GLBLnoDataTiffFiles, dtype=np.float32)
        arrayPctjPorcentajeDeProximidad = np.full_like(arrayBandaTipoMasa, self.GLBLnoDataTiffFiles, dtype=np.float32)
        # ======================================================================

        # ======================================================================
        dictSelecMultiBandaClusterDasoVars = {}
        dictArrayMultiBandaClusterDasoVars = {}
        for outputNBand in range(1, self.nBandasPrevistasOutput + 1):
            dictSelecMultiBandaClusterDasoVars[outputNBand] = outputDatasetClusterDasoVarMultiple.GetRasterBand(outputNBand)
            dictArrayMultiBandaClusterDasoVars[outputNBand] = dictSelecMultiBandaClusterDasoVars[outputNBand].ReadAsArray().astype(self.outputNpDatatypeAll)
            # print(f'{TB}-> Banda: {outputNBand} -> shape: {dictArrayMultiBandaClusterDasoVars[outputNBand].shape}')
        # print(f'{TB}claves de dictArrayMultiBandaClusterDasoVars: {dictArrayMultiBandaClusterDasoVars.keys()}')
        if self.LOCLverbose > 1:
            print('\n{:_^80}'.format(''))
            print(f'clidtwins-> Dimensiones de los raster creados (pixeles): {arrayBandaTipoMasa.shape}')
            print(f'-> Tipo de dato de los rasters creados::')
            print(
                f'{TB}-> Raster bibanda con el tipo de masa:           '
                f'{type(arrayBandaTipoMasa)}, dtype: {arrayBandaTipoMasa.dtype} '
                f'-> {self.outputClusterTiposDeMasaFileNameSinPath}'
            )
            print(
                f'{TB}-> Raster bibanda con la DistanciaEuclideaMedia: '
                f'{type(arrayBandaDistanciaEuclideaMedia)}, dtype: {arrayBandaDistanciaEuclideaMedia.dtype} '
                f'-> {self.outputClusterDistanciaEuFileNameSinPath}'
            )
            print(
                f'{TB}-> Raster bibanda con el PorcentajeDeProximidad: '
                f'{type(arrayBandaPorcentajeDeProximidad)}, dtype: {arrayBandaPorcentajeDeProximidad.dtype} '
                f'-> {self.outputClusterFactorProxiFileNameSinPath}'
            )
            print(
                f'{TB}-> Raster multibanda con las clusterDasoVars:    '
                f'{type(arrayBandaClusterDasoVarBanda1)}, dtype: {arrayBandaClusterDasoVarBanda1.dtype} '
                f'-> {self.outputClusterAllDasoVarsFileNameSinPath}'
            )
            # print(f'-> Otros datos del rater cluster multibanda creado ({self.outputClusterAllDasoVarsFileNameSinPath}:')
            # print(f'-> Datos del raster cluster multibanda creado ({self.outputClusterAllDasoVarsFileNameSinPath}:')
            # print(f'{TB}-> Tipo de dato:              {type(dictArrayMultiBandaClusterDasoVars[1])} = {self.outputNpDatatypeAll}, dtype: {dictArrayMultiBandaClusterDasoVars[1].dtype}')
            # print(f'{TB}-> Dimensiones de las bandas: {dictArrayMultiBandaClusterDasoVars[1].shape}')
            print('{:=^80}'.format(''))
        # ======================================================================

        # ======================================================================
        # Array con unos en el circulo central (se usa como peso para los histogramas, como una mascara)
        localClusterArrayRound = np.ones((ladoCluster ** 2), dtype=np.uint8).reshape(ladoCluster, ladoCluster)
        nRowCenter = localClusterArrayRound.shape[0] / 2
        nColCenter = localClusterArrayRound.shape[1] / 2
        for nRowCell in range(localClusterArrayRound.shape[0]):
            for nColCell in range(localClusterArrayRound.shape[1]):
                if np.sqrt(((nRowCell - nRowCenter) ** 2) + ((nColCell - nColCenter) ** 2)) > ladoCluster / 2:
                    localClusterArrayRound[nRowCell, nColCell] = 0
        # ======================================================================

        # ======================================================================
        contadorAvisosCluster = 0
        if self.LOCLverbose:
            print('\n{:_^80}'.format(''))
            print(f'Recorriendo raster multibanda para calcular clusterVars, tipoDeMasa y parametros de proximidad (nBandas: {self.nBandasRasterOutput}; ladoCluster: {ladoCluster})\n')
        for nRowRaster in range(arrayBandaTipoMasa.shape[0]):
            if self.LOCLverbose:
                if nRowRaster % (arrayBandaTipoMasa.shape[0] / 10) == 0:
                    print(f'\nRecorriendo fila {nRowRaster} de {arrayBandaTipoMasa.shape[0]}', end ='')
                else:
                    print('.', end ='')
            coordY = arrayBandaTipoMasa.shape[0] - nRowRaster
            for nColRaster in range(arrayBandaTipoMasa.shape[1]):
                coordX = nColRaster
                TRNSsaltarPixelsSinTipoBosque = True
                if TRNSsaltarPixelsSinTipoBosque:
                    if arrayBandaXinputMonoPixelAll[nBanda - 1][nRowRaster, nColRaster] == self.noDataDasoVarAll:
                        continue

                # if (
                #     nRowRaster % (int(arrayBandaTipoMasa.shape[0] / 5)) == 0
                #     and nColRaster % (int(arrayBandaTipoMasa.shape[1] / 5)) == 0
                # ):
                if nRowRaster == 0 and nColRaster == 0:
                    TRNSmostrarClusterMatch = True
                else:
                    if (
                        coordX == 0 or coordX == 35 or coordX == 59
                    ) and (
                        coordY == 0 or coordY == 85 or coordY == 95
                    ):
                        TRNSmostrarClusterMatch = True
                    else:
                        TRNSmostrarClusterMatch = False
                # TRNSmostrarClusterMatch = False

                (clusterRelleno, contadorAvisosCluster) = rellenarLocalCluster(
                    arrayBandaXinputMonoPixelAll,
                    nRowRaster,
                    nColRaster,
                    self_LOCLradioClusterPix=self.LOCLradioClusterPix,
                    self_noDataDasoVarAll=self.noDataDasoVarAll,
                    self_outputNpDatatypeAll=self.outputNpDatatypeAll,
                    self_LOCLverbose=self.LOCLverbose,
                    TRNSmostrarClusterMatch=TRNSmostrarClusterMatch,
                    contadorAvisosCluster=contadorAvisosCluster,
                )
                if not clusterRelleno[0]:
                    continue
                clusterCompleto = clusterRelleno[1]
                localClusterArrayMultiBandaDasoVars = clusterRelleno[2]
                localSubClusterArrayMultiBandaDasoVars = clusterRelleno[3]
                listaCeldasConDasoVarsCluster = clusterRelleno[4]
                listaCeldasConDasoVarsSubCluster = clusterRelleno[5]
                arrayBandaXMaskCluster = clusterRelleno[6]
                arrayBandaXMaskSubCluster = clusterRelleno[7]

                # if not nCeldasConDasoVarsOk and self.LOCLverbose > 1:
                #     # Por aqui no pasa porque ya he interceptado este problema mas arriba
                #     print(f'{TB}{TV}-> AVISO (c): {nRowRaster} {nColRaster} -> celda sin valores disponibles para generar cluster')
                #     continue

                # ==============================================================
                nVariablesNoOk = 0
                tipoBosqueOk = 0
                for nBanda in range(1, self.nBandasRasterOutput + 1):
                    nInputVar = nBanda - 1
                    ponderacionDeLaVariable = self.LOCLlistLstDasoVars[nInputVar][6] / 10.0
                    # Factor entre 0 y 1 que modifica el numero de clases que estan fuera de rango
                    # El valor 1 suma todos los "fuera de rango"; el factor 0.5 los contabiliza mitad
                    multiplicadorDeFueraDeRangoParaLaVariable = ponderacionDeLaVariable
                    if TRNSmostrarClusterMatch:
                        if nBanda == self.nBandasRasterOutput - 1:
                            print(f'{TB}-> Banda {nBanda} -> (cluster) Chequeando tipo de bosque.')
                        elif nInputVar >= 0 and nInputVar < self.nInputVars:
                            claveDef = f'{str(nInputVar)}_{self.LOCLlistLstDasoVars[nInputVar][1]}_ref'
                            print(f'{TB}-> Banda {nBanda} -> (cluster) Chequeando rangos admisibles para: {claveDef} (pondera: {ponderacionDeLaVariable})')

                    # if clusterCompleto:
                    #     localClusterArrayMultiBandaDasoVars[nBanda-1] = arrayBandaXinputMonoPixelAll[nBanda - 1][
                    #         nRowClusterIni:nRowClusterFin + 1, nColClusterIni:nColClusterFin + 1
                    #     ]
                    #     # Sustituyo el self.noDataDasoVarAll (-9999) por self.GLBLnoDataTipoDMasa (255)
                    #     # localClusterArrayMultiBandaDasoVars[nBanda-1][localClusterArrayMultiBandaDasoVars[nBanda-1] == self.noDataDasoVarAll] = self.GLBLnoDataTipoDMasa
                    #     if (localClusterArrayMultiBandaDasoVars[nBanda-1] == self.noDataDasoVarAll).all():
                    #         continue
                    # else:
                    #     for desplY in range(-self.LOCLradioClusterPix, self.LOCLradioClusterPix + 1):
                    #         for desplX in range(-self.LOCLradioClusterPix, self.LOCLradioClusterPix + 1):
                    #             nRowCluster = nRowRaster + desplY
                    #             nColCluster = nColRaster + desplX
                    #             if (
                    #                 nRowCluster >= 0
                    #                 and nRowCluster < (arrayBandaXinputMonoPixelAll[nBanda - 1]).shape[0]
                    #                 and nColCluster >= 0
                    #                 and nColCluster < (arrayBandaXinputMonoPixelAll[nBanda - 1]).shape[1]
                    #             ):
                    #                 try:
                    #                     localClusterArrayMultiBandaDasoVars[nInputVar, self.LOCLradioClusterPix + desplY, self.LOCLradioClusterPix + desplX] = (arrayBandaXAll[nBanda - 1])[nRowCluster, nColCluster]
                    #                 except:
                    #                     print('\n-> Revsar error:', nInputVar, self.LOCLradioClusterPix + desplY, self.LOCLradioClusterPix + desplX)
                    #                     print('localClusterArrayMultiBandaDasoVars.shape:', localClusterArrayMultiBandaDasoVars.shape)
                    #                     print('nRowCluster, nColCluster:', nRowCluster, nColCluster)
                    #                     sys.exit(0)
                    #     localSubClusterArrayMultiBandaDasoVars[nBanda-1] = localClusterArrayMultiBandaDasoVars[nInputVar, nRowClustIni:nRowClustFin, nColClustIni:nColClustFin]
                    #     # Sustituyo el self.noDataDasoVarAll (-9999) por self.GLBLnoDataTipoDMasa (255)
                    #     # localSubClusterArrayMultiBandaDasoVars[localSubClusterArrayMultiBandaDasoVars == self.noDataDasoVarAll] = self.GLBLnoDataTipoDMasa
                    #     if (localSubClusterArrayMultiBandaDasoVars == self.noDataDasoVarAll).all():
                    #         continue
                    #
                    #     # print(localClusterArrayMultiBandaDasoVars[nBanda-1])
                    #     # print(localSubClusterArrayMultiBandaDasoVars)
                    #         #     else:
                    #         #         clusterCompleto = False
                    #         #         break
                    #         # if not clusterCompleto:
                    #         #     break

                    (
                        histNumberCluster,
                        histProb01cluster,
                        localClusterArrayMultiBandaDasoVarsMasked,
                        localSubClusterArrayMultiBandaDasoVarsMasked,
                    ) = calculaHistogramas(
                        nRowRaster,
                        nColRaster,
                        clusterCompleto,
                        localClusterArrayMultiBandaDasoVars,
                        localSubClusterArrayMultiBandaDasoVars,
                        listaCeldasConDasoVarsCluster,
                        listaCeldasConDasoVarsSubCluster,
                        arrayBandaXMaskCluster,
                        arrayBandaXMaskSubCluster,
                        localClusterArrayRound,
                        nBanda,
                        self.myNBins,
                        self.myRange,
                        self_LOCLradioClusterPix=self.LOCLradioClusterPix,
                        self_outputNpDatatypeAll=self.outputNpDatatypeAll,
                        TRNSmostrarClusterMatch=TRNSmostrarClusterMatch,
                    )

                    if len(np.nonzero(histNumberCluster[0])[0]) == 0:
                        # print(f'clidtwins-> ATENCION: revisar porque que el cluster no tiene elementos no nulos (clusterCompleto: {clusterCompleto}):')
                        # print('nRowColRaster:', nRowRaster, nColRaster, 'nBanda:', nBanda, 'self.myRange[nBanda]:', self.myRange[nBanda], 'self.myNBins[nBanda]:', self.myNBins[nBanda], 'self.myNBins:', self.myNBins)
                        # if nInputVar < len(self.LOCLlistLstDasoVars):
                        #     print('Variable:', self.LOCLlistLstDasoVars[nInputVar][1], 'nBins:', self.LOCLlistLstDasoVars[nInputVar][4], 'nRango:', self.LOCLlistLstDasoVars[nInputVar][2:4])
                        # print('localClusterArrayMultiBandaDasoVars:', localClusterArrayMultiBandaDasoVars[nBanda-1])
                        # print('nonzero:', np.nonzero(histNumberCluster[0]))
                        continue

                    (
                        dictArrayMultiBandaClusterDasoVars,
                        nVariablesNoOk,
                        tipoBosqueOk,
                    ) = calculaClusterDasoVars(
                        dictArrayMultiBandaClusterDasoVars,
                        nBanda,
                        histNumberCluster,
                        histProb01cluster,
                        self.dictHistProb01,
                        self.codeTipoBosquePatronMasFrecuente1,
                        self.pctjTipoBosquePatronMasFrecuente1,
                        self.codeTipoBosquePatronMasFrecuente2,
                        self.pctjTipoBosquePatronMasFrecuente2,
                        self.nInputVars,
                        self.myNBins,
                        self.myRange,
                        self.LOCLlistLstDasoVars,
                        multiplicadorDeFueraDeRangoParaLaVariable,
                        ponderacionDeLaVariable,
                        nVariablesNoOk,
                        tipoBosqueOk,
                        # localClusterArrayMultiBandaDasoVars,
                        nRowRaster=nRowRaster,
                        nColRaster=nColRaster,
                        TRNSmostrarClusterMatch=TRNSmostrarClusterMatch,
                        )

                # ==================================================================
                if clusterCompleto:
                    matrizDeDistancias = distance_matrix(self.listaCeldasConDasoVarsPatron, listaCeldasConDasoVarsCluster)
                    distanciaEuclideaMedia = np.average(matrizDeDistancias)
                    if TRNSmostrarClusterMatch:
                        print('Numero de puntos Cluster con dasoVars ok:', len(ma.compressed(localClusterArrayMultiBandaDasoVarsMasked)))
                        print(f'matrizDeDistancias.shape: {matrizDeDistancias.shape} Distancia media: {distanciaEuclideaMedia}')
                        # print('clidtwins-> Matriz de distancias:')
                        # print(matrizDeDistancias[:5,:5])
                else:
                    matrizDeDistancias = distance_matrix(self.listaCeldasConDasoVarsPatron, listaCeldasConDasoVarsSubCluster)
                    distanciaEuclideaMedia = np.average(matrizDeDistancias)
                    if TRNSmostrarClusterMatch:
                        print('Numero de puntos subCluster con dasoVars ok:', len(ma.compressed(localSubClusterArrayMultiBandaDasoVarsMasked)))
                        print(f'matrizDeDistancias.shape: {matrizDeDistancias.shape} Distancia media: {distanciaEuclideaMedia}')
                        # print('clidtwins-> Matriz de distancias:')
                        # print(matrizDeDistancias[:5,:5])
                # ==================================================================
                # ññ
                tipoMasaOk = tipoBosqueOk >= 5 and nVariablesNoOk <= 1
                if TRNSmostrarClusterMatch:
                    print(
                        f'nRowColRaster: {nRowRaster} {nColRaster}; '
                        f'coordXY: {coordX} {coordY} '
                        f'-> Resumen del match-> tipoBosqueOk: {tipoBosqueOk} '
                        f'nVariablesNoOk: {nVariablesNoOk}. '
                        f'Match: {tipoMasaOk}')
                arrayBandaTipoMasa[nRowRaster, nColRaster] = tipoMasaOk
                arrayProximidadInterEspecies[nRowRaster, nColRaster] = tipoBosqueOk
                arrayDistanciaEuclideaMedia[nRowRaster, nColRaster] = distanciaEuclideaMedia
                if np.ma.count(matrizDeDistancias) != 0:
                    arrayPctjPorcentajeDeProximidad[nRowRaster, nColRaster] = 100 * (
                        np.count_nonzero(matrizDeDistancias < self.GLBLumbralMatriDist)
                        / np.ma.count(matrizDeDistancias)
                    )
                # else:
                #     print('---->', nRowRaster, nColRaster, matrizDeDistancias[:5,:5])

        print()
        # PENDIENTE: ofrecer la conversión de asc de 10x10 en tif de 20x20
        # y verificar que al escribir en una fila del tif no se carga lo que hay previamente en esa fila

        # El noDataTiffProvi es el propio self.GLBLnoDataTipoDMasa; no necesito esto:
        # arrayBandaTipoMasa[arrayBandaTipoMasa == self.GLBLnoDataTiffFiles] = self.GLBLnoDataTipoDMasa
        # print('\nAsigno valores de matchTipoMasa al raster')
        # nFilas = outputBandaTipoMasa.shape[0]
        # nColumnas = outputBandaTipoMasa.shape[1]
        # print('outputBandaTipoMasa:', outputBandaTipoMasa)
        # print(dir(outputBandaTipoMasa))
        # print('arrayBandaTipoMasa:', arrayBandaTipoMasa)
        # print(dir(arrayBandaTipoMasa))
        # print('arrayBandaTipoMasa.shape:', arrayBandaTipoMasa.shape)

        outputBandaTipoMasa = guardarArrayEnBandaDataset(
            arrayBandaTipoMasa, outputBandaTipoMasa
        )
        outputBandaProximidadInterEspecies1 = guardarArrayEnBandaDataset(
            arrayProximidadInterEspecies, outputBandaProximidadInterEspecies1
        )
        outputBandaProximidadInterEspecies2 = guardarArrayEnBandaDataset(
            arrayProximidadInterEspecies, outputBandaProximidadInterEspecies2
        )
        outputBandaDistanciaEuclideaMedia = guardarArrayEnBandaDataset(
            arrayDistanciaEuclideaMedia, outputBandaDistanciaEuclideaMedia
        )
        outputBandaPorcentajeDeProximidad = guardarArrayEnBandaDataset(
            arrayPctjPorcentajeDeProximidad, outputBandaPorcentajeDeProximidad
        )
        for outputNBand in range(1, self.nBandasPrevistasOutput + 1):
            dictSelecMultiBandaClusterDasoVarsNBand = guardarArrayEnBandaDataset(
                dictArrayMultiBandaClusterDasoVars[outputNBand],
                dictSelecMultiBandaClusterDasoVars[outputNBand]
            )
            dictSelecMultiBandaClusterDasoVars[outputNBand] = dictSelecMultiBandaClusterDasoVarsNBand


# ==============================================================================
def guardarArrayEnBandaDataset(
        arrayBandaActualizado,
        outputBandaActualizar,
        nOffsetX=0,
        nOffsetY=0,
    ):
    for nFila in range(arrayBandaActualizado.shape[0]):
        nxarray = arrayBandaActualizado[nFila, :]
        nxarray.shape = (1, -1)
        outputBandaActualizar.WriteArray(nxarray, nOffsetX, nOffsetY + nFila)
    outputBandaActualizar.FlushCache()
    return outputBandaActualizar


# ==============================================================================
def rellenarLocalCluster(
        arrayBandaXinputMonoPixelAll,
        nRowRaster,
        nColRaster,
        self_LOCLradioClusterPix=3,
        self_noDataDasoVarAll=-9999,
        self_outputNpDatatypeAll=None,
        self_LOCLverbose=False,
        TRNSmostrarClusterMatch=False,
        contadorAvisosCluster=0,
    ):
    self_nBandasRasterOutput = len(arrayBandaXinputMonoPixelAll)
    if self_outputNpDatatypeAll is None:
        self_outputNpDatatypeAll = arrayBandaXinputMonoPixelAll.dtype
    ladoCluster = (self_LOCLradioClusterPix * 2) + 1
    coordY = (arrayBandaXinputMonoPixelAll[0]).shape[0] - nRowRaster
    coordX = nColRaster
    listaCeldasConDasoVarsCluster = None
    listaCeldasConDasoVarsSubCluster = None
    arrayBandaXMaskCluster = None
    arrayBandaXMaskSubCluster = None
    localClusterArrayMultiBandaDasoVars = None
    localSubClusterArrayMultiBandaDasoVars = None


    # ======================================================================
    # Array con los valores de las dasoVars en el cluster local,
    # cambia para cada el cluster local de cada pixel
    localClusterArrayMultiBandaDasoVars = np.zeros(
        (self_nBandasRasterOutput)
        * (ladoCluster ** 2),
        dtype=self_outputNpDatatypeAll
    ).reshape(
        self_nBandasRasterOutput,
        ladoCluster,
        ladoCluster
    )
    # localClusterArrayMultiBandaDasoVars.fill(0)

    # print('-->>nRowRaster:', nRowRaster, 'nColRaster:', nColRaster) 
    nRowClusterIni = nRowRaster - self_LOCLradioClusterPix
    nRowClusterFin = nRowRaster + self_LOCLradioClusterPix
    nColClusterIni = nColRaster - self_LOCLradioClusterPix
    nColClusterFin = nColRaster + self_LOCLradioClusterPix
    if (
        nRowClusterIni >= 0
        and nColClusterIni >= 0
        and nRowClusterFin < (arrayBandaXinputMonoPixelAll[self_nBandasRasterOutput - 1]).shape[0]
        and nColClusterFin < (arrayBandaXinputMonoPixelAll[self_nBandasRasterOutput - 1]).shape[1]
    ):
        clusterCompleto = True
    else:
        clusterCompleto = False
        if nRowClusterIni < 0:
            nRowClustIni = - nRowClusterIni
        else:
            nRowClustIni = 0
        if nColClusterIni < 0:
            nColClustIni = - nColClusterIni
        else:
            nColClustIni = 0
        if nRowClusterFin >= (arrayBandaXinputMonoPixelAll[self_nBandasRasterOutput - 1]).shape[0]:
            nRowClustFin = ladoCluster - (nRowClusterFin - (arrayBandaXinputMonoPixelAll[self_nBandasRasterOutput - 1]).shape[0])
        else:
            nRowClustFin = ladoCluster
        if nColClusterFin >= (arrayBandaXinputMonoPixelAll[self_nBandasRasterOutput - 1]).shape[1]:
            nColClustFin = ladoCluster - (nColClusterFin - (arrayBandaXinputMonoPixelAll[self_nBandasRasterOutput - 1]).shape[1])
        else:
            nColClustFin = ladoCluster
        # print('-->>nRowClusterIniFin:', nRowClusterIni, nRowClusterFin, 'nColClustIniFin:', nColClusterIni, nColClusterFin, 'clusterCompleto:', clusterCompleto)
        # print('-->>(arrayBandaXinputMonoPixelAll[self_nBandasRasterOutput - 1]).shape:', (arrayBandaXinputMonoPixelAll[self_nBandasRasterOutput - 1]).shape)
        # print('-->>nRowClustIniFin:', nRowClustIni, nRowClustFin, 'nColClustIniFin:', nColClustIni, nColClustFin)

    # ==================================================================
    # Tengo que recorrer todas las bandas para enmascarar las celdas con alguna banda noData
    # Empiezo contando el numero de celdas con valor valido en todas las bandas
    # Una vez contadas (nCeldasConDasoVarsOk) creo el array listaCeldasConDasoVarsCluster
    if clusterCompleto:
        # Para contar el numero de celdas con valor distinto de noData en alguna banda,
        # se parte de un array con todos los valores cero (arrayBandaXMaskCluster),
        # se ponen a 1 las celdas con algun valor noData y, despues de recorrer 
        # todas las bandas, se cuenta el numero de celdas igual a cero.
        arrayBandaXMaskCluster = np.zeros((ladoCluster ** 2), dtype=np.uint8).reshape(ladoCluster, ladoCluster)
        # Recorro todas las bandas para verificar en cada celda si hay valores validos en todas las bandas
        # Calculo arrayBandaXMaskCluster y con ella enmascaro los noData al calcular el histograma de cada banda
        for nBanda in range(1, self_nBandasRasterOutput + 1):
            localClusterArrayMultiBandaDasoVars[nBanda-1] = arrayBandaXinputMonoPixelAll[nBanda - 1][
                nRowClusterIni:nRowClusterFin + 1,
                nColClusterIni:nColClusterFin + 1
            ]
            # Sustituyo el self_noDataDasoVarAll (-9999) por self_GLBLnoDataTipoDMasa (255)
            # localClusterArrayMultiBandaDasoVars[nBanda-1][localClusterArrayMultiBandaDasoVars[nBanda-1] == self_noDataDasoVarAll] = self_GLBLnoDataTipoDMasa
            if (localClusterArrayMultiBandaDasoVars[nBanda-1] == self_noDataDasoVarAll).all():
                localClusterOk = False
                return (
                    (
                        localClusterOk,
                    ),
                    contadorAvisosCluster,
                )
                # continue
            arrayBandaXMaskCluster[localClusterArrayMultiBandaDasoVars[nBanda-1] == self_noDataDasoVarAll] = 1

        if (arrayBandaXMaskCluster == 1).all():
            if self_LOCLverbose > 1:
                print(f'{TB}{TV}-> AVISO (cluster): {nRowRaster} {nColRaster} -> celda sin valores disponibles para generar cluster')
            localClusterOk = False
            return (
                (
                    localClusterOk,
                ),
                contadorAvisosCluster,
            )
            # continue
        elif (arrayBandaXMaskCluster != 1).sum() < MINIMO_PIXELS_POR_CLUSTER:
            if self_LOCLverbose > 2:
                print(f'{TB}{TV}-> AVISO (cluster): {nRowRaster} {nColRaster} -> celda con pocos valores disponibles para generar cluster: {(arrayBandaXMaskCluster != 1).sum()}')
            localClusterOk = False
            return (
                (
                    localClusterOk,
                ),
                contadorAvisosCluster,
            )
            # continue

        nCeldasConDasoVarsOk = np.count_nonzero(arrayBandaXMaskCluster == 0)
        listaCeldasConDasoVarsCluster = np.zeros(nCeldasConDasoVarsOk * self_nBandasRasterOutput, dtype=self_outputNpDatatypeAll).reshape(nCeldasConDasoVarsOk, self_nBandasRasterOutput)
    else:
        localSubClusterArrayMultiBandaDasoVars = np.zeros(
            (self_nBandasRasterOutput)
            * (nRowClustFin - nRowClustIni)
            * (nColClustFin - nColClustIni),
            dtype=self_outputNpDatatypeAll
        ).reshape(
            self_nBandasRasterOutput,
            nRowClustFin - nRowClustIni,
            nColClustFin - nColClustIni
        )
        # Este array es para contar las celda con valores validos en todas las bandas:
        arrayBandaXMaskSubCluster = np.zeros(
            (nRowClustFin - nRowClustIni)
            * (nColClustFin - nColClustIni),
            dtype=np.uint8
        ).reshape(
            nRowClustFin - nRowClustIni,
            nColClustFin - nColClustIni
        )
        localClusterArrayMultiBandaDasoVars.fill(self_noDataDasoVarAll)
        # Recorro todas las bandas para verificar en cada celda si hay valores validos en todas las bandas
        # Calculo arrayBandaXMaskSubCluster y con ella enmascaro los noData al calcular el histograma de cada banda
        for nBanda in range(1, self_nBandasRasterOutput + 1):
            nInputVar = nBanda - 1
            for desplY in range(-self_LOCLradioClusterPix, self_LOCLradioClusterPix + 1):
                for desplX in range(-self_LOCLradioClusterPix, self_LOCLradioClusterPix + 1):
                    nRowCluster = nRowRaster + desplY
                    nColCluster = nColRaster + desplX
                    if (
                        nRowCluster >= 0
                        and nRowCluster < (arrayBandaXinputMonoPixelAll[nBanda - 1]).shape[0]
                        and nColCluster >= 0
                        and nColCluster < (arrayBandaXinputMonoPixelAll[nBanda - 1]).shape[1]
                    ):
                        try:
                            localClusterArrayMultiBandaDasoVars[
                                nInputVar,
                                self_LOCLradioClusterPix + desplY,
                                self_LOCLradioClusterPix + desplX
                            ] = arrayBandaXinputMonoPixelAll[nBanda - 1][
                                nRowCluster, nColCluster
                            ]
                        except:
                            print('\n-> Revisar error:', nInputVar, self_LOCLradioClusterPix + desplY, self_LOCLradioClusterPix + desplX)
                            print('localClusterArrayMultiBandaDasoVars.shape:', localClusterArrayMultiBandaDasoVars.shape)
                            print('nRowCluster, nColCluster:', nRowCluster, nColCluster)
                            sys.exit(0)
            localSubClusterArrayMultiBandaDasoVars[nBanda-1] = localClusterArrayMultiBandaDasoVars[nBanda - 1][
                nRowClustIni:nRowClustFin,
                nColClustIni:nColClustFin
            ]
            # Sustituyo el self_noDataDasoVarAll (-9999) por self_GLBLnoDataTipoDMasa (255)
            # localSubClusterArrayMultiBandaDasoVars[localSubClusterArrayMultiBandaDasoVars == self_noDataDasoVarAll] = self_GLBLnoDataTipoDMasa
            if (localSubClusterArrayMultiBandaDasoVars == self_noDataDasoVarAll).all():
                localClusterOk = False
                return (
                    (
                        localClusterOk,
                    ),
                    contadorAvisosCluster,
                )
                # continue
            arrayBandaXMaskSubCluster[localSubClusterArrayMultiBandaDasoVars[nBanda-1] == self_noDataDasoVarAll] = 1

        if (arrayBandaXMaskSubCluster == 1).all():
            if self_LOCLverbose > 1:
                if contadorAvisosCluster < 20:
                    print(f'{TB}{TV}-> AVISO (subcluster): {nRowRaster} {nColRaster} -> celda sin valores disponibles para generar cluster')
                elif contadorAvisosCluster == 20:
                    print(f'{TB}{TV}-> AVISO (subcluster): hay mas celdas sin valores disponibles o con pocos valores para generar cluster; no se muestran mas.')
            contadorAvisosCluster += 1
            localClusterOk = False
            return (
                (
                    localClusterOk,
                ),
                contadorAvisosCluster,
            )
            # continue
        elif (arrayBandaXMaskSubCluster != 1).sum() < MINIMO_PIXELS_POR_CLUSTER:
            if self_LOCLverbose > 2:
                if contadorAvisosCluster < 20:
                    print(f'{TB}{TV}-> AVISO (subcluster): {nRowRaster} {nColRaster} -> celda con pocos valores disponibles para generar cluster: {(arrayBandaXMaskSubCluster != 1).sum()}')
                elif contadorAvisosCluster == 20:
                    print(f'{TB}{TV}-> AVISO (subcluster): hay mas celdas sin valores disponibles o con pocos valores para generar cluster; no se muestran mas.')
            contadorAvisosCluster += 1
            localClusterOk = False
            return (
                (
                    localClusterOk,
                ),
                contadorAvisosCluster,
            )
            # continue

        nCeldasConDasoVarsOk = np.count_nonzero(arrayBandaXMaskSubCluster == 0)
        listaCeldasConDasoVarsSubCluster = np.zeros(nCeldasConDasoVarsOk * self_nBandasRasterOutput, dtype=self_outputNpDatatypeAll).reshape(nCeldasConDasoVarsOk, self_nBandasRasterOutput)
    # ==============================================================

    if TRNSmostrarClusterMatch:
        print(f'\n-> nRowColRaster: {nRowRaster} {nColRaster}; coordXY: {coordX} {coordY}')
        print(f'{TB}{TV}-> clusterCompleto: {clusterCompleto}')
        print(f'{TB}{TV}-> Numero de celdas con dasoVars ok en todas las bandas: {nCeldasConDasoVarsOk}')
        print(f'{TB}{TV}-> Celdas noData (valor=1): {arrayBandaXMaskSubCluster}')

    localClusterOk = True
    return (
        (
            localClusterOk,
            clusterCompleto,
            localClusterArrayMultiBandaDasoVars,
            localSubClusterArrayMultiBandaDasoVars,
            listaCeldasConDasoVarsCluster,
            listaCeldasConDasoVarsSubCluster,
            arrayBandaXMaskCluster,
            arrayBandaXMaskSubCluster,
        ),
        contadorAvisosCluster,
    )



# ==============================================================================
def calculaHistogramas(
        nRowRaster,
        nColRaster,
        clusterCompleto,
        localClusterArrayMultiBandaDasoVars,
        localSubClusterArrayMultiBandaDasoVars,
        listaCeldasConDasoVarsCluster,
        listaCeldasConDasoVarsSubCluster,
        arrayBandaXMaskCluster,
        arrayBandaXMaskSubCluster,
        localClusterArrayRound,
        nBanda,
        self_myNBins,
        self_myRange,
        self_LOCLradioClusterPix=3,
        self_outputNpDatatypeAll=None,
        TRNSmostrarClusterMatch=False,
    ):
    if self_outputNpDatatypeAll is None:
        self_outputNpDatatypeAll = localClusterArrayMultiBandaDasoVars.dtype
    nInputVar = nBanda - 1
    ladoCluster = (self_LOCLradioClusterPix * 2) + 1
    nRowClusterIni = nRowRaster - self_LOCLradioClusterPix
    # nRowClusterFin = nRowRaster + self_LOCLradioClusterPix
    nColClusterIni = nColRaster - self_LOCLradioClusterPix
    # nColClusterFin = nColRaster + self_LOCLradioClusterPix
    localClusterArrayMultiBandaDasoVarsMasked = None
    localSubClusterArrayMultiBandaDasoVarsMasked = None

    # print(f'\nCluster asignado a la variable {nInputVar}, coordendas del raster -> row: {nRowRaster} col: {nColRaster} (completo: {clusterCompleto}):')
    if clusterCompleto:
        localClusterArrayMultiBandaDasoVarsMasked = ma.masked_array(
            localClusterArrayMultiBandaDasoVars[nBanda-1],
            mask=arrayBandaXMaskCluster,
            dtype=self_outputNpDatatypeAll
        )
        listaCeldasConDasoVarsCluster[:, nInputVar] = ma.compressed(localClusterArrayMultiBandaDasoVarsMasked)
    
        # Utilizo el mismo localClusterArrayRound para todos los clusters porque tienen las mismas dimensiones
        histNumberCluster = np.histogram(
            localClusterArrayMultiBandaDasoVars[nBanda-1],
            bins=self_myNBins[nBanda],
            range=self_myRange[nBanda],
            weights=localClusterArrayRound
        )
        histProbabCluster = np.histogram(
            localClusterArrayMultiBandaDasoVars[nBanda-1],
            bins=self_myNBins[nBanda],
            range=self_myRange[nBanda],
            weights=localClusterArrayRound,
            density=True
        )
        # print(f'\nhistProbabCluster[0]: {type(histProbabCluster[0])}')
        histProb01cluster = np.array(histProbabCluster[0]) * (
            (self_myRange[nBanda][1] - self_myRange[nBanda][0])
            / self_myNBins[nBanda]
        )
        if TRNSmostrarClusterMatch:
            print(f'{TB}{TV}->->localClusterArrayMultiBandaDasoVars', localClusterArrayMultiBandaDasoVars[nBanda-1])
            print(f'{TB}{TV}->->localClusterArrayMultiBandaDasoVarsMasked', localClusterArrayMultiBandaDasoVarsMasked[nBanda-1])
            print(f'{TB}{TV}->->histNumberCluster', histNumberCluster)
    else:
        # print('---->>>>', localSubClusterArrayMultiBandaDasoVars.shape)
        # print('---->>>>', arrayBandaXMaskSubCluster.shape, nRowClustFin - nRowClustIni, nColClustFin - nColClustIni)
        # print('---->>>>', nRowClustFin, nRowClustIni, nColClustFin, nColClustIni)
        # print('---->>>>', nRowClusterFin, nRowClusterIni, nColClusterFin, nColClusterIni)
        localSubClusterArrayMultiBandaDasoVarsMasked = ma.masked_array(
            localSubClusterArrayMultiBandaDasoVars[nBanda-1],
            mask=arrayBandaXMaskSubCluster,
            dtype=self_outputNpDatatypeAll
            )
        listaCeldasConDasoVarsSubCluster[:, nInputVar] = ma.compressed(localSubClusterArrayMultiBandaDasoVarsMasked)

        # print(localSubClusterArrayMultiBandaDasoVars[nBanda-1])

        # Utilizo un arrayRoundSubCluster especifico para este subCluster aunque creo q no es imprescindible
        arrayRoundSubCluster = np.full_like(localSubClusterArrayMultiBandaDasoVars[nBanda-1], 1, dtype=np.uint8)
        desplRow = nRowClusterIni - (nRowRaster - self_LOCLradioClusterPix)
        desplCol = nColClusterIni - (nColRaster - self_LOCLradioClusterPix)
        # Posicion del centro del cluster completo referido a la esquina sup-izda del subCluster
        #     En coordenadas referidas al array completo: nRowRaster, nColRaster
        #     En coordenadas referidas al subCluster hay que tener en cuenta el origen del subCluster dentro del cluster (desplRow, desplCol)
        nRowCenter = (arrayRoundSubCluster.shape[0] / 2) - desplRow
        nColCenter = (arrayRoundSubCluster.shape[1] / 2) - desplCol
        for nRowCell in range(arrayRoundSubCluster.shape[0]):
            for nColCell in range(arrayRoundSubCluster.shape[1]):
                if np.sqrt(((nRowCell - nRowCenter) ** 2) + ((nColCell - nColCenter) ** 2)) > ladoCluster / 2:
                    arrayRoundSubCluster[nRowCell, nColCell] = 0
    
        try:
            # print('localSubClusterArrayMultiBandaDasoVars', localSubClusterArrayMultiBandaDasoVars.shape)
            # print('localClusterArrayRound', localClusterArrayRound.shape)
            histNumberCluster = np.histogram(
                localSubClusterArrayMultiBandaDasoVars[nBanda-1],
                bins=self_myNBins[nBanda],
                range=self_myRange[nBanda],
                weights=arrayRoundSubCluster
            )
            histProbabCluster = np.histogram(
                localSubClusterArrayMultiBandaDasoVars[nBanda-1],
                bins=self_myNBins[nBanda],
                range=self_myRange[nBanda],
                weights=arrayRoundSubCluster,
                density=True
            )
            # print(f'\nhistProbabCluster[0]: {type(histProbabCluster[0])}')
            histProb01cluster = np.array(histProbabCluster[0]) * (
                (self_myRange[nBanda][1] - self_myRange[nBanda][0])
                / self_myNBins[nBanda]
                )
        except:
            print('\nclidtwins-> AVISO: error al generar histograma con el cluster:', localSubClusterArrayMultiBandaDasoVars[nBanda-1])
            # histNumberCluster = np.array([])
            # histProbabCluster = np.array([])
            # histProb01cluster = np.array([])
            sys.exit(0)
        if TRNSmostrarClusterMatch:
            print(f'{TB}{TV}->->localClusterArrayMultiBandaDasoVars', localClusterArrayMultiBandaDasoVars[nBanda-1])
            print('-------->self_outputNpDatatypeAll:', self_outputNpDatatypeAll)
            print(f'{TB}{TV}->->localSubClusterArrayMultiBandaDasoVars', localSubClusterArrayMultiBandaDasoVars[nBanda-1])
            print(f'{TB}{TV}->->arrayRoundSubCluster', arrayRoundSubCluster)
            print(f'{TB}{TV}->->histNumberCluster', histNumberCluster)

    return (
        histNumberCluster,
        histProb01cluster,
        localClusterArrayMultiBandaDasoVarsMasked,
        localSubClusterArrayMultiBandaDasoVarsMasked,
    )


# ==============================================================================
def calculaClusterDasoVars(
        dictArrayMultiBandaClusterDasoVars,
        nBanda,
        histNumberCluster,
        histProb01cluster,
        self_dictHistProb01,
        self_codeTipoBosquePatronMasFrecuente1,
        self_pctjTipoBosquePatronMasFrecuente1,
        self_codeTipoBosquePatronMasFrecuente2,
        self_pctjTipoBosquePatronMasFrecuente2,
        self_nInputVars,
        self_myNBins,
        self_myRange,
        self_LOCLlistLstDasoVars,
        multiplicadorDeFueraDeRangoParaLaVariable,
        ponderacionDeLaVariable,
        nVariablesNoOk,
        tipoBosqueOk,
        # localClusterArrayMultiBandaDasoVars,
        nRowRaster=0,
        nColRaster=0,
        TRNSmostrarClusterMatch=False,
    ):
    nInputVar = nBanda - 1
    self_nBandasRasterOutput = self_nInputVars + 2

    if nBanda == self_nBandasRasterOutput - 1:
        if TRNSmostrarClusterMatch:
            # El primer elemento de histNumberCluster[0] son las frecuencias del histograma
            # El segundo elemento de histNumberCluster[0] son los limites de las clases del histograma
            print(
                f'Histograma del cluster de Tipos de bosque (banda {nBanda}):',
                'histNumberCluster[0]:', histNumberCluster[0]
            )
        try:
            tipoBosqueUltimoNumero = np.max(np.nonzero(histNumberCluster[0]))
        except:
            tipoBosqueUltimoNumero = 0
        histogramaTemp = (histNumberCluster[0]).copy()
        histogramaTemp.sort()
        codeTipoBosqueClusterMasFrecuente1 = (histNumberCluster[0]).argmax(axis=0)
        arrayPosicionTipoBosqueCluster1 = np.where(histNumberCluster[0] == histogramaTemp[-1])
        arrayPosicionTipoBosqueCluster2 = np.where(histNumberCluster[0] == histogramaTemp[-2])

        if TRNSmostrarClusterMatch:
            print(f'{TB}{TV}-->>> Valor original de la celda: '
                  f'{dictArrayMultiBandaClusterDasoVars[nBanda][nRowRaster, nColRaster]}; ' 
                  f'TipoBosqueClusterMasFrecuente: '
                  f'{codeTipoBosqueClusterMasFrecuente1}'
                  f' = {arrayPosicionTipoBosqueCluster1[0][0]}')

        # print(f'{TB}-> Tipo de bosque principal (cluster): {codeTipoBosqueClusterMasFrecuente1}; frecuencia: {int(round(100 * histProb01cluster[codeTipoBosqueClusterMasFrecuente1], 0))} %')
        # print(f'{TB}-> {arrayPosicionTipoBosqueCluster1}')

        # for contadorTB1, numPosicionTipoBosqueCluster1 in enumerate(arrayPosicionTipoBosqueCluster1[0]):
        #     print(f'{TB}-> {numPosicionTipoBosqueCluster1}')
        #     print(f'{TB}-> {contadorTB1} Tipo de bosque primero (cluster): {numPosicionTipoBosqueCluster1}; frecuencia: {int(round(100 * histProb01cluster[numPosicionTipoBosqueCluster1], 0))} %')
        # if histProb01cluster[arrayPosicionTipoBosqueCluster2[0][0]] != 0:
        #     for contadorTB2, numPosicionTipoBosqueCluster2 in enumerate(arrayPosicionTipoBosqueCluster2[0]):
        #         print(f'{TB}-> {numPosicionTipoBosqueCluster2}')
        #         print(f'{TB}-> {contadorTB2} Tipo de bosque segundo (cluster): {numPosicionTipoBosqueCluster2}; frecuencia: {int(round(100 * histProb01cluster[numPosicionTipoBosqueCluster2], 0))} %')
        # else:
        #     print(f'{TB}-> Solo hay tipo de bosque princial')

        if codeTipoBosqueClusterMasFrecuente1 != arrayPosicionTipoBosqueCluster1[0][0]:
            print(f'{TB}-> ATENCION: revisar esto porque debe haber algun error: {codeTipoBosqueClusterMasFrecuente1} != {arrayPosicionTipoBosqueCluster1[0][0]}')
        if len(arrayPosicionTipoBosqueCluster1[0]) == 1:
            codeTipoBosqueClusterMasFrecuente2 = arrayPosicionTipoBosqueCluster2[0][0]
        else:
            codeTipoBosqueClusterMasFrecuente2 = arrayPosicionTipoBosqueCluster1[0][1]

        pctjTipoBosqueClusterMasFrecuente1 = int(round(100 * histProb01cluster[codeTipoBosqueClusterMasFrecuente1], 0))
        pctjTipoBosqueClusterMasFrecuente2 = int(round(100 * histProb01cluster[codeTipoBosqueClusterMasFrecuente2], 0))

        # codeTipoBosqueClusterMasFrecuente1 = (localClusterArrayMultiBandaDasoVars[nBanda-1]).flatten()[(localClusterArrayMultiBandaDasoVars[nBanda-1]).argmax()]
        # if nRowRaster >= 16 and nRowRaster <= 30 and nColRaster <= 5:
        #     print(
        #         f'{TB}', nRowRaster, nColRaster, 'nBanda', nBanda, 
        #         f'-> codeTipoBosqueClusterMasFrecuente1: {codeTipoBosqueClusterMasFrecuente1} ({pctjTipoBosqueClusterMasFrecuente1})',
        #         f'-> codeTipoBosqueClusterMasFrecuente2: {codeTipoBosqueClusterMasFrecuente2} ({pctjTipoBosqueClusterMasFrecuente2})')

        # ==================================================
        dictArrayMultiBandaClusterDasoVars[nBanda][nRowRaster, nColRaster] = codeTipoBosqueClusterMasFrecuente1
        # ==================================================

        if TRNSmostrarClusterMatch:
            if codeTipoBosqueClusterMasFrecuente1 != 0:
                # print(f'{TB}-> nRowColRaster: {nRowRaster} {nColRaster} -> (cluster) Chequeando tipo de bosque: codeTipoBosqueClusterMasFrecuente1: {dictArrayMultiBandaClusterDasoVars[nBanda][nRowRaster, nColRaster]} = {codeTipoBosqueClusterMasFrecuente1}')
                print(f'{TB}{TV}-> Tipos de bosque mas frecuentes (cluster): 1-> {codeTipoBosqueClusterMasFrecuente1} ({pctjTipoBosqueClusterMasFrecuente1} %); 2-> {codeTipoBosqueClusterMasFrecuente2} ({pctjTipoBosqueClusterMasFrecuente2} %)')
                print(f'{TB}{TV}-> Numero pixeles de cada tipo de bosque (cluster) ({(histNumberCluster[0]).sum()}):\n{histNumberCluster[0][:tipoBosqueUltimoNumero + 1]}')
            else:
                # print('nRow:', nRowRaster, 'nCol', nColRaster, '->codeTipoBosqueClusterMasFrecuente1:', localClusterArrayMultiBandaDasoVars[nBanda-1][nRowRaster, nColRaster], 'Revisar')
                print('nRow:', nRowRaster, 'nCol', nColRaster, '-> Revisar')

        if self_pctjTipoBosquePatronMasFrecuente1 >= 70 and pctjTipoBosqueClusterMasFrecuente1 >= 70:
            if (codeTipoBosqueClusterMasFrecuente1 == self_codeTipoBosquePatronMasFrecuente1):
                tipoBosqueOk = 10
                if TRNSmostrarClusterMatch:
                    print(f'{TB}-> Tipo de bosque principal con mas del 70 de ocupacion SI ok:')
            else:
                binomioEspecies = f'{codeTipoBosqueClusterMasFrecuente1}_{self_codeTipoBosquePatronMasFrecuente1}'
                if binomioEspecies in (GLO.GLBLdictProximidadInterEspecies).keys():
                    tipoBosqueOk = GLO.GLBLdictProximidadInterEspecies[binomioEspecies]
                else:
                    tipoBosqueOk = 0
                if TRNSmostrarClusterMatch:
                    print(f'{TB}-> Tipo de bosque principal con mas del 70 de ocupacion NO ok: {tipoBosqueOk}')
            if TRNSmostrarClusterMatch:
                print(f'{TB}{TV}-> Tipo mas frecuente (patron): 1-> {self_codeTipoBosquePatronMasFrecuente1} ({self_pctjTipoBosquePatronMasFrecuente1} %)')
                print(f'{TB}{TV}-> Tipo mas frecuente (cluster): 1-> {codeTipoBosqueClusterMasFrecuente1} ({pctjTipoBosqueClusterMasFrecuente1} %)')
        else:
            if (
                codeTipoBosqueClusterMasFrecuente1 == self_codeTipoBosquePatronMasFrecuente1
                and codeTipoBosqueClusterMasFrecuente2 == self_codeTipoBosquePatronMasFrecuente2
            ):
                tipoBosqueOk = 10
                if TRNSmostrarClusterMatch:
                    print(f'{TB}-> Tipo de bosque principal (menos del 70 de ocupacion) y segundo SI ok:')
            elif (
                codeTipoBosqueClusterMasFrecuente1 == self_codeTipoBosquePatronMasFrecuente2
                and codeTipoBosqueClusterMasFrecuente2 == self_codeTipoBosquePatronMasFrecuente1
            ):
                tipoBosqueOk = 7
                if TRNSmostrarClusterMatch:
                    print(f'{TB}-> Tipo de bosque principal (menos del 70 de ocupacion) y segundo XX ok:')
            else:
                binomioEspecies = f'{codeTipoBosqueClusterMasFrecuente1}_{self_codeTipoBosquePatronMasFrecuente1}'
                if binomioEspecies in (GLO.GLBLdictProximidadInterEspecies).keys():
                    tipoBosqueOk = GLO.GLBLdictProximidadInterEspecies[binomioEspecies] - 1
                else:
                    tipoBosqueOk = 0
                if TRNSmostrarClusterMatch:
                    print(f'{TB}-> Tipos de bosque principal (menos del 70 de ocupacion) y segundo NO ok: {tipoBosqueOk}')

            if TRNSmostrarClusterMatch:
                print(f'{TB}{TV}-> Tipo mas frecuente (patron): 1-> {self_codeTipoBosquePatronMasFrecuente1} ({self_pctjTipoBosquePatronMasFrecuente1} %)')
                print(f'{TB}{TV}-> Tipo mas frecuente (cluster): 1-> {codeTipoBosqueClusterMasFrecuente1} ({pctjTipoBosqueClusterMasFrecuente1} %)')
                print(f'{TB}{TV}-> Tipo mas frecuente (patron): 2-> {self_codeTipoBosquePatronMasFrecuente2} ({self_pctjTipoBosquePatronMasFrecuente2} %)')
                print(f'{TB}{TV}-> Tipo mas frecuente (cluster): 2-> {codeTipoBosqueClusterMasFrecuente2} ({pctjTipoBosqueClusterMasFrecuente2} %)')

    elif nInputVar >= 0 and nInputVar < self_nInputVars:
        claveDef = f'{str(nInputVar)}_{self_LOCLlistLstDasoVars[nInputVar][1]}_ref'
        claveMin = f'{str(nInputVar)}_{self_LOCLlistLstDasoVars[nInputVar][1]}_min'
        claveMax = f'{str(nInputVar)}_{self_LOCLlistLstDasoVars[nInputVar][1]}_max'
        # self_dictHistProb01[claveDef] = histProb01cluster

        todosLosRangosOk = True
        nTramosFueraDeRango = 0
        for nRango in range(len(histProb01cluster)):
            histProb01cluster[nRango] = round(histProb01cluster[nRango], 3)
            limInf = nRango * (self_myRange[nBanda][1] - self_myRange[nBanda][0]) / self_myNBins[nBanda]
            limSup = (nRango + 1) * (self_myRange[nBanda][1] - self_myRange[nBanda][0]) / self_myNBins[nBanda]
            miRango = f'{limInf}-{limSup}'
            if histProb01cluster[nRango] < self_dictHistProb01[claveMin][nRango]:
                todosLosRangosOk = False
                # nTramosFueraDeRango += 1
                esteTramoFueraDeRango = (
                    (self_dictHistProb01[claveMin][nRango] - histProb01cluster[nRango])
                    / (self_dictHistProb01[claveMax][nRango] - self_dictHistProb01[claveMin][nRango])
                )
                nTramosFueraDeRango += esteTramoFueraDeRango
                if TRNSmostrarClusterMatch:
                    print(
                        f'{TB}{TV}-> {claveDef}-> nRango {nRango} ({miRango}): '
                        f'{histProb01cluster[nRango]} debajo del rango '
                        f'{self_dictHistProb01[claveMin][nRango]} '
                        f'- {self_dictHistProb01[claveMax][nRango]};'
                        f' Valor de referencia: {self_dictHistProb01[claveDef][nRango]} '
                        f'-> fuera: {esteTramoFueraDeRango}'
                    )
            if histProb01cluster[nRango] > self_dictHistProb01[claveMax][nRango]:
                todosLosRangosOk = False
                # nTramosFueraDeRango += 1
                esteTramoFueraDeRango = (
                    (histProb01cluster[nRango] - self_dictHistProb01[claveMax][nRango])
                    / (self_dictHistProb01[claveMax][nRango] - self_dictHistProb01[claveMin][nRango])
                )
                nTramosFueraDeRango += esteTramoFueraDeRango
                if TRNSmostrarClusterMatch:
                    print(
                        f'{TB}{TV}-> {claveDef}-> nRango {nRango} ({miRango}): '
                        f'{histProb01cluster[nRango]} encima del rango '
                        f'{self_dictHistProb01[claveMin][nRango]} '
                        f'- {self_dictHistProb01[claveMax][nRango]}; '
                        f'Valor de referencia: {self_dictHistProb01[claveDef][nRango]} '
                        f'-> fuera: {esteTramoFueraDeRango}')
        if todosLosRangosOk:
            if TRNSmostrarClusterMatch:
                print(f'{TB}{TV}-> Todos los tramos ok.')
        else:
            if TRNSmostrarClusterMatch:
                print(
                    '{}{}-> Cluster-> Numero de tramos fuera de rango: {} (ponderado: {:0.2f})'.format(
                        TB, TV,
                        nTramosFueraDeRango,
                        nTramosFueraDeRango * multiplicadorDeFueraDeRangoParaLaVariable
                    )
                )
            if nTramosFueraDeRango * multiplicadorDeFueraDeRangoParaLaVariable >= 1:
                nVariablesNoOk += 1 * ponderacionDeLaVariable 
                if TRNSmostrarClusterMatch:
                    print(
                        '{}{}{}-> Esta variable desviaciones respecto a zona de referencia (patron) con {:0.2f} puntos'.format(
                            TB, TV, TV,
                            ponderacionDeLaVariable
                        )
                    )
        # ==========================================================
        dictArrayMultiBandaClusterDasoVars[nBanda][nRowRaster, nColRaster] = nTramosFueraDeRango * multiplicadorDeFueraDeRangoParaLaVariable
        # ==========================================================
    return (
        dictArrayMultiBandaClusterDasoVars,
        nVariablesNoOk,
        tipoBosqueOk,
    )


# ==============================================================================
def verificarExistencia(
        LOCLvectorFileName,
        LOCLrutaAscBase=None,
    ):
    if ':/' in LOCLvectorFileName or ':\\' in LOCLvectorFileName:
        patronVectrNameConPath = LOCLvectorFileName
    elif LOCLrutaAscBase is None:
        patronVectrNameConPath = os.path.abspath(LOCLvectorFileName)
    else:
        patronVectrNameConPath = os.path.join(LOCLrutaAscBase, LOCLvectorFileName)
    try:
        if os.path.exists(patronVectrNameConPath):
            return (True, patronVectrNameConPath)
        else:
            return (False, patronVectrNameConPath)
    except:
        return (False, patronVectrNameConPath)


# ==============================================================================
def obtenerExtensionDeCapaVectorial(
        LOCLrutaAscBase,
        LOCLvectorFileName,
        LOCLlayerName=None,
        LOCLverbose=False,
    ):
    # print('----->>> LOCLlayerName', type(LOCLlayerName))
    (usarVectorFileParaDelimitarZona, patronVectrNameConPath) = verificarExistencia(
        LOCLvectorFileName,
        LOCLrutaAscBase=LOCLrutaAscBase,
        )
    if not usarVectorFileParaDelimitarZona:
        print('\nclidtwins-> ATENCION: no esta disponible el fichero %s' % (patronVectrNameConPath))
        return None
    if not gdalOk:
        print('\nclidtwins-> ATENCION: Gdal no disponible; no se puede leer %s' % (patronVectrNameConPath))
        sys.exit(0)

    if LOCLverbose:
        print('\n{:_^80}'.format(''))
        print('clidtwins-> Leyendo vector file {}'.format(patronVectrNameConPath))
    if (LOCLvectorFileName.lower()).endswith('.shp'):
        LOCLPatronVectorDriverName = 'ESRI Shapefile'
    elif (LOCLvectorFileName.lower()).endswith('.gpkg'):
        # Ver mas en https://gdal.org/drivers/vector/gpkg.html
        # Ver tb https://gdal.org/drivers/raster/gpkg.html#raster-gpkg
        LOCLPatronVectorDriverName = 'GPKG'
    else:
        LOCLPatronVectorDriverName = ''
        print(f'clidtwins-> No se ha identificado bien el driver para este fichero: {patronVectrNameConPath}')
        sys.exit(0)
    if LOCLverbose > 1:
        print(f'{TB}-> inputVectorDriverName:           {LOCLPatronVectorDriverName}')

    inputVectorRefOgrDriver = ogr.GetDriverByName(LOCLPatronVectorDriverName)
    if inputVectorRefOgrDriver is None:
        print('\nclidtwins-> ATENCION: el driver {} no esta disponible.'.format(LOCLPatronVectorDriverName))
        sys.exit(0)
    try:
        patronVectorRefDataSource = inputVectorRefOgrDriver.Open(patronVectrNameConPath, 0)  # 0 means read-only. 1 means writeable.
    except:
        print('\nclidtwins-> No se puede abrir {}-> revisar si esta corrupto, faltan ficheros o esta bloqueado'.format(patronVectrNameConPath))
        sys.exit(0)
    try:
        if LOCLlayerName == '' or LOCLlayerName is None or (LOCLvectorFileName.lower()).endswith('.shp'):
            # or LOCLlayerName == 'None':
            patronVectorRefLayer = patronVectorRefDataSource.GetLayer()
        else:
            # Ver: https://developer.ogc.org/samples/build/python-osgeo-gdal/text/load-data.html#using-the-gdal-ogr-library
            # Ver tb: https://pcjericks.github.io/py-gdalogr-cookbook/vector_layers.html
            # Ver tb: https://gdal.org/tutorials/vector_api_tut.html
            # Para editar los registros de forma rápida usar StartTransaction:
            #  https://gis.stackexchange.com/questions/277587/why-editing-a-geopackage-table-with-ogr-is-very-slow
            patronVectorRefLayer = patronVectorRefDataSource.GetLayer(LOCLlayerName)
    except:
        print('\nclidtwins-> ATENCION: el fichero {} no tiene al layer {} (o da error al intentar leerlo).'.format(patronVectrNameConPath, LOCLlayerName))
        print(f'{TB}-> LOCLlayerName: {LOCLlayerName} {type(LOCLlayerName)}')
        sys.exit(0)
    if patronVectorRefLayer is None:
        print('\nclidtwins-> ATENCION: el fichero {} no tiene al layer {} (o no esta accesible).'.format(patronVectrNameConPath, LOCLlayerName))
        print(f'{TB}-> LOCLlayerName: {LOCLlayerName} {type(LOCLlayerName)}')
        sys.exit(0)
    patronVectorRefFeatureCount = patronVectorRefLayer.GetFeatureCount()
    (
        patronVectorXmin,
        patronVectorXmax,
        patronVectorYmin,
        patronVectorYmax,
    ) = patronVectorRefLayer.GetExtent()

    if LOCLverbose:
        print(f'{TB}-> Layer:                           {LOCLlayerName}')
        print(f'{TB}-> Numero de elementos en el layer: {patronVectorRefFeatureCount}')
        print('{:=^80}'.format(''))

    return (
        patronVectorXmin,
        patronVectorXmax,
        patronVectorYmin,
        patronVectorYmax,
    )


# ==============================================================================
def recortarRasterTiffPatronDasoLidar(
        self_LOCLrutaAscRaizBase,
        self_LOCLoutPathNameRuta,
        self_LOCLoutFileNameWExt_mergedUniCellAllDasoVars,
        noDataDasoVarAll,
        outputNpDatatypeAll,
        nMinTipoMasa,
        nMaxTipoMasa,
        nInputVars,
        nFicherosDisponiblesPorTipoVariable,
        self_LOCLlistaDasoVarsMovilidad=GLO.GLBLlistaDasoVarsMovilidad,
        # self_LOCLlistaDasoVarsPonderado=GLO.GLBLlistaDasoVarsPonderado,
        self_LOCLvarsTxtFileName=GLO.GLBLvarsTxtFileNamePorDefecto,
        self_LOCLpatronVectrName=GLO.GLBLpatronVectrNamePorDefecto,
        self_LOCLpatronLayerName=GLO.GLBLpatronLayerNamePorDefecto,
        self_LOCLlistLstDasoVars=GLO.GLBLlistLstDasoVarsPorDefecto,

        self_nCeldasX_Destino=0,
        self_nCeldasY_Destino=0,
        self_metrosPixelX_Destino=0,
        self_metrosPixelY_Destino=0,
        self_nMinX_tif=0,
        self_nMaxY_tif=0,

        self_LOCLverbose=False,
    ):
    # print('----->>> self_LOCLpatronLayerName', type(self_LOCLpatronLayerName))
    # ==========================================================================
    if ':/' in self_LOCLpatronVectrName or ':\\' in self_LOCLpatronVectrName:
        patronVectrNameConPath = self_LOCLpatronVectrName
    else:
        patronVectrNameConPath = os.path.join(self_LOCLrutaAscRaizBase, self_LOCLpatronVectrName)
    # ==========================================================================
    envolventeShape = obtenerExtensionDeCapaVectorial(
        self_LOCLrutaAscRaizBase,
        self_LOCLpatronVectrName,
        LOCLlayerName=self_LOCLpatronLayerName,
        LOCLverbose=False,
    )
    if envolventeShape is None:
        print('\nclidtwins-> ATENCION: no esta disponible el fichero {}'.format(self_LOCLpatronVectrName))
        print(f'{TB}-> Ruta base: {self_LOCLrutaAscRaizBase}')
        sys.exit(0)
    patronVectorXmin = envolventeShape[0]
    patronVectorXmax = envolventeShape[1]
    patronVectorYmin = envolventeShape[2]
    patronVectorYmax = envolventeShape[3]

    self_nMaxX_tif = self_nMinX_tif + (self_nCeldasX_Destino * self_metrosPixelX_Destino)
    self_nMinY_tif = self_nMaxY_tif + (self_nCeldasY_Destino * self_metrosPixelY_Destino)  # self_metrosPixelY_Destino es negativo

    if (
        self_nMinX_tif > patronVectorXmax
        or self_nMaxX_tif < patronVectorXmin
        or self_nMinY_tif > patronVectorYmax
        or self_nMaxY_tif < patronVectorYmin
    ):
        print('\nclidtwins-> ATENCION: el perimetro de referencia (patron) no esta dentro de la zona analizada:')
        print(
            '{}-> Rango de coordenadas UTM de la zona analizada: X: {:0.2f} - {:0.2f}; Y: {:0.2f} - {:0.2f}'.format(
                TB,
                self_nMinX_tif, self_nMaxX_tif, self_nMinY_tif, self_nMaxY_tif,
            )
        )
        print(
            '{}-> Rango de coord UTM del perimetro del patron:   X: {:0.2f} - {:0.2f}; Y: {:0.2f} - {:0.2f}'.format(
                TB,
                patronVectorXmin,
                patronVectorXmax,
                patronVectorYmin,
                patronVectorYmax,
            )
        )
        print(
            '{}-> Raster con la zona analizada (envolvente de los asc): {}/{}'.format(
                TB,
                self_LOCLoutPathNameRuta,
                self_LOCLoutFileNameWExt_mergedUniCellAllDasoVars,
            )
        )
        print(f'{TB}-> Vector file con el perimetro de referencia (patron):  {patronVectrNameConPath}')
        sys.exit(0)
    #===========================================================================

    # ==========================================================================
    mergedUniCellAllDasoVarsFileNameConPath = os.path.join(self_LOCLoutPathNameRuta, self_LOCLoutFileNameWExt_mergedUniCellAllDasoVars)
    outputRasterNameClip = mergedUniCellAllDasoVarsFileNameConPath.replace('Global.', 'Patron.')
    print('\n{:_^80}'.format(''))
    print(f'clidtwins-> Abriendo raster creado mergedUniCellAllDasoVars:\n{TB}{mergedUniCellAllDasoVarsFileNameConPath}')
    rasterDatasetAll = gdal.Open(mergedUniCellAllDasoVarsFileNameConPath, gdalconst.GA_ReadOnly)
    # print('--->>> rasterDatasetAll (1):', rasterDatasetAll)
    #===========================================================================

    LOCLoutputRangosFileNpzSinPath = self_LOCLvarsTxtFileName.replace('.txt', '.npz')
    LOCLdictHistProb01 = {}

    # outputBand1 = rasterDatasetAll.GetRasterBand(1)
    # arrayBanda1 = outputBand1.ReadAsArray().astype(outputNpDatatypeAll)
    if self_LOCLverbose:
        print(f'\nclidtwins-> Recortando el raster con poligono de referencia (patron):\n'
              f'{TB}File:  {patronVectrNameConPath}')
    # Ver: https://gdal.org/python/osgeo.gdal-module.html
    try:
        if self_LOCLpatronLayerName == '' or self_LOCLpatronLayerName is None:
            rasterDatasetClip = gdal.Warp(
                outputRasterNameClip,
                rasterDatasetAll,
                cutlineDSName=patronVectrNameConPath,
                cropToCutline=True,
                # dstNodata=np.nan,
                dstNodata=noDataDasoVarAll,
            )
        else:
            if self_LOCLverbose:
                print(f'{TB}Layer: {self_LOCLpatronLayerName}')
            rasterDatasetClip = gdal.Warp(
                outputRasterNameClip,
                rasterDatasetAll,
                cutlineDSName=patronVectrNameConPath,
                cutlineLayer=self_LOCLpatronLayerName,
                cropToCutline=True,
                # dstNodata=np.nan,
                dstNodata=noDataDasoVarAll,
            )
    except:
        print(f'\nclidtwins-> No se ha podido recortar el raster generado con {patronVectrNameConPath}, cutlineLayer: {self_LOCLpatronLayerName}, {type(self_LOCLpatronLayerName)}')
        print(f'{TB}Revisar si se ha generado adecuadamente el raster {mergedUniCellAllDasoVarsFileNameConPath}')
        print(f'{TB}Revisar si la capa vectorial de recorte es correcta, no esta bloqueada (y tiene un poligono) {patronVectrNameConPath}')
        sys.exit(0)

    rasterDatasetClip = gdal.Open(outputRasterNameClip, gdalconst.GA_ReadOnly)
    nBandasRasterOutput = rasterDatasetClip.RasterCount

    outputBand1Clip = rasterDatasetClip.GetRasterBand(1)
    arrayBanda1Clip = outputBand1Clip.ReadAsArray().astype(outputNpDatatypeAll)
    # Mascara con ceros en celdas con alguna variable noData
    arrayBandaXMaskClip = np.full_like(arrayBanda1Clip, 0, dtype=np.uint8)
    for nBanda in range(1, nBandasRasterOutput + 1):
        outputBandXClip = rasterDatasetClip.GetRasterBand(nBanda)
        arrayBandaXClip = outputBandXClip.ReadAsArray().astype(outputNpDatatypeAll)
        arrayBandaXMaskClip[arrayBandaXClip == noDataDasoVarAll] = 1

    nCeldasConDasoVarsOk = np.count_nonzero(arrayBandaXMaskClip == 0)
    listaCeldasConDasoVarsPatron = np.zeros(nCeldasConDasoVarsOk * nBandasRasterOutput, dtype=outputNpDatatypeAll).reshape(nCeldasConDasoVarsOk, nBandasRasterOutput)
    print(f'{TB}Numero de celdas patron con dasoVars ok: {nCeldasConDasoVarsOk}')

    # if nBandasRasterOutput != nBandasPrevistasOutput:
    #     print(f'\nAVISO: el numero de bandas del raster generado ({nBandasRasterOutput}) no es igual al previsto ({nBandasPrevistasOutput}), es decir num. de variables + 2 (num variables: {nInputVars})')
    # Las nInputVars primeras bandas corresponden a las variables utilizadas (self_LOCLlistaDasoVarsFileTypes)
    # La penultima corresponde al tipo de bosque o cobertura MFE
    # La ultima corresponde al tipo de masa.
    # La numeracion de las bandas empieza en 1 y la de variables empieza en 0.

    myRange = {}
    myNBins = {}
    factorMovilidad = {}
    for nBanda in range(1, nBandasRasterOutput + 1):
        nInputVar = nBanda - 1
        factorMovilidad[nBanda] = self_LOCLlistaDasoVarsMovilidad[nInputVar] / 100
        if nBanda == nBandasRasterOutput:
            # TipoMasa
            myRange[nBanda] = (nMinTipoMasa, nMaxTipoMasa)
            myNBins[nBanda] = nMaxTipoMasa - nMinTipoMasa
            # factorMovilidad[nBanda] = 0
        elif nBanda == nBandasRasterOutput - 1:
            # TipoBosqueMfe
            myRange[nBanda] = (0, 255)
            myNBins[nBanda] = 255
            # factorMovilidad[nBanda] = 0
        else:
            # Alturas y Coberturas
            myRange[nBanda] = (self_LOCLlistLstDasoVars[nInputVar][2], self_LOCLlistLstDasoVars[nInputVar][3])
            myNBins[nBanda] = self_LOCLlistLstDasoVars[nInputVar][4]
            # factorMovilidad[nBanda] = 0.25

    for nBanda in range(1, nBandasRasterOutput + 1):
        # Si para esa variable estan todos los bloques:
        nInputVar = nBanda - 1
        if nInputVar >= 0 and nInputVar < nInputVars:
            if nFicherosDisponiblesPorTipoVariable[nInputVar] != nFicherosDisponiblesPorTipoVariable[0]:
                print(f'\nHistograma para banda {nBanda} (variable {nInputVar}: {self_LOCLlistLstDasoVars[nInputVar][1]})')
                # claveDef = f'{str(nInputVar)}_{self_LOCLlistLstDasoVars[nInputVar][1]}_ref'
                # print(f'\n(1) Chequeando rangos admisibles para: {claveDef}')
                print(f'{TB}AVISO: La banda {nBanda} (variable {nInputVar}) no cuenta con fichero para todos los bloques ({nFicherosDisponiblesPorTipoVariable[nInputVar]} de {nFicherosDisponiblesPorTipoVariable[0]})')
                continue
        outputBandXClip = rasterDatasetClip.GetRasterBand(nBanda)
        arrayBandaXClip = outputBandXClip.ReadAsArray().astype(outputNpDatatypeAll)

        # print(f'\nFragmento de banda {nBanda} ({outputNpDatatypeAll}):')
        # print(arrayBandaXClip[20:25, 10:20])

        # https://numpy.org/doc/stable/reference/maskedarray.html
        # https://numpy.org/doc/stable/reference/routines.ma.html#conversion-operations
        arrayBandaXClipMasked = ma.masked_array(
            arrayBandaXClip,
            mask=arrayBandaXMaskClip,
            dtype=outputNpDatatypeAll
            )
        print(f'{TB}Numero de puntos patron con dasoVars ok:', len(ma.compressed(arrayBandaXClipMasked)))
        listaCeldasConDasoVarsPatron[:, nInputVar] = ma.compressed(arrayBandaXClipMasked)

        histNumberPatron = np.histogram(arrayBandaXClip, bins=myNBins[nBanda], range=myRange[nBanda])
        histProbabPatron = np.histogram(arrayBandaXClip, bins=myNBins[nBanda], range=myRange[nBanda], density=True)
        # print(f'\nhistProbabPatron[0]: {type(histProbabPatron[0])}')
        histProb01Patron = np.array(histProbabPatron[0]) * ((myRange[nBanda][1] - myRange[nBanda][0]) / myNBins[nBanda])

        if nBanda == nBandasRasterOutput:
            if self_LOCLverbose:
                print(f'\nHistograma para tipos de masa (banda {nBanda})')
                print(f'{TB}Por el momento no utilizo esta informacion.')
            try:
                tipoDeMasaUltimoNumero = np.max(np.nonzero(histNumberPatron[0]))
            except:
                tipoBosqueUltimoNumero = 0
            histogramaTemp = (histNumberPatron[0]).copy()
            histogramaTemp.sort()
            codeTipoDeMasaPatronMasFrecuente1 = (histNumberPatron[0]).argmax(axis=0)
            arrayPosicionTipoDeMasaPatron1 = np.where(histNumberPatron[0] == histogramaTemp[-1])
            arrayPosicionTipoDeMasaPatron2 = np.where(histNumberPatron[0] == histogramaTemp[-2])
            if self_LOCLverbose:
                print(f'{TB}-> Tipo de masa principal (patron): {codeTipoDeMasaPatronMasFrecuente1}; frecuencia: {int(round(100 * histProb01Patron[codeTipoDeMasaPatronMasFrecuente1], 0))} %')
                # print(f'{TB}-> {arrayPosicionTipoDeMasaPatron1}')
                for contadorTB1, numPosicionTipoDeMasaPatron1 in enumerate(arrayPosicionTipoDeMasaPatron1[0]):
                    # print(f'{TB}-> {numPosicionTipoDeMasaPatron1}')
                    print(f'{TB}-> {contadorTB1} Tipo de masa primero (patron): {numPosicionTipoDeMasaPatron1}; frecuencia: {int(round(100 * histProb01Patron[numPosicionTipoDeMasaPatron1], 0))} %')
                if histProb01Patron[arrayPosicionTipoDeMasaPatron2[0][0]] != 0:
                    for contadorTB2, numPosicionTipoDeMasaPatron2 in enumerate(arrayPosicionTipoDeMasaPatron2[0]):
                        # print(f'{TB}-> {numPosicionTipoDeMasaPatron2}')
                        print(f'{TB}-> {contadorTB2} Tipo de masa segundo (patron): {numPosicionTipoDeMasaPatron2}; frecuencia: {int(round(100 * histProb01Patron[numPosicionTipoDeMasaPatron2], 0))} %')

            if codeTipoDeMasaPatronMasFrecuente1 != arrayPosicionTipoDeMasaPatron1[0][0]:
                print(f'{TB}-> ATENCION: revisar esto porque debe haber algun error: {codeTipoDeMasaPatronMasFrecuente1} != {arrayPosicionTipoDeMasaPatron1[0][0]}')
            if len(arrayPosicionTipoDeMasaPatron1[0]) == 1:
                codeTipoDeMasaPatronMasFrecuente2 = arrayPosicionTipoDeMasaPatron2[0][0]
            else:
                codeTipoDeMasaPatronMasFrecuente2 = arrayPosicionTipoDeMasaPatron1[0][1]

            pctjTipoDeMasaPatronMasFrecuente1 = int(round(100 * histProb01Patron[codeTipoDeMasaPatronMasFrecuente1], 0))
            pctjTipoDeMasaPatronMasFrecuente2 = int(round(100 * histProb01Patron[codeTipoDeMasaPatronMasFrecuente2], 0))

            if self_LOCLverbose:
                print(f'{TB}-> Tipos de masa mas frecuentes (patron): 1-> {codeTipoDeMasaPatronMasFrecuente1} ({pctjTipoDeMasaPatronMasFrecuente1} %); 2-> {codeTipoDeMasaPatronMasFrecuente2} ({pctjTipoDeMasaPatronMasFrecuente2} %)')
                print(f'{TB}-> Numero pixeles de cada tipo de masa (patron) ({(histNumberPatron[0]).sum()}):')
                for numTipoMasa in range(len(histNumberPatron[0])):
                    if histNumberPatron[0][numTipoMasa] != 0:
                        print(f'{TB}{TV}-> tipoMasa: {numTipoMasa} -> nPixeles: {histNumberPatron[0][numTipoMasa]}')

        elif nBanda == nBandasRasterOutput - 1:
            if self_LOCLverbose:
                print(f'\nHistograma para tipos de bosque (banda {nBanda})')
            # tipoBosquePrimerNumero = np.min(np.nonzero(histNumberPatron[0]))
            try:
                tipoBosqueUltimoNumero = np.max(np.nonzero(histNumberPatron[0]))
            except:
                tipoBosqueUltimoNumero = 0
            histogramaTemp = (histNumberPatron[0]).copy()
            histogramaTemp.sort()
            codeTipoBosquePatronMasFrecuente1 = (histNumberPatron[0]).argmax(axis=0)
            arrayPosicionTipoBosquePatron1 = np.where(histNumberPatron[0] == histogramaTemp[-1])
            arrayPosicionTipoBosquePatron2 = np.where(histNumberPatron[0] == histogramaTemp[-2])
            if self_LOCLverbose:
                print(f'{TB}-> Tipo de bosque principal (patron): {codeTipoBosquePatronMasFrecuente1}; frecuencia: {int(round(100 * histProb01Patron[codeTipoBosquePatronMasFrecuente1], 0))} %')
                # print(f'{TB}-> {arrayPosicionTipoBosquePatron1}')
                for contadorTB1, numPosicionTipoBosquePatron1 in enumerate(arrayPosicionTipoBosquePatron1[0]):
                    # print(f'{TB}-> {numPosicionTipoBosquePatron1}')
                    print(f'{TB}-> {contadorTB1} Tipo de bosque primero (patron): {numPosicionTipoBosquePatron1}; frecuencia: {int(round(100 * histProb01Patron[numPosicionTipoBosquePatron1], 0))} %')
                if histProb01Patron[arrayPosicionTipoBosquePatron2[0][0]] != 0:
                    for contadorTB2, numPosicionTipoBosquePatron2 in enumerate(arrayPosicionTipoBosquePatron2[0]):
                        # print(f'{TB}-> {numPosicionTipoBosquePatron2}')
                        print(f'{TB}-> {contadorTB2} Tipo de bosque segundo (patron): {numPosicionTipoBosquePatron2}; frecuencia: {int(round(100 * histProb01Patron[numPosicionTipoBosquePatron2], 0))} %')
            else:
                if self_LOCLverbose:
                    print(f'{TB}-> Solo hay tipo de bosque princial')
            if codeTipoBosquePatronMasFrecuente1 != arrayPosicionTipoBosquePatron1[0][0]:
                print(f'{TB}-> ATENCION: revisar esto porque debe haber algun error: {codeTipoBosquePatronMasFrecuente1} != {arrayPosicionTipoBosquePatron1[0][0]}')
            if len(arrayPosicionTipoBosquePatron1[0]) == 1:
                codeTipoBosquePatronMasFrecuente2 = arrayPosicionTipoBosquePatron2[0][0]
            else:
                codeTipoBosquePatronMasFrecuente2 = arrayPosicionTipoBosquePatron1[0][1]

            pctjTipoBosquePatronMasFrecuente1 = int(round(100 * histProb01Patron[codeTipoBosquePatronMasFrecuente1], 0))
            pctjTipoBosquePatronMasFrecuente2 = int(round(100 * histProb01Patron[codeTipoBosquePatronMasFrecuente2], 0))

            if self_LOCLverbose:
                print(f'{TB}-> Tipos de bosque mas frecuentes (patron): 1-> {codeTipoBosquePatronMasFrecuente1} ({pctjTipoBosquePatronMasFrecuente1} %); 2-> {codeTipoBosquePatronMasFrecuente2} ({pctjTipoBosquePatronMasFrecuente2} %)')
                print(f'{TB}-> Numero pixeles de cada tipo de bosque (patron) ({(histNumberPatron[0]).sum()}):')
                for numTipoBosque in range(len(histNumberPatron[0])):
                    if histNumberPatron[0][numTipoBosque] != 0:
                        print(f'tipoBosque: {numTipoBosque} -> nPixeles: {histNumberPatron[0][numTipoBosque]}')
        else:
            if self_LOCLverbose:
                if nInputVar < len(self_LOCLlistLstDasoVars):
                    print(f'\nHistograma para banda {nBanda} (variable {nInputVar}: {self_LOCLlistLstDasoVars[nInputVar][1]}) con {myNBins[nBanda]} Clases')
                else:
                    print(f'\nHistograma para banda {nBanda} (variable {nInputVar} de {self_LOCLlistLstDasoVars})')
                print(f'{TB}-> myRange: {myRange[nBanda]}; nBins: {myNBins[nBanda]}')
            try:
                ultimoNoZero = np.max(np.nonzero(histNumberPatron[0]))
            except:
                ultimoNoZero = 0
            if self_LOCLverbose:
                print(f'{TB}-> Numero puntos: {(histNumberPatron[0]).sum()} -> Histograma: {histNumberPatron[0][:ultimoNoZero + 2]}')
            # print(f'{TB}-> Numero pixeles de cada rango de la variable (patron) (total: {(histNumberPatron[0]).sum()}):')
            # for numRango in range(len(histNumberPatron[0])):
            #     if histNumberPatron[0][numRango] != 0:
            #         print(f'{TB}{TV}-> Rango num: {numRango} -> nPixeles: {histNumberPatron[0][numRango]}')
        # print(f'{TB}-> Suma frecuencias: {round(histProb01Patron.sum(), 2)}')

        if nInputVar >= 0 and nInputVar < nInputVars:
            claveDef = f'{str(nInputVar)}_{self_LOCLlistLstDasoVars[nInputVar][1]}_ref'
            claveMin = f'{str(nInputVar)}_{self_LOCLlistLstDasoVars[nInputVar][1]}_min'
            claveMax = f'{str(nInputVar)}_{self_LOCLlistLstDasoVars[nInputVar][1]}_max'
            LOCLdictHistProb01[claveDef] = histProb01Patron
            LOCLdictHistProb01[claveMin] = np.zeros(myNBins[nBanda], dtype=np.float32)
            LOCLdictHistProb01[claveMax] = np.zeros(myNBins[nBanda], dtype=np.float32)
            # if 0 in LOCLdictHistProb01[claveDef]:
            #     primerCero = LOCLdictHistProb01[claveDef].index(0)
            # else:
            #     primerCero = len(LOCLdictHistProb01[claveDef])
            try:
                ultimoNoZero = np.max(np.nonzero(LOCLdictHistProb01[claveDef]))
            except:
                ultimoNoZero = 0
            if self_LOCLverbose > 1:
                print(f'{TB}-> Creando rangos admisibles para: {claveDef}')
                print(f'{TB}{TV}Valores de referencia (patron):')
                print(f'{TB}{TV}-> LOCLdictHistProb01[{claveDef}]:', LOCLdictHistProb01[claveDef][:ultimoNoZero + 2])
            # print('LOCLdictHistProb01[claveMin]:', LOCLdictHistProb01[claveMin])
            # print('LOCLdictHistProb01[claveMax]:', LOCLdictHistProb01[claveMax])
            for nRango in range(len(histProb01Patron)):
                # print(f'claveDef: {claveDef}; nRango: {type(nRango)} {nRango}')
                # print('->', LOCLdictHistProb01[claveDef])
                # print('->', LOCLdictHistProb01[claveDef][nRango])
                decrementoFrecuencia = max(0.05, (factorMovilidad[nBanda] * LOCLdictHistProb01[claveDef][nRango]))
                LOCLdictHistProb01[claveMin][nRango] = round(LOCLdictHistProb01[claveDef][nRango] - decrementoFrecuencia, 3)
                if LOCLdictHistProb01[claveMin][nRango] < 0.05:
                    LOCLdictHistProb01[claveMin][nRango] = 0
                if nRango == 0:
                    if LOCLdictHistProb01[claveDef][nRango] > 0 or LOCLdictHistProb01[claveDef][nRango + 1] > 0:
                        incrementoMinimo = 0.05
                    else:
                        incrementoMinimo = 0.1
                    incrementoFrecuencia = max(
                        incrementoMinimo, (
                            # (factorMovilidad[nBanda] * LOCLdictHistProb01[claveDef][nRango] * 2)
                            + (
                                factorMovilidad[nBanda] * 0.5 * (
                                    LOCLdictHistProb01[claveDef][nRango]
                                    + LOCLdictHistProb01[claveDef][nRango + 1]
                                )
                            )
                        )
                    )
                    if self_LOCLverbose > 1:
                        print(
                            '{}{}{}+{:03}-> claveDef: {} nRango: {}; prev: {}; this: {:0.3f}; post: {:0.3f}'.format(
                                TB, TV, TV,
                                incrementoMinimo * 100,
                                claveDef,
                                nRango,
                                '-.---',
                                LOCLdictHistProb01[claveDef][nRango],
                                LOCLdictHistProb01[claveDef][nRango + 1],
                            )
                        )
                elif nRango == len(histProb01Patron) - 1:
                    if LOCLdictHistProb01[claveDef][nRango] > 0 or LOCLdictHistProb01[claveDef][nRango - 1] > 0:
                        incrementoMinimo = 0.05
                    else:
                        incrementoMinimo = 0.02
                    incrementoFrecuencia = max(
                        incrementoMinimo, (
                            # (factorMovilidad[nBanda] * LOCLdictHistProb01[claveDef][nRango] * 2)
                            + (
                                factorMovilidad[nBanda] * 0.5 * (
                                    LOCLdictHistProb01[claveDef][nRango]
                                    + LOCLdictHistProb01[claveDef][nRango - 1]
                                )
                            )
                        )
                    )
                    if self_LOCLverbose > 1:
                        print(
                            '{}{}{}+{:03}-> claveDef: {} nRango: {}; prev: {:0.3f}; this: {:0.3f}; post: {}'.format(
                                TB, TV, TV,
                                incrementoMinimo * 100,
                                claveDef,
                                nRango,
                                LOCLdictHistProb01[claveDef][nRango - 1],
                                LOCLdictHistProb01[claveDef][nRango],
                                '-.---',
                            )
                        )
                else:
                    if LOCLdictHistProb01[claveDef][nRango] > 0 or (LOCLdictHistProb01[claveDef][nRango - 1] > 0 and LOCLdictHistProb01[claveDef][nRango + 1] > 0):
                        incrementoMinimo = 0.1
                        if self_LOCLverbose > 1:
                            print(
                                '{}{}{}+{:03}-> claveDef: {} nRango: {}; prev: {:0.3f}; this: {:0.3f}; post: {:0.3f}'.format(
                                    TB, TV, TV,
                                    10,
                                    claveDef,
                                    nRango,
                                    LOCLdictHistProb01[claveDef][nRango - 1],
                                    LOCLdictHistProb01[claveDef][nRango],
                                    LOCLdictHistProb01[claveDef][nRango + 1],
                                )
                            )
                    elif LOCLdictHistProb01[claveDef][nRango - 1] > 0 or LOCLdictHistProb01[claveDef][nRango + 1] > 0:
                        incrementoMinimo = 0.05
                        if self_LOCLverbose > 1:
                            print(
                                '{}{}{}+{:03}-> claveDef: {} nRango: {}; prev: {:0.3f}; this: {:0.3f}; post: {:0.3f}'.format(
                                    TB, TV, TV,
                                    5,
                                    claveDef,
                                    nRango,
                                    LOCLdictHistProb01[claveDef][nRango - 1],
                                    LOCLdictHistProb01[claveDef][nRango],
                                    LOCLdictHistProb01[claveDef][nRango + 1],
                                )
                            )
                    elif LOCLdictHistProb01[claveDef][nRango - 1] != 0 or LOCLdictHistProb01[claveDef][nRango + 1] != 0:
                        incrementoMinimo = 0.01
                        if self_LOCLverbose > 1:
                            print(
                                '{}{}{}+{:03}-> claveDef: {} nRango: {}; prev: {:0.3f}; this: {:0.3f}; post: {:0.3f}'.format(
                                    TB, TV, TV,
                                    1,
                                    claveDef,
                                    nRango,
                                    LOCLdictHistProb01[claveDef][nRango - 1],
                                    LOCLdictHistProb01[claveDef][nRango],
                                    LOCLdictHistProb01[claveDef][nRango + 1],
                                )
                            )
                    incrementoFrecuencia = max(
                        incrementoMinimo, (
                            # (factorMovilidad[nBanda] * LOCLdictHistProb01[claveDef][nRango] * 2)
                            + (
                                factorMovilidad[nBanda] * 0.5 * (
                                    LOCLdictHistProb01[claveDef][nRango]
                                    + LOCLdictHistProb01[claveDef][nRango - 1]
                                )
                            )
                            + (
                                factorMovilidad[nBanda] * 0.5 * (
                                    LOCLdictHistProb01[claveDef][nRango]
                                    + LOCLdictHistProb01[claveDef][nRango + 1]
                                )
                            )
                        )
                    )
                LOCLdictHistProb01[claveMax][nRango] = round(LOCLdictHistProb01[claveDef][nRango] + incrementoFrecuencia, 3)
                if self_LOCLverbose > 1:
                    print(
                        '{}{}{}-> Rango: {} -> decrementoFrecuencia: {} incrementoFrecuencia: {} -> min/max: {:0.3f} / {:0.3f}'.format(
                            TB, TV, TV,
                            nRango,
                            decrementoFrecuencia,
                            incrementoFrecuencia,
                            LOCLdictHistProb01[claveMin][nRango],
                            LOCLdictHistProb01[claveMax][nRango],
                        )
                    )
                if LOCLdictHistProb01[claveMax][nRango] - LOCLdictHistProb01[claveMin][nRango] < 0.05:
                    ampliarLimites = False
                    if nRango == 0:
                        if LOCLdictHistProb01[claveDef][nRango + 1] != 0:
                            ampliarLimites = True
                    elif nRango == len(histProb01Patron) - 1:
                        if LOCLdictHistProb01[claveDef][nRango - 1] != 0:
                            ampliarLimites = True
                    else:
                        if (
                            LOCLdictHistProb01[claveDef][nRango + 1] != 0
                            or LOCLdictHistProb01[claveDef][nRango - 1] != 0
                        ):
                            ampliarLimites = True
                    if ampliarLimites:
                        LOCLdictHistProb01[claveMin][nRango] -= 0.02
                        LOCLdictHistProb01[claveMax][nRango] += 0.03

                if LOCLdictHistProb01[claveMin][nRango] > 1:
                    LOCLdictHistProb01[claveMin][nRango] = 1
                if LOCLdictHistProb01[claveMin][nRango] < 0:
                    LOCLdictHistProb01[claveMin][nRango] = 0
                if LOCLdictHistProb01[claveMax][nRango] > 1:
                    LOCLdictHistProb01[claveMax][nRango] = 1
                if LOCLdictHistProb01[claveMax][nRango] < 0:
                    LOCLdictHistProb01[claveMax][nRango] = 0

            if self_LOCLverbose:
                print(f'{TB}{TV}Rangos admisibles:')
                # print('LOCLdictHistProb01[claveDef]:', LOCLdictHistProb01[claveDef])
                try:
                    ultimoNoZero = np.max(np.nonzero(LOCLdictHistProb01[claveMin]))
                except:
                    ultimoNoZero = 0
                print(f'{TB}{TV}{TV}-> LOCLdictHistProb01[claveMin]:', LOCLdictHistProb01[claveMin][:ultimoNoZero + 2])
                print(f'{TB}{TV}{TV}-> LOCLdictHistProb01[claveMax]:', LOCLdictHistProb01[claveMax][:ultimoNoZero + 9])

        # if nInputVar >= 0:
        #     print(f'{TB}-> valores de referencia: {histProb01Patron}')
        #     print(f'{TB}{TV}-> Rango min admisible:   {LOCLdictHistProb01[claveMin]}')
        #     print(f'{TB}{TV}-> Rango max admisible:   {LOCLdictHistProb01[claveMax]}')


        mostrarGraficaHistograma = False
        if mostrarGraficaHistograma:
            # rng = np.random.RandomState(10)  # deterministic random data
            # a = np.hstack((rng.normal(size=1000),
            #                rng.normal(loc=5, scale=2, size=1000)))
            _ = plt.hist(arrayBandaXClip.flatten(), bins=myNBins[nBanda], range=myRange[nBanda])  # arguments are passed to np.histogram
            if nBanda == nBandasRasterOutput:
                plt.title(f'Histograma para tipos de masa (banda {nBanda})')
            elif nBanda == nBandasRasterOutput - 1:
                plt.title(f'\nHistograma para tipos de bosque (banda {nBanda})')
            else:
                plt.title(f'Histograma para (banda {nBanda})-> variable {nInputVar}: {self_LOCLlistLstDasoVars[nInputVar][1]}')
            plt.show()

    # Descartado porque no funciona:
    # recortarRasterConShape( patronVectrNameConPath, mergedUniCellAllDasoVarsFileNameConPath )
    #===========================================================================
    return (
        LOCLoutputRangosFileNpzSinPath,
        nBandasRasterOutput,
        rasterDatasetAll,
        listaCeldasConDasoVarsPatron,
        LOCLdictHistProb01,
        myNBins,
        myRange,
        pctjTipoBosquePatronMasFrecuente1,
        codeTipoBosquePatronMasFrecuente1,
        pctjTipoBosquePatronMasFrecuente2,
        codeTipoBosquePatronMasFrecuente2,
        histProb01Patron,
    )


# ==============================================================================
def mostrarExportarRangos(
        self_LOCLoutPathNameRuta,
        self_outputRangosFileNpzSinPath,
        self_LOCLdictHistProb01,
        self_nInputVars,
        self_myRange,
        self_myNBins,
        self_nFicherosDisponiblesPorTipoVariable,
        self_LOCLvarsTxtFileName=GLO.GLBLvarsTxtFileNamePorDefecto,
        self_LOCLlistLstDasoVars=GLO.GLBLlistLstDasoVarsPorDefecto,
    ):
    self_nBandasRasterOutput = self_nInputVars + 2

    #===========================================================================
    outputRangosFileTxtConPath = os.path.join(self_LOCLoutPathNameRuta, self_LOCLvarsTxtFileName)
    outputRangosFileNpzConPath = os.path.join(self_LOCLoutPathNameRuta, self_outputRangosFileNpzSinPath)

    outputRangosFileTxtControl = open(outputRangosFileTxtConPath, mode='w+')
    outputRangosFileTxtControl.write('Valores y rangos admisibles para el histograma de frecuencias de las variables analizadas.\n')

    print('\nMostrando rangos para cada variable en self_LOCLdictHistProb01[claveDef]')
    for claveDef in self_LOCLdictHistProb01.keys():
        try:
            ultimoNoZero = np.max(np.nonzero(self_LOCLdictHistProb01[claveDef]))
        except:
            ultimoNoZero = 0
        print(f'{TB}-> claveDef: {claveDef} -> num. de rangos: {len(self_LOCLdictHistProb01[claveDef])} -> self_LOCLdictHistProb01: {self_LOCLdictHistProb01[claveDef][:ultimoNoZero + 2]}')

    print('\nclidtwins-> Recorriendo bandas para guardar intervalos para el histograma de cada variable:')
    for nBanda in range(1, self_nBandasRasterOutput + 1):
        nInputVar = nBanda - 1
        if nInputVar < 0 or nInputVar >= self_nInputVars:
            continue
        claveDef = f'{str(nInputVar)}_{self_LOCLlistLstDasoVars[nInputVar][1]}_ref'
        claveMin = f'{str(nInputVar)}_{self_LOCLlistLstDasoVars[nInputVar][1]}_min'
        claveMax = f'{str(nInputVar)}_{self_LOCLlistLstDasoVars[nInputVar][1]}_max'
        # self_myRange[nBanda] = (self_LOCLlistLstDasoVars[nInputVar][2], self_LOCLlistLstDasoVars[nInputVar][3])
        # self_myNBins[nBanda] = self_LOCLlistLstDasoVars[nInputVar][4]
        if nBanda == self_nBandasRasterOutput:
            outputRangosFileTxtControl.write(f'\nTipoMasa{TB}Band{nBanda}{TB}\n')
        else:
            outputRangosFileTxtControl.write(f'\n{self_LOCLlistLstDasoVars[nInputVar][1]}{TB}Var{nInputVar}{TB}RangoVar:{TB}{self_myRange[nBanda][0]}{TB}{self_myRange[nBanda][1]}{TB}nClases{TB}{self_myNBins[nBanda]}\n')
        print(f'{TB}-> nBanda: ', nBanda)
        print(f'{TB}{TV}-> self_myRange:', self_myRange[nBanda])
        print(f'{TB}{TV}-> nBins:  ', self_myNBins[nBanda])
        try:
            ultimoNoZero = np.max(np.nonzero(self_LOCLdictHistProb01[claveDef]))
        except:
            ultimoNoZero = 0

        print(f'{TB}{TV}{TV}-> self_LOCLdictHistProb01[claveDef]:', self_LOCLdictHistProb01[claveDef][:ultimoNoZero + 2])
        for nRango in range(self_myNBins[nBanda]):
            self_LOCLdictHistProb01[claveDef][nRango] = round(self_LOCLdictHistProb01[claveDef][nRango], 3)
            self_LOCLdictHistProb01[claveMin][nRango] = round(self_LOCLdictHistProb01[claveMin][nRango], 3)
            self_LOCLdictHistProb01[claveMax][nRango] = round(self_LOCLdictHistProb01[claveMax][nRango], 3)

            limInf = nRango * (self_myRange[nBanda][1] - self_myRange[nBanda][0]) / self_myNBins[nBanda]
            limSup = (nRango + 1) * (self_myRange[nBanda][1] - self_myRange[nBanda][0]) / self_myNBins[nBanda]
            if claveDef in self_LOCLdictHistProb01.keys():
                if limInf < 10:
                    signoInf = '+'
                else:
                    signoInf = ''
                if limSup < 10:
                    signoSup = '+'
                else:
                    signoSup = ''
                valDef = round(100 * self_LOCLdictHistProb01[claveDef][nRango], 0)
                valInf = round(100 * self_LOCLdictHistProb01[claveMin][nRango], 0)
                valSup = round(100 * self_LOCLdictHistProb01[claveMax][nRango], 0)
                signoDef = '+' if valDef < 10 else ''
                if valDef != 0 or valInf != 0 or valSup > 5:
                    textoWrite = '{}{}nClase{}{:02}{}TramoVar->{}{:0.2f}{}{:0.2f}{}valDef{}{:0.2f}{}limInf{}{:0.2f}{}limSup{}{:0.2f}'.format(
                        TB, TV, TV,
                        nRango, TB,
                        TB, limInf,
                        TB, limSup, TB,
                        TB, valDef, TB,
                        TB, valInf, TB,
                        TB, valSup,
                        )
                    print(f'{TB}{TV}{TV}{textoWrite}')
                    outputRangosFileTxtControl.write(f'{textoWrite}\n')
    outputRangosFileTxtControl.close()

    if os.path.exists(outputRangosFileNpzConPath):
        print(f'{TB}-> clidnat-> Antes se va a eliminar el fichero npz existente: {outputRangosFileNpzConPath}')
        os.remove(outputRangosFileNpzConPath)
        if os.path.exists(outputRangosFileNpzConPath):
            print(f'{TB}No se ha podido eliminar el fichero npz existente: {outputRangosFileNpzConPath}')
    np.savez_compressed(
        outputRangosFileNpzConPath,
        listaDasoVars=self_LOCLlistLstDasoVars,
        nInputVars=self_nInputVars,
        nBandasRasterOutput=self_nBandasRasterOutput,
        nFicherosDisponiblesPorTipoVariable=self_nFicherosDisponiblesPorTipoVariable,
        myRange=self_myRange[nBanda],
        dictHistProb01=self_LOCLdictHistProb01,
    )


# ==============================================================================
def infoSrcband(srcband):
    print('Tipo de datos de la banda=', gdal.GetDataTypeName(srcband.DataType))
    stats1 = srcband.GetStatistics(True, True)
    stats2 = srcband.ComputeStatistics(0)
    if stats1 is None or stats2 is None:
        exit
    print('Estadisticas guardadas en metadatos:')
    print('Minimum=%.3f, Maximum=%.3f, Mean=%.3f, StdDev=%.3f' % (stats1[0], stats1[1], stats1[2], stats1[3]))
    print('Estadisticas recalculadas:')
    print('Minimum=%.3f, Maximum=%.3f, Mean=%.3f, StdDev=%.3f' % (stats2[0], stats2[1], stats2[2], stats2[3]))
    # Tambien se puede conocer el minimo y el maximo con:
    # minimo = srcband.GetMinimum()
    # maximo = srcband.GetMaximum()
    # Y tambien con:
    # (minimo,maximo) = srcband.ComputeRasterMinMax(1)
    print('Otras caracteristicas de la capa:')
    print("No data value= ", srcband.GetNoDataValue())
    print("Scale=         ", srcband.GetScale())
    print("Unit type=     ", srcband.GetUnitType())

    ctable = srcband.GetColorTable()
    if not ctable is None:
        print("Color table count= ", ctable.GetCount())
        for i in range(0, ctable.GetCount()):
            entry = ctable.GetColorEntry(i)
            if not entry:
                continue
            print("Color entry RGB=   ", ctable.GetColorEntryAsRGB(i, entry))
    else:
        print('No ColorTable')
        # sys.exit(0)
    if not srcband.GetRasterColorTable() is None:
        print('Band has a color table with ', srcband.GetRasterColorTable().GetCount(), ' entries.')
    else:
        print('No RasterColorTable')
    if srcband.GetOverviewCount() > 0:
        print('Band has ', srcband.GetOverviewCount(), ' overviews.')
    else:
        print('No overviews')


# ==============================================================================
def mostrarListaDrivers():
    cnt = ogr.GetDriverCount()
    formatsList = []
    for i in range(cnt):
        driver = ogr.GetDriver(i)
        driverName = driver.GetName()
        if not driverName in formatsList:
            formatsList.append(driverName)
    formatsList.sort()
    for i in formatsList:
        print(i)


# ==============================================================================
def leerConfig(LOCL_configDictPorDefecto, LOCL_configFileNameCfg, LOCL_verbose=False):
    print('\n{:_^80}'.format(''))
    print('clidtwins-> Fichero de configuracion:  {}'.format(LOCL_configFileNameCfg))
    # ==========================================================================
    if not os.path.exists(LOCL_configFileNameCfg):
        print(f'{TB}  clidtwins-> Fichero no encontrado: se crea con valores por defecto')
        # En ausencia de fichero de configuracion, uso valores por defecto y los guardo en un nuevo fichero cfg
        config = RawConfigParser()
        config.optionxform = str  # Avoid change to lowercase

        for nombreParametroDeConfiguracion in LOCL_configDictPorDefecto.keys():
            grupoParametroConfiguracion = LOCL_configDictPorDefecto[nombreParametroDeConfiguracion][1]
            if not grupoParametroConfiguracion in config.sections():
                if LOCL_verbose and False:
                    print(f'{TB}{TV}clidtwins-> grupoParametros nuevo:', grupoParametroConfiguracion)
                config.add_section(grupoParametroConfiguracion)
        # Puedo agregar otras secciones:
        config.add_section('Custom')

        if LOCL_verbose and False:
            print(f'{TB}{TV}clidtwins-> Lista de parametros de configuracion por defecto:')
        for nombreParametroDeConfiguracion in LOCL_configDictPorDefecto.keys():
            listaParametroConfiguracion = LOCL_configDictPorDefecto[nombreParametroDeConfiguracion]
            valorParametroConfiguracion = listaParametroConfiguracion[0]
            grupoParametroConfiguracion = listaParametroConfiguracion[1]
            tipoParametroConfiguracion = listaParametroConfiguracion[2]
            descripcionParametroConfiguracion = listaParametroConfiguracion[3]

            # config.set(grupoParametroConfiguracion, nombreParametroDeConfiguracion, [str(valorParametroConfiguracion), tipoParametroConfiguracion])
            if not descripcionParametroConfiguracion is None:
                if (
                    'á' in descripcionParametroConfiguracion
                    or 'é' in descripcionParametroConfiguracion
                    or 'í' in descripcionParametroConfiguracion
                    or 'ó' in descripcionParametroConfiguracion
                    or 'ú' in descripcionParametroConfiguracion
                    or 'ñ' in descripcionParametroConfiguracion
                    or 'ç' in descripcionParametroConfiguracion
                ):
                    descripcionParametroConfiguracion = ''.join(unicodedata.normalize("NFD", c)[0] for c in str(descripcionParametroConfiguracion))
                if (descripcionParametroConfiguracion.encode('utf-8')).decode('cp1252') != descripcionParametroConfiguracion:
                    descripcionParametroConfiguracion = ''

            listaConcatenada = '{}|+|{}|+|{}'.format(
                str(valorParametroConfiguracion),
                str(tipoParametroConfiguracion),
                str(descripcionParametroConfiguracion)
            )

            config.set(
                grupoParametroConfiguracion,
                nombreParametroDeConfiguracion,
                listaConcatenada
            )
            if LOCL_verbose and False:
                print(f'{TB}{TV}{TV}-> {nombreParametroDeConfiguracion}: {valorParametroConfiguracion} (tipo {tipoParametroConfiguracion})-> {descripcionParametroConfiguracion}')

        try:
            with open(LOCL_configFileNameCfg, mode='w+') as configfile:
                config.write(configfile)
        except:
            print('\nclidtwins-> ATENCION, revisar caracteres no admitidos en el fichero de configuracion:', LOCL_configFileNameCfg)
            print(f'{TB}Ejemplos: vocales acentuadas, ennes, cedillas, flecha dchea (->), etc.')

    # Asigno los parametros de configuracion a varaible globales:
    config = RawConfigParser()
    config.optionxform = str  # Avoid change to lowercase

    # Confirmo que se ha creado correctamente el fichero de configuracion
    if not os.path.exists(LOCL_configFileNameCfg):
        print('\nclidtwins-> ATENCION: fichero de configuracion no encontrado ni creado:', LOCL_configFileNameCfg)
        print(f'{TB}-> Revisar derechos de escritura en la ruta en la que esta la aplicacion')
        sys.exit(0)

    try:
        LOCL_configDict = {}
        config.read(LOCL_configFileNameCfg)
        if LOCL_verbose:
            print(f'{TB}-> clidtwins-> Parametros de configuracion (guardados en {LOCL_configFileNameCfg}):')
        for grupoParametroConfiguracion in config.sections():
            for nombreParametroDeConfiguracion in config.options(grupoParametroConfiguracion):
                strParametroConfiguracion = config.get(grupoParametroConfiguracion, nombreParametroDeConfiguracion)
                listaParametroConfiguracion = strParametroConfiguracion.split('|+|')
                valorPrincipal = listaParametroConfiguracion[0]
                if len(listaParametroConfiguracion) > 1:
                    tipoParametroConfiguracion = listaParametroConfiguracion[1]
                else:
                    tipoParametroConfiguracion = 'str'
                valorParametroConfiguracion = clidconfig.valorConfig(
                    valorPrincipal,
                    valorAlternativoTxt='',
                    usarAlternativo=False,
                    nombreParametro=nombreParametroDeConfiguracion,
                    tipoVariable=tipoParametroConfiguracion,
                )

                if len(listaParametroConfiguracion) > 2:
                    descripcionParametroConfiguracion = listaParametroConfiguracion[2]
                else:
                    descripcionParametroConfiguracion = ''
                if nombreParametroDeConfiguracion[:1] == '_':
                    grupoParametroConfiguracion_new = '_%s' % grupoParametroConfiguracion
                else:
                    grupoParametroConfiguracion_new = grupoParametroConfiguracion
                LOCL_configDict[nombreParametroDeConfiguracion] = [
                    valorParametroConfiguracion,
                    grupoParametroConfiguracion_new,
                    descripcionParametroConfiguracion,
                    tipoParametroConfiguracion,
                ]
                if LOCL_verbose:
                    print(
                        '{}{}-> parametro {:<35} -> {}'.format(
                            TB, TV,
                            nombreParametroDeConfiguracion,
                            LOCL_configDict[nombreParametroDeConfiguracion]
                        )
                    )

        # Compruebo que el fichero de configuracion tiene todos los parametros de LOCL_configDictPorDefecto
        for nombreParametroDeConfiguracion in LOCL_configDictPorDefecto.keys():
            if not nombreParametroDeConfiguracion in LOCL_configDict:
                listaParametroConfiguracion = LOCL_configDictPorDefecto[nombreParametroDeConfiguracion]
                valorPrincipal = listaParametroConfiguracion[0]
                grupoParametroConfiguracion = listaParametroConfiguracion[1]
                if len(listaParametroConfiguracion) > 1:
                    tipoParametroConfiguracion = listaParametroConfiguracion[2]
                else:
                    tipoParametroConfiguracion = 'str'
                valorParametroConfiguracion = clidconfig.valorConfig(
                    valorPrincipal,
                    valorAlternativoTxt='',
                    usarAlternativo=False,
                    nombreParametro=nombreParametroDeConfiguracion,
                    tipoVariable=tipoParametroConfiguracion,
                )
                descripcionParametroConfiguracion = listaParametroConfiguracion[3]
                LOCL_configDict[nombreParametroDeConfiguracion] = [
                    valorParametroConfiguracion,
                    grupoParametroConfiguracion,
                    tipoParametroConfiguracion,
                    descripcionParametroConfiguracion,
                ]
                if LOCL_verbose or True:
                    print(f'{TB}-> AVISO: el parametro <{nombreParametroDeConfiguracion}> no esta en' ,
                          f'el fichero de configuacion; se adopta valor por defecto: <{valorParametroConfiguracion}>')

        config_ok = True
    except:
        print('clidtwins-> Error al leer la configuracion del fichero:', LOCL_configFileNameCfg)
        config_ok = False
        sys.exit(0)
    # print(f'{TB}{TV}clidtwins-> LOCL_configDict:', LOCL_configDict)

    print('{:=^80}'.format(''))
    return LOCL_configDict
    # ==========================================================================


# ==============================================================================
class myClass(object):
    pass

# ==============================================================================
def fxn():
    warnings.warn("deprecated", DeprecationWarning)

# ==============================================================================
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    fxn()
# ==============================================================================

ogr.RegisterAll()
gdal.UseExceptions()

# ==============================================================================
def foo():
    pass

# ==============================================================================
if __name__ == '__main__':
    pass

