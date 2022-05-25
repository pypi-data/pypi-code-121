#!/usr/bin/python
# -*- coding: UTF-8 -*-
'''
Created on 16 jun. 2019

@author: joseb
'''
from __future__ import division, print_function
import inspect
import os
import sys
import time
import math
import random
import pathlib
# import struct

import numpy as np
# import scipy
# import scipy.misc
import scipy.ndimage.interpolation
from PIL import Image
# from pandas.io import orc

##No usar esto con Anaconda
# Con esto resuelvo el error al cargar gdal, que ocurre en eclipse pero no el cmd.
# No entiendo porque en eclipse mira antes algun diretorio que tiene un gdal que no es el correcto (el de OSGeo4W64)
# os.environ['PATH'] = 'C:/OSGeo4W64/bin;' + os.environ['PATH']
# print(os.environ['PATH'])
# sys.path.insert(0,'C:\OSGeo4W64\bin')

# Para que funcione GDAL en eclipse he hecho esto:
# En Windows->Preferences->Pydev->Interpreters->Python interpreter->Pestanna environment -> INlcuir PATH = C:/OSGeo4W64/bin
try:
    import gdal, ogr, osr, gdalnumeric, gdalconst
    gdalOk = True
except:
    gdalOk = False
    print('clidcarto-> No se ha podido cargar gdal directamente, se intente de la carpeta osgeo')
if not gdalOk:
    try:
        from osgeo import gdal, ogr, osr, gdalnumeric, gdalconst
        gdalOk = True
    except:
        gdalOk = False
        print('clidcarto-> Tampoco se ha podido cargar desde la carpeta osgeo')
        sys.exit(0)
ogr.RegisterAll()
# Enable GDAL/OGR exceptions
gdal.UseExceptions()

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
    print(f'clidcarto-> __name__:     <{__name__}>')
    print(f'clidcarto-> __package__ : <{__package__ }>')
# ==============================================================================

# Anulo esta importacion porque por el momento no las uso
# from cartolidar.clidax import clidaux
# La importacion de clidconfig (GLO) y clidnaux la pospongo a mas adelante
# from cartolidar.clidax import clidconfig
# from cartolidar.clidnb import clidnaux
# Hasta despues de leer el callingModuleInicial y verificar que no son:
#        'clidtwins', 'qlidtwins'


# ==============================================================================
class myClass(object):
    pass


# ==============================================================================
def showCallingModules(inspect_stack=inspect.stack(), verbose=False):
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
            print('\tclidcarto-> Error identificando el modulo 1')
            return 'desconocido1', 'desconocido1'
    else:
        print('\tclidcarto-> No hay modulos que identificar')
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
        print('\tclidcarto-> El modulo {} ({}) ha sido'.format(esteModuloName, esteModuloNum), end=' ')
    for llamada in inspect_stack[stackSiguiente:]:
        if 'cartolid' in llamada[1] or 'clid' in llamada[1] or 'qlid' in llamada[1]:
            callingModule = inspect.getmodulename(llamada[1])
            if callingModule != esteModuloName and callingModulePrevio == '':
                callingModulePrevio = callingModule
            callingModuleInicial = callingModule
            # if callingModule != 'clidaux' and callingModule != 'callingModule':
                # print('clidcarto-> llamado por', llamada[1:3], end=' ')
            if verbose:
                print('importado desde: {} ({})'.format(callingModule, llamada[2]), end='; ')
    if verbose:
        print()
    return callingModulePrevio, callingModuleInicial
# ==============================================================================

# ==============================================================================
CONFIGverbose = False
if CONFIGverbose:
    print('clidcarto-> Directorio desde el que se lanza la aplicacion-> os.getcwd():', os.getcwd())
    print('clidcarto-> Cargando clidaux; reviso la pila de llamadas')
callingModulePrevio, callingModuleInicial = showCallingModules(inspect_stack=inspect.stack(), verbose=CONFIGverbose)
if CONFIGverbose:
    print('clidcarto-> Pila de llamadas revisada-> callingModulePrevio:', callingModulePrevio, 'callingModuleInicial:', callingModuleInicial)

try:
    from cartolidar.clidax import clidconfig
except:
    if __verbose__ > 2:
        print(f'qlidtwins-> Se importan clidconfig desde clidcarto del directorio local {os.getcwd()}/clidtools')
        print('\tNo hay vesion de cartolidar instalada en site-packages.')
    from clidax import clidconfig

if (
    callingModuleInicial != 'runpy'
    and callingModuleInicial != '__init__'
    and callingModuleInicial != '__main__'
    and callingModuleInicial != 'clidtwins' and callingModuleInicial != 'qlidtwins'
    and callingModuleInicial != 'clidmerge' and callingModuleInicial != 'qlidmerge'
):
    try:
        from cartolidar.clidnb import clidnaux
    except:
        print('clidcarto-> ATENCION: error al cargar clidnaux desde clidcarto ')
        print('\t-> Modulo inicial: <{}>'.format(callingModuleInicial))
        print('\t-> Modificar el codigo para que no importe clidnaux')
        print('\t   cuando se llama desde este modulo inicial.')

# ==============================================================================
if (
    callingModuleInicial == 'runpy'
    or callingModuleInicial == '__init__'
    or callingModuleInicial == '__main__'
    or callingModuleInicial == 'clidtwins' or callingModuleInicial == 'qlidtwins'
    or callingModuleInicial == 'clidmerge' or callingModuleInicial == 'qlidmerge'
    or callingModuleInicial == 'clidgis'
):

    # print('clidcarto-> Modulo importado desde', os.getcwd(), 'No se cargan las variables globales de cartolid.xls')
    class Object(object):
        pass
    GLO = Object()
    GLO.MAINidProceso = 0
    GLO.GLBLverbose = False
    GLO.GLBLmetrosSubCelda = 2.0
    GLO.GLBLmetrosCelda = 10.0
    GLO.GLBLtileSizeMetros = 512
    GLO.GLBLtileSemiSolapeMetros = 6
    GLO.GLBLnoData = -9999
    GLO.GLBLnoData8bits = 255
    GLO.GLBLrasterPixelSize = 10
else:
    configVarsDict = clidconfig.leerCambiarVariablesGlobales()
    GLO = clidconfig.VariablesGlobales(configVarsDict)

if GLO.GLBLverbose:
    print('->->Cargando clidcarto')
    # clidaux.showCallingModules(inspect_stack=inspect.stack())

GLBNsubCeldasPorCelda = int(GLO.GLBLmetrosCelda / GLO.GLBLmetrosSubCelda)

if False:
    inputVectorDriverName = 'ESRI Shapefile'
    inputVectorDriverName = 'GPKG'
    drv = ogr.GetDriverByName( inputVectorDriverName )
    if drv is None:
        print('El driver {} esta disponible.'.format(inputVectorDriverName))
    else:
        print('Atencion: el driver {} NO esta disponible.'.format(inputVectorDriverName))
        sys.exit(0)
    quit()


# ==============================================================================
def crearASC(ascFileName, arrayGridData, imgShape, ncols, nRows, cellsize, xInfIzdaTile, yInfIzdaTile, nodata_value, nTipoDato=0):
    maxVal = arrayGridData.max()
    tipoVal = arrayGridData.dtype
    if (
        tipoVal == np.int8 or tipoVal == np.uint8
        or tipoVal == np.int16 or tipoVal == np.uint16
        or tipoVal == np.int32
        or tipoVal == np.int64
    ):
        if maxVal < 999:
            tipoDat = 'int1'
        else:
            tipoDat = 'int2'
    else:
        if maxVal < 9:
            tipoDat = 'float1'
        elif maxVal < 99:
            tipoDat = 'float2'
        else:
            tipoDat = 'float3'
    ascFile = open(ascFileName, mode='w+')
    ascFile.write('ncols %i \n' % ncols)
    ascFile.write('nrows %i \n' % nRows)
    ascFile.write('xllcenter %0.4f \n' % (xInfIzdaTile + (cellsize / 2)))
    ascFile.write('yllcenter %0.4f \n' % (yInfIzdaTile + (cellsize / 2)))
    ascFile.write('cellsize %0.4f \n' % cellsize)
    ascFile.write('nodata_value %i \n' % nodata_value)
    for nSubY in reversed(range(imgShape[1])):
        for nSubX in range(imgShape[0]):
            if nTipoDato == 1:
                ascFile.write('%i ' % arrayGridData[nSubX, nSubY])
            elif nTipoDato == 2:
                ascFile.write('%02i ' % arrayGridData[nSubX, nSubY])
            elif nTipoDato == 3:
                ascFile.write('%03i ' % arrayGridData[nSubX, nSubY])
            elif nTipoDato == 4:
                ascFile.write('%05i ' % arrayGridData[nSubX, nSubY])
            elif nTipoDato == 5:
                ascFile.write('%05.2f ' % arrayGridData[nSubX, nSubY])
            elif nTipoDato == 7:
                ascFile.write('%07.2f ' % arrayGridData[nSubX, nSubY])
            else:
                if tipoDat == 'int1':
                    ascFile.write('%03i ' % arrayGridData[nSubX, nSubY])
                elif tipoDat == 'int2':
                    ascFile.write('%06i ' % arrayGridData[nSubX, nSubY])
                elif tipoDat == 'float1':
                    ascFile.write('%06.3f ' % arrayGridData[nSubX, nSubY])
                elif tipoDat == 'float2':
                    ascFile.write('%06.2f ' % arrayGridData[nSubX, nSubY])
                elif tipoDat == 'float3':
                    ascFile.write('%07.1f ' % arrayGridData[nSubX, nSubY])
        ascFile.write('\n')
    ascFile.close()


# ==============================================================================
class CartoRefVector(object):
    """
    classdocs
    """

    # ooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo
    def __init__(
            self,
            myLasHead,
            myLasData,
            miRutaCartoRecortes,
            rutaCartoCompleta,
            inputVectorDriverName,
            nombreCampoLandUseCover,
            subDirCapaInputVector,
            nombreCapaInputVector,
            nombreCapaOutputRaster,
            tipoInfoRaster='',
            LCLhusoUTM=30,
            LCLverbose=False,
        ):
        self.myLasHead = myLasHead
        self.myLasData = myLasData
        self.miRutaCartoRecortes = miRutaCartoRecortes
        self.rutaCartoCompleta = rutaCartoCompleta
        self.inputVectorDriverName = inputVectorDriverName
        self.nombreCampoLandUseCover = nombreCampoLandUseCover
        self.subDirCapaInputVector = subDirCapaInputVector
        self.nombreCapaInputVector = nombreCapaInputVector
        self.nombreCapaOutputRaster = nombreCapaOutputRaster
        self.tipoInfoRaster = tipoInfoRaster
        self.LCLhusoUTM = LCLhusoUTM
        self.LCLverbose = LCLverbose

        # self.ySupIzdaDelLas = myLasHead.xSupIzdaDelNombre
        # self.ySupIzdaDelLas = myLasHead.ySupIzdaDelNombre
        # self.xSupIzdaDelLas = int(round(myLasHead.xSupIzdaFromLasHead, 0))
        # self.ySupIzdaDelLas = int(round(myLasHead.ySupIzdaFromLasHead, 0))
        self.xSupIzdaDelLas = myLasHead.xSupIzda
        self.ySupIzdaDelLas = myLasHead.ySupIzda

        self.noDataVectorRef = GLO.GLBLnoData
        self.usarVectorRef = 0

        self.vectorRefMinX, self.vectorRefMaxX = 0, 0
        self.vectorRefMinY, self.vectorRefMaxY = 0, 0
        self.vectorRefNumCeldasX, self.vectorRefNumCeldasY = 0, 0
        self.vectorRefOrigenX, self.vectorRefOrigenY = 0, 0
        self.vectorRefPixelX, self.vectorRefPixelY = 0, 0

        self.aCeldasVectorRecRasterizado = np.zeros(1 * 1, dtype=np.uint8).reshape(1, 1)

        self.chequearPuntosDeEjemplo = False

        self.miRasterRefOrigen = np.array([0, 0], dtype=np.float32)
        self.miRasterRefPixel = np.array([0, 0], dtype=np.float32)
        self.miRasterRefNumCeldas = np.array([0, 0], dtype=np.float32)
        self.miRasterRefCoordenadas = np.array([0, 0, 0, 0], dtype=np.float32)

        self.numTilesGenerados = 0

        self.aCeldasLandUseCover = np.zeros(self.myLasData.nCeldasX * self.myLasData.nCeldasY, dtype=np.uint8).reshape(
            self.myLasData.nCeldasX, self.myLasData.nCeldasY
        )


    # ooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo
    def leerArraysGuardadasVuelta01_cartoRefVector(self, npzFileNameArraysVuelta0a1, LCLverbose=False):
        self.LCLverbose = LCLverbose
        if GLO.GLBLverbose or self.LCLverbose:
            print('\t-> clidndat-> Leyendo npz:', npzFileNameArraysVuelta0a1)
        if os.path.exists(npzFileNameArraysVuelta0a1):
            try:
                npzArraysVuelta01 = np.load(npzFileNameArraysVuelta0a1, allow_pickle=True)
                if GLO.GLBLverbose or self.LCLverbose:
                    print('\tLista de arrays guardadas en npz:')
                for nArray in range(len(npzArraysVuelta01.files)):
                    npzArrayName = npzArraysVuelta01.files[nArray]
                    npzArrayData = npzArraysVuelta01[npzArrayName]
                    if GLO.GLBLverbose or self.LCLverbose:
                        try:
                            if npzArrayData.shape[0] < 10:
                                print('\t-> Array:', npzArrayName, '-> shape:', npzArrayData.shape, '-> dtype:', npzArrayData.dtype, 'Valores:', npzArrayData)
                            else:
                                print('\t-> Array:', npzArrayName, '-> shape:', npzArrayData.shape, '-> dtype:', npzArrayData.dtype)
                        except:
                            print('\t-> Variable:', npzArrayName, 'Valor:', npzArrayData)
                    if npzArrayData.shape == (): # ndim = 0
                        setattr(self, npzArrayName, npzArrayData.item())
                        if GLO.GLBLverbose or self.LCLverbose:
                            print('\t\t-> Valor asignado:', getattr(self, npzArrayName), type(getattr(self, npzArrayName)))
                    else:
                        setattr(self, npzArrayName, npzArrayData)
                        if GLO.GLBLverbose or self.LCLverbose:
                            try:
                                if npzArrayData.shape[0] < 10:
                                    print('\t\t-> Array asignada:', type(getattr(self, npzArrayName)), getattr(self, npzArrayName))
                                else:
                                    print('\t\t-> Array asignada:', type(getattr(self, npzArrayName)))
                            except:
                                print('\t\t-> Valor asignado:', type(getattr(self, npzArrayName)), getattr(self, npzArrayName))
                self.leidoNpzVuelta0a1 = True
            except:
                print('clidcarto-> Aviso: error intentando leer {}'.format(npzFileNameArraysVuelta0a1))
                print('\t-> Es probable que el fichero este corrupto por producirse una interrupcion mientras se generaba')
                print('\t-> Se intenta borrar ese fichero:')
                try:
                    os.remove(npzFileNameArraysVuelta0a1)
                    print('\t\t-> Fichero npz borrado ok.')
                except:
                    print('\t\t-> Aviso: no se ha podido borrar el Fichero npz.')
                self.leidoNpzVuelta0a1 = False
        else:
            print('\tAviso: no se encuentra el npz:', npzFileNameArraysVuelta0a1)
            self.leidoNpzVuelta0a1 = False


    # ooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo
    def guardarArraysTrasVuelta01_cartoRefVector(self, npzFileNameArraysVuelta0a1_cartoRef):
        print('\tclidcarto-> Guardando cartoRef {}. ->usarVectorRef: {}'.format(
            npzFileNameArraysVuelta0a1_cartoRef, self.usarVectorRef
            )
        )
        np.savez_compressed(
            npzFileNameArraysVuelta0a1_cartoRef,
            subDirCapaInputVector=self.subDirCapaInputVector,
            nombreCapaInputVector=self.nombreCapaInputVector,
            usarVectorRef=self.usarVectorRef,
            aCeldasLandUseCover = self.aCeldasLandUseCover,
            numTilesGenerados = self.numTilesGenerados,
            cartoRefRecortadaOrigenX = self.cartoRefRecortadaOrigenX,
            cartoRefRecortadaOrigenY = self.cartoRefRecortadaOrigenY,
            cartoRefRecortadaPixelX = self.cartoRefRecortadaPixelX,
            cartoRefRecortadaPixelY = self.cartoRefRecortadaPixelY,
            cartoRefRecortadaNumCeldasX = self.cartoRefRecortadaNumCeldasX,
            cartoRefRecortadaNumCeldasY = self.cartoRefRecortadaNumCeldasY,
            cartoRefRecortadaMinX = self.cartoRefRecortadaMinX,
            cartoRefRecortadaMaxX = self.cartoRefRecortadaMaxX,
            cartoRefRecortadaMinY = self.cartoRefRecortadaMinY,
            cartoRefRecortadaMaxY = self.cartoRefRecortadaMaxY,
            miRasterRefMinXY = self.miRasterRefMinXY,
            miRasterRefOrigen = self.miRasterRefOrigen,
            miRasterRefPixel = self.miRasterRefPixel,
            miRasterRefNumCeldas = self.miRasterRefNumCeldas,
            miRasterRefCoordenadas = self.miRasterRefCoordenadas,
            noDataRasterRef = self.noDataRasterRef,
            aCeldasVectorRecRasterizado = self.aCeldasVectorRecRasterizado,
            nPixelsPorCelda = self.nPixelsPorCelda,
        )


    # ooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo
    def leerElRasterYaRecortado(self):
        targetRasterFileName = os.path.join(self.miRutaCartoRecortes, '{}.tif'.format(self.nombreCapaOutputRaster))
        try:
            targetRasterDataset = gdal.Open(targetRasterFileName, gdalconst.GA_ReadOnly)
            if targetRasterDataset is None:
                print('\tclidcarto-> Error abriendo raster', targetRasterFileName)
                return False
            # print('\tclidcarto-> Capa leida ok:', targetRasterFileName)
    
            geotransform = targetRasterDataset.GetGeoTransform()
            self.cartoRefRecortadaOrigenX = geotransform[0]
            self.cartoRefRecortadaOrigenY = geotransform[3]
            self.cartoRefRecortadaPixelX = geotransform[1]
            self.cartoRefRecortadaPixelY = geotransform[5]
            self.cartoRefRecortadaNumCeldasX = targetRasterDataset.RasterXSize
            self.cartoRefRecortadaNumCeldasY = targetRasterDataset.RasterYSize
    
            self.cartoRefRecortadaMinX = self.cartoRefRecortadaOrigenX
            self.cartoRefRecortadaMaxX = self.cartoRefRecortadaOrigenX + (self.cartoRefRecortadaNumCeldasX * self.cartoRefRecortadaPixelX)
            self.cartoRefRecortadaMinY = self.cartoRefRecortadaOrigenY + (self.cartoRefRecortadaNumCeldasY * self.cartoRefRecortadaPixelY)
            self.cartoRefRecortadaMaxY = self.cartoRefRecortadaOrigenY
    
            self.miRasterRefMinXY = np.array([self.cartoRefRecortadaMinX, self.cartoRefRecortadaMinY], dtype=np.float32)
            self.miRasterRefOrigen = np.array([self.cartoRefRecortadaOrigenX, self.cartoRefRecortadaOrigenY], dtype=np.float32)
            self.miRasterRefPixel = np.array([self.cartoRefRecortadaPixelX, self.cartoRefRecortadaPixelY], dtype=np.float32)
            self.miRasterRefNumCeldas = np.array([self.cartoRefRecortadaNumCeldasX, self.cartoRefRecortadaNumCeldasY], dtype=np.int32)
            self.miRasterRefCoordenadas = np.array(
                [self.cartoRefRecortadaMinX, self.cartoRefRecortadaMaxX, self.cartoRefRecortadaMinY, self.cartoRefRecortadaMaxY], dtype=np.float32
            )
    
            #         imagenCompleta = True
            #         nBandas = 0
            #         infoTargetRasterDataset = infoRasterDataset( sourceRasterDataset, mostrar=True)
            #         #origenX_Imagen = infoTargetRasterDataset['origenX']
            #         #origenY_Imagen = infoTargetRasterDataset['origenY']
            #         pixelX = infoTargetRasterDataset['pixelX']
            #         pixelY = infoTargetRasterDataset['pixelY']
            #         nCeldasX = infoTargetRasterDataset['nPixelsX']
            #         nCeldasY = infoTargetRasterDataset['nPixelsY']
            #         if nBandas == 0:
            #             nBandas = infoTargetRasterDataset['nBandas']
    
            nBand = 0
            srcBandTargetRasterRec = targetRasterDataset.GetRasterBand(nBand + 1)
            self.noDataRasterRef = self.noDataVectorRef
            srcBandTargetRasterRec.SetNoDataValue(self.noDataRasterRef)
            srcBandTargetRasterRec.FlushCache()
            # Ocasionalmente esta linea me ha dado error, puede deberse a que el fichero tif este corrupto:
            self.aCeldasVectorRecRasterizado = srcBandTargetRasterRec.ReadAsArray()[::-1].transpose()
    
            #         #stats1, stats2, ctable = infoSrcband(srcBandTargetRasterRec, True, False)
            #         xOffRaster, yOffRaster = 0, 0
            #         nCeldasX_Intersec = self.cartoRefRecortadaNumCeldasX
            #         nCeldasY_Intersec = self.cartoRefRecortadaNumCeldasY
            #         verbose = True
            #         srcBandAsArrayInt, noData = infoSrcbandAsArray(srcBandTargetRasterRec,
            #                                                        xOffRaster, yOffRaster,
            #                                                        nCeldasX_Intersec, nCeldasY_Intersec,
            #                                                        verbose, self.tipoInfoRaster)
            #         self.aCeldasVectorRecRasterizado = srcBandAsArrayInt[::-1].transpose()
            #         self.aCeldasRasterRef = self.aCeldasVectorRecRasterizado
            #         self.noDataRasterRef = 0 if noData is None else noData
    
    
            if (
                self.cartoRefRecortadaMinX == self.xminBloqueH30
                and self.cartoRefRecortadaMaxX == self.xmaxBloqueH30
                and self.cartoRefRecortadaMinY == self.yminBloqueH30
                and self.cartoRefRecortadaMaxY == self.ymaxBloqueH30
            ):

                # ATENCION:
                # Revisar la idea de recorrer cada celda, su lote de pixeles,
                # porque lo logico es recorrer los pixeles del raster, con independencia de las celda
                self.nPixelsPorCelda = GLO.GLBLmetrosCelda / GLO.GLBLrasterPixelSize
                self.nPixelsXRaster = int((self.xmaxBloqueH30 - self.xminBloqueH30) / GLO.GLBLrasterPixelSize)
                self.nPixelsYRaster = int((self.ymaxBloqueH30 - self.yminBloqueH30) / GLO.GLBLrasterPixelSize)
                if (
                    self.cartoRefRecortadaNumCeldasX / self.myLasData.nCeldasX != self.nPixelsPorCelda
                    or self.cartoRefRecortadaNumCeldasY / self.myLasData.nCeldasY != self.nPixelsPorCelda
                ):
                    print('clidcarto-> ATENCION: no sale una de estas cuentas:')
                    print('\tcartoRefRecortadaNumCeldasX: {} / nCeldasX {}  != self.nPixelsPorCelda {}'.format(
                        self.cartoRefRecortadaNumCeldasX,
                        self.myLasData.nCeldasX,
                        self.nPixelsPorCelda,
                        )
                    )
                    print('\tcartoRefRecortadaNumCeldasY: {} / nCeldasY {}  != self.nPixelsPorCelda {}'.format(
                        self.cartoRefRecortadaNumCeldasY,
                        self.myLasData.nCeldasY,
                        self.nPixelsPorCelda,
                        )
                    )
                if self.cartoRefRecortadaPixelX != GLO.GLBLrasterPixelSize or self.cartoRefRecortadaPixelY != -GLO.GLBLrasterPixelSize:
                    print('clidcarto-> ATENCION: revisar metros pixel', self.cartoRefRecortadaPixelX, GLO.GLBLrasterPixelSize)
                self.vectorRasterizadoCongruenteLidar = True
            else:
                print('clidcarto-> La cartoRef no cubre todo el ambito del Lidar y/o el ambito del fichero lidar no cubre todo el bloque')
                self.vectorRasterizadoCongruenteLidar = False
        except:
            print('clidcarto-> ATENCION: error al leer o procesar {}. Se intenta borrar el fichero:'.format(targetRasterFileName))
            print('\t-> Es probable que el fichero este corrupto por producirse una interrupcion mientras se generaba')
            try:
                os.remove(targetRasterFileName)
                print('\t\t-> Fichero tif borrado ok.')
            except:
                print('\t\t-> Aviso: no se ha podido borrar el fichero tif.')
            return False
        return True


    # ooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo
    def leerVector(self):
        if GLO.GLBLverbose:
            print('\tclidcarto-> Leyendo vector file {}'.format(self.nombreCapaInputVector))
        # if GLO.GLBLverbose > 1:
        #     print(f'\t\t-> inputVectorDriverName: {self.inputVectorDriverName}')
        # inDriver = 'PostgreSQL'
        if self.inputVectorDriverName == 'ESRI Shapefile':
            driverExt = 'shp'
        elif self.inputVectorDriverName == 'GPKG':
            driverExt = 'gpkg'
        nombreConPathCapaInputVector = os.path.join(
            self.rutaCartoCompleta,
            self.subDirCapaInputVector,
            '{}.{}'.format(self.nombreCapaInputVector, driverExt)
        )
        if not gdalOk:
            print('\tclidcarto-> Gdal no disponible; no se puede leer %s' % (nombreConPathCapaInputVector))
            self.usarVectorRef = 0
            self.inputVectorRefLayer = None
            return
        if not os.path.exists(nombreConPathCapaInputVector):
            print('\tclidcarto-> no esta disponible el fichero %s' % (nombreConPathCapaInputVector))
            self.usarVectorRef = 0
            self.inputVectorRefLayer = None
            return
        inputVectorRefOgrDriver = ogr.GetDriverByName(self.inputVectorDriverName)
#         if inputVectorRefOgrDriver is None:
#             print('El driver {} esta disponible.'.format(self.inputVectorDriverName))
#         else:
#             print('Atencion: el driver {} NO esta disponible.'.format(self.inputVectorDriverName))
#         print( 'clidcarto-> inputVectorRefOgrDriver->', inputVectorRefOgrDriver)
 
        try:
            self.inputVectorRefDataSource = inputVectorRefOgrDriver.Open(nombreConPathCapaInputVector, 0)  # 0 means read-only. 1 means writeable.
        except:
            print('\tclidcarto-> No se puede abrir {}-> revisar si esta corrupto, faltan ficheros o esta bloqueado'.format(nombreConPathCapaInputVector))
            quit()
        if self.inputVectorRefDataSource is None:
            print('\tclidcarto-> No se puede abrir {}: possible corrupto'.format(nombreConPathCapaInputVector))
            self.usarVectorRef = 0
            self.inputVectorRefLayer = None
            return
        else:
            self.usarVectorRef = 1
        self.inputVectorRefLayer = self.inputVectorRefDataSource.GetLayer()
        self.inputVectorRefFeatureCount = self.inputVectorRefLayer.GetFeatureCount()
        (
            self.inputVectorXmin,
            self.inputVectorXmax,
            self.inputVectorYmin,
            self.inputVectorYmax,
        ) = self.inputVectorRefLayer.GetExtent()
        if GLO.GLBLverbose or self.LCLverbose:
            print('clidcarto-> usarVectorRef: {}; Numero de registros en {}: {}'.format(self.usarVectorRef, os.path.basename(nombreConPathCapaInputVector), self.inputVectorRefFeatureCount))
        # wkt = "POLYGON ((494000 4606000, 496000 4606000, 496000 4604000, 494000 4604000, 494000 4606000))"
        # wkt = 'POLYGON ((%i %i, %i %i, %i %i, %i %i, %i %i))' % (self.myLasHead.xmin, self.myLasHead.ymin,
        #                                                         self.myLasHead.xmin, self.myLasHead.ymax,
        #                                                         self.myLasHead.xmax, self.myLasHead.ymax,
        #                                                         self.myLasHead.xmax, self.myLasHead.ymin,
        #                                                         self.myLasHead.xmin, self.myLasHead.ymin)
        # miPoligono = ogr.CreateGeometryFromWkt(wkt5)
        # self.inputVectorRefLayer.SetSpatialFilter(miPoligono)
        # miFiltro = self.inputVectorRefLayer.GetSpatialFilter()


    # ooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo
    def recortarVector(
            self,
            forzarRecorteCuadrado=True,
        ):
        tiempo0 = time.time()
        guardarVector = True
        if guardarVector:
            outputVectorDriverName = 'ESRI Shapefile'
            outputVectorRecFileName = os.path.join(
                self.miRutaCartoRecortes, '{}_recortada_id{}.shp'.format(
                    self.nombreCapaInputVector, GLO.MAINidProceso
                )
            )
            outputVectorRecLayerName = self.nombreCapaInputVector
            print('\tclidcarto-> outputVectorRecFileName', outputVectorRecFileName)
            # print('\tclidcarto-> outputVectorRecLayerName', outputVectorRecLayerName)
        else:
            outputVectorDriverName = 'Memory'
            outputVectorRecFileName = '{}DataFrameInMemory{}'.format(
                self.nombreCapaInputVector, GLO.MAINidProceso
            )
            outputVectorRecLayerName = self.nombreCapaInputVector + 'layerInMemory'
        if not gdalOk:
            print('clidcarto-> Gdal no disponible; no se puede generar %s: ' % (outputVectorDriverName))
            self.usarVectorRef = 0
            return
        self.inputVectorRefSRS = self.inputVectorRefLayer.GetSpatialRef()
        self.inputVectorRefWkt = self.inputVectorRefSRS.ExportToWkt()
        # self.inputVectorRefSRS = osr.SpatialReference(wkt = inputVectorRefWkt) #Reciproco de inputVectorRefSRS.ExportToWkt()
        print('\tclidcarto-> Revisando srs: self.inputVectorRefWkt:', self.inputVectorRefWkt)

        if self.LCLhusoUTM != 30:
            self.xminBloqueH30 = self.myLasHead.xminBloqueH30
            self.yminBloqueH30 = self.myLasHead.yminBloqueH30
            self.xmaxBloqueH30 = self.myLasHead.xmaxBloqueH30
            self.ymaxBloqueH30 = self.myLasHead.ymaxBloqueH30
        else:
            self.xminBloqueH30 = self.myLasHead.xmin
            self.yminBloqueH30 = self.myLasHead.ymin
            self.xmaxBloqueH30 = self.myLasHead.xmax
            self.ymaxBloqueH30 = self.myLasHead.ymax

        pixelRational = (float(abs(GLO.GLBLrasterPixelSize))).as_integer_ratio()
        if pixelRational[1] == 1:
            # Numero entero
            metrosPorPixel = int(abs(GLO.GLBLrasterPixelSize))
            pixelsPorMetro = 1
        elif float(1 / abs(GLO.GLBLrasterPixelSize)).is_integer():
            # Fraccion entera de 1 m
            metrosPorPixel = 1
            pixelsPorMetro = int(1 / abs(GLO.GLBLrasterPixelSize))
        elif pixelRational[1] < 10:
            # Numero fraccionario racional
            metrosPorPixel = pixelRational[0]
            pixelsPorMetro = pixelRational[1]
        else:
            metrosPorPixel = -1
            pixelsPorMetro = -1

        if self.LCLhusoUTM != 30:
            print(f'\ncartolider-> Ajustando la ventana del bloque Lidar a los pixeles del raster de referencia para que contenga integramente al bloque:')
            print(f'\t-> Previamente se abre la primera ortofoto, solo para conocer la dimension del pixel y hacer este ajuste antes de las intersecciones')
            print(f'\t\t-> Dimension del pixel -> cartoRefRecortadaPixelX: {GLO.GLBLrasterPixelSize}; cartoRefRecortadaPixelY: {GLO.GLBLrasterPixelSize}')
            print(f'\t\t-> metrosPorPixel/pixelsPorMetro: {metrosPorPixel}/{pixelsPorMetro}')
            print(f'\t-> Antes del ajuste:')
            print(f'\t\t-> xminBloqueH30: {self.xminBloqueH30}; xmaxBloqueH30: {self.xmaxBloqueH30}')
            print(f'\t\t-> yminBloqueH30: {self.yminBloqueH30}; ymaxBloqueH30: {self.ymaxBloqueH30}')
        if pixelsPorMetro != -1 and metrosPorPixel != -1:
            self.xminBloqueH30 = (metrosPorPixel / pixelsPorMetro) * math.floor(self.xminBloqueH30 * (pixelsPorMetro / metrosPorPixel))
            self.xmaxBloqueH30 = (metrosPorPixel / pixelsPorMetro) * math.ceil(self.xmaxBloqueH30 * (pixelsPorMetro / metrosPorPixel))
            self.yminBloqueH30 = (metrosPorPixel / pixelsPorMetro) * math.floor(self.yminBloqueH30 * (pixelsPorMetro / metrosPorPixel))
            self.ymaxBloqueH30 = (metrosPorPixel / pixelsPorMetro) * math.ceil(self.ymaxBloqueH30 * (pixelsPorMetro / metrosPorPixel))
            if forzarRecorteCuadrado:
                if (self.ymaxBloqueH30 - self.yminBloqueH30) > (self.xmaxBloqueH30 - self.xminBloqueH30):
                    self.xmaxBloqueH30 = self.xminBloqueH30 + (self.ymaxBloqueH30 - self.yminBloqueH30)
                if (self.xmaxBloqueH30 - self.xminBloqueH30) > (self.ymaxBloqueH30 - self.yminBloqueH30):
                    self.ymaxBloqueH30 = self.yminBloqueH30 + (self.xmaxBloqueH30 - self.xminBloqueH30)
        if self.LCLhusoUTM == 29:
            print(f'\t-> Despues del ajuste:')
            print(f'\t\t-> xminBloqueH30: {self.xminBloqueH30}; xmaxBloqueH30: {self.xmaxBloqueH30}')
            print(f'\t\t-> yminBloqueH30: {self.yminBloqueH30}; ymaxBloqueH30: {self.ymaxBloqueH30}')

        # Filter (select) features that intersect my las block
        self.inputVectorRefLayer.SetSpatialFilterRect(
            self.xminBloqueH30,
            self.yminBloqueH30,
            self.xmaxBloqueH30,
            self.ymaxBloqueH30,
        )

        self.nPixelsPorCelda = GLO.GLBLmetrosCelda / GLO.GLBLrasterPixelSize
        self.nPixelsXRaster = int((self.xmaxBloqueH30 - self.xminBloqueH30) / GLO.GLBLrasterPixelSize)
        self.nPixelsYRaster = int((self.ymaxBloqueH30 - self.yminBloqueH30) / GLO.GLBLrasterPixelSize)

        if GLO.GLBLverbose:
            print('\tclidcarto-> Creando capa vectorial:', outputVectorRecFileName, 'layer:', outputVectorRecLayerName)
        # Create a vectorDataSet in memory for the selected features
        outputOgrDriver = ogr.GetDriverByName(outputVectorDriverName)
        # Remove output shapefile if it already exists
        if outputVectorDriverName == 'ESRI Shapefile' and os.path.exists(outputVectorRecFileName):
            outputOgrDriver.DeleteDataSource(outputVectorRecFileName)
        self.outputVectorRecDataSource = outputOgrDriver.CreateDataSource(outputVectorRecFileName)
        #         print( 'clidcarto-> outputOgrDriver', outputOgrDriver)
        #         print( 'clidcarto-> outputVectorRecFileName', outputVectorRecFileName)
        #         print( 'clidcarto-> self.outputVectorRecDataSource', self.outputVectorRecDataSource)
        numIntentosEscritura = 0
        while True:
            numIntentosEscritura += 1
            try:
                self.inputVectorRefLayerRec = self.outputVectorRecDataSource.CreateLayer(
                    outputVectorRecLayerName, srs=self.inputVectorRefSRS, geom_type=ogr.wkbPolygon
                )
                break
            except:
                print(
                    'clidcarto-> No se puede borrar o escribir {} -> Se reintenta despues de 5 segundos ({} de 5).'.format(
                        outputVectorRecFileName, numIntentosEscritura
                    )
                )
                time.sleep(5)
                if numIntentosEscritura > 5:
                    break

        # Add an ID field
        # idField = ogr.FieldDefn("id", ogr.OFTInteger)
        # self.inputVectorRefLayerRec.CreateField(idField)
        landUseCoverField = ogr.FieldDefn(self.nombreCampoLandUseCover, ogr.OFTInteger)
        landUseCoverField.SetWidth(3)
        landUseCoverField.SetPrecision(0)
        #         FID_UsosSiField = ogr.FieldDefn("FID_UsosSi", ogr.OFTString)
        #         FID_UsosSiField.SetWidth(6)
        #         FID_UsosSiField.SetPrecision(0)

        self.inputVectorRefLayerRec.CreateField(landUseCoverField)
        #         self.inputVectorRefLayerRec.CreateField(FID_UsosSiField)
        # Create the feature and set values
        featureDefn = self.inputVectorRefLayerRec.GetLayerDefn()
        featureNew = ogr.Feature(featureDefn)
        # print( '\tclidcarto-> Mostrando features copiadas')
        nFeature = 0
        for feature in self.inputVectorRefLayer:
            geom = feature.GetGeometryRef()
            try:
                landUseCoverValue = feature.GetField(self.nombreCampoLandUseCover)
                # FID_UsosSi = feature.GetField("FID_UsosSi")
                nFeature += 1
                # print( '\tclidcarto-> nFeature', nFeature, FID_UsosSi, landUseCoverValue)
                # print( '\tclidcarto-> nFeature', nFeature, landUseCoverValue)
            except:
                print('\tclidcarto-> nFeature', nFeature, 'ERROR')
                landUseCoverValue = 0
                # FID_UsosSi = ''
            featureNew.SetGeometry(geom)
            featureNew.SetField(self.nombreCampoLandUseCover, landUseCoverValue)
            # featureNew.SetField("FID_UsosSi", FID_UsosSi)
            self.inputVectorRefLayerRec.CreateFeature(featureNew)

        self.outputVectorRecLayer_featureCount = self.inputVectorRefLayerRec.GetFeatureCount()
        if GLO.GLBLverbose:
            tiempo1 = time.time()
            print(
                '\tclidcarto-> recortarVector - Number of features in %s: %d' % (os.path.basename(outputVectorRecFileName), self.outputVectorRecLayer_featureCount)
            )
            print('\tclidcarto-> Tiempo para recortar capa: %0.1f segundos' % (tiempo1 - tiempo0))

        if self.chequearPuntosDeEjemplo:
            aNumPuntosPorClase = np.zeros(256, dtype=np.int16)
            aTiposDeNucleoUrbano = [
                'No es nucleo',
                'Nucleo Urbano INE',
                'Nucleo Urbano JCyL',
                'Nucleo Bodegas JCyL',
                'Espacio Comercial',
                'Deportivo y Ocio',
                'Area Industrial',
                'Areas Militares y Centros Penitenciarios',
                'Cementerio',
                'Diseminados JCyL',
                'Despoblado JCyL',
            ]
            nPuntosMuestreo = 40
            print(f'clidcarto-> Muestreo {nPuntosMuestreo} x {nPuntosMuestreo} vector:', end='')
            for nPuntoY in range(nPuntosMuestreo):
                print('\nclidcarto-> ', '%02i' % nPuntoY, end='->')
                for nPuntoX in range(40):
                    miPuntoX = self.xminBloqueH30 + 605 + (nPuntoX * 5)
                    miPuntoY = self.yminBloqueH30 + 305 + (nPuntoY * 5)
                    wkt = 'POINT (%i %i)' % (miPuntoX, miPuntoY)
                    miPunto = ogr.CreateGeometryFromWkt(wkt)
                    # print("Punto creado desde WKT: %d,%d" % (miPunto.GetX(), miPunto.GetY()))
                    self.inputVectorRefLayerRec.SetSpatialFilter(miPunto)
                    numPoligonos = self.inputVectorRefLayerRec.GetFeatureCount()

                    if numPoligonos == 0:
                        print('0', end='')
                    elif numPoligonos > 1:
                        print('clidcarto-> Numero de poligonos en el punto (%i, %i): %i' % (miPuntoX, miPuntoY, numPoligonos))

                    landCover = 0
                    for feature in self.inputVectorRefLayerRec:
                        try:
                            landCover = feature.GetField(self.nombreCampoLandUseCover)
                            print(landCover, end='')
                        except:
                            print('!', end='')
                            landCover = 0
                        aNumPuntosPorClase[landCover] += 1
            #                     if nPuntoX == 12 and nPuntoY == 12:
            #                         print( 'clidcarto-> nPuntoXY', nPuntoX, nPuntoY, 'miPuntoXY', miPuntoX, miPuntoY, 'miPunto', miPunto)
            #                         print('        landCover:', landCover)
            if GLO.GLBLverbose:
                print()
                if self.nombreCapaInputVector == 'IGR0204NUC_URB_CYL_S_E25':
                    for nClase in range(len(aTiposDeNucleoUrbano)):
                        if aNumPuntosPorClase[nClase] > 0:
                            print(
                                'clidcarto-> Leyendo vector: numero de puntos clasCob %i (%s): %i de 100'
                                % (nClase, aTiposDeNucleoUrbano[nClase], aNumPuntosPorClase[nClase])
                            )
                elif self.nombreCapaInputVector == 'SingularUse' or self.nombreCapaInputVector.strartswith('BTN25'):
                    print('clidcarto-> Numero de puntos clasCob 1 (edificio):    %i de 100' % aNumPuntosPorClase[1])
                    print('clidcarto-> Numero de puntos clasCob 2 (via):         %i de 100' % aNumPuntosPorClase[2])
                    print('clidcarto-> Numero de puntos clasCob 3 (ferrocarril): %i de 100' % aNumPuntosPorClase[3])
                    print('clidcarto-> Numero de puntos clasCob 4 (agua):        %i de 100' % aNumPuntosPorClase[4])

            if GLO.GLBLverbose:
                tiempo2 = time.time()
                print('clidcarto-> Tiempo para leer 100 puntos en el vector: %0.2f mili-segundos' % ((tiempo2 - tiempo1) * 1e3))

        self.inputVectorRefLayer.SetSpatialFilter(None)
        self.inputVectorRefLayerRec.SetSpatialFilter(None)


    # ooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo
    def rasterizarVectorRecortado(self):
        if not gdalOk:
            print('clidcarto-> Gdal no disponible; no se puede crear %s: ' % (self.nombreCapaOutputRaster + '.tif'))
            self.usarVectorRef = 0
            return False

        if GLO.GLBLverbose:
            tiempo0 = time.time()
            print('\tclidcarto-> Preparando nuevo raster...', end=' -> ')
        # print( 'clidcarto-> ->->->GLBLrasterPixelSize', GLO.GLBLrasterPixelSize)
        # Filename of the raster Tiff that will be created
        targetRasterFileName = os.path.join(self.miRutaCartoRecortes, '{}.tif'.format(self.nombreCapaOutputRaster))
        # vectorDataset = ogr.GetDriverByName("Memory").CopyDataSource(vectorFile, "")

        # self.inputVectorRefSRS = self.inputVectorRefLayerRec.GetSpatialRef()
        # Coordenadas del vector recortado
        # x_min, x_max, y_min, y_max = self.inputVectorRefLayerRec.GetExtent()
        # Coordenadas del rectangulo que contiene al fichero lidar
        x_min, x_max = self.xminBloqueH30, self.xmaxBloqueH30
        y_min, y_max = self.yminBloqueH30, self.ymaxBloqueH30

        # field_def = ogr.FieldDefn(self.nombreCampoLandUseCover, ogr.OFTReal)
        # self.inputVectorRefLayerRec.CreateField(field_def)
        # outputVectorRecLayer_def = self.inputVectorRefLayerRec.GetLayerDefn()
        # fieldIndexColor = outputVectorRecLayer_def.GetFieldIndex(self.nombreCampoLandUseCover)

        nPixelesXraster = int((x_max - x_min) / GLO.GLBLrasterPixelSize)
        nPixelesYraster = int((y_max - y_min) / GLO.GLBLrasterPixelSize)
        if nPixelesXraster == 0 or nPixelesYraster == 0:
            print(
                'clidcarto-> La capa %s no tiene poligonos en el bloque %i-%i, %i-%i'
                % (self.nombreCapaInputVector, self.xminBloqueH30, self.xmaxBloqueH30, self.yminBloqueH30, self.ymaxBloqueH30)
            )
            self.usarVectorRef = 0
            return False
        if GLO.GLBLverbose or True:
            print('\t-> nPixelesXraster (X x Y): {} x {}'.format(nPixelesXraster, nPixelesYraster))
        targetBands = 1
        targetDatatype = gdal.GDT_Byte
        driver = gdal.GetDriverByName('GTiff')
        # targetOptions = ['COMPRESS=LZW']
        # targetOptions = None
        # targetRasterDataset = driver.Create(targetRasterFileName, nPixelesXraster,nPixelesYraster,
        #                                    targetBands, targetDatatype, targetOptions)
        nIntentosEscritura = 0
        while True:
            nIntentosEscritura += 1
            try:
                targetRasterDataset = driver.Create(
                    targetRasterFileName,
                    nPixelesXraster,
                    nPixelesYraster,
                    targetBands,
                    targetDatatype
                )
                targetRasterDataset.SetGeoTransform(
                    (
                        x_min,
                        GLO.GLBLrasterPixelSize,
                        0,
                        y_max,
                        0,
                        -GLO.GLBLrasterPixelSize,
                    )
                )
                break
            except:
                if nIntentosEscritura > 5:
                    print('\nclidcarto.{:006}-> ATENCION!!!: No se ha podido crear crear {}'.format(GLO.MAINidProceso, targetRasterFileName))
                    return False
                print('\nclidcarto.{:006}-> ATENCION: error al crear {}'.format(GLO.MAINidProceso, targetRasterFileName))
                time.sleep(5)

        try:
            if GLO.GLBLverbose:
                print('\tclidcarto-> targetRasterDataset.SetGeoTransform', x_min, y_max)
            # Pendiente revisar si esto es cierto para mi capa, que esta proyectada:
            # Si quisiera importar directamente la proyeccion de la capa vectorial:
            # targetRasterDataset.SetProjection(self.inputVectorRefSRS.ExportToWkt())
            # Pero de esta forma se importa el geoide pero no la proyeccion (UTM 30)
            # Por eso creo una Spatial Reference para el raster:
    
            if self.inputVectorRefSRS:
                # Utilizo el SRS de la capa vectorial:
                # PROJCS["ETRS89 / UTM zone 30N",GEOGCS["ETRS89",DATUM["European_Terrestrial_Reference_System_1989",SPHEROID["GRS 1980",6378137,298.257222101,AUTHORITY["EPSG","7019"]],TOWGS84[0,0,0,0,0,0,0],AUTHORITY["EPSG","6258"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4258"]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",-3],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AXIS["Easting",EAST],AXIS["Northing",NORTH],AUTHORITY["EPSG","25830"]]
                # print( 'clidcarto-> ->SRS de la capa vectorial:', self.inputVectorRefSRS.ExportToWkt())
                # print( 'clidcarto-> Unidad:', self.inputVectorRefSRS.GetAttrValue('UNIT'))
                targetRasterDataset.SetProjection(self.inputVectorRefSRS.ExportToWkt())
            else:
                print('clidcarto-> La capa de entrada no tiene info de proyeccion (needs GDAL >= 1.7.0). Se selecciona EPSG 25830', end=' -> ')
                miRasterSRS = osr.SpatialReference()
                # miRasterSRS.SetUTM(30, True)
                # miRasterSRS.SetWellKnownGeogCS( 'EPSG:25830' ) #ETRS89 30N -> No funciona
                # miRasterSRS.SetWellKnownGeogCS( "WGS84" ) #->ok
                miRasterSRS.ImportFromEPSG(25830)  # ->ok
                # print( 'clidcarto-> ->SRS creado por mi:       ', miRasterSRS.ExportToWkt())
                # print( 'clidcarto-> Unidad:', miRasterSRS.GetAttrValue('UNIT'))
                targetRasterDataset.SetProjection(miRasterSRS.ExportToWkt())
    
            # miWkt = targetRasterDataset.GetProjection()
            # targetRasterSRS = osr.SpatialReference(wkt = miWkt) #->self.inputVectorRefSRS o miRasterSRS
            # print( 'clidcarto-> ->->SRS del raster creado: ', miWkt)
            # print( 'clidcarto-> Unidad:', targetRasterSRS.GetAttrValue('UNIT'))
    
            outputRasterRecBandLandCover = targetRasterDataset.GetRasterBand(1)
            outputRasterRecBandLandCover.SetNoDataValue(self.noDataVectorRef)
            outputRasterRecBandLandCover.FlushCache()

            if GLO.GLBLverbose:
                print('\tclidcarto-> Rasterizing...', end=' -> ')
            # Si creo un raster de 3 bandas, uso esto:
            # err = gdal.RasterizeLayer(targetRasterDataset, (3, 2, 1), self.inputVectorRefLayerRec,
            #                          burn_values=(0, 0, 0),
            #                          options=["ATTRIBUTE=%s" % self.nombreCampoLandUseCover])
            # Para raster de 1 banda:
            # No puede extraer el spatial reference on layer edifica para ver si hay que transformar coordenadas.
            # Como targetRasterDataset y self.inputVectorRefLayerRec tienen el mismo srs no pasa nada por este warning.
            err = gdal.RasterizeLayer(
                targetRasterDataset,
                (1,),
                self.inputVectorRefLayerRec,
                burn_values=(0,),
                options=["ATTRIBUTE=%s" % self.nombreCampoLandUseCover]
            )
            geotransform = targetRasterDataset.GetGeoTransform()
            self.vectorRefOrigenX = geotransform[0]
            self.vectorRefOrigenY = geotransform[3]
            self.vectorRefPixelX = geotransform[1]
            self.vectorRefPixelY = geotransform[5]
            self.vectorRefNumCeldasX = targetRasterDataset.RasterXSize
            self.vectorRefNumCeldasY = targetRasterDataset.RasterYSize
            self.vectorRefMinX = self.vectorRefOrigenX
            self.vectorRefMaxX = self.vectorRefOrigenX + (self.vectorRefNumCeldasX * self.vectorRefPixelX)
            self.vectorRefMinY = self.vectorRefOrigenY + (self.vectorRefNumCeldasY * self.vectorRefPixelY)
            self.vectorRefMaxY = self.vectorRefOrigenY
        except:
            print('\nclidcarto.{:006}-> ATENCION!!!: Error al crear {}'.format(GLO.MAINidProceso, targetRasterFileName))
            return False

        if GLO.GLBLverbose or True:
            print(
                'clidcarto-> Nuevo raster creado (vector rasterizado):',
                'vectorRefOrigen:',
                self.vectorRefOrigenX,
                self.vectorRefOrigenY,
                'NumCeldas:',
                self.vectorRefNumCeldasX,
                self.vectorRefNumCeldasY,
                'RefPixel:',
                self.vectorRefPixelX,
                self.vectorRefPixelY,
                'noData:',
                self.noDataVectorRef,
            )
            # print('clidcarto-> Algunos valores del raster creado-:', self.aCeldasVectorRecRasterizado)
        if (
            self.vectorRefMinX == self.xminBloqueH30
            and self.vectorRefMaxX == self.xmaxBloqueH30
            and self.vectorRefMinY == self.yminBloqueH30
            and self.vectorRefMaxY == self.ymaxBloqueH30
        ):
            self.nPixelsPorCelda = GLO.GLBLmetrosCelda / GLO.GLBLrasterPixelSize
            self.nPixelsXRaster = int((self.xmaxBloqueH30 - self.xminBloqueH30) / GLO.GLBLrasterPixelSize)
            self.nPixelsYRaster = int((self.ymaxBloqueH30 - self.yminBloqueH30) / GLO.GLBLrasterPixelSize)
            if self.vectorRefNumCeldasX / self.myLasData.nCeldasX != self.nPixelsPorCelda or self.vectorRefNumCeldasY / self.myLasData.nCeldasY != self.nPixelsPorCelda:
                print('clidcarto-> ATENCION: no salen las cuentas')
            if self.vectorRefPixelX != GLO.GLBLrasterPixelSize or self.vectorRefPixelY != -GLO.GLBLrasterPixelSize:
                print('clidcarto-> ATENCION: revisar metros pixel', self.vectorRefPixelX, GLO.GLBLrasterPixelSize)
            self.vectorRasterizadoCongruenteLidar = True
        else:
            self.vectorRasterizadoCongruenteLidar = False
            print('clidcarto-> La cartoRef no cubre todo el ambito del Lidar y/o el ambito del fichero lidar no cubre todo el bloque')
            print('\t-> self.vectorRefMinX:', self.vectorRefMinX, 'self.xminBloqueH30:', self.xminBloqueH30)
            print('\t-> self.vectorRefMaxX:', self.vectorRefMaxX, 'self.xmaxBloqueH30:', self.xmaxBloqueH30)
            print('\t-> self.vectorRefMinY:', self.vectorRefMinY, 'self.yminBloqueH30:', self.yminBloqueH30)
            print('\t-> self.vectorRefMaxY:', self.vectorRefMaxY, 'self.ymaxBloqueH30:', self.ymaxBloqueH30)

        if GLO.GLBLverbose:
            print('\tclidcarto-> vectorRasterizadoCongruenteLidar', self.vectorRasterizadoCongruenteLidar)

        self.miRasterRefMinXY = np.array([self.vectorRefMinX, self.vectorRefMinY], dtype=np.float32)
        self.miRasterRefOrigen = np.array([self.vectorRefOrigenX, self.vectorRefOrigenY], dtype=np.float32)
        self.miRasterRefPixel = np.array([self.vectorRefPixelX, self.vectorRefPixelY], dtype=np.float32)
        self.miRasterRefNumCeldas = np.array([self.vectorRefNumCeldasX, self.vectorRefNumCeldasY], dtype=np.int32)
        self.miRasterRefCoordenadas = np.array([self.vectorRefMinX, self.vectorRefMaxX, self.vectorRefMinY, self.vectorRefMaxY], dtype=np.float32)

        # print( 'clidcarto-> ->->->self.vectorRefOrigenX', self.vectorRefOrigenX)
        # print( 'clidcarto-> ->->->self.vectorRefOrigenY', self.vectorRefOrigenY)
        # print( 'clidcarto-> ->->->self.vectorRefPixelX', self.vectorRefPixelX)
        # print( 'clidcarto-> ->->->self.vectorRefPixelY', self.vectorRefPixelY)
        # print( 'clidcarto-> ->->->self.vectorRefNumCeldasX', self.vectorRefNumCeldasX)
        # print( 'clidcarto-> ->->->self.vectorRefNumCeldasY', self.vectorRefNumCeldasY)

        if err != 0:
            raise Exception("error rasterizing layer: %s" % err)

        # self.aCeldasVectorRecRasterizado = np.transpose(outputRasterRecBandLandCover.ReadAsArray()) #Es uint8 -> No necesito .astype(np.int8)
        # ->Giro la imagen 90 grados destrogiros para cambiarlo al formato de los arrays: filas<=>y, columnas<=>x).
        #  Tb se puede hacer con array = np.rot90(image, 3)
        self.aCeldasVectorRecRasterizado = outputRasterRecBandLandCover.ReadAsArray()[::-1].transpose()

        if GLO.GLBLverbose:
            print('clidcarto-> Algunos valores del raster creado+:', self.aCeldasVectorRecRasterizado[:5, :10])

        if GLO.GLBLverbose:
            tiempo1 = time.time()
            print('\tclidcarto-> Tiempo para rasterize %s vector layer %0.2f segundos' % (self.nombreCapaInputVector, ((tiempo1 - tiempo0))))
        self.inputVectorRefDataSource.Destroy()

        if self.chequearPuntosDeEjemplo:
            aNumPuntosPorClase = np.zeros(256, dtype=np.int16)
            aTiposDeNucleoUrbano = [
                'No es nucleo',
                'Nucleo Urbano INE',
                'Nucleo Urbano JCyL',
                'Nucleo Bodegas JCyL',
                'Espacio Comercial',
                'Deportivo y Ocio',
                'Area Industrial',
                'Areas Militares y Centros Penitenciarios',
                'Cementerio',
                'Diseminados JCyL',
                'Despoblado JCyL',
            ]
            nPuntosMuestreo = 40
            print(f'clidcarto-> Muestreo {nPuntosMuestreo} x {nPuntosMuestreo} raster:', end='')
            for nPuntoY in range(nPuntosMuestreo):
                print('\nclidcarto->', '%02i' % nPuntoY, end='>>')
                for nPuntoX in range(40):
                    miPuntoX = self.xminBloqueH30 + 605 + (nPuntoX * 5)
                    miPuntoY = self.yminBloqueH30 + 305 + (nPuntoY * 5)
                    # structval = outputRasterRecBandLandCover.ReadRaster(self.xminBloqueH30 + 275 + nPuntoX, yminBloqueH30 + 115 + nPuntoY, 1, 1, buf_type=gdal.GDT_Byte)
                    miPuntoXraster = (miPuntoX - self.vectorRefOrigenX) / self.vectorRefPixelX
                    # miPuntoYraster = (miPuntoY - self.vectorRefOrigenY) / self.vectorRefPixelY
                    miPuntoYraster = (self.vectorRefMinY - miPuntoY) / self.vectorRefPixelY
                    # self.vectorRefNumCeldasY * self.vectorRefPixelY
                    # structval = outputRasterRecBandLandCover.ReadRaster(miPuntoXraster, miPuntoYraster, 1, 1, buf_type=gdal.GDT_Byte)
                    # landCover = struct.unpack('b' , structval)
                    if (
                        int(miPuntoXraster) >= 0
                        and int(miPuntoXraster) < self.aCeldasVectorRecRasterizado.shape[0]
                        and int(miPuntoYraster) >= 0
                        and int(miPuntoYraster) < self.aCeldasVectorRecRasterizado.shape[1]
                    ):
                        landCover = self.aCeldasVectorRecRasterizado[int(miPuntoXraster), int(miPuntoYraster)]
                        print(self.aCeldasVectorRecRasterizado[int(miPuntoXraster), int(miPuntoYraster)], end='')
                    else:
                        print(miPuntoXraster, miPuntoYraster, 'fuera del rasterArray de dimensiones', self.aCeldasVectorRecRasterizado.shape)
                        landCover = 0
                    #                     if nPuntoX == 12 and nPuntoY == 12:
                    #                         print( 'clidcarto-> nPuntoXY', nPuntoX, nPuntoY, 'miPuntoXY', miPuntoX, miPuntoY)
                    #                         print('        landCover:', landCover)
                    aNumPuntosPorClase[landCover] += 1

            if GLO.GLBLverbose:
                print()
                print(
                    'clidcarto-> self.xminBloqueH30',
                    self.xminBloqueH30,
                    'self.vectorRefOrigenX',
                    self.vectorRefOrigenX,
                    'self.yminBloqueH30',
                    self.yminBloqueH30,
                    'self.vectorRefOrigenY',
                    self.vectorRefOrigenY,
                )

                if self.nombreCapaInputVector == 'IGR0204NUC_URB_CYL_S_E25':
                    for nClase in range(len(aTiposDeNucleoUrbano)):
                        if aNumPuntosPorClase[nClase] > 0:
                            print(
                                'clidcarto-> Leyendo raster: numero de puntos clasCob %i (%s): %i de 100'
                                % (nClase, aTiposDeNucleoUrbano[nClase], aNumPuntosPorClase[nClase])
                            )
                elif self.nombreCapaInputVector == 'SingularUse' or self.nombreCapaInputVector.strartswith('BTN25'):
                    print('clidcarto-> Numero de puntos clasCob 1 (edificio):    %i de 100' % aNumPuntosPorClase[1])
                    print('clidcarto-> Numero de puntos clasCob 2 (via):         %i de 100' % aNumPuntosPorClase[2])
                    print('clidcarto-> Numero de puntos clasCob 3 (ferrocarril): %i de 100' % aNumPuntosPorClase[3])
                    print('clidcarto-> Numero de puntos clasCob 4 (agua):        %i de 100' % aNumPuntosPorClase[4])

                tiempo2 = time.time()
                print('\tclidcarto-> Tiempo para leer 100 puntos en el raster: %0.2f mili-segundos' % ((tiempo2 - tiempo1) * 1e3))

        if self.vectorRefNumCeldasX != self.aCeldasVectorRecRasterizado.shape[0] or self.vectorRefNumCeldasX != nPixelesXraster:
            print(self.vectorRefNumCeldasX, self.aCeldasVectorRecRasterizado.shape[0])
            input('clidcarto-> revisarX')
        if self.vectorRefNumCeldasY != self.aCeldasVectorRecRasterizado.shape[1] or self.vectorRefNumCeldasY != nPixelesYraster:
            print(self.vectorRefNumCeldasY, self.aCeldasVectorRecRasterizado.shape[1])
            input('clidcarto-> revisarY')

        return True


    # ooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo
    def asignarUsoSingularArrayCeldas(self):
        print('clidcarto-> Se va a asignar UsoSingular al arrayCeldas.')
        print('\t-> Num de columnas en el raster (dimension X):', self.nPixelsXRaster)
        print('\t-> Num de filas en el raster (dimension Y):   ', self.nPixelsYRaster)
        print('\t-> self.vectorRasterizadoCongruenteLidar:     ', self.vectorRasterizadoCongruenteLidar)
        print('\t-> self.nPixelsPorCelda:                      ', self.nPixelsPorCelda)
        if self.usarVectorRef:
            if self.LCLhusoUTM != 30:
                for nXrasterSingularUse in range(int(self.nPixelsXRaster)):
                    for nYrasterSingularUse in range(int(self.nPixelsYRaster)):
                        esUsoSingular = 0
                        if (
                            nXrasterSingularUse < self.aCeldasVectorRecRasterizado.shape[0]
                            and nYrasterSingularUse < self.aCeldasVectorRecRasterizado.shape[1]
                        ):
                            if self.aCeldasVectorRecRasterizado[nXrasterSingularUse, nYrasterSingularUse] != 0:
                                esUsoSingular = self.aCeldasVectorRecRasterizado[nXrasterSingularUse, nYrasterSingularUse]
                        # print(
                        #     # 'clidcarto->', nX, nY,
                        #     # 'nXYpixel:', nXpixel, nYpixel,
                        #     'nXYraster:', nXrasterSingularUse, nYrasterSingularUse,
                        #     'esUsoSingular:', esUsoSingular,
                        #     'shape:', self.aCeldasVectorRecRasterizado.shape,
                        # )
                        # ATENCION: queda esto sin resolver:
                        # self.aCeldasLandUseCover[nX, nY] = esUsoSingular
            else:
                for nY in reversed(range(self.myLasData.nCeldasY)):
                    for nX in range(self.myLasData.nCeldasX):
                        if self.vectorRasterizadoCongruenteLidar:
                            # Si el vectorial de nucleos urbanos excede completamente
                            # al bloque y consigo recortarlo con las coordendas que me interesan
                            # las coordenadas de mi celda dentro del raster recortado son nX, nY
                            # self.nPixelsPorCelda = GLO.GLBLmetrosCelda / GLO.GLBLrasterPixelSize
                            # self.nPixelsPorCelda = (self.xmaxBloqueH30 - self.xminBloqueH30) / GLO.GLBLrasterPixelSize
                            esUsoSingular = 0
                            for nXpixel in range(int(self.nPixelsPorCelda)):
                                for nYpixel in range(int(self.nPixelsPorCelda)):
                                    nXrasterSingularUse = int((nX * self.nPixelsPorCelda) + nXpixel)
                                    nYrasterSingularUse = int((nY * self.nPixelsPorCelda) + nYpixel)
                                    if (
                                        nXrasterSingularUse < self.aCeldasVectorRecRasterizado.shape[0]
                                        and nYrasterSingularUse < self.aCeldasVectorRecRasterizado.shape[1]
                                    ):
                                        if self.aCeldasVectorRecRasterizado[nXrasterSingularUse, nYrasterSingularUse] != 0:
                                            esUsoSingular = self.aCeldasVectorRecRasterizado[nXrasterSingularUse, nYrasterSingularUse]
                                    else:
                                        esUsoSingular = 0
                                    # print(
                                    #     'clidcarto->', nX, nY,
                                    #     'nXYpixel:', nXpixel, nYpixel,
                                    #     'nXYraster:', nXrasterSingularUse, nYrasterSingularUse,
                                    #     'esUsoSingular:', esUsoSingular,
                                    #     'shape:', self.aCeldasVectorRecRasterizado.shape,
                                    # )
                        else:
                            print('clidcarto-> Revisar este codigo que se queda sin terminar:')
                            sys.exit(0)
                            esUsoSingular = 0
                            for nXpixel in range(int(self.nPixelsPorCelda)):
                                for nYpixel in range(int(self.nPixelsPorCelda)):
                                    miPtoX = self.vectorRefOrigenX + (nX + (nXpixel / self.nPixelsPorCelda)) * GLO.GLBLmetrosCelda
                                    # miPtoY = self.vectorRefOrigenY + (nY + (nYpixel / self.nPixelsPorCelda)) * GLO.GLBLmetrosCelda
                                    miPtoY = self.vectorRefMinY + (nY + (nYpixel / self.nPixelsPorCelda)) * GLO.GLBLmetrosCelda
                                    miPuntoXrasterSingularUse = int((miPtoX - self.vectorRefOrigenX) / self.vectorRefPixelX)
                                    # miPuntoYrasterSingularUse = int((miPtoY - self.vectorRefOrigenY) / self.vectorRefPixelY)
                                    miPuntoYrasterSingularUse = int((self.vectorRefMinY - miPtoY) / self.vectorRefPixelY)
                                    if (
                                        miPuntoXrasterSingularUse < 0
                                        or miPuntoXrasterSingularUse >= self.vectorRefNumCeldasX
                                        or miPuntoYrasterSingularUse < 0
                                        or miPuntoYrasterSingularUse >= self.vectorRefNumCeldasY
                                    ):
                                        print(
                                            'clidcarto-> Atencion: error al identificar el uso singurar del punto {}, {} (probablemente por solape solo parcial con el bloque).'.format(
                                                miPtoX, miPtoY
                                            )
                                        )
                                        print(
                                            '\t-> El punto {}, {} esta fuera del raster de dimension {} x {}'.format(
                                                miPuntoXrasterSingularUse,
                                                miPuntoYrasterSingularUse,
                                                self.vectorRefNumCeldasX,
                                                self.vectorRefNumCeldasY
                                            )
                                        )
                                        continue
                                    else:
                                        if (
                                            miPuntoXrasterSingularUse < self.aCeldasVectorRecRasterizado.shape[0]
                                            and miPuntoYrasterSingularUse < self.aCeldasVectorRecRasterizado.shape[1]
                                        ):
                                            if self.aCeldasVectorRecRasterizado[miPuntoXrasterSingularUse, miPuntoYrasterSingularUse] != 0:
                                                esUsoSingular = self.aCeldasVectorRecRasterizado[miPuntoXrasterSingularUse, miPuntoYrasterSingularUse]
                                        else:
                                            esUsoSingular = 0
                        self.aCeldasLandUseCover[nX, nY] = esUsoSingular


    # ooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo
    def asignarNucleoUrbanoArrayCeldas(self):
        if self.usarVectorRef:
            for nY in reversed(range(self.myLasData.nCeldasY)):
                for nX in range(self.myLasData.nCeldasX):
                    if self.vectorRasterizadoCongruenteLidar:
                        # Si el vectorial de nucleos urbanos excede completamente
                        # al bloque y consigo recortarlo con las coordendas que me interesan
                        # las coordenadas de mi celda dentro del raster recortado son nX, nY
                        # self.nPixelsPorCelda = GLO.GLBLmetrosCelda / GLO.GLBLrasterPixelSize
                        self.nPixelsPorCelda = (self.xmaxBloqueH30 - self.xminBloqueH30) / GLO.GLBLrasterPixelSize
                        nXrasterNucleosUrbanos = int((nX + 0.5) * self.nPixelsPorCelda)
                        nYrasterNucleosUrbanos = int((nY + 0.5) * self.nPixelsPorCelda)
                        if (
                            nXrasterNucleosUrbanos < self.aCeldasVectorRecRasterizado.shape[0]
                            and nYrasterNucleosUrbanos < self.aCeldasVectorRecRasterizado.shape[1]
                        ):
                            esUrbano = self.aCeldasVectorRecRasterizado[nXrasterNucleosUrbanos, nYrasterNucleosUrbanos]
                        else:
                            esUrbano = 0
                    else:
                        miPtoX = self.vectorRefOrigenX + (nX + 0.5) * GLO.GLBLmetrosCelda
                        # miPtoY = self.vectorRefOrigenY + (nY + 0.5) * GLO.GLBLmetrosCelda
                        miPtoY = self.vectorRefMinY + (nY + 0.5) * GLO.GLBLmetrosCelda
                        if miPtoX <= self.vectorRefMinX or miPtoX >= self.vectorRefMaxX or miPtoY <= self.vectorRefMinY or miPtoY >= self.vectorRefMaxY:
                            esUrbano = 0
                        else:
                            miPuntoXraster = int((miPtoX - self.vectorRefOrigenX) / self.vectorRefPixelX)
                            # miPuntoYraster = int((miPtoY - self.vectorRefOrigenY) / self.vectorRefPixelY)
                            miPuntoYraster = int((self.vectorRefMinY - miPtoY) / self.vectorRefPixelY)
                            if (
                                miPuntoXraster < 0
                                or miPuntoXraster >= self.vectorRefNumCeldasX
                                or miPuntoYraster < 0
                                or miPuntoYraster >= self.vectorRefNumCeldasY
                            ):
                                esUrbano = 0
                            else:
                                if (
                                    miPuntoXraster < self.aCeldasVectorRecRasterizado.shape[0]
                                    and miPuntoYraster < self.aCeldasVectorRecRasterizado.shape[1]
                                ):
                                    esUrbano = self.aCeldasVectorRecRasterizado[miPuntoXraster, miPuntoYraster]
                                else:
                                    esUrbano = 0
                    self.aCeldasLandUseCover[nX, nY] = esUrbano


    # ooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo
    def asignarLitologiaArrayCeldas(self):
        if self.usarVectorRef:
            for nY in reversed(range(self.myLasData.nCeldasY)):
                for nX in range(self.myLasData.nCeldasX):
                    if self.vectorRasterizadoCongruenteLidar:
                        # Si el vectorial del geologico excede completamente
                        # al bloque y consigo recortarlo con las coordendas que me interesan
                        # las coordenadas de mi celda dentro del raster recortado son nX, nY
                        # self.nPixelsPorCelda = GLO.GLBLmetrosCelda / GLO.GLBLrasterPixelSize
                        self.nPixelsPorCelda = (self.xmaxBloqueH30 - self.xminBloqueH30) / GLO.GLBLrasterPixelSize
                        nXrasterGeologico = int((nX + 0.5) * self.nPixelsPorCelda)
                        nYrasterGeologico = int((nY + 0.5) * self.nPixelsPorCelda)
                        if (
                            nXrasterGeologico < self.aCeldasVectorRecRasterizado.shape[0]
                            and nYrasterGeologico < self.aCeldasVectorRecRasterizado.shape[1]
                        ):
                            usoGeo = self.aCeldasVectorRecRasterizado[nXrasterGeologico, nYrasterGeologico]
                        else:
                            usoGeo = 0
                    else:
                        miPtoX = self.vectorRefOrigenX + (nX + 0.5) * GLO.GLBLmetrosCelda
                        # miPtoY = self.vectorRefOrigenY + (nY + 0.5) * GLO.GLBLmetrosCelda
                        miPtoY = self.vectorRefMinY + (nY + 0.5) * GLO.GLBLmetrosCelda
                        if miPtoX <= self.vectorRefMinX or miPtoX >= self.vectorRefMaxX or miPtoY <= self.vectorRefMinY or miPtoY >= self.vectorRefMaxY:
                            usoGeo = 0
                        else:
                            miPuntoXraster = int((miPtoX - self.vectorRefOrigenX) / self.vectorRefPixelX)
                            # miPuntoYraster = int((miPtoY - self.vectorRefOrigenY) / self.vectorRefPixelY)
                            miPuntoYraster = int((self.vectorRefMinY - miPtoY) / self.vectorRefPixelY)
                            if (
                                miPuntoXraster < 0
                                or miPuntoXraster >= self.vectorRefNumCeldasX
                                or miPuntoYraster < 0
                                or miPuntoYraster >= self.vectorRefNumCeldasY
                            ):
                                usoGeo = 0
                            else:
                                if (
                                    miPuntoXraster < self.aCeldasVectorRecRasterizado.shape[0]
                                    and miPuntoYraster < self.aCeldasVectorRecRasterizado.shape[1]
                                ):
                                    usoGeo = self.aCeldasVectorRecRasterizado[miPuntoXraster, miPuntoYraster]
                                else:
                                    usoGeo = 0
                    self.aCeldasLandUseCover[nX, nY] = usoGeo



    # oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo
    def crearRutasFromVector(self):
        # Aviso: los tiles target de cartoSingu pueden ser comunes a varios entrenamientos
        # cambiando el exData para entrenar con unas categorias u otras
        if GLO.GLBLformatoTilesNpz:
            self.trainPathNpz = os.path.join(
                GLO.MAINrutaOutput,
                GLO.GLBL_TRAIN_DIR,
                'npz{}/'.format(self.tilesTargetPathTroncal)
            )
            if not os.path.isdir(self.trainPathNpz):
                numIntentosEscritura = 0
                while True:
                    numIntentosEscritura += 1
                    try:
                        os.makedirs(self.trainPathNpz)
                        break
                    except:
                        time.sleep(5)
                        if numIntentosEscritura > 5:
                            break
                if GLO.GLBLverbose:
                    print(
                        'cartolider.{}-> Creando directorio train_npz...: {}'.format(
                            self.fileCoordYear, self.trainPathNpz
                        )
                    )
        else:
            self.trainPathNpz = ''

        if GLO.GLBLsoloGuardarArraysNpzSinCrearOutputFiles:
            self.trainPathPng = ''
            self.trainPathExDataCartoRefA = ''
            self.trainPathExDataCartoRefB = ''
            self.trainPathPng1m = ''
            self.trainPathAsc = ''
            return

        if GLO.GLBLformatoTilesPng:
            self.trainPathPng = os.path.join(
                GLO.MAINrutaOutput,
                GLO.GLBL_TRAIN_DIR,
                'png{}/'.format(self.tilesTargetPathTroncal)
            )
            if not os.path.isdir(self.trainPathPng):
                numIntentosEscritura = 0
                while True:
                    numIntentosEscritura += 1
                    try:
                        os.makedirs(self.trainPathPng)
                        break
                    except:
                        time.sleep(5)
                        if numIntentosEscritura > 5:
                            break
                if GLO.GLBLverbose:
                    print(
                        'cartolider.{}-> Creando directorio train_png...: {}'.format(
                            self.fileCoordYear, self.trainPathPng
                        )
                    )
        else:
            self.trainPathPng = ''

        # Para el mismo targetCartoRef se usan dos exData distintos (con y sin agua) para los dos modelos A y B.
        if GLO.GLBLcrearTilesExDataCartoSinguEdiXXXYY:
            if not (self.tilesExDataPathTroncalA).endswith('SinUso'):
                self.trainPathExDataCartoRefA = os.path.join(
                    GLO.MAINrutaOutput,
                    GLO.GLBL_TRAIN_DIR,
                    'png{}'.format(self.tilesExDataPathTroncalA)
                )
                if not os.path.isdir(self.trainPathExDataCartoRefA):
                    numIntentosEscritura = 0
                    while True:
                        numIntentosEscritura += 1
                        try:
                            os.makedirs(self.trainPathExDataCartoRefA)
                            break
                        except:
                            time.sleep(5)
                            if numIntentosEscritura > 5:
                                break
                    if GLO.GLBLverbose or True:
                        print(
                            'cartolider.{}-> Creando directorio exDataA: {}'.format(
                                self.fileCoordYear, self.trainPathExDataCartoRefA
                            )
                        )
            else:
                self.trainPathExDataCartoRefA = ''
            if not (self.tilesExDataPathTroncalB).endswith('SinUso'):
                self.trainPathExDataCartoRefB = os.path.join(
                    GLO.MAINrutaOutput,
                    GLO.GLBL_TRAIN_DIR,
                    'png{}'.format(self.tilesExDataPathTroncalB)
                )
                if not os.path.isdir(self.trainPathExDataCartoRefB):
                    numIntentosEscritura = 0
                    while True:
                        numIntentosEscritura += 1
                        try:
                            os.makedirs(self.trainPathExDataCartoRefB)
                            break
                        except:
                            time.sleep(5)
                            if numIntentosEscritura > 5:
                                break
                    if GLO.GLBLverbose or True:
                        print(
                            'cartolider.{}-> Creando directorio exDataB: {}'.format(
                                self.fileCoordYear, self.trainPathExDataCartoRefB
                            )
                        )
            else:
                self.trainPathExDataCartoRefB = ''
        else:
            self.trainPathExDataCartoRefA = ''
            self.trainPathExDataCartoRefB = ''

        if self.nombreCapa == 'SingUse' and GLO.GLBLcrearTilesTargetDeCartoRefPixel1m:
            self.trainPathPng1m = os.path.join(
                GLO.MAINrutaOutput,
                GLO.GLBL_TRAIN_DIR,
                'png1m{}/'.format(self.tilesTargetPathTroncal)
            )
            if not os.path.isdir(self.trainPathPng1m):
                numIntentosEscritura = 0
                while True:
                    numIntentosEscritura += 1
                    try:
                        os.makedirs(self.trainPathPng1m)
                        break
                    except:
                        time.sleep(5)
                        if numIntentosEscritura > 5:
                            break
                if GLO.GLBLverbose:
                    print(
                        'cartolider.{}-> Creando directorio train/png...: {}'.format(
                            self.fileCoordYear, self.trainPathPng1m
                        )
                    )
        else:
            self.trainPathPng1m = ''

        if GLO.GLBLformatoTilesAscRasterRef:
            self.trainPathAsc = os.path.join(
                GLO.MAINrutaOutput,
                GLO.GLBL_TRAIN_DIR,
                'asc{}/'.format(self.tilesTargetPathTroncal)
            )
            if not os.path.isdir(self.trainPathAsc):
                numIntentosEscritura = 0
                while True:
                    numIntentosEscritura += 1
                    try:
                        os.makedirs(self.trainPathAsc)
                        break
                    except:
                        time.sleep(5)
                        if numIntentosEscritura > 5:
                            break
                if GLO.GLBLverbose:
                    print(
                        'cartolider.{}-> Creando directorio train/asc...: {}'.format(
                            self.fileCoordYear, self.trainPathAsc
                        )
                    )
        else:
            self.trainPathAsc = ''


    # oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo
    def crearTilesTargetFromVector(
        self,
        LCLtileSizeMetros=GLO.GLBLtileSizeMetros,
        LCLtileSemiSolapeMetros=GLO.GLBLtileSemiSolapeMetros,
        interpolarValores=False,
        LCLmantenerTilesGuardados=False,
        TRNStilesRefuerzo=False,
    ):
        # Generar tiles a partir de una capa originalmente vectorial
        mapUsoSingular = np.zeros(256, dtype=np.uint8)

        print('clidcarto-> Creando tiles de cartoref y exData:')
        print('\t-> self.trainPathPng:    ', self.trainPathPng)
        print('\t-> self.trainPathExDataCartoRefA:', self.trainPathExDataCartoRefA)
        print('\t-> self.trainPathExDataCartoRefB:', self.trainPathExDataCartoRefB)

        # oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo
        # ATENCION: CODIGOS ANTIGUOS
        # oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo
        # # NoSingular -> 0
        # mapUsoSingular[1] = 1  # Rio
        # mapUsoSingular[2:4] = 2  # Embalse, lago
        # mapUsoSingular[20:26] = 3  # Camino
        # mapUsoSingular[10] = 4  # Carretera
        # mapUsoSingular[14] = 4  # Carretera
        # mapUsoSingular[5] = 5  # Puente
        # mapUsoSingular[[i for i in [11, 12, 13, 15, 16, 17, 19]]] = 5  # Puente
        # mapUsoSingular[41:51] = 5  # Puente
        # mapUsoSingular[75] = 0  # SubEdificio
        # mapUsoSingular[100:] = 7  # Edificio, Nave
        # # mapUsoSingular[220:] = 7 #Nave
        # mapUsoSingular[92:94] = 8  # Aerogenerador
        # mapUsoSingular[91] = 9  # Apoyo electrico, Torre comunicaciones
        # oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo

        # ======================================================================
        # ======================================================================
        mapUsoSingularNoSingular = 0
        mapUsoSingularAnulado = 0
        mapUsoSingularRio = 1
        mapUsoSingularEmbalseLago = 2
        mapUsoSingularCamino = 3
        mapUsoSingularFerrocarril = 4
        mapUsoSingularCarretera = 5
        mapUsoSingularCalzadaUrbana = 6
        mapUsoSingularPuente = 7
        mapUsoSingularEdificioNave = 8
        mapUsoSingularMiscelaneaConPosibleConstruccion = 9
        mapUsoSingular[0] = mapUsoSingularNoSingular            # 0, Celdas sin uso singular
        mapUsoSingular[1] = mapUsoSingularRio                   # 1. Rio (por el momento no se han incluido)
        mapUsoSingular[2:4] = mapUsoSingularEmbalseLago         # 2. Embalse, lago
        mapUsoSingular[5] = mapUsoSingularCamino                # 3. Camino (por el momento se han excluido)
        mapUsoSingular[14] = mapUsoSingularFerrocarril          # 4. Ferrocaril
        mapUsoSingular[10] = mapUsoSingularCarretera            # 5. Carretera
        mapUsoSingular[15] = mapUsoSingularCalzadaUrbana        # 6. Calzadas urbanas
        mapUsoSingular[20] = mapUsoSingularPuente               # 7. Puente
        mapUsoSingular[100:200] = mapUsoSingularEdificioNave    # 8. Edificio (100, 125, 150)
        mapUsoSingular[200:256] = mapUsoSingularEdificioNave    # 8. Nave (200, 225)
        mapUsoSingular[50] = mapUsoSingularMiscelaneaConPosibleConstruccion # 9. Construcciones menores (no seguras): excluir de entrenamiento con weight=0
        mapUsoSingular[75] = mapUsoSingularAnulado # 0. Zonas con construcciones (no seguras): Ya no excluir de entrenamiento con weight=0
        mapUsoSingular[175] = mapUsoSingularMiscelaneaConPosibleConstruccion # 9. Parkings: excluir de entrenamiento con weight=0
        # ======================================================================
        mainUsoSingular = np.array([mapUsoSingular[val] for val in self.aCeldasVectorRecRasterizado.flatten()]).reshape(self.aCeldasVectorRecRasterizado.shape)
        # Mapeo las categorias de self.aCeldasVectorRecRasterizado a una lista 0..4:
        # ======================================================================
        # ======================================================================

        if GLO.GLBLverbose:
            print('\t\tclidcarto-> Dimensiones del pixel de %s: %i x %i metros' % (self.nombreCapa, self.miRasterRefPixel[0], self.miRasterRefPixel[1]))
            print('\t\tclidcarto-> nCeldas del recorte de %s: %i x %i celdas' % (self.nombreCapa, self.miRasterRefNumCeldas[0], self.miRasterRefNumCeldas[1]))
            if GLO.GLBLformatoTilesNpz:
                print('\t\tclidcarto-> Guardando %s en %s' % (self.nombreCapa, self.trainPathNpz))
            if GLO.GLBLformatoTilesPng:
                print('\t\tclidcarto-> Guardando %s en %s' % (self.nombreCapa, self.trainPathPng))

        # import matplotlib.pyplot as plt
        # plt.imshow(self.aCeldasVectorRecRasterizado)
        # plt.show()

        if interpolarValores:
            ordenPolinomioInterpolacion = 3
        else:
            ordenPolinomioInterpolacion = 0

        # ==========================================================================
        # Dimension de los pixels
        GLBNmetrosRasterRx = self.miRasterRefPixel[0] # 1.0 m
        GLBNmetrosRasterRy = self.miRasterRefPixel[1] # -1.0 m
        GLBNmetrosSubCelda = GLO.GLBLmetrosSubCelda # 2.0 m
        GLBNmetrosCeldilla = GLO.GLBLmetrosCeldilla # 1.0 m
        # ==========================================================================
        # Num de pixels del Tile para distintos pixelSize:
        GLBNtileSizeEnPixelsRasterRx = int(math.ceil(LCLtileSizeMetros / GLBNmetrosRasterRx)) # -> 256 ($512)
        GLBNtileSizeEnPixelsRasterRy = int(math.ceil(LCLtileSizeMetros / -GLBNmetrosRasterRy)) # -> 256 ($512)
        GLBNtileSizeEnPixelsSubCelda = int(math.ceil(LCLtileSizeMetros / GLBNmetrosSubCelda)) # -> 128 ($256)
        GLBNtileSizeEnPixelsCeldilla = int(math.ceil(LCLtileSizeMetros / GLBNmetrosCeldilla)) # -> 256 ($512)
        # ==========================================================================
        # SemiSolape y Kernel
        GLBNtileSemiSolapePixelsRasterRx = int(math.floor(LCLtileSemiSolapeMetros / GLBNmetrosRasterRx)) # -> 0 ($6)
        GLBNtileSemiSolapePixelsRasterRy = int(math.floor(LCLtileSemiSolapeMetros / -GLBNmetrosRasterRy)) # -> 0 ($6)
        GLBNtileSemiSolapePixelsSubCelda = int(math.floor(LCLtileSemiSolapeMetros / GLBNmetrosSubCelda)) # -> 0 ($3)
        GLBNtileSemiSolapePixelsCeldilla = int(math.floor(LCLtileSemiSolapeMetros / GLBNmetrosCeldilla)) # -> 0 ($6)
        GLBNtileKernelMetros = (LCLtileSizeMetros - (2 * LCLtileSemiSolapeMetros)) # -> 256 ($500)
        GLBNtileKernelPixelsRasterRx = (GLBNtileSizeEnPixelsRasterRx - (2 * GLBNtileSemiSolapePixelsRasterRx)) # -> 256 ($500)
        GLBNtileKernelPixelsRasterRy = (GLBNtileSizeEnPixelsRasterRy - (2 * GLBNtileSemiSolapePixelsRasterRy)) # -> 256 ($500)
        GLBNtileKernelPixelsSubCelda = (GLBNtileSizeEnPixelsSubCelda - (2 * GLBNtileSemiSolapePixelsSubCelda)) # -> 128 ($250)
        GLBNtileKernelPixelsCeldilla = (GLBNtileSizeEnPixelsCeldilla - (2 * GLBNtileSemiSolapePixelsSubCelda)) # -> 256 ($500)
        # ==========================================================================
        # Num de pixels del RasterRef (equivale a un bloque, normalmente de 2 x 2 km)
        if self.miRasterRefNumCeldas[0] != self.aCeldasVectorRecRasterizado.shape[0] or self.miRasterRefNumCeldas[1] != self.aCeldasVectorRecRasterizado.shape[1]:
            print('clidcarto-> Revisar esto porque algo no lo he hecho bien')
            print(self.miRasterRefNumCeldas[0], self.aCeldasVectorRecRasterizado.shape[0], self.miRasterRefNumCeldas[1], self.aCeldasVectorRecRasterizado.shape[1])
        nPixelsRasterRefX = self.miRasterRefNumCeldas[0] # -> 2000
        nPixelsRasterRefY = self.miRasterRefNumCeldas[1] # -> 2000
        # ==========================================================================
        # Numero de Tiles (nRows & nCols)
        numTilesRows = int(math.ceil(nPixelsRasterRefY / GLBNtileSizeEnPixelsRasterRy)) # -> 8 ($4)
        numTilesCols = int(math.ceil(nPixelsRasterRefX / GLBNtileSizeEnPixelsRasterRx)) # -> 8 ($4)
        # ==========================================================================
        # Margen que sobresalen los Tiles fuera del rasterRef (bloque)
        margenXsobresalienteMetros = LCLtileSemiSolapeMetros + (((numTilesCols * GLBNtileKernelMetros) - GLO.GLBLmetrosBloque) / 2) # -> 24 ($6)
        margenYsobresalienteMetros = LCLtileSemiSolapeMetros + (((numTilesRows * GLBNtileKernelMetros) - GLO.GLBLmetrosBloque) / 2) # -> 24 ($6)
        margenXsobresalientePixelsRxA = int(math.floor(margenXsobresalienteMetros / GLBNmetrosRasterRx))
        margenXsobresalientePixelsRxB = int(math.ceil(margenXsobresalienteMetros / GLBNmetrosRasterRx))
        margenYsobresalientePixelsRxA = int(math.floor(margenYsobresalienteMetros / GLBNmetrosRasterRx))
        margenYsobresalientePixelsRxB = int(math.ceil(margenYsobresalienteMetros / GLBNmetrosRasterRx))
        margenXsobresalientePixelsCdA = int(math.floor(margenXsobresalienteMetros / GLBNmetrosCeldilla))
        margenXsobresalientePixelsCdB = int(math.ceil(margenXsobresalienteMetros / GLBNmetrosCeldilla))
        margenYsobresalientePixelsCdA = int(math.floor(margenYsobresalienteMetros / GLBNmetrosCeldilla))
        margenYsobresalientePixelsCdB = int(math.ceil(margenYsobresalienteMetros / GLBNmetrosCeldilla))

        # ======================================================================
        if LCLmantenerTilesGuardados:
            tilesEncontrados = True
            for nRow in range(numTilesRows):
                for nCol in range(numTilesCols):
                    pngFileName = os.path.join(self.trainPathPng, '%s_%s_%i_%i.png' % (self.fileCoordYear, 'Train', nRow, nCol))
                    if not os.path.exists(pngFileName):
                        tilesEncontrados = False
                        break
                if not tilesEncontrados:
                    break
            if GLO.GLBLformatoTilesAscRasterRef:
                for nRow in range(numTilesRows):
                    for nCol in range(numTilesCols):
                        # self.trainPathAsc = (self.trainPathPng.replace('/png', '/asc')).replace('\png', '/asc')
                        pngFileName = os.path.join(self.trainPathAsc, '%s_%s_%i_%i.png' % (self.fileCoordYear, 'Train', nRow, nCol))
                        if not os.path.exists(pngFileName):
                            tilesEncontrados = False
                            break
                        if GLO.GLBLcrearTilesExDataCartoSinguEdiXXXYY:
                            pngFileNameExDataA = os.path.join(
                                self.trainPathExDataCartoRefA,
                                '%s_%s_%i_%i.png' % (self.fileCoordYear, 'Train', nRow, nCol)
                            )
                            if not os.path.exists(pngFileNameExDataA):
                                tilesEncontrados = False
                                break
                            pngFileNameExDataB = os.path.join(
                                self.trainPathExDataCartoRefB,
                                '%s_%s_%i_%i.png' % (self.fileCoordYear, 'Train', nRow, nCol)
                            )
                            if not os.path.exists(pngFileNameExDataB):
                                tilesEncontrados = False
                                break
                    if not tilesEncontrados:
                        break

            if tilesEncontrados:
                print('clidcarto-> No es necesario crear tiles porque ya se han creado previamente')
                return
        # ======================================================================

        if GLO.GLBLverbose:
            print('\tclidcarto->> Se van a crear %i x %i tiles' % (numTilesRows, numTilesCols))
            print('\t\tLCLtileSizeMetros:', LCLtileSizeMetros,
                  'LCLtileSemiSolapeMetros:', LCLtileSemiSolapeMetros,
                  'GLBNtileSemiSolapePixelsSubCelda:', GLBNtileSemiSolapePixelsSubCelda
            )
            print('\t\tGLBNtileKernelPixelsSubCelda:', GLBNtileKernelPixelsSubCelda,
                  'GLBNtileKernelMetros:', GLBNtileKernelMetros,
                  'GLBNtileKernelPixelsRasterRx:', GLBNtileKernelPixelsRasterRx,
                  'GLBNtileKernelPixelsRasterRy:', GLBNtileKernelPixelsRasterRy,
              )
                  
            print('\t\tGLBNtileSizeEnPixelsRasterRx 2m', GLBNtileSizeEnPixelsRasterRx,
                  'GLBNtileSizeEnPixelsCeldilla 1m', GLBNtileSizeEnPixelsCeldilla
            )
            print('\t\tGLBNtileSemiSolapePixelsRasterRx:', GLBNtileSemiSolapePixelsRasterRx,
                  'GLBNtileSemiSolapePixelsRasterRy:', GLBNtileSemiSolapePixelsRasterRy)
            print(
                '\t\tmargenXsobresalienteMetros', margenXsobresalienteMetros, '=', margenXsobresalienteMetros, 'm;',
                'margenYsobresalienteMetros', margenYsobresalienteMetros, '=', margenYsobresalienteMetros, 'm;',
                'margenXsobresalientePixelsRxA', margenXsobresalientePixelsRxA, 'pixels;'
            )

        if margenXsobresalienteMetros < 0 or margenYsobresalienteMetros < 0:
            print(
                '\nclidcarto-> ATENCION capa raster: {}-> reducir GLBLtileSemiSolapeMetros ({:0.1f} m) para que los tiles cubran todo el bloque.'.format(
                    self.nombreCapa,
                    LCLtileSemiSolapeMetros,
                )
            )
            print(
                'MargenX: {}; numTilesCols: {}, GLBNtileKernelMetros: {}, metrosBloque: {}'.format(
                    margenXsobresalienteMetros,
                    numTilesCols,
                    GLBNtileKernelMetros,
                    GLO.GLBLmetrosBloque
                )
            )
            # sys.exit(0)
#         elif LCLtileSemiSolapeMetros % GLBNmetrosRasterRx != 0:
#             print(
#                 '\nclidcarto-> ATENCION: cambiar GLBLtileSemiSolapeMetros ({:0.1f} m) para que el semi-solape sea un numero entero de subCeldas (subcelda: {} m)'.format(
#                     LCLtileSemiSolapeMetros,
#                     GLBNmetrosRasterRx,
#                 )
#             )
#             sys.exit(0)
#         elif margenXsobresalienteMetros % GLBNmetrosRasterRx != 0 or margenYsobresalienteMetros  % GLBNmetrosRasterRx != 0:
#             print(
#                 '\nclidcarto-> ATENCION: cambiar GLBLtileSemiSolapeMetros ({:0.1f} m) para que el margen exterior sea un numero entero de subCeldas (subcelda: {} m)'.format(
#                     LCLtileSemiSolapeMetros,
#                     GLBNmetrosRasterRx,
#     
#                 )
#             )
#             sys.exit(0)
        # ==========================================================================

        # ==========================================================================
        for nRow in range(numTilesRows):
            for nCol in range(numTilesCols):
                tileRecorte = np.zeros((GLBNtileSizeEnPixelsRasterRy, GLBNtileSizeEnPixelsRasterRx), dtype=mainUsoSingular.dtype)
                tileRecorte1m = np.zeros((LCLtileSizeMetros, LCLtileSizeMetros), dtype=mainUsoSingular.dtype)
                # # Esto es igual para tiles de subceldas (2 m) y para tiles de MetricOs (metricos)
                # xInfIzdaTile = self.miRasterRefMinXY[0] + (nRow * GLBNtileSizeEnPixelsRasterRx * GLBNmetrosRasterRx)
                # yInfIzdaTile = self.miRasterRefMinXY[1] + (nCol * GLBNtileSizeEnPixelsRasterRx * GLBNmetrosRasterRx)
                if nRow == 0:
                    xInfIzdaTile = (self.miRasterRefMinXY[0] - margenXsobresalienteMetros)
                    recorteIniY = 0
                    recorteIniY1m = 0
                else:
                    xInfIzdaTile = (
                        self.miRasterRefMinXY[0]
                        + (
                            LCLtileSizeMetros
                            - margenXsobresalienteMetros
                            - LCLtileSemiSolapeMetros
                        )
                        + ((nRow - 1) * GLBNtileKernelMetros)
                        - LCLtileSemiSolapeMetros
                    )
                    recorteIniY = int(
                        (
                            GLBNtileSizeEnPixelsRasterRy
                            - margenYsobresalientePixelsRxA
                            - GLBNtileSemiSolapePixelsRasterRy
                        )
                        + ((nRow - 1) * GLBNtileKernelPixelsRasterRy)
                        - GLBNtileSemiSolapePixelsRasterRy
                    )
                    recorteIniY1m = int(
                        (
                            GLBNtileSizeEnPixelsCeldilla
                            - margenYsobresalientePixelsCdA
                            - GLBNtileSemiSolapePixelsCeldilla
                        )
                        + ((nRow - 1) * GLBNtileKernelPixelsCeldilla)
                        - GLBNtileSemiSolapePixelsCeldilla
                     )
                if nCol == 0:
                    yInfIzdaTile = (self.miRasterRefMinXY[1] - margenYsobresalienteMetros)
                    recorteIniX = 0
                    recorteIniX1m = 0
                else:
                    yInfIzdaTile = (
                        self.miRasterRefMinXY[1]
                        + (
                            LCLtileSizeMetros
                            - margenYsobresalienteMetros
                            - LCLtileSemiSolapeMetros
                        )
                        + ((nCol - 1) * GLBNtileKernelMetros)
                        - LCLtileSemiSolapeMetros
                    )
                    recorteIniX = int(
                        (
                            GLBNtileSizeEnPixelsRasterRx
                            - margenXsobresalientePixelsRxA
                            - GLBNtileSemiSolapePixelsRasterRx
                        )
                        + ((nCol - 1) * GLBNtileKernelPixelsRasterRx)
                        - GLBNtileSemiSolapePixelsRasterRx
                    )
                    recorteIniX1m = int(
                        (
                            GLBNtileSizeEnPixelsCeldilla
                            - margenXsobresalientePixelsCdA
                            - GLBNtileSemiSolapePixelsCeldilla
                        )
                        + ((nCol - 1) * GLBNtileKernelPixelsCeldilla)
                        - GLBNtileSemiSolapePixelsCeldilla
                    )
    
                if nRow == 0:
                    iniY = margenYsobresalientePixelsRxA
                    iniY1m = margenYsobresalientePixelsCdA
                else:
                    iniY = 0
                    iniY1m = 0
                if nCol == 0:
                    iniX = margenXsobresalientePixelsRxA
                    iniX1m = margenXsobresalientePixelsCdA
                else:
                    iniX = 0
                    iniX1m = 0
    
                if nRow == numTilesRows - 1:
                    finY = int(GLBNtileSizeEnPixelsRasterRy - margenYsobresalientePixelsRxB)
                    finY1m = int(GLBNtileSizeEnPixelsCeldilla - margenYsobresalientePixelsCdB)
                else:
                    finY = int(GLBNtileSizeEnPixelsRasterRy)
                    finY1m = int(GLBNtileSizeEnPixelsCeldilla)
                if nCol == numTilesCols - 1:
                    finX = int(GLBNtileSizeEnPixelsRasterRx - margenXsobresalientePixelsRxB)
                    finX1m = int(GLBNtileSizeEnPixelsCeldilla - margenXsobresalientePixelsCdB)
                else:
                    finX = int(GLBNtileSizeEnPixelsRasterRx)
                    finX1m = int(GLBNtileSizeEnPixelsCeldilla)
        
                if GLO.GLBLverbose:
                    print('\tclidcarto->>> tiles 2m:', nRow, nCol, '->', iniY, finY, iniX, finX,
                          '->1m', nRow, nCol, '->', iniY1m, finY1m, iniX1m, finX1m)
                    print('\t\ttiles 2m recorte', recorteIniY, recorteIniY + finY - iniY,
                          recorteIniX, recorteIniX + finX - iniX,
                          '->1m recorte', recorteIniY1m, recorteIniY1m + finY1m - iniY1m,
                          recorteIniX1m, recorteIniX1m + finX1m - iniX1m)


                usoSingRecorteShape = mainUsoSingular[recorteIniY : recorteIniY + finY - iniY, recorteIniX : recorteIniX + finX - iniX].shape
                funY = iniY + usoSingRecorteShape[0]
                funX = iniX + usoSingRecorteShape[1]
                if tileRecorte[iniY:funY, iniX:funX].shape == usoSingRecorteShape:
                    tileRecorte[iniY:funY, iniX:funX] = mainUsoSingular[recorteIniY : recorteIniY + finY - iniY, recorteIniX : recorteIniX + finX - iniX]
                else:
                    print(
                        'ATENCION: REVISAR LIMITES DE LAS CAPAS DE REFERENCIA 1. nRow: {}, nCol: {} -> tileRecorte.shape: {} != usoSingusoSingRecorteShape: {}'.format(
                            nRow, nCol,
                            tileRecorte[iniY:finY, iniX:finX].shape,
                            usoSingRecorteShape,
                        )
                    )
                    self.tilesRecortadosOk = False
                    continue
                if (
                    GLO.GLBLcrearTilesTargetDeCartoRefSoloSiHaySingUseSuficientes
                    and (
                        GLO.GLBLsoloCrearTilesNoGuardarAsc
                        or (
                            not GLO.GLBLpredecirCubiertasSingularesConvolucional
                            and not GLO.GLBLpredecirClasificaMiniSubCelConvolucional
                        )
                    )
                ):
                    # porcentajeUsoSingular = 100.0 * (
                    #     np.count_nonzero(tileRecorte != 0) - np.count_nonzero(tileRecorte == 9)
                    # ) / (
                    #     tileRecorte.shape[0] * tileRecorte.shape[1]
                    # )
                    countHistograma = np.bincount(tileRecorte.flatten())
                    # porcentajeUsoSingular_ = 100.0 * (countHistograma[1:9].sum() / countHistograma.sum())
                    if GLO.GLBLverbose:
                        print(
                            'clidcarto-> Tile {}_{} ->histograma de usos singulares: {}'.format(
                                nRow, nCol,
                                countHistograma
                            )
                        )
                    try:
                        listaNumMinPixelesTxt = (GLO.GLBLminPixelesCartoRef_Rio_Emb_Camino_FFCC_Ctra_CtraUrb_Pte_Edific).split()
                        listaNumMinPixeles = [int(i) for i in listaNumMinPixelesTxt]
                        numMinPixelesRios = listaNumMinPixeles[0]
                        numMinPixelesEmbalsesLagos = listaNumMinPixeles[1]
                        numMinPixelesCaminos = listaNumMinPixeles[2]
                        numMinPixelesFerrocarriles = listaNumMinPixeles[3]
                        numMinPixelesCarreteras = listaNumMinPixeles[4]
                        numMinPixelesCalzadasUrbanas = listaNumMinPixeles[5]
                        numMinPixelesPuentes = listaNumMinPixeles[6]
                        numMinPixelesEdific = listaNumMinPixeles[7]
                    except:
                        print(
                            'clidcarto-> ATENCION, error al interpretar GLBLminPixelesCartoRef_Rio_Emb_Camino_FFCC_Ctra_CtraUrb_Pte_Edific: {}'.format(
                                GLO.GLBLminPixelesCartoRef_Rio_Emb_Camino_FFCC_Ctra_CtraUrb_Pte_Edific
                            )
                        )
                        print('\t-> Se adoptan valores por defecto')
                        numMinPixelesRios = 100
                        numMinPixelesEmbalsesLagos = 500
                        numMinPixelesCaminos = 200
                        numMinPixelesFerrocarriles = 200
                        numMinPixelesCarreteras = 400
                        numMinPixelesCalzadasUrbanas = 500
                        numMinPixelesPuentes = 10
                        numMinPixelesEdific = 200
                    aPixelesSingulares = np.zeros(10, dtype=np.uint8)
                    for usoSingular in range(len(aPixelesSingulares)):
                        if len(countHistograma) > usoSingular:
                            aPixelesSingulares[usoSingular] = countHistograma[usoSingular]
                    if (
                        aPixelesSingulares[1] < numMinPixelesRios
                        and aPixelesSingulares[2] < numMinPixelesEmbalsesLagos
                        and aPixelesSingulares[3] < numMinPixelesCaminos
                        and aPixelesSingulares[4] < numMinPixelesFerrocarriles
                        and aPixelesSingulares[5] < numMinPixelesCarreteras
                        and aPixelesSingulares[6] < numMinPixelesCalzadasUrbanas
                        and aPixelesSingulares[7] < numMinPixelesPuentes
                        and aPixelesSingulares[8] < numMinPixelesEdific
                    ):
                        continue

                self.numTilesGenerados += 1

                usoSingRecorteShape = mainUsoSingular[recorteIniY1m : recorteIniY1m + finY1m - iniY1m, recorteIniX1m : recorteIniX1m + finX1m - iniX1m].shape
                funY1m = iniY1m + usoSingRecorteShape[0]
                funX1m = iniX1m + usoSingRecorteShape[1]
                if (
                    tileRecorte1m[iniY1m:funY1m, iniX1m:funX1m].shape
                    == mainUsoSingular[recorteIniY1m : recorteIniY1m + finY1m - iniY1m, recorteIniX1m : recorteIniX1m + finX1m - iniX1m].shape
                ):
                    tileRecorte1m[iniY1m:funY1m, iniX1m:funX1m] = mainUsoSingular[
                        recorteIniY1m : recorteIniY1m + finY1m - iniY1m, recorteIniX1m : recorteIniX1m + finX1m - iniX1m
                    ]
                else:
                    print('ATENCION: REVISAR LIMITES DE LAS CAPAS DE REFERENCIA 2', tileRecorte1m[iniY1m:finY1m, iniX1m:finX1m].shape, usoSingRecorteShape)

                #                 if (nRow + 1) * GLBNtileSizeEnPixelsRasterRy <= mainUsoSingular.shape[0] and\
                #                    (nCol + 1) * GLBNtileSizeEnPixelsRasterRx <= mainUsoSingular.shape[1]:
                #                     tileRecorte = mainUsoSingular[nRow * GLBNtileSizeEnPixelsRasterRy :
                #                                                   (nRow + 1) * GLBNtileSizeEnPixelsRasterRy,
                #                                                   nCol * GLBNtileSizeEnPixelsRasterRx :
                #                                                   (nCol + 1) * GLBNtileSizeEnPixelsRasterRx ]
                #                 elif (nRow + 1) * GLBNtileSizeEnPixelsRasterRy <= mainUsoSingular.shape[0]:
                #                     reCorteX = mainUsoSingular.shape[1] - (nCol * GLBNtileSizeEnPixelsRasterRx)
                #                     tileRecorte = np.zeros((GLBNtileSizeEnPixelsRasterRy, GLBNtileSizeEnPixelsRasterRx), dtype=mainUsoSingular.dtype)
                #                     tileRecorte[:, :reCorteX] = mainUsoSingular[nRow * GLBNtileSizeEnPixelsRasterRy :
                #                                                                 (nRow + 1) * GLBNtileSizeEnPixelsRasterRy,
                #                                                                 nCol * GLBNtileSizeEnPixelsRasterRx :
                #                                                                 mainUsoSingular.shape[1]]
                #                 elif (nCol + 1) * GLBNtileSizeEnPixelsRasterRx <= mainUsoSingular.shape[1]:
                #                     reCorteY = mainUsoSingular.shape[0] - (nRow * GLBNtileSizeEnPixelsRasterRy)
                #                     tileRecorte = np.zeros((GLBNtileSizeEnPixelsRasterRy, GLBNtileSizeEnPixelsRasterRx), dtype=mainUsoSingular.dtype)
                #                     tileRecorte[:reCorteY, :] = mainUsoSingular[nRow * GLBNtileSizeEnPixelsRasterRy :
                #                                                                 mainUsoSingular.shape[0],
                #                                                                 nCol * GLBNtileSizeEnPixelsRasterRx :
                #                                                                 (nCol + 1) * GLBNtileSizeEnPixelsRasterRx]
                #                 else:
                #                     reCorteY = mainUsoSingular.shape[0] - (nRow * GLBNtileSizeEnPixelsRasterRy)
                #                     reCorteX = mainUsoSingular.shape[1] - (nCol * GLBNtileSizeEnPixelsRasterRx)
                #                     tileRecorte = np.zeros((GLBNtileSizeEnPixelsRasterRy, GLBNtileSizeEnPixelsRasterRx), dtype=mainUsoSingular.dtype)
                #                     tileRecorte[:reCorteY, :reCorteX] = mainUsoSingular[nRow * GLBNtileSizeEnPixelsRasterRy :
                #                                                                         mainUsoSingular.shape[0],
                #                                                                         nCol * GLBNtileSizeEnPixelsRasterRx :
                #                                                                         mainUsoSingular.shape[1]]
                #                     #print( '\t\tclidcarto-> el tile', nRow, nCol, 'excede las dimensiones de array SingUse:', mainUsoSingular.shape, 'GLBNtileSizeEnPixelsRasterRy:', GLBNtileSizeEnPixelsRasterRy, 'GLBNtileSizeEnPixelsRasterRx', GLBNtileSizeEnPixelsRasterRx)

                # Interpolacion con scipy: como es una capa con clases: polinomio de orden 0 para que no interpole valores (vecino mas proximo)
                tileRecorteZoom = scipy.ndimage.interpolation.zoom(
                    tileRecorte, GLBNtileSizeEnPixelsSubCelda / GLBNtileSizeEnPixelsRasterRx, order=ordenPolinomioInterpolacion, prefilter=True
                )

                if GLO.GLBLverbose:
                    print('\t\tclidcarto-> tileRecorte.shape', tileRecorte.shape, 'mainUsoSingular.shape', mainUsoSingular.shape)
                    print('\t\tclidcarto-> usoSingRecorteShape', usoSingRecorteShape, tileRecorte[iniY:funY, iniX:funX].shape)

                if GLO.GLBLverbose:
                    print('clidcarto-> revisando capa {}, nCol: {}, nRow: {}, tileRecorte: {}, tileRecorteZoom: {}'.format(
                        self.nombreCapa, 
                        nCol, nRow,
                        tileRecorte.shape, tileRecorteZoom.shape))
                    print('\t->> tiles ->',
                          '2m-> Ini-Fin X->', iniX, finX, 'Ini-Fin Y->', iniY, finY,
                          '1m->', nRow, nCol, '->', iniY1m, finY1m, iniX1m, finX1m)
                    print('\t->> tiles ->2m-> recorte del raster-> recorteIni-Fin Y:', recorteIniY, recorteIniY + finY - iniY,
                          'recorteIni-Fin X:', recorteIniX, recorteIniX + finX - iniX,
                          '->1m recorte', recorteIniY1m, recorteIniY1m + finY1m - iniY1m,
                          recorteIniX1m, recorteIniX1m + finX1m - iniX1m)

                # print(tileRecorte[10:13, 10:13])
                # print(tileRecorteZoom[10:13, 10:13])

                # Si la capa original tiene pixel de 1 m, no hay zoom (GLBNtileSizeEnPixelsCeldilla=GLBNtileSizeEnPixelsRasterRx -> 1:1)
                tileRecorteZoom1m = scipy.ndimage.interpolation.zoom(
                    tileRecorte1m, GLBNtileSizeEnPixelsCeldilla / GLBNtileSizeEnPixelsRasterRx, order=ordenPolinomioInterpolacion, prefilter=True
                )

                if GLO.GLBLformatoTilesNpz:
                    npzFileName = os.path.join(self.trainPathNpz, '%s_%s_%i_%i.npz' % (self.fileCoordYear, 'Train', nRow, nCol))
                    np.savez_compressed(npzFileName, capa=tileRecorteZoom)

                if GLO.GLBLformatoTilesPng:
                    # tileRecorteNormalizado = np.flip(normalizar8bits(tileRecorteZoom).transpose(1, 0), axis=0)
                    # Los valores son clases, no hay que normalizar
                    # ->Giro el array 90 grados levogiros para cambiarlo al formato de las imagenes: filas<=>y, columnas<=>x).
                    #  Tb se puede hacer con imagenPng = np.rot90(array)
                    tileRecorteNormalizado = np.flip(tileRecorteZoom.transpose(1, 0), axis=0)
                    pngFileName = os.path.join(self.trainPathPng, '%s_%s_%i_%i.png' % (self.fileCoordYear, 'Train', nRow, nCol))

                    # -> colorMode
                    #  The mode of an image defines the type and depth of a pixel in the image.
                    #  Each pixel uses the full range of the bit depth.
                    #  So a 1-bit pixel has a range of 0-1, an 8-bit pixel has a range of 0-255 and so on.
                    #  1 (1-bit pixels, black and white, stored with one pixel per byte)
                    #  L (8-bit pixels, black and white)
                    #  P (8-bit pixels, mapped to any other mode using a color palette)
                    #  RGB (3x8-bit pixels, true color)
                    #  RGBA (4x8-bit pixels, true color with transparency mask)
                    # The Python Imaging Library uses a Cartesian pixel coordinate system, with (0,0) in the upper left corner.
                    # Note that the coordinates refer to the implied pixel corners;
                    # the centre of a pixel addressed as (0, 0) actually lies at (0.5, 0.5).
                    # colorMode = 'P' # (8-bit pixels, mapped to any other mode using a color palette) #Genera imagenes que no me valen ->Espacio de color: Color indexado (256 colores)
                    colorMode = 'L'  # (8-bit pixels, black and white) -> lleva el valor max a 255 y el min a 0 -> No respeta los valores del array ->Espacio de color: Escala de grises
                    if os.path.exists(pngFileName) and not LCLmantenerTilesGuardados:
                        print('clidcarto-> Eliminando tile pngFromVector previo: {}'.format(pngFileName))
                        os.remove(pngFileName)
                    Image.fromarray(tileRecorteNormalizado, colorMode).save(pngFileName)

                    if (
                        GLO.GLBLcrearTilesExDataCartoSinguEdiXXXYY
                        and not self.trainPathExDataCartoRefA is None
                    ):
                        if TRNStilesRefuerzo:
                            pesoOkData = 5
                        else:
                            pesoOkData = 1
                        lookupTableA = [0 if (i == 9) else pesoOkData for i in range(256)]
                        for usoSingNoData in GLO.GLBLlistaUsosSingularesExDataAlCrearTilesTargetDeCartoRefA:
                            if usoSingNoData == 'X' or usoSingNoData == '_':
                                continue
                            try:
                                lookupTableA[int(usoSingNoData)] = 0
                            except:
                                pass
                        lookupTableB = [0 if (i == 9) else pesoOkData for i in range(256)]
                        for usoSingNoData in GLO.GLBLlistaUsosSingularesExDataAlCrearTilesTargetDeCartoRefB:
                            if usoSingNoData == 'X' or usoSingNoData == '_':
                                continue
                            try:
                                lookupTableB[int(usoSingNoData)] = 0
                            except:
                                pass
                        pngFileNameExDataA = os.path.join(
                            self.trainPathExDataCartoRefA,
                            '%s_%s_%i_%i.png' % (self.fileCoordYear, 'Train', nRow, nCol)
                        )
                        pngFileNameExDataB = os.path.join(
                            self.trainPathExDataCartoRefB,
                            '%s_%s_%i_%i.png' % (self.fileCoordYear, 'Train', nRow, nCol)
                        )

                        # Mapeo las 10 categorias de tileRecorteNormalizado a 1 y 0 (ceros las que se excluyen del entrenamiento):
                        # Atencion: si uso colorMode = 'L' tengo que usar dtype=np.uint8
                        colorMode = 'L'  # (8-bit pixels, black and white) -> lleva el valor max a 255 y el min a 0 -> No respeta los valores del array ->Espacio de color: Escala de grises
                        tileRecorteExDataA = np.array(
                            [lookupTableA[val] for val in tileRecorteNormalizado.flatten()],
                            dtype=np.uint8
                        ).reshape(tileRecorteNormalizado.shape)
                        tileRecorteExDataB = np.array(
                            [lookupTableB[val] for val in tileRecorteNormalizado.flatten()],
                            dtype=np.uint8
                        ).reshape(tileRecorteNormalizado.shape)
                        if os.path.exists(pngFileNameExDataA) and not LCLmantenerTilesGuardados:
                            print('clidcarto-> Eliminando tile ExDataFromVector previo: {}'.format(pngFileNameExDataA))
                            os.remove(pngFileNameExDataA)
                        if os.path.exists(pngFileNameExDataB) and not LCLmantenerTilesGuardados:
                            print('clidcarto-> Eliminando tile ExDataFromVector previo: {}'.format(pngFileNameExDataB))
                            os.remove(pngFileNameExDataB)
                        Image.fromarray(tileRecorteExDataA, colorMode).save(pngFileNameExDataA)
                        # print('clidcato-> Creado tileA',pngFileNameExDataA)
                        Image.fromarray(tileRecorteExDataB, colorMode).save(pngFileNameExDataB)
                        # print('clidcato-> Creado tileB',pngFileNameExDataB)

                        if False:
                            # Esta es otra forma de generar el exData a partir de los png
                            # Se puede hacer a posteriori, como hago en genaux.py
                            colorMode = '1'  #  1 (1-bit pixels, black and white, stored with one pixel per byte)
                            myImg = Image.open(pngFileName)
                            NewImg = myImg.point(lookupTableA)
                            NewImg.save(pngFileNameExDataA)

                    if self.trainPathPng1m != '':
                        tileRecorteNormalizado1m = np.flip(tileRecorteZoom1m.transpose(1, 0), axis=0)
                        pngFileName1m = os.path.join(self.trainPathPng1m, '%s_%s_%i_%i.png' % (self.fileCoordYear, 'Train', nRow, nCol))
                        if os.path.exists(pngFileName1m) and not LCLmantenerTilesGuardados:
                            print('clidcarto-> Eliminando tile 1mFromVector previo: {}'.format(pngFileName1m))
                            os.remove(pngFileName1m)
                        Image.fromarray(tileRecorteNormalizado1m, colorMode).save(pngFileName1m)

                if GLO.GLBLformatoTilesAscRasterRef:
                    ascFileNameScipyZoom = os.path.join(self.trainPathAsc, '%s_%s_%i_%i.asc' % (self.fileCoordYear, self.nombreCapa, nRow, nCol))
                    # print('clidcarto-> creando asc from vectorRaster', self.nombreCapa, nRow, nCol, tileRecorteZoom.shape, GLBNtileSizeEnPixelsSubCelda, GLBNtileSizeEnPixelsSubCelda)
                    crearASC(
                        ascFileNameScipyZoom,
                        tileRecorteZoom,
                        tileRecorteZoom.shape,
                        GLBNtileSizeEnPixelsSubCelda,
                        GLBNtileSizeEnPixelsSubCelda,
                        GLO.GLBLmetrosSubCelda,
                        xInfIzdaTile,
                        yInfIzdaTile,
                        0,
                        nTipoDato=1,
                    )

        cargarSample = False
        if cargarSample:
            npzFileSampleName = os.path.join(self.trainPathNpz, '%s_%s_%i_%i.npz' % (self.fileCoordYear, self.nombreCapa, 0, 0))
            npzfileSample = np.load(npzFileSampleName, allow_pickle=True)
            if GLO.GLBLverbose:
                print('\t\tclidcarto-> arrays guardadas en npzFileSampleName:', npzfileSample.files)
                print('\t\tclidcarto-> Contenido del primer array ( shape:', npzfileSample[npzfileSample.files[0]].shape, '):')
                print(npzfileSample[npzfileSample.files[0]])


# ==============================================================================
class CartoRefRaster(object):
    """
    classdocs
    """

    # ooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo
    def __init__(
            self,
            myLasHead,
            myLasData,
            rutaCartoCompleta,
            nombreCapaInputRaster,
            tipoInfoRaster='',
            LCLhusoUTM=30,
            LCLverbose=False,
        ):
        self.myLasHead = myLasHead
        self.myLasData = myLasData
        self.rutaCartoCompleta = rutaCartoCompleta
        self.nombreCapaInputRaster = nombreCapaInputRaster
        self.tipoInfoRaster = tipoInfoRaster
        self.LCLhusoUTM = LCLhusoUTM
        self.LCLverbose = LCLverbose

        self.intersectMinX = 0
        self.intersectMinY = 0
        self.intersectMaxX = 0
        self.intersectMaxY = 0
        self.rasterRefMetrosPixelX = 0
        self.rasterRefMetrosPixelY = 0
        self.nCeldasX_Intersec = 0
        self.nCeldasY_Intersec = 0
        self.xOffRaster = 0
        self.yOffRaster = 0

        self.miRasterRefVentanaOk = 0
        self.rasterIncluyeLas = 0
        self.noDataRasterRef = GLO.GLBLnoData

        self.usarRasterRef = 0
        self.chequearPuntosDeEjemplo = True

        self.miRasterRefOrigen = np.array([0, 0], dtype=np.float32)
        self.miRasterRefPixel = np.array([0, 0], dtype=np.float32)
        self.miRasterRefNumCeldas = np.array([0, 0], dtype=np.float32)
        self.miRasterRefCoordenadas = np.array([0, 0, 0, 0], dtype=np.float32)


    # ooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo
    def leerArraysGuardadasVuelta01_cartoRefRaster(self, npzFileNameArraysVuelta0a1, LCLverbose=False):
        self.LCLverbose = LCLverbose
        if GLO.GLBLverbose or self.LCLverbose:
            print('\t-> clidndat-> Leyendo npz:', npzFileNameArraysVuelta0a1)
        if os.path.exists(npzFileNameArraysVuelta0a1):
            try:
                npzArraysVuelta01 = np.load(npzFileNameArraysVuelta0a1, allow_pickle=True)
                if GLO.GLBLverbose or self.LCLverbose:
                    print('\tLista de arrays guardadas en npz:')
                for nArray in range(len(npzArraysVuelta01.files)):
                    npzArrayName = npzArraysVuelta01.files[nArray]
                    npzArrayData = npzArraysVuelta01[npzArrayName]
                    if GLO.GLBLverbose or self.LCLverbose:
                        try:
                            if npzArrayData.shape[0] < 10:
                                print('\t-> Array:', npzArrayName, '-> shape:', npzArrayData.shape, '-> dtype:', npzArrayData.dtype, 'Valores:', npzArrayData)
                            else:
                                print('\t-> Array:', npzArrayName, '-> shape:', npzArrayData.shape, '-> dtype:', npzArrayData.dtype)
                        except:
                            print('\t-> Variable:', npzArrayName, 'Valor:', npzArrayData)
                    if npzArrayData.shape == (): # ndim = 0
                        setattr(self, npzArrayName, npzArrayData.item())
                        if GLO.GLBLverbose or self.LCLverbose:
                            print('\t\t-> Valor asignado:', getattr(self, npzArrayName), type(getattr(self, npzArrayName)))
                    else:
                        setattr(self, npzArrayName, npzArrayData)
                        if GLO.GLBLverbose or self.LCLverbose:
                            try:
                                if npzArrayData.shape[0] < 10:
                                    print('\t\t-> Array asignada:', type(getattr(self, npzArrayName)), getattr(self, npzArrayName))
                                else:
                                    print('\t\t-> Array asignada:', type(getattr(self, npzArrayName)))
                            except:
                                print('\t\t-> Valor asignado:', type(getattr(self, npzArrayName)), getattr(self, npzArrayName))
                self.leidoNpzVuelta0a1 = True
            except:
                print('clidcarto-> Aviso: error intentando leer {}'.format(npzFileNameArraysVuelta0a1))
                print('\t-> Es probable que el fichero este corrupto por producirse una interrupcion mientras se generaba')
                print('\t-> Se intenta borrar ese fichero:')
                try:
                    os.remove(npzFileNameArraysVuelta0a1)
                    print('\t\t-> Fichero npz borrado ok.')
                except:
                    print('\t\t-> Aviso: no se ha podido borrar el Fichero npz.')
                self.leidoNpzVuelta0a1 = False
        else:
            print('\tAtencion: no se encuentra el npz:', npzFileNameArraysVuelta0a1)
            self.leidoNpzVuelta0a1 = False

        if self.leidoNpzVuelta0a1:
            # try:
            #     print('self.miRasterRefVentanaOk:', self.miRasterRefVentanaOk)
            # except:
            #     print('El fichero no tiene la variable miRasterRefVentanaOk')
            #     self.miRasterRefVentanaOk = 0
            if not hasattr(self, 'miRasterRefVentanaOk'):
                print('El fichero no tiene la variable miRasterRefVentanaOk')
                self.miRasterRefVentanaOk = 0


    # ooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo
    def guardarArraysTrasVuelta01_cartoRefRaster(self, npzFileNameArraysVuelta0a1_cartoRefLandCover):
        np.savez_compressed(
            npzFileNameArraysVuelta0a1_cartoRefLandCover,
            nombreCapaInputRaster=self.nombreCapaInputRaster,
            reClassList=self.reClassList,
            miRasterRefVentanaOk=self.miRasterRefVentanaOk,
            usarRasterRef=self.usarRasterRef,
            aCeldasRasterRef=self.aCeldasRasterRef,
            miRasterRefPixel=self.miRasterRefPixel,
            miRasterRefCoordenadas=self.miRasterRefCoordenadas,
        )


    # oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo
    def dimensionarRaster(self):

        if self.tipoInfoRaster == 'landCover':
            self.tipoDatoRaster = np.uint8
            self.nBandasPrevistas = 1
            LCLrasterPixelSize = GLO.GLBLrasterPixelSize
            LCLrasterPixelSizeX = LCLrasterPixelSize
            LCLrasterPixelSizeY = LCLrasterPixelSize
        elif self.tipoInfoRaster == 'Mdt':
            self.tipoDatoRaster = np.float32
            self.nBandasPrevistas = 1
            LCLrasterPixelSize = GLO.GLBLrasterPixelSize
            LCLrasterPixelSizeX = LCLrasterPixelSize
            LCLrasterPixelSizeY = LCLrasterPixelSize
        elif self.tipoInfoRaster == 'Orto':
            self.tipoDatoRaster = np.uint8
            self.nBandasPrevistas = 4
            LCLrasterPixelSize = 0.25
            LCLrasterPixelSizeX = LCLrasterPixelSize
            LCLrasterPixelSizeY = LCLrasterPixelSize
        elif self.tipoInfoRaster == 'EGM08':
            self.tipoDatoRaster = np.float32
            # Raster de X: 818 Y: 657 pixeles
            self.nBandasPrevistas = 1
            LCLrasterPixelSize = 1565.073809109065223
            LCLrasterPixelSizeX = LCLrasterPixelSize
            LCLrasterPixelSizeY = LCLrasterPixelSize
            # Raster de X: 818 Y: 657 pixeles
        else:
            self.tipoDatoRaster = np.int8
            self.nBandasPrevistas = 1
            LCLrasterPixelSize = GLO.GLBLrasterPixelSize
            LCLrasterPixelSizeX = LCLrasterPixelSize
            LCLrasterPixelSizeY = LCLrasterPixelSize

        if self.LCLhusoUTM != 30:
            self.xminBloqueH30 = self.myLasHead.xminBloqueH30
            self.yminBloqueH30 = self.myLasHead.yminBloqueH30
            self.xmaxBloqueH30 = self.myLasHead.xmaxBloqueH30
            self.ymaxBloqueH30 = self.myLasHead.ymaxBloqueH30
        else:
            self.xminBloqueH30 = self.myLasHead.xmin
            self.yminBloqueH30 = self.myLasHead.ymin
            self.xmaxBloqueH30 = self.myLasHead.xmax
            self.ymaxBloqueH30 = self.myLasHead.ymax

        pixelRational = (float(abs(LCLrasterPixelSize))).as_integer_ratio()
        if pixelRational[1] == 1:
            # Numero entero
            metrosPorPixel = int(abs(LCLrasterPixelSize))
            pixelsPorMetro = 1
        elif float(1 / abs(LCLrasterPixelSize)).is_integer():
            # Fraccion entera de 1 m
            metrosPorPixel = 1
            pixelsPorMetro = int(1 / abs(LCLrasterPixelSize))
        elif pixelRational[1] < 10:
            # Numero fraccionario racional
            metrosPorPixel = pixelRational[0]
            pixelsPorMetro = pixelRational[1]
        else:
            metrosPorPixel = -1
            pixelsPorMetro = -1

        if self.LCLhusoUTM != 30:
            print(f'\ncartolider-> Ajustando la ventana del bloque Lidar a los pixeles del raster de referencia para que contenga integramente al bloque:')
            print(f'\t-> Previamente se abre la primera ortofoto, solo para conocer la dimension del pixel y hacer este ajuste antes de las intersecciones')
            print(f'\t\t-> Dimension del pixel -> rasterRefMetrosPixelX: {self.rasterRefMetrosPixelX}; rasterRefMetrosPixelY: {self.rasterRefMetrosPixelY}')
            print(f'\t\t-> metrosPorPixel/pixelsPorMetro: {metrosPorPixel}/{pixelsPorMetro}')
            print(f'\t-> Antes del ajuste:')
            print(f'\t\t-> xminBloqueH30: {self.xminBloqueH30}; xmaxBloqueH30: {self.xmaxBloqueH30}')
            print(f'\t\t-> yminBloqueH30: {self.yminBloqueH30}; ymaxBloqueH30: {self.ymaxBloqueH30}')
        if pixelsPorMetro != -1 and metrosPorPixel != -1:
            self.xminBloqueH30 = (metrosPorPixel / pixelsPorMetro) * math.floor(self.xminBloqueH30 * (pixelsPorMetro / metrosPorPixel))
            self.xmaxBloqueH30 = (metrosPorPixel / pixelsPorMetro) * math.ceil(self.xmaxBloqueH30 * (pixelsPorMetro / metrosPorPixel))
            self.yminBloqueH30 = (metrosPorPixel / pixelsPorMetro) * math.floor(self.yminBloqueH30 * (pixelsPorMetro / metrosPorPixel))
            self.ymaxBloqueH30 = (metrosPorPixel / pixelsPorMetro) * math.ceil(self.ymaxBloqueH30 * (pixelsPorMetro / metrosPorPixel))
            if (self.ymaxBloqueH30 - self.yminBloqueH30) > (self.xmaxBloqueH30 - self.xminBloqueH30):
                self.xmaxBloqueH30 = self.xminBloqueH30 + (self.ymaxBloqueH30 - self.yminBloqueH30)
            if (self.xmaxBloqueH30 - self.xminBloqueH30) > (self.ymaxBloqueH30 - self.yminBloqueH30):
                self.ymaxBloqueH30 = self.yminBloqueH30 + (self.xmaxBloqueH30 - self.xminBloqueH30)
        if self.LCLhusoUTM == 29:
            print(f'\t-> Despues del ajuste:')
            print(f'\t\t-> xminBloqueH30: {self.xminBloqueH30}; xmaxBloqueH30: {self.xmaxBloqueH30}')
            print(f'\t\t-> yminBloqueH30: {self.yminBloqueH30}; ymaxBloqueH30: {self.ymaxBloqueH30}')


        # self.ySupIzdaDelLas = self.xSupIzdaDelNombre
        # self.ySupIzdaDelLas = self.ySupIzdaDelNombre
        # self.xSupIzdaDelLas = int(round(self.xSupIzdaFromLasHead, 0))
        # self.ySupIzdaDelLas = int(round(self.ySupIzdaFromLasHead, 0))
        self.xSupIzdaDelLas = self.myLasHead.xSupIzda
        self.ySupIzdaDelLas = self.myLasHead.ySupIzda

        nPixelesXraster = math.ceil((self.xmaxBloqueH30 - self.xminBloqueH30) / LCLrasterPixelSizeX)
        nPixelesYraster = math.ceil((self.ymaxBloqueH30 - self.yminBloqueH30) / LCLrasterPixelSizeY)

        if self.nBandasPrevistas == 1:
            self.aCeldasRasterRef = np.zeros([nPixelesXraster, nPixelesYraster], dtype=self.tipoDatoRaster)
        else:
            self.aCeldasRasterRef = np.zeros([self.nBandasPrevistas, nPixelesXraster, nPixelesYraster], dtype=self.tipoDatoRaster)


    # ooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo
    def leerRaster(self):
        if not gdalOk:
            print('\tclidcarto-> Gdal no disponible; no se puede leer %s' % (self.rasterRefFileName))
            self.usarRasterRef = 0
            return

        self.rasterRefFileName = os.path.join(self.rutaCartoCompleta, self.nombreCapaInputRaster)
        print('\t-> clidcarto-> Leyendo raster file', self.nombreCapaInputRaster)
        if not os.path.exists(self.rasterRefFileName):
            print('\tclidcarto-> no esta disponible el fichero %s' % (self.rasterRefFileName))
            self.usarRasterRef = 0
            return

        self.usarRasterRef = 1

        try:
            sourceDatasetRasterOriginal = gdal.Open(self.rasterRefFileName, gdalconst.GA_ReadOnly)
        except:
            sourceDatasetRasterOriginal = None
        if sourceDatasetRasterOriginal is None:
            print('\tclidcarto-> Error abriendo raster', self.rasterRefFileName)
            print('\t\t-> Comprobar si esta bloqueada por otra aplicacion o tiene algun error', self.rasterRefFileName)
            rasterUsable = False
            self.usarRasterRef = 0
            return

        self.usarRasterRef = 1
        infoSourceDatasetRasterOriginal = infoRasterDataset(sourceDatasetRasterOriginal, mostrar=GLO.GLBLverbose)
        # origenX_Imagen = infoSourceDatasetRasterOriginal['origenX']
        # origenY_Imagen = infoSourceDatasetRasterOriginal['origenY']
        self.rasterRefMetrosPixelX = infoSourceDatasetRasterOriginal['pixelX']
        self.rasterRefMetrosPixelY = infoSourceDatasetRasterOriginal['pixelY']
        # nPixelsX = infoSourceDatasetRasterOriginal['nPixelsX']
        # nPixelsY = infoSourceDatasetRasterOriginal['nPixelsY']
        self.nBandasRaster = infoSourceDatasetRasterOriginal['nBandas']
        sourceDatasetRasterOriginal = None

        self.dimensionarRaster()
        if self.nBandasPrevistas != self.nBandasRaster:
            print(f'clidcarto-> ATENCION: nBandasPrevistas:   {self.nBandasPrevistas}; nBandasRaster: {self.nBandasRaster} (deben ser iguales)')


        # coordVentana_ = np.array([self.xminBloqueH30, self.yminBloqueH30, self.xmaxBloqueH30, self.ymaxBloqueH30], dtype=np.float32) # Atencion, esta conversion a float32 elimina los decimales ??
        coordVentana = np.array([self.xminBloqueH30, self.yminBloqueH30, self.xmaxBloqueH30, self.ymaxBloqueH30])

        aNumCeldas = np.array([self.myLasData.nCeldasX, self.myLasData.nCeldasY], dtype=np.int32)
        (
            self.miRasterRefVentanaOk,
            self.rasterIncluyeLas,
            self.nBandasRaster,
            rasterRefRecortadoAsArrayInt,
            self.rasterRefMetrosPixelX,
            self.rasterRefMetrosPixelY,
            self.intersectMinX,
            self.intersectMinY,
            self.intersectMaxX,
            self.intersectMaxY,
            self.nCeldasX_Intersec,
            self.nCeldasY_Intersec,
            self.xOffRaster,
            self.yOffRaster,
            noData,
        ) = leerVentanaRaster(
            self.rasterRefFileName,
            coordVentana,
            aNumCeldas,
            self.tipoInfoRaster,
            self.nBandasPrevistas,
            self.tipoDatoRaster,
            gdalOk,
        )

        if not self.miRasterRefVentanaOk:
            #             rasterOk = 0
            #             #srcBandAsArrayInt = np.zeros(nCeldasX_Intersec * nCeldasY_Intersec, dtype=np.uint8).reshape(nCeldasX_Intersec, nCeldasY_Intersec)
            #             srcBandAsArrayInt = np.zeros(aNumCeldas[0] * aNumCeldas[1], dtype=np.uint8).reshape(aNumCeldas[0], aNumCeldas[1])
            #             pixelX = 0
            #             pixelY = 0
            #             intersectMinX = 0
            #             intersectMinY = 0
            #             intersectMaxX = 0
            #             intersectMaxY = 0
            #             nCeldasX_Intersec = 0
            #             nCeldasY_Intersec = 0
            #             xOffRaster = 0
            #             yOffRaster = 0
            #             noData = 0
            self.usarRasterRef = 0
            return

        self.rasterRefOrigenX = self.intersectMinX
        self.rasterRefOrigenY = self.intersectMaxY

        self.miRasterRefMinXY = np.array([self.intersectMinX, self.intersectMinY], dtype=np.float32)
        self.miRasterRefOrigen = np.array([self.rasterRefOrigenX, self.rasterRefOrigenY], dtype=np.float32)
        self.miRasterRefPixel = np.array([self.rasterRefMetrosPixelX, self.rasterRefMetrosPixelY], dtype=np.float32)
        self.miRasterRefNumCeldas = np.array([self.nCeldasX_Intersec, self.nCeldasY_Intersec], dtype=np.int32)
        self.miRasterRefCoordenadas = np.array([self.intersectMinX, self.intersectMaxX, self.intersectMinY, self.intersectMaxY], dtype=np.float32)

        # ======================================================================
        # Traspongo el raster y cambio el orden de la nY (arriba<->abajo)
        # Para revertir el orden ver: https://stackoverflow.com/questions/6771428/most-efficient-way-to-reverse-a-numpy-array
        # ->Giro la imagen 90 grados destrogiros para cambiarlo al formato de los arrays: filas<=>y, columnas<=>x).
        #  Tb se puede hacer con array = np.rot90(image, 3)
        # https://stackoverflow.com/questions/6771428/most-efficient-way-to-reverse-a-numpy-array
        # Uso de flip y [...::-1...]
        # https://numpy.org/doc/stable/reference/generated/numpy.flip.html
        # https://stackoverflow.com/questions/49545758/flip-or-reverse-columns-in-numpy-array
        # -> m[::-1] equivale a un np.flip(m, axis=0); el flip que necesitaria cuando hay varias bandas (bandas=axes 0) seria np.flip(m, axis=1)
        print('\t-> clidcarto-> rasterRefRecortadoAsArrayInt.shape (bandas, filas, columnas):', rasterRefRecortadoAsArrayInt.shape)
        if rasterRefRecortadoAsArrayInt.ndim == 2: # self.nBandasPrevistas = 1
            # mdt o landCover con 1 banda
            # self.aCeldasRasterRef = np.rot90(rasterRefRecortadoAsArrayInt, 3)
            self.aCeldasRasterRef = rasterRefRecortadoAsArrayInt[::-1].transpose()
            # self.aCeldasRasterRef = rasterRefRecortadoAsArrayInt[::-1]
        else: # self.nBandasPrevistas = 4
            # ortofoto con n bandas
            self.aCeldasRasterRef = np.rot90(rasterRefRecortadoAsArrayInt, k=3, axes=(1, 2))
            # self.aCeldasRasterRef = np.flip(rasterRefRecortadoAsArrayInt, axis=1)
        self.noDataRasterRef = 0 if noData is None else noData
        # ======================================================================

        if self.rasterRefMetrosPixelX == 0 or self.rasterRefMetrosPixelY == 0:
            print('clidcarto-> ATENCION: error en el raster', self.rasterRefFileName)
            print('\tclidcarto-> self.miRasterRefVentanaOk', self.miRasterRefVentanaOk)
            print('\tclidcarto-> self.rasterIncluyeLas', self.rasterIncluyeLas)
            print('\tclidcarto-> rasterRefRecortadoAsArrayInt', rasterRefRecortadoAsArrayInt)
            print('\tclidcarto-> self.rasterRefMetrosPixelX, self.rasterRefMetrosPixelY', self.rasterRefMetrosPixelX, self.rasterRefMetrosPixelY)
            print('\tclidcarto-> self.intersectMinX, self.intersectMinY', self.intersectMinX, self.intersectMinY)
            print('\tclidcarto-> self.intersectMaxX, self.intersectMaxY', self.intersectMaxX, self.intersectMaxY)
            print('\tclidcarto-> self.nCeldasX_Intersec, self.nCeldasY_Intersec', self.nCeldasX_Intersec, self.nCeldasY_Intersec)
            print('\tclidcarto-> self.xOffRaster, self.yOffRaster', self.xOffRaster, self.yOffRaster)
            self.miRasterRefVentanaOk = 0
            return
        elif self.chequearPuntosDeEjemplo:
            listaCeldas = clidnaux.celdasDeControl()
            for celdaDeControl in listaCeldas:
                nX, nY = celdaDeControl[0], celdaDeControl[1]
                coordX = self.xminBloqueH30 + ((nX + 0.5) * self.rasterRefMetrosPixelX)
                coordY = self.yminBloqueH30 - ((nY + 0.5) * self.rasterRefMetrosPixelY)  # rasterRefMetrosPixelY es negativo
                if self.nBandasPrevistas == 1:
                    if self.nombreCapaInputRaster == 'clasificacion_2017_diciembre_CyL_sieve':
                        print(
                            'clidcarto->landCover-> Clase de land conver en aCeldasRasterRef: celda %i, %i (center: %i, %i): %i'
                            % (nX, nY, coordX, coordY, self.aCeldasRasterRef[nX, nY])
                        )
                    elif self.nombreCapaInputRaster == 'PNOA_CYL_2014_MDE32Bit_10m':
                        print('clidcarto->landCover-> aCeldasRasterRef: celda %i, %i (center: %i, %i): %0.2f' % (nX, nY, coordX, coordY, self.aCeldasRasterRef[nX, nY]))
                else:
                    print(f'clidcarto-> RGBI (ortofoto) guardado en aCeldasRasterRef: celda {nX}, {nY} (center: {coordX}, {coordX}): {self.aCeldasRasterRef[:, nX, nY]}')

                # if self.nBandasPrevistas == 1:
                #     print( 'clidcarto-> noData', self.noDataRasterRef)
                #     numPixelsNoCero = 0
                #     for nY in reversed(range(self.myLasData.nCeldasY)):
                #        for nX in range(self.myLasData.nCeldasX):
                #            if self.aCeldasRasterRef[nXarray, nYarray] != self.noDataRasterRef:
                #                print(nX, nY, '->->->', self.aCeldasRasterRef[n, nY])
                #                numPixelsNoCero += 1
                #     print( 'clidcarto-> numPixelsNoCero', numPixelsNoCero)


    # oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo
    def crearRutasFromRaster(self):
        # Aviso: los tiles target de cartoSingu pueden ser comunes a varios entrenamientos
        # cambiando el exData para entrenar con unas categorias u otras
        if GLO.GLBLformatoTilesNpz:
            self.trainPathNpz = os.path.join(
                GLO.MAINrutaOutput,
                GLO.GLBL_TRAIN_DIR,
                'npz{}/'.format(self.tilesTargetPathTroncal)
            )
            if not os.path.isdir(self.trainPathNpz):
                numIntentosEscritura = 0
                while True:
                    numIntentosEscritura += 1
                    try:
                        os.makedirs(self.trainPathNpz)
                        break
                    except:
                        time.sleep(5)
                        if numIntentosEscritura > 5:
                            break
                if GLO.GLBLverbose:
                    print(
                        'cartolider.{}-> Creando directorio train_npz...: {}'.format(
                            self.fileCoordYear, self.trainPathNpz
                        )
                    )
        else:
            self.trainPathNpz = ''

        if GLO.GLBLsoloGuardarArraysNpzSinCrearOutputFiles:
            self.trainPathPng = ''
            self.trainPathAsc = ''
            return

        if GLO.GLBLformatoTilesPng:
            self.trainPathPng = os.path.join(
                GLO.MAINrutaOutput,
                GLO.GLBL_TRAIN_DIR,
                'png{}/'.format(self.tilesTargetPathTroncal)
            )
            if not os.path.isdir(self.trainPathPng):
                numIntentosEscritura = 0
                while True:
                    numIntentosEscritura += 1
                    try:
                        os.makedirs(self.trainPathPng)
                        break
                    except:
                        time.sleep(5)
                        if numIntentosEscritura > 5:
                            break
                if GLO.GLBLverbose:
                    print(
                        'cartolider.{}-> Creando directorio train_png...: {}'.format(
                            self.fileCoordYear, self.trainPathPng
                        )
                    )
        else:
            self.trainPathPng = ''

        if GLO.GLBLformatoTilesAscRasterRef:
            self.trainPathAsc = os.path.join(
                GLO.MAINrutaOutput,
                GLO.GLBL_TRAIN_DIR,
                'asc{}/'.format(self.tilesTargetPathTroncal)
            )
            if not os.path.isdir(self.trainPathAsc):
                numIntentosEscritura = 0
                while True:
                    numIntentosEscritura += 1
                    try:
                        os.makedirs(self.trainPathAsc)
                        break
                    except:
                        time.sleep(5)
                        if numIntentosEscritura > 5:
                            break
                if GLO.GLBLverbose:
                    print(
                        'cartolider.{}-> Creando directorio train/asc...: {}'.format(
                            self.fileCoordYear, self.trainPathAsc
                        )
                    )
        else:
            self.trainPathAsc = ''


    # ooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo
    def crearTilesTargetFromRaster(
        self,
        LCLtileSizeMetros=GLO.GLBLtileSizeMetros,
        LCLtileSemiSolapeMetros=GLO.GLBLtileSemiSolapeMetros,
        interpolarValores=False,
        LCLmantenerTilesGuardados=False
    ):

        # Generar tiles a partir de una capa originalmente raster
        if GLO.GLBLverbose:
            print('\t\tclidcarto-> Dimensiones del pixel de %s: %i x %i metros' % (self.nombreCapa, self.rasterRefMetrosPixelX, self.rasterRefMetrosPixelY))
            print('\t\tclidcarto-> nCeldas del recorte de %s: %i x %i celdas' % (self.nombreCapa, self.nCeldasX_Intersec, self.nCeldasY_Intersec))
            if GLO.GLBLformatoTilesNpz:
                print('\t\tclidcarto-> Guardando %s en %s' % (self.nombreCapa, self.trainPathNpz))
            if GLO.GLBLformatoTilesPng:
                print('\t\tclidcarto-> Guardando %s en %s' % (self.nombreCapa, self.trainPathPng))

        if interpolarValores:
            ordenPolinomioInterpolacion = 3
        else:
            ordenPolinomioInterpolacion = 0
        '''
        Pruebo a interpolar array de dos formas (PIL y scipy) y a guardar el resultado en dos formatos (npz y asc)
        PIL permite mas opciones de interpolacion pero requiere un paso intermedio, de pasarlo a imagen:
          https://www.geeksforgeeks.org/python-pil-image-resize-method/
        sciy solo permite interpolacion spline aunque permite modificar el orden del polinomio (0-5):
          https://docs.scipy.org/doc/scipy-0.15.1/reference/generated/scipy.ndimage.interpolation.zoom.html#scipy.ndimage.interpolation.zoom
        Con npz (np.savez_compressed) ocupan la tercera parte
        '''

#         GLBNtileSizeEnPixelsRasterRy = int(math.ceil(LCLtileSizeMetros / -self.rasterRefMetrosPixelY))
#         GLBNtileSizeEnPixelsRasterRx = int(math.ceil(LCLtileSizeMetros / self.rasterRefMetrosPixelX))
#         numTilesRows = int(math.ceil(self.aCeldasRasterRef.shape[0] / GLBNtileSizeEnPixelsRasterRy))
#         numTilesCols = int(math.ceil(self.aCeldasRasterRef.shape[1] / GLBNtileSizeEnPixelsRasterRx))
#         margenXsobresalienteMetros = ((numTilesCols * LCLtileSizeMetros) - GLO.GLBLmetrosBloque) / 2
#         margenYsobresalienteMetros = ((numTilesRows * LCLtileSizeMetros) - GLO.GLBLmetrosBloque) / 2
# 
#         GLBNtileSizeEnPixelsSubCelda = int(math.ceil(LCLtileSizeMetros / GLO.GLBLmetrosSubCelda)) # -> 128 ($256)
#         GLBNtileSizeEnPixelsCeldilla = int(math.ceil(LCLtileSizeMetros / GLO.GLBLmetrosCeldilla)) # -> 256 ($512)



        # ==========================================================================
        # Dimension de los pixels
        GLBNmetrosRasterRx = self.miRasterRefPixel[0] # 1.0 m
        GLBNmetrosRasterRy = self.miRasterRefPixel[1] # -1.0 m
        GLBNmetrosSubCelda = GLO.GLBLmetrosSubCelda # 2.0 m
        GLBNmetrosCeldilla = GLO.GLBLmetrosCeldilla # 1.0 m
        # ==========================================================================
        # Num de pixels del Tile para distintos pixelSize:
        GLBNtileSizeEnPixelsRasterRx = int(math.ceil(LCLtileSizeMetros / GLBNmetrosRasterRx)) # -> 256 ($512)
        GLBNtileSizeEnPixelsRasterRy = int(math.ceil(LCLtileSizeMetros / -GLBNmetrosRasterRy)) # -> 256 ($512)
        GLBNtileSizeEnPixelsSubCelda = int(math.ceil(LCLtileSizeMetros / GLBNmetrosSubCelda)) # -> 128 ($256)
        GLBNtileSizeEnPixelsCeldilla = int(math.ceil(LCLtileSizeMetros / GLBNmetrosCeldilla)) # -> 256 ($512)
        # ==========================================================================
        # SemiSolape y Kernel
        GLBNtileSemiSolapePixelsRasterRx = int(math.floor(LCLtileSemiSolapeMetros / GLBNmetrosRasterRx)) # -> 0 ($6)
        GLBNtileSemiSolapePixelsRasterRy = int(math.floor(LCLtileSemiSolapeMetros / -GLBNmetrosRasterRy)) # -> 0 ($6)
        GLBNtileSemiSolapePixelsSubCelda = int(math.floor(LCLtileSemiSolapeMetros / GLBNmetrosSubCelda)) # -> 0 ($3)
        GLBNtileSemiSolapePixelsCeldilla = int(math.floor(LCLtileSemiSolapeMetros / GLBNmetrosCeldilla)) # -> 0 ($6)
        GLBNtileKernelMetros = (LCLtileSizeMetros - (2 * LCLtileSemiSolapeMetros)) # -> 256 ($500)
        GLBNtileKernelPixelsRasterRx = (GLBNtileSizeEnPixelsRasterRx - (2 * GLBNtileSemiSolapePixelsRasterRx)) # -> 256 ($500)
        GLBNtileKernelPixelsRasterRy = (GLBNtileSizeEnPixelsRasterRy - (2 * GLBNtileSemiSolapePixelsRasterRy)) # -> 256 ($500)
        GLBNtileKernelPixelsSubCelda = (GLBNtileSizeEnPixelsSubCelda - (2 * GLBNtileSemiSolapePixelsSubCelda)) # -> 128 ($250)
        GLBNtileKernelPixelsCeldilla = (GLBNtileSizeEnPixelsCeldilla - (2 * GLBNtileSemiSolapePixelsCeldilla)) # -> 256 ($500)
        # ==========================================================================
        # Num de pixels del RasterRef (equivale a un bloque, normalmente de 2 x 2 km)
        if self.miRasterRefNumCeldas[0] != self.aCeldasRasterRef.shape[0] or self.miRasterRefNumCeldas[1] != self.aCeldasRasterRef.shape[1]:
            print('clidcarto-> Revisar esto porque algo no lo he hecho bien en la lectura del raster')
        nPixelsRasterRefX = self.miRasterRefNumCeldas[0] # -> 2000
        nPixelsRasterRefY = self.miRasterRefNumCeldas[1] # -> 2000
        # ==========================================================================
        # Numero de Tiles (nRows & nCols)
        numTilesRows = int(math.ceil(nPixelsRasterRefY / GLBNtileSizeEnPixelsRasterRy)) # -> 8 ($4)
        numTilesCols = int(math.ceil(nPixelsRasterRefX / GLBNtileSizeEnPixelsRasterRx)) # -> 8 ($4)
        # ==========================================================================
        # Margen que sobresalen los Tiles fuera del rasterRef (bloque)
        margenXsobresalienteMetros = LCLtileSemiSolapeMetros + (((numTilesCols * GLBNtileKernelMetros) - GLO.GLBLmetrosBloque) / 2) # -> 24 ($6)
        margenYsobresalienteMetros = LCLtileSemiSolapeMetros + (((numTilesRows * GLBNtileKernelMetros) - GLO.GLBLmetrosBloque) / 2) # -> 24 ($6)
        margenXsobresalientePixelsRxA = int(math.floor(margenXsobresalienteMetros / GLBNmetrosRasterRx))
        margenXsobresalientePixelsRxB = int(math.ceil(margenXsobresalienteMetros / GLBNmetrosRasterRx))
        margenYsobresalientePixelsRxA = int(math.floor(margenYsobresalienteMetros / GLBNmetrosRasterRx))
        margenYsobresalientePixelsRxB = int(math.ceil(margenYsobresalienteMetros / GLBNmetrosRasterRx))
        margenXsobresalientePixelsCdA = int(math.floor(margenXsobresalienteMetros / GLBNmetrosCeldilla))
        margenXsobresalientePixelsCdB = int(math.ceil(margenXsobresalienteMetros / GLBNmetrosCeldilla))
        margenYsobresalientePixelsCdA = int(math.floor(margenYsobresalienteMetros / GLBNmetrosCeldilla))
        margenYsobresalientePixelsCdB = int(math.ceil(margenYsobresalienteMetros / GLBNmetrosCeldilla))
        # ======================================================================

        # ======================================================================
        if LCLmantenerTilesGuardados:
            tilesEncontrados = True
            for nRow in range(numTilesRows):
                for nCol in range(numTilesCols):
                    pngFileName = os.path.join(self.trainPathPng, '%s_%s_%i_%i.png' % (self.fileCoordYear, 'Train', nRow, nCol))
                    if not os.path.exists(pngFileName):
                        tilesEncontrados = False
                        break
                if not tilesEncontrados:
                    break
            if tilesEncontrados:
                print('clidcarto-> No es necesario crear tiles porque ya se han creado previamente')
                return
        # ======================================================================

        if GLO.GLBLverbose:
            print('\tclidcarto->> Se van a crear %i x %i tiles' % (numTilesRows, numTilesCols))
            print('\t\tLCLtileSizeMetros:', LCLtileSizeMetros,
                  'LCLtileSemiSolapeMetros:', LCLtileSemiSolapeMetros,
                  'GLBNtileSemiSolapePixelsSubCelda:', GLBNtileSemiSolapePixelsSubCelda
            )
            print('\t\tGLBNtileKernelPixelsSubCelda:', GLBNtileKernelPixelsSubCelda,
                  'GLBNtileKernelMetros:', GLBNtileKernelMetros,
                  'GLBNtileKernelPixelsRasterRx:', GLBNtileKernelPixelsRasterRx,
                  'GLBNtileKernelPixelsRasterRy:', GLBNtileKernelPixelsRasterRy,
              )
                  
            print('\t\tGLBNtileSizeEnPixelsRasterRx 2m', GLBNtileSizeEnPixelsRasterRx,
                  'GLBNtileSizeEnPixelsCeldilla 1m', GLBNtileSizeEnPixelsCeldilla
            )
            print('\t\tGLBNtileSemiSolapePixelsRasterRx:', GLBNtileSemiSolapePixelsRasterRx,
                  'GLBNtileSemiSolapePixelsRasterRy:', GLBNtileSemiSolapePixelsRasterRy)
            print(
                '\t\tmargenXsobresalienteMetros', margenXsobresalienteMetros, '=', margenXsobresalienteMetros, 'm;',
                'margenYsobresalienteMetros', margenYsobresalienteMetros, '=', margenYsobresalienteMetros, 'm;',
                'margenXsobresalientePixelsRxA', margenXsobresalientePixelsRxA, 'pixels;'
            )

        if margenXsobresalienteMetros < 0 or margenYsobresalienteMetros < 0:
            print(
                '\nclidcarto-> ATENCION capa raster: {}-> reducir GLBLtileSemiSolapeMetros ({:0.1f} m) para que los tiles cubran todo el bloque.'.format(
                    self.nombreCapa,
                    LCLtileSemiSolapeMetros,
                )
            )
            print(
                'MargenX: {}; numTilesCols: {}, GLBNtileKernelMetros: {}, metrosBloque: {}'.format(
                    margenXsobresalienteMetros,
                    numTilesCols,
                    GLBNtileKernelMetros,
                    GLO.GLBLmetrosBloque
                )
            )
            # sys.exit(0)
#         elif LCLtileSemiSolapeMetros % GLBNmetrosRasterRx != 0:
#             print(
#                 '\nclidcarto-> ATENCION: cambiar GLBLtileSemiSolapeMetros ({:0.1f} m) para que el semi-solape sea un numero entero de subCeldas (subcelda: {} m)'.format(
#                     LCLtileSemiSolapeMetros,
#                     GLBNmetrosRasterRx,
#                 )
#             )
#             sys.exit(0)
#         elif margenXsobresalienteMetros % GLBNmetrosRasterRx != 0 or margenYsobresalienteMetros  % GLBNmetrosRasterRx != 0:
#             print(
#                 '\nclidcarto-> ATENCION: cambiar GLBLtileSemiSolapeMetros ({:0.1f} m) para que el margen exterior sea un numero entero de subCeldas (subcelda: {} m)'.format(
#                     LCLtileSemiSolapeMetros,
#                     GLBNmetrosRasterRx,
#     
#                 )
#             )
#             sys.exit(0)
        # ==========================================================================

        # ==========================================================================
        for nRow in range(numTilesRows):
            for nCol in range(numTilesCols):
                tileRecorte = np.zeros((GLBNtileSizeEnPixelsRasterRy, GLBNtileSizeEnPixelsRasterRx), dtype=self.miRasterRefPixel.dtype)
                tileRecorte1m = np.zeros((LCLtileSizeMetros, LCLtileSizeMetros), dtype=self.miRasterRefPixel.dtype)
                # # Esto es igual para tiles de subceldas (2 m) y para tiles de celdillas (metricos)
                # xInfIzdaTile = self.intersectMinX + (nRow * GLBNtileSizeEnPixelsSubCelda * GLO.GLBLmetrosSubCelda)
                # yInfIzdaTile = self.intersectMinY + (nCol * GLBNtileSizeEnPixelsSubCelda * GLO.GLBLmetrosSubCelda)
                if nRow == 0:
                    xInfIzdaTile = (self.miRasterRefMinXY[0] - margenXsobresalienteMetros)
                    recorteIniY = 0
                    recorteIniY1m = 0
                else:
                    xInfIzdaTile = (
                        self.miRasterRefMinXY[0]
                        + (
                            LCLtileSizeMetros
                            - margenXsobresalienteMetros
                            - LCLtileSemiSolapeMetros
                        )
                        + ((nRow - 1) * GLBNtileKernelMetros)
                        - LCLtileSemiSolapeMetros
                    )
                    recorteIniY = int(
                        (
                            GLBNtileSizeEnPixelsRasterRy
                            - margenYsobresalientePixelsRxA
                            - GLBNtileSemiSolapePixelsRasterRy
                        )
                        + ((nRow - 1) * GLBNtileKernelPixelsRasterRy)
                        - GLBNtileSemiSolapePixelsRasterRy
                    )
                    recorteIniY1m = int(
                        (
                            GLBNtileSizeEnPixelsCeldilla
                            - margenYsobresalientePixelsCdA
                            - GLBNtileSemiSolapePixelsCeldilla
                        )
                        + ((nRow - 1) * GLBNtileKernelPixelsCeldilla)
                        - GLBNtileSemiSolapePixelsCeldilla
                     )
                if nCol == 0:
                    yInfIzdaTile = (self.miRasterRefMinXY[1] - margenYsobresalienteMetros)
                    recorteIniX = 0
                    recorteIniX1m = 0
                else:
                    yInfIzdaTile = (
                        self.miRasterRefMinXY[1]
                        + (
                            LCLtileSizeMetros
                            - margenYsobresalienteMetros
                            - LCLtileSemiSolapeMetros
                        )
                        + ((nCol - 1) * GLBNtileKernelMetros)
                        - LCLtileSemiSolapeMetros
                    )
                    recorteIniX = int(
                        (
                            GLBNtileSizeEnPixelsRasterRx
                            - margenXsobresalientePixelsRxA
                            - GLBNtileSemiSolapePixelsRasterRx
                        )
                        + ((nCol - 1) * GLBNtileKernelPixelsRasterRx)
                        - GLBNtileSemiSolapePixelsRasterRx
                    )
                    recorteIniX1m = int(
                        (
                            GLBNtileSizeEnPixelsCeldilla
                            - margenXsobresalientePixelsCdA
                            - GLBNtileSemiSolapePixelsCeldilla
                        )
                        + ((nCol - 1) * GLBNtileKernelPixelsCeldilla)
                        - GLBNtileSemiSolapePixelsCeldilla
                    )
    
                if nRow == 0:
                    iniY = margenYsobresalientePixelsRxA
                    iniY1m = margenYsobresalientePixelsCdA
                else:
                    iniY = 0
                    iniY1m = 0
                if nCol == 0:
                    iniX = margenXsobresalientePixelsRxA
                    iniX1m = margenXsobresalientePixelsCdA
                else:
                    iniX = 0
                    iniX1m = 0
    
                if nRow == numTilesRows - 1:
                    finY = int(GLBNtileSizeEnPixelsRasterRy - margenYsobresalientePixelsRxB)
                    finY1m = int(GLBNtileSizeEnPixelsCeldilla - margenYsobresalientePixelsCdB)
                else:
                    finY = int(GLBNtileSizeEnPixelsRasterRy)
                    finY1m = int(GLBNtileSizeEnPixelsCeldilla)
                if nCol == numTilesCols - 1:
                    finX = int(GLBNtileSizeEnPixelsRasterRx - margenXsobresalientePixelsRxB)
                    finX1m = int(GLBNtileSizeEnPixelsCeldilla - margenXsobresalientePixelsCdB)
                else:
                    finX = int(GLBNtileSizeEnPixelsRasterRx)
                    finX1m = int(GLBNtileSizeEnPixelsCeldilla)
    
                if GLO.GLBLverbose:
                    print('\tclidcarto->>> tiles 2m:', nRow, nCol, '->', iniY, finY, iniX, finX,
                          '->1m', nRow, nCol, '->', iniY1m, finY1m, iniX1m, finX1m)
                    print('\t\ttiles 2m recorte', recorteIniY, recorteIniY + finY - iniY,
                          recorteIniX, recorteIniX + finX - iniX,
                          '->1m recorte', recorteIniY1m, recorteIniY1m + finY1m - iniY1m,
                          recorteIniX1m, recorteIniX1m + finX1m - iniX1m)


                rasterRefRecorteShape = self.aCeldasRasterRef[recorteIniY : recorteIniY + finY - iniY, recorteIniX : recorteIniX + finX - iniX].shape
                funY = iniY + rasterRefRecorteShape[0]
                funX = iniX + rasterRefRecorteShape[1]
                if (
                    tileRecorte[iniY:funY, iniX:funX].shape
                    == self.aCeldasRasterRef[recorteIniY : recorteIniY + finY - iniY, recorteIniX : recorteIniX + finX - iniX].shape
                ):
                    tileRecorte[iniY:funY, iniX:funX] = self.aCeldasRasterRef[recorteIniY : recorteIniY + finY - iniY, recorteIniX : recorteIniX + finX - iniX]
                rasterRefRecorteShape = self.aCeldasRasterRef[recorteIniY1m : recorteIniY1m + finY1m - iniY1m, recorteIniX1m : recorteIniX1m + finX1m - iniX1m].shape
                funY1m = iniY1m + rasterRefRecorteShape[0]
                funX1m = iniX1m + rasterRefRecorteShape[1]
                if (
                    tileRecorte1m[iniY1m:funY1m, iniX1m:funX1m]
                    == self.aCeldasRasterRef[recorteIniY1m : recorteIniY1m + finY1m - iniY1m, recorteIniX1m : recorteIniX1m + finX1m - iniX1m].shape
                ):
                    tileRecorte1m[iniY1m:funY1m, iniX1m:funX1m] = self.aCeldasRasterRef[
                        recorteIniY1m : recorteIniY1m + finY1m - iniY1m, recorteIniX1m : recorteIniX1m + finX1m - iniX1m
                    ]

                #         for nRow in range(numTilesRows):
                #             for nCol in range(numTilesCols):
                #                 if (nRow + 1) * GLBNtileSizeEnPixelsRasterRy <= self.aCeldasRasterRef.shape[0] and\
                #                    (nCol + 1) * GLBNtileSizeEnPixelsRasterRx <= self.aCeldasRasterRef.shape[1]:
                #                     tileRecorte = self.aCeldasRasterRef[nRow * GLBNtileSizeEnPixelsRasterRy :
                #                                                         (nRow + 1) * GLBNtileSizeEnPixelsRasterRy,
                #                                                         nCol * GLBNtileSizeEnPixelsRasterRx :
                #                                                         (nCol + 1) * GLBNtileSizeEnPixelsRasterRx ]
                #                 elif (nRow + 1) * GLBNtileSizeEnPixelsRasterRy <= self.aCeldasRasterRef.shape[0]:
                #                     reCorteX = self.aCeldasRasterRef.shape[1] - (nCol * GLBNtileSizeEnPixelsRasterRx)
                #                     tileRecorte = np.zeros((GLBNtileSizeEnPixelsRasterRy, GLBNtileSizeEnPixelsRasterRx), dtype=self.aCeldasRasterRef.dtype)
                #                     tileRecorte[:, :reCorteX] = self.aCeldasRasterRef[nRow * GLBNtileSizeEnPixelsRasterRy :
                #                                                                       (nRow + 1) * GLBNtileSizeEnPixelsRasterRy,
                #                                                                       nCol * GLBNtileSizeEnPixelsRasterRx :
                #                                                                       self.aCeldasRasterRef.shape[1]]
                #                 elif (nCol + 1) * GLBNtileSizeEnPixelsRasterRx <= self.aCeldasRasterRef.shape[1]:
                #                     reCorteY = self.aCeldasRasterRef.shape[0] - (nRow * GLBNtileSizeEnPixelsRasterRy)
                #                     tileRecorte = np.zeros((GLBNtileSizeEnPixelsRasterRy, GLBNtileSizeEnPixelsRasterRx), dtype=self.aCeldasRasterRef.dtype)
                #                     tileRecorte[:reCorteY, :] = self.aCeldasRasterRef[nRow * GLBNtileSizeEnPixelsRasterRy :
                #                                                                       self.aCeldasRasterRef.shape[0],
                #                                                                       nCol * GLBNtileSizeEnPixelsRasterRx :
                #                                                                       (nCol + 1) * GLBNtileSizeEnPixelsRasterRx]
                #                 else:
                #                     reCorteY = self.aCeldasRasterRef.shape[0] - (nRow * GLBNtileSizeEnPixelsRasterRy)
                #                     reCorteX = self.aCeldasRasterRef.shape[1] - (nCol * GLBNtileSizeEnPixelsRasterRx)
                #                     tileRecorte = np.zeros((GLBNtileSizeEnPixelsRasterRy, GLBNtileSizeEnPixelsRasterRx), dtype=self.aCeldasRasterRef.dtype)
                #                     tileRecorte[:reCorteY, :reCorteX] = self.aCeldasRasterRef[nRow * GLBNtileSizeEnPixelsRasterRy :
                #                                                                               self.aCeldasRasterRef.shape[0],
                #                                                                               nCol * GLBNtileSizeEnPixelsRasterRx :
                #                                                                               self.aCeldasRasterRef.shape[1]]

                # print( '\t\tclidcarto-> el tile (%i, %i) excede las dimensiones de array %s (%ix%i)-> GLBNtileSizeEnPixelsSubCelda (YxX): %ix%i' %
                #      (nRow, nCol, self.nombreCapa, self.aCeldasRasterRef.shape[0], self.aCeldasRasterRef.shape[1], GLBNtileSizeEnPixelsRasterRy, GLBNtileSizeEnPixelsRasterRx))

                ##Interpolacion con PIL -> Me convence menos y requiere mas pasos
                ##->Ver
                ##  https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.fromarray
                ##  https://pillow.readthedocs.io/en/stable/handbook/concepts.html#concept-modes
                # tileImgPIL = PIL.Image.fromarray(tileRecorte, "F") #Se convierte a una imagen con valores float32
                # tileImgPIL = tileImgPIL.resize((GLBNtileSizeEnPixelsSubCelda, GLBNtileSizeEnPixelsSubCelda), PIL.Image.BICUBIC)
                # npzFileNamePIL = os.path.join(trainPath, 'tile_%s_%i_%i.npz' % (self.nombreCapa, nRow, nCol))
                # np.savez_compressed(npzFileNamePIL, mdt=tileImgPIL)
                ##->Para poder leer el valor de un pixel tengo que convertirlo en un objeto lgible (subscriptable):
                ##  http://effbot.org/imagingbook/image.htm#tag-Image.Image.load
                ##  Esto es mas rapido que Image.getpixel(x, y)
                ##->Para girar la imagen:
                ##  http://effbot.org/imagingbook/image.htm#tag-Image.Image.transpose
                ##tileImgPILReadable = tileImgPIL.transpose(PIL.Image.ROTATE_270).load()
                # tileImgPILReadable = tileImgPIL.load()
                # print('tileImgPIL->', type(tileImgPIL)) #
                # print('tileImgPILReadable->', type(tileImgPILReadable)) #<class 'PixelAccess'>

                # Interpolacion con scipy
                tileRecorteZoom = scipy.ndimage.interpolation.zoom(
                    tileRecorte, GLBNtileSizeEnPixelsSubCelda / GLBNtileSizeEnPixelsRasterRx, order=ordenPolinomioInterpolacion, prefilter=True
                )
                # Si la capa original tiene pixel de 1 m, no hay zoom (GLBNtileSizeEnPixelsCeldilla=GLBNtileSizeEnPixelsRasterRx -> 1:1)
                tileRecorteZoom1m = scipy.ndimage.interpolation.zoom(
                    tileRecorte1m, GLBNtileSizeEnPixelsCeldilla / GLBNtileSizeEnPixelsRasterRx, order=ordenPolinomioInterpolacion, prefilter=True
                )

                if GLO.GLBLformatoTilesNpz:
                    npzFileName = os.path.join(self.trainPathNpz, '%s_%s_%i_%i.npz' % (self.fileCoordYear, 'Train', nRow, nCol))
                    np.savez_compressed(npzFileName, capa=tileRecorteZoom)

                if GLO.GLBLformatoTilesPng:
                    # tileRecorteNormalizado = np.flip(normalizar8bits(tileRecorteZoom).transpose(1, 0), axis=0)
                    # Los valores son clases, no hay que normalizar
                    # ->Giro el array 90 grados levogiros para cambiarlo al formato de las imagenes: filas<=>y, columnas<=>x).
                    #  Tb se puede hacer con imagenPng = np.rot90(array)
                    tileRecorteNormalizado = np.flip(tileRecorteZoom.transpose(1, 0), axis=0)
                    pngFileName = os.path.join(self.trainPathPng, '%s_%s_%i_%i.png' % (self.fileCoordYear, 'Train', nRow, nCol))

                    # -> colorMode
                    #  The mode of an image defines the type and depth of a pixel in the image.
                    #  Each pixel uses the full range of the bit depth.
                    #  So a 1-bit pixel has a range of 0-1, an 8-bit pixel has a range of 0-255 and so on.
                    #  1 (1-bit pixels, black and white, stored with one pixel per byte)
                    #  L (8-bit pixels, black and white)
                    #  P (8-bit pixels, mapped to any other mode using a color palette)
                    #  RGB (3x8-bit pixels, true color)
                    #  RGBA (4x8-bit pixels, true color with transparency mask)
                    # The Python Imaging Library uses a Cartesian pixel coordinate system, with (0,0) in the upper left corner.
                    # Note that the coordinates refer to the implied pixel corners;
                    # the centre of a pixel addressed as (0, 0) actually lies at (0.5, 0.5).
                    # colorMode = 'P' # (8-bit pixels, mapped to any other mode using a color palette) ---> Genera imagenes queno me valen ->Espacio de color: Color indexado (256 colores)
                    colorMode = 'L'  # (8-bit pixels, black and white) -> lleva el valor max a 255 y el min a 0 -> No respeta los valores del array ->Espacio de color: Escala de grises
                    if os.path.exists(pngFileName) and not LCLmantenerTilesGuardados:
                        print('clidcarto-> Eliminando tile pngFromRaster previo: {}'.format(pngFileName))
                        os.remove(pngFileName)
                    Image.fromarray(tileRecorteNormalizado, colorMode).save(pngFileName)
                    print('clidcarto-> Creando tile pngFromRaster: {}-{}-> {}'.format(nRow, nCol, pngFileName))

                    if self.trainPathPng1m != '':
                        tileRecorteNormalizado1m = np.flip(tileRecorteZoom1m.transpose(1, 0), axis=0)
                        pngFileName1m = os.path.join(self.trainPathPng1m, '%s_%s_%i_%i.png' % (self.fileCoordYear, 'Train', nRow, nCol))
                        if os.path.exists(pngFileName1m) and not LCLmantenerTilesGuardados:
                            print('clidcarto-> Eliminando tile 1mFromRaster previo: {}'.format(pngFileName1m))
                            os.remove(pngFileName1m)
                        Image.fromarray(tileRecorteNormalizado1m, colorMode).save(pngFileName1m)

                if GLO.GLBLformatoTilesAscRasterRef:
                    ascFileNameScipyZoom = os.path.join(self.trainPathAsc, '%s_%s_%i_%i.asc' % (self.fileCoordYear, self.nombreCapa, nRow, nCol))
                    print('clidcarto-> creando asc from rasterRaster', self.nombreCapa, nRow, nCol, tileRecorteZoom.shape, GLBNtileSizeEnPixelsSubCelda, GLBNtileSizeEnPixelsSubCelda)
                    crearASC(
                        ascFileNameScipyZoom,
                        tileRecorteZoom,
                        tileRecorteZoom.shape,
                        GLBNtileSizeEnPixelsSubCelda,
                        GLBNtileSizeEnPixelsSubCelda,
                        GLO.GLBLmetrosSubCelda,
                        xInfIzdaTile,
                        yInfIzdaTile,
                        0,
                        nTipoDato=3,
                    )

        cargarSample = False
        if cargarSample:
            npzFileSampleName = os.path.join(self.trainPathNpz, '%s_%s_%i_%i.npz' % (self.fileCoordYear, self.nombreCapa, 0, 0))
            npzfileSample = np.load(npzFileSampleName, allow_pickle=True)
            if GLO.GLBLverbose:
                print('\t\tclidcarto-> arrays guardadas en npzFileSampleName:', npzfileSample.files)
                print('\t\tclidcarto-> Contenido del primer array ( shape:', npzfileSample[npzfileSample.files[0]].shape, '):')
                print(npzfileSample[npzfileSample.files[0]])


# ==============================================================================
def leerVentanaRaster(
        rasterConRuta,
        coordVentana,
        aNumCeldas,
        tipoInfoRaster,
        nBandasPrevistas,
        tipoDatoRaster,
        gdalOk,
    ):
    rasterExiste = True
    rasterUsable = True
    rasterSolapa = True
    rasterIncluyeLas = 1
    if not os.path.exists(rasterConRuta):
        print('clidcarto-> no esta disponible el fichero %s' % (rasterConRuta))
        rasterExiste = False
    if rasterExiste:
        try:
            sourceDatasetRasterOriginal = gdal.Open(rasterConRuta, gdalconst.GA_ReadOnly)
        except:
            sourceDatasetRasterOriginal = None
        if sourceDatasetRasterOriginal is None:
            print('\tclidcarto-> Error abriendo raster', rasterConRuta)
            print('\t\t-> Comprobar si esta bloqueada por otra aplicacion o tiene algun error', rasterConRuta)
            rasterUsable = False

    if rasterExiste and rasterUsable:
        infoSourceDatasetRasterOriginal = infoRasterDataset(sourceDatasetRasterOriginal, mostrar=GLO.GLBLverbose)
        # origenX_Imagen = infoSourceDatasetRasterOriginal['origenX']
        # origenY_Imagen = infoSourceDatasetRasterOriginal['origenY']
        rasterRefMetrosPixelX = infoSourceDatasetRasterOriginal['pixelX']
        rasterRefMetrosPixelY = infoSourceDatasetRasterOriginal['pixelY']
        # nPixelsX = infoSourceDatasetRasterOriginal['nPixelsX']
        # nPixelsY = infoSourceDatasetRasterOriginal['nPixelsY']
        nBandasRaster = infoSourceDatasetRasterOriginal['nBandas']
        if nBandasPrevistas != nBandasRaster:
            print(f'clidcarto-> ATENCION: nBandasPrevistas:   {nBandasPrevistas}; nBandasRaster: {nBandasRaster} (deben ser iguales)')

        if tipoInfoRaster == 'EGM08':
            imagenCompleta = True
        else:
            imagenCompleta = False
        laInterseccion = calculaInterseccion(
            infoSourceDatasetRasterOriginal,
            coordVentana,
            imagenCompleta=imagenCompleta,
            LCLverbose=GLO.GLBLverbose,
        )
        rasterSolapa = laInterseccion[0]
        if rasterSolapa:
            xOffRaster = laInterseccion[1]
            yOffRaster = laInterseccion[2]
            nCeldasX_Intersec = laInterseccion[3]
            nCeldasY_Intersec = laInterseccion[4]
            intersectMinX = laInterseccion[5]
            intersectMinY = laInterseccion[6]
            intersectMaxX = laInterseccion[7]
            intersectMaxY = laInterseccion[8]

            if nBandasRaster == 1:
                rasterRefRecortadoAsArrayInt = np.zeros([nCeldasY_Intersec, nCeldasX_Intersec], dtype=tipoDatoRaster)
            else:
                rasterRefRecortadoAsArrayInt = np.zeros([nBandasRaster, nCeldasY_Intersec, nCeldasX_Intersec], dtype=tipoDatoRaster)

            if rasterRefMetrosPixelX != GLO.GLBLmetrosCelda or rasterRefMetrosPixelY != -GLO.GLBLmetrosCelda:
                if GLO.GLBLverbose and tipoInfoRaster != 'Orto':
                    print(f'\tclidcarto-> Aviso: dimensiones de pixel del raster {tipoInfoRaster} ({rasterRefMetrosPixelX} m) distinto a la dimension de las celdas elegidas para el lasFile ({GLO.GLBLmetrosCelda} m)')
            elif nCeldasX_Intersec != aNumCeldas[0] or nCeldasY_Intersec != aNumCeldas[1]:
                rasterIncluyeLas = 0
            if GLO.GLBLverbose:
                print('\nclidcarto-> Parametros de la interseccion (para obtener el ndarray interseccion a partir de la imagen):')
                print(f'\t-> xOffRaster: {xOffRaster}, yOffRaster: {yOffRaster}')
                print(f'\t-> nCeldasX_Intersec: {nCeldasX_Intersec}, nCeldasY_Intersec: {nCeldasY_Intersec}')
                print('\t-> Coordenadas de la interseccion:')
                print(f'\t\t-> nMin_XY: {intersectMinX}, {intersectMinY}')
                print(f'\t\t-> nMax_XY: {intersectMaxX}, {intersectMaxY}')
                print('\tclidcarto-> rasterExiste rasterUsable rasterSolapa:', rasterExiste, rasterUsable, rasterSolapa)
                print(
                    '\tclidcarto-> nCeldasX_Intersec, aNumCeldas[0], nCeldasY_Intersec, aNumCeldas[1]',
                    nCeldasX_Intersec,
                    aNumCeldas[0],
                    nCeldasY_Intersec,
                    aNumCeldas[1],
                )
            if GLO.GLBLverbose:
                print('\nclidcarto-> Recorriendo bandas del raster a intersectar (leer ventana):')
            for nBand in range(nBandasRaster):
                if GLO.GLBLverbose:
                    print(f'\tclidcarto-> nBand: {nBand}')
                srcbandOriginal = sourceDatasetRasterOriginal.GetRasterBand(nBand + 1)
                # stats1, stats2, ctable = infoSrcband(srcbandOriginal, True, False)
                srcbandOriginalAsArrayInt, noData = infoSrcbandAsArray(srcbandOriginal, xOffRaster, yOffRaster, nCeldasX_Intersec, nCeldasY_Intersec, verbose=GLO.GLBLverbose, tipoInfoRaster=tipoInfoRaster)
                if GLO.GLBLverbose:
                    print('\tclidcarto-> srcbandOriginalAsArrayInt.shape', srcbandOriginalAsArrayInt.shape)
                if nBandasRaster == 1:
                    rasterRefRecortadoAsArrayInt = srcbandOriginalAsArrayInt
                else:
                    rasterRefRecortadoAsArrayInt[nBand] = srcbandOriginalAsArrayInt
        else:
            print(f'clidcarto-> ATENCION: raster {nBandasPrevistas} no solapa.')
            origenX_Imagen = infoSourceDatasetRasterOriginal['origenX']
            origenY_Imagen = infoSourceDatasetRasterOriginal['origenY']
            pixelX = infoSourceDatasetRasterOriginal['pixelX']
            pixelY = infoSourceDatasetRasterOriginal['pixelY']
            nPixelsX = infoSourceDatasetRasterOriginal['nPixelsX']
            nPixelsY = infoSourceDatasetRasterOriginal['nPixelsY']
            rasterMinX = origenX_Imagen
            rasterMaxX = origenX_Imagen + (nPixelsX * pixelX)
            rasterMinY = origenY_Imagen + (nPixelsY * pixelY)
            rasterMaxY = origenY_Imagen
            pixel_with = abs(pixelX)
            pixel_height = abs(pixelY)
            # Esto viene de: coordVentana = np.array([self.xminBloqueH30, self.yminBloqueH30, self.xmaxBloqueH30, self.ymaxBloqueH30], dtype=np.float32)
            #  Estas coordenadas de ventana ya estan ajustadas a un orgen en numero entero de pixeles de ortofoto
            #  Otra cosa es que la ortofoto tambien tenga su origen en un numero entero de sus pixeles
            xInfIzdaLas = coordVentana[0]
            yInfIzdaLas = coordVentana[1]
            xSupDchaLas = coordVentana[2]
            ySupDchaLas = coordVentana[3]
            # ySupIzdaLas = coordVentana[3]
            print('\tclidcarto-> Revisando coordenadas del bloque Lidar y del rasterRef')
            print('\t\t-> xInfIzdaLas, rasterMinX:', xInfIzdaLas, rasterMinX)
            print('\t\t-> xSupDchaLas, rasterMaxX:', xSupDchaLas, rasterMaxX)
            print('\t\t-> yInfIzdaLas, rasterMinY:', yInfIzdaLas, rasterMinY)
            print('\t\t-> ySupDchaLas, rasterMaxY:', ySupDchaLas, rasterMaxY)
            rasterSolapa = 0
            nCeldasX_Intersec = 0
            nCeldasY_Intersec = 0

        xInfIzdaLas = coordVentana[0]
        yInfIzdaLas = coordVentana[1]
        xSupDchaLas = coordVentana[2]
        ySupDchaLas = coordVentana[3]
        ySupIzdaLas = coordVentana[3]
        if GLO.GLBLverbose:
            print('\tclidcarto-> xInfIzdaLas, yInfIzdaLas:', xInfIzdaLas, yInfIzdaLas)
            print('\tclidcarto-> xSupDchaLas, ySupDchaLas:', xSupDchaLas, ySupDchaLas)
    else:
        rasterSolapa = 0
        nCeldasX_Intersec = 0
        nCeldasY_Intersec = 0

    if rasterExiste and rasterUsable and rasterSolapa:
        miRasterRefVentanaOk = 1
    else:
        miRasterRefVentanaOk = 0
        # srcbandOriginalAsArrayInt = np.zeros(nCeldasX_Intersec * nCeldasY_Intersec, dtype=np.uint8).reshape(nCeldasY_Intersec, nCeldasX_Intersec)
        # srcbandOriginalAsArrayInt = np.zeros(aNumCeldas[0] * aNumCeldas[1], dtype=np.uint8).reshape(aNumCeldas[0], aNumCeldas[1])
        if nBandasRaster == 1:
            rasterRefRecortadoAsArrayInt = np.zeros([nCeldasY_Intersec, nCeldasX_Intersec], dtype=tipoDatoRaster)
        else:
            rasterRefRecortadoAsArrayInt = np.zeros([nBandasRaster, nCeldasY_Intersec, nCeldasX_Intersec], dtype=tipoDatoRaster)

        rasterRefMetrosPixelX = 0
        rasterRefMetrosPixelY = 0
        intersectMinX = 0
        intersectMinY = 0
        intersectMaxX = 0
        intersectMaxY = 0
        nCeldasX_Intersec = 0
        nCeldasY_Intersec = 0
        xOffRaster = 0
        yOffRaster = 0
        noData = 0

    return (
        miRasterRefVentanaOk,
        rasterIncluyeLas,
        nBandasRaster,
        rasterRefRecortadoAsArrayInt,
        rasterRefMetrosPixelX,
        rasterRefMetrosPixelY,
        intersectMinX,
        intersectMinY,
        intersectMaxX,
        intersectMaxY,
        nCeldasX_Intersec,
        nCeldasY_Intersec,
        xOffRaster,
        yOffRaster,
        noData,
    )


# ==============================================================================
def foo():
    pass

# #ooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo
# def leer_CapaRaster(inputName, nBandas, soloInfo ):
#     RASTERDATA_DIR = ('D:/_ws/laz/')
#     print('\\nnoooooooooooooooooooooooooooooo Inicio oooooooooooooooooooooooooooooooo')
#     print( 'clidcarto-> 1. Imagen completa')
#     print( 'clidcarto-> 2. Cuadricula predeterminada')
#     selec = input('Selecciona opcion 1-2:')
#     #print(selec, type(selec))
#     if int(selec) == 1:
#         imagenCompleta = True
#     elif int(selec) == 2:
#         imagenCompleta = False
#     else:
#         quit()
#
#     print( 'clidcarto-> Leer el raster:', inputName)
#     print( 'clidcarto-> Y guardarlo en un fichero de texto')
#
#     sourceDataset = gdal.Open( inputName, gdalconst.GA_ReadOnly )
#     if sourceDataset is None:
#         print( 'clidcarto-> Error abriendo raster')
#         sys.exit(1)
#
#     infoSourceDataset = infoRasterDataset( sourceDataset, mostrar0True)
#     origenX_Imagen = infoSourceDataset['origenX']
#     origenY_Imagen = infoSourceDataset['origenY']
#     pixelX = infoSourceDataset['pixelX']
#     pixelY = infoSourceDataset['pixelY']
#     nCeldasX = infoSourceDataset['nPixelsX']
#     nCeldasY = infoSourceDataset['nPixelsY']
#     if nBandas == 0:
#         nBandas = infoSourceDataset['nBandas']
#
#     if imagenCompleta:
#         X_ORIGEN = origenX_Imagen
#         Y_ORIGEN = origenY_Imagen
#         X_TOTAL = nCeldasX * abs(pixelX)
#         Y_TOTAL = nCeldasY * abs(pixelY)
#     else:
#         X_ORIGEN = 458000.0 + 200
#         Y_ORIGEN = 4690000.0 + 200
#         X_TOTAL = 2000
#         Y_TOTAL = 2000
#
#     if soloInfo:
#         band = sourceDataset.GetRasterBand(1)
#         # Get "natural" block size, and total raster XY size.
#         block_sizes = band.GetBlockSize()
#         x_block_size = block_sizes[0]
#         y_block_size = block_sizes[1]
#         print( 'clidcarto-> Dimensiones del bloque interno: %ix%i' % (x_block_size, y_block_size))
#         return
#
#     xInfIzdaRaster = X_ORIGEN
#     xSupDchaRaster = X_ORIGEN + X_TOTAL
#     yInfIzdaRaster = Y_ORIGEN - Y_TOTAL
#     ySupDchaRaster = Y_ORIGEN
#     coordVentana = [xInfIzdaRaster,
#                     yInfIzdaRaster,
#                     xSupDchaRaster,
#                     ySupDchaRaster]
#     laInterseccion = calculaInterseccion( infoSourceDataset,
#                                           coordVentana,
#                                           imagenCompleta=imagenCompleta )
#     xOffRaster = laInterseccion[0]
#     yOffRaster = laInterseccion[1]
#     nCeldasX_Intersec = laInterseccion[2]
#     nCeldasY_Intersec = laInterseccion[3]
#     intersectMinX = laInterseccion[4]
#     #intersectMinY = laInterseccion[5]
#     #intersectMaxX = laInterseccion[6]
#     intersectMaxY = laInterseccion[7]
#     print( '\nclidcarto-> Parametros usados para pasar los datos de la imagen a un ndarray:')
#     print( 'clidcarto-> xOffRaster: %i, yOffRaster: %i, nCeldasX_Intersec: %i, nCeldasY_Intersec: %i' \
#                 % (xOffRaster, yOffRaster, nCeldasX_Intersec, nCeldasY_Intersec))
#
#     #Ajustes para colocar la capa en su sitio (esto no deberia ser necesario)
#     #Para la Hoja_20-11.ers
#     #ajusteX = -25.5 #Para el ED50, UTM 30
#     #ajusteY = +12 #Para el ED50, UTM 30
#     #ajusteX = -23.6 #Para el WGS84, UTM 30
#     #ajusteY = -71.51 #Para el WGS84, UTM 30
#     #Para 20131f_453.img:
#     #ajusteX = +19.42
#     #ajusteY = -0.18
#     ajusteX = 0
#     ajusteY = 0
#
#     #Por ahora trabajo solo con la primera banda
#     nBandas = infoSourceDataset['nBandas']
#     srcBandAsArrayIntAcum = {}
#     for nBand in range(nBandas):
#         print("\n-------->Descripcion de la banda num.:", nBand)
#         try:
#             srcband = sourceDataset.GetRasterBand(nBand+1)
#         except:
#                 sys.exit(1)
# #         except (RuntimeError, e):
# #             print( 'clidcarto-> Este raster no tiene la banda %i' % nBand)
# #             print( 'clidcarto-> Error:', e)
# #             sys.exit(1)
#         infoSrcband(srcband)
#         srcBandAsArrayInt, noData = infoSrcbandAsArray( srcband,
#                                                         xOffRaster, yOffRaster,
#                                                         nCeldasX_Intersec, nCeldasY_Intersec,
#                                                         verbose=True)
#         srcBandAsArrayIntAcum[nBand] = srcBandAsArrayInt
#
#     '''
#     for nBand in range(nBandas):
#         print( '\nclidcarto-> Uso el arrayInt para contar pixeles totales y no ceros')
#         print( 'clidcarto-> Banda num.:', nBand)
#         segundos1= time.clock( )
#         suma1, count = 0, 0
#         suma2, count_ = 0, 0
#         srcBandAsArrayInt = srcBandAsArrayIntAcum[nBand]
#         for row in srcBandAsArrayInt[:,]:
#             for item in row:
#                 count += 1
#                 suma1 += int(item)
#                 if int(item) >0:
#                     count_ += 1
#                     suma2 += int(item)
#         print( 'clidcarto-> Num pixeles totales y valor medio:', count, suma1/count)
#         print( 'clidcarto-> Num pixeles no nulos y valor medio:', count_, suma2/count_)
#         '''
#
#     '''
#     print( '\nclidcarto-> Escribo el contenido del arrayInt en un fichero con python .write:')
#     segundos2= time.clock( )
#     target_file = RASTERDATA_DIR+'Banda%i_ConWrite.csv' % (nBand+1)
#     print(target_file)
#     t = open(target_file, 'wb')
#     for row in srcBandAsArrayInt[:,]:
#         t.write(','.join(str(r) for r in row))
#         t.write('\n')
#     t.close
#
#     print( 'clidcarto-> Escribo el contenido del arrayInt en un fichero con csv .writerow:')
#     segundos3= time.clock( )
#     target_file = RASTERDATA_DIR+'Banda%i_ConWriteRow.csv' % (nBand+1)
#     print(target_file)
#     t = open(target_file, 'wb')
#     writer = csv.writer(t)
#     for row in srcBandAsArrayInt[:,]:
#         writer.writerow(row)
#     t.close
#     '''
#     segundos4= time.clock( )
#
#     #Para cada pixel de la banda guardo las coordenadas y respuesta radiometrica
#     print( '\nclidcarto-> Escribo la respuesta espectral en un fichero de texto:')
#     target_file1 = RASTERDATA_DIR+'RptaEspectral_%iBandas_1.txt' % (nBandas)
#     target_file2 = RASTERDATA_DIR+'RptaEspectral_%iBandas_2.txt' % (nBandas)
#     t = open(target_file1, 'wb')
#
#     #srcBandAsArrayInt0 = srcBandAsArrayIntAcum[0]
#     #srcBandAsArrayInt1 = srcBandAsArrayIntAcum[1]
#     #srcBandAsArrayInt2 = srcBandAsArrayIntAcum[2]
#     for nX in range(srcBandAsArrayIntAcum[0].shape[0]):
#         for nY in range(srcBandAsArrayIntAcum[0].shape[1]):
#             coordX = int(origenX_Imagen + ajusteX + ((nX+0.5) * pixelX))
#             coordY = int(origenY_Imagen + ajusteY + ((nY+0.5) * pixelY))
#             valor = {}
#             t.write(str(coordX) + '\t' +
#                             str(coordY) + '\t')
#             for nBand in range(nBandas):
#                 valor[nBand] = srcBandAsArrayIntAcum[nBand][nX,nY]
#                 t.write(str(valor[nBand])+ '\t')
#             '''
#             valor0 = srcBandAsArrayInt0[nX,nY]
#             valor1 = srcBandAsArrayInt1[nX,nY]
#             valor2 = srcBandAsArrayInt2[nX,nY]
#             t.write(str(coordX) + '\t' +
#                             str(coordY) + '\t' +
#                             str(valor0)+ '\t' +
#                             str(valor1)+ '\t' +
#                             str(valor2))
#             '''
#             t.write('\n')
#     t.close
#
#     '''
#     print( 'clidcarto-> Se puede leer linea a linea, guardar los contenidos en una lista')
#     print( 'clidcarto-> y escribir ese contenido con una coletilla en otro fichero:' )
#     lineasTexto = []
#     lineasLista = []
#     t = open(target_file2, 'wb')
#
#     #En vez de s = open(source_file, 'r') uso la estructira with -> ventajas?
#     #Abro en modo 'rb', de forma que los retornos de linea se dejan
#     #intactos ('r' los convierte a \n); segun de que plataforma venga el fichero:
#     # '\n' (Unix), '\r' (Mac) o '\r\n' (Windows)
#     #El modo 'r' convierte los retornos de linea a la plataforma en la que corre la app.
#     with open(target_file1,'rb') as s:
#         #En cada linea se pueden separar las palabras o los numeros:
#         #    Tokenizar si es un texto
#         #    Hacer un split() o rsplit()
#         #        considerando el separador que proceda (',', ';', '\t'...)
#         #        El split la convierte en una lista de strings
#         contador = 0
#         while True:
#             contador+=1
#             linea = s.readline()
#             if not linea: break
#             # Quito el \n que no lo interpreta bien
#             linea = linea.replace('\n', '').replace('\r', '')
#             #Buscar estoooooooooooooooooo
#             #targets.writerows(prediccion)
#             t.write(linea + ';999')
#             t.write('\n')
#             lineasTexto.append(linea)
#             #lineasTexto.extend(linea)
#             lineasLista.append(linea.split( ';' ))
#             #print( 'clidcarto-> a)', linea, 'b)', lineasLista[-1])
#     print( '\nclidcarto-> Listas creadas')
#     #print(lineasTexto)
#     #print(lineasLista)
#     t.close()
#     '''
#
#
#     segundos5= time.clock( )
#
#     #print( 'clidcarto-> Segundos para para contar pixeles:', int(segundos2-segundos1))
#     #print( 'clidcarto-> Segundos para escribir con python write:', int(segundos3-segundos2))
#     #print( 'clidcarto-> Segundos para escribir con csv writerow:', int(segundos4-segundos3))
#     print( 'clidcarto-> Minutos para procesar coordenadas y respuesta espectral:', round((segundos5-segundos4)/60, 1))
#
#     srcband = None
#     #ATENCION: se transfiere solo la ultima banda leida
#     return (sourceDataset, srcBandAsArrayInt,
#                     nCeldasX_Intersec, nCeldasY_Intersec,
#                     intersectMinX, intersectMaxY,
#                     pixelX, pixelY,
#                     ajusteX, ajusteY)
# ==============================================================================


# ==============================================================================
# ==============================================================================
# ==============================================================================
# Puede hacerse una clase raster con todos los metodos para los raster
def infoSrcband(srcband, verbose=False, reclaculaStats=False):
    stats1 = srcband.GetStatistics(True, True)
    if stats1 is None:
        exit
    if reclaculaStats:
        stats2 = srcband.ComputeStatistics(0)
        if stats2 is None:
            print('\tclidcarto-> No se han podido recalcular las estadisticas')
    else:
        stats2 = []

    if verbose:
        if gdalOk:
            print('\tclidcarto-> Tipo de datos de la banda=', gdal.GetDataTypeName(srcband.DataType))
        print('\nclidcarto-> Estadisticas guardadas en metadatos:')
        print('\tclidcarto-> Minimum=%.3f, Maximum=%.3f, Mean=%.3f, StdDev=%.3f' % (stats1[0], stats1[1], stats1[2], stats1[3]))
        # print( '\tclidcarto-> Estadisticas recalculadas:' )
        # print( '\tclidcarto-> Minimum=%.3f, Maximum=%.3f, Mean=%.3f, StdDev=%.3f' % ( \
        #             stats2[0], stats2[1], stats2[2], stats2[3] ) )
        # Tambien se puede conocer el minimo y el maximo con:
        # minimo = srcband.GetMinimum()
        # maximo = srcband.GetMaximum()
        # Y tambien con:
        # (minimo,maximo) = srcband.ComputeRasterMinMax(1)
        print('\tclidcarto-> Otras caracteristicas de la capa:')
        print("\tNo data value= ", srcband.GetNoDataValue())
        print("\tScale=                 ", srcband.GetScale())
        print("\tUnit type=         ", srcband.GetUnitType())

    ctable = srcband.GetColorTable()
    if verbose:
        if not ctable is None:
            print('clidcarto-> Color table count= ', ctable.GetCount())
            for i in range(0, ctable.GetCount()):
                entry = ctable.GetColorEntry(i)
                if not entry:
                    continue
                print('\tColor entry RGB=     ', ctable.GetColorEntryAsRGB(i, entry))
        else:
            print('clidcarto-> No ColorTable')
            # sys.exit(1)
        if not srcband.GetRasterColorTable() is None:
            print('clidcarto-> Band has a color table with ', srcband.GetRasterColorTable().GetCount(), ' entries.')
        else:
            print('clidcarto-> No RasterColorTable')
        if srcband.GetOverviewCount() > 0:
            print('clidcarto-> Band has ', srcband.GetOverviewCount(), ' overviews.')
        else:
            print('clidcarto-> No overviews')
    return stats1, stats2, ctable


# ==============================================================================
def infoSrcbandAsArray(srcband, xOffRaster, yOffRaster, nCeldasX_Intersec, nCeldasY_Intersec, verbose=False, tipoInfoRaster=''):
    srcbandAsArray = srcband.ReadAsArray(xOffRaster, yOffRaster, nCeldasX_Intersec, nCeldasY_Intersec)
    if tipoInfoRaster == 'landCover':
        srcBandAsArrayInt = srcbandAsArray.astype(np.uint8)
    elif tipoInfoRaster == 'Mdt':
        srcBandAsArrayInt = srcbandAsArray.astype(np.float32)
    elif tipoInfoRaster == 'Orto':
        srcBandAsArrayInt = srcbandAsArray.astype(np.uint8)
    elif tipoInfoRaster == 'EGM08':
        srcBandAsArrayInt = srcbandAsArray.astype(np.float32)
    else:
        srcBandAsArrayInt = srcbandAsArray
        # srcBandAsArrayInt = srcbandAsArray.astype(int)
    # La banda srcband puede tener pixeles 'NoData', trasparentes
    # Al pasarlo al srcBandAsArrayInt toman el valor 0. No consigo pasar a 'NoData'

    ############### Leer fragmentos parciales #################
    '''
    The ReadRaster() call has the arguments:
    def ReadRaster(self, xoff, yoff, xsize, ysize, 
                                 buf_xsize = None, buf_ysize = None, 
                                 buf_type = None, band_list = None ):
        xoff, yoff, xsize, ysize are the rectangle on the raster file to read.
        The buf_xsize, buf_ysize values are the size of the resulting buffer.
        Aviso:
            When loading data at full resolution buf_xsize y buf_ysize would be 
            the same as the window size. However, to load a reduced resolution 
            overview this could be set to smaller than the window on disk.
            So you might say "0,0,512,512,100,100" to read a 512x512 block at
            the top left of the image into a 100x100 buffer (downsampling the image).
    '''
    if verbose:
        print('\t\t-> Tipo de array:                    ', type(srcBandAsArrayInt))
        print('\t\t-> Dimensiones del array (shape):    ', srcBandAsArrayInt.shape)
        print('\t\t-> Tipo de datos del array original: ', srcbandAsArray.dtype)
        print('\t\t-> Tipo de datos del array Int:      ', srcBandAsArrayInt.dtype)
        # print( '\t\t-> Contenido del array:' )
        # print( '\t\t->', srcBandAsArrayInt )
        # print( '\t\t-> Ancho de la linea del raster completo:', srcband.XSize )

    '''
    try:
        print( '\tclidcarto-> Para leer una linea determinada:' )
        scanline1 = srcband.ReadRaster( 0, 0, srcband.XSize, 1, srcband.XSize, 1, 
                                                                     gdalconst.GDT_Byte, 1 )
        #scanline2 = srcband.ReadRaster( 0, 1, srcband.XSize, 1, srcband.XSize, 1, 
        #                                                             GDT_Byte, 1 )
        #scanlineFloat = srcband.ReadRaster( 0, 0, srcband.XSize, 1, srcband.XSize, 1, 
        #                                                             GDT_Float32, 1 )
    except RuntimeError, e:
        print( 'clidcarto-> No se lee la linea' )
        print( e )
        sys.exit(1)
    scanlineNumeros1 = map(ord, scanline1)
    #O lo que es lo mismo:
    scanlineNumeros1 = map(lambda x: ord, scanline1)
    #Se podrian filtrar los valores que se quiera de ese array con filter(lambda...)
    #Se puede operar sobre la secuencia de los valores para obtener uno final:
    #P. ej.: suma = reduce(lambda x,y: x+y, map(ord, scanline1))
    if verbose:
        pass
        print( 'clidcarto-> Linea1 en caracteres:', scanline1 )
        print( 'clidcarto-> Numeros:', scanlineNumeros1 )
    scanlineByte1 = bytearray(scanline1, 'cp1252')
    print( type(scanlineByte1) )
    print( 'clidcarto-> Linea1 en Bytearray:', scanlineByte1 )
    print( 'clidcarto-> Primer Byte:', scanlineByte1[0] )
 
    #Si la banda es de datos tipo Float32 (de 4 bytes)
    #scanline es una string con xsize*4 bytes de datos binarios:
    #Un pixel corresponde a un Float32, es decir 4 bytes de esa string
    #Para convertirlo a una tupla de floats uso la libreria struct
    import struct
    if len(scanlineFloat) == struct.calcsize('i')*srcband.XSize:
        tuple_of_floats = struct.unpack('f' * srcband.XSize, scanlineFloat)
        print( 'clidcarto-> String:', len(scanlineFloat), '->', scanlineFloat )
        print( 'clidcarto-> Tupla: ', len(tuple_of_floats), '->', tuple_of_floats )
    '''

    ############### Generar estadisticas #################
    # import np.ma as ma
    # Puedo crear una mascara para considerar solo parte de los pixeles
    # La mascara funciona de forma que los ceros no estan enmascarados:

    datamask = np.zeros((srcbandAsArray.shape[0], srcbandAsArray.shape[1]), dtype=np.uint8)  # No enmascara ninguno
    selectedZoneRaster = np.ma.masked_array(srcBandAsArrayInt, datamask)
    # print( type(selectedZoneRaster), selectedZoneRaster.shape, selectedZoneRaster.dtype )
    # print( 'clidcarto-> Elemento [0,0]:', selectedZoneRaster[0,0], type(selectedZoneRaster[1,1]) )
    # print( selectedZoneRaster )

    # Enmascaro los valores nodata
    nodata = srcband.GetNoDataValue()
    maskedArray = np.ma.masked_equal(srcbandAsArray, nodata)
    srcBandAsArrayIntSinCeros = np.ma.masked_where(srcBandAsArrayInt == 0, srcBandAsArrayInt)

    # Calculate statistics of zonal raster
    if verbose:
        print('\tclidcarto-> Estadistica obtenida del Array, considerando todos los valores:')
        print(
            '\t\t-> Min=%.3f, Max=%.3f, Mean=%.3f, StdDev=%.3f'
            % ((np.min(selectedZoneRaster)), (np.max(selectedZoneRaster)), (np.mean(selectedZoneRaster)), (np.std(selectedZoneRaster)))
        )
        if nodata is not None:
            print('\t\t-> El valor nodata es:', nodata)
        else:
            print('\t\t-> El valor nodata es -> None')
        print('\tclidcarto-> Estadistica obtenida del Array, sin considerar los valores nodata:')
        print('\t\t-> min: %s, max: %s, mean: %s, std: %s' % (maskedArray.min(), maskedArray.max(), maskedArray.mean(), maskedArray.std()))

        print('\tclidcarto-> Estadistica obtenida del Array, sin considerar los ceros:')
        print(
            '\t\t-> min: %s, max: %s, mean: %s, std: %s'
            % (srcBandAsArrayIntSinCeros.min(), srcBandAsArrayIntSinCeros.max(), srcBandAsArrayIntSinCeros.mean(), srcBandAsArrayIntSinCeros.std())
        )
        # print( '\tclidcarto-> Valores del array srcbandAsArray:'    )
        # print( srcbandAsArray )
        # print( '\tclidcarto-> Valores del array srcBandAsArrayInt:'    )
        # print( srcBandAsArrayInt )
        # print( '\t\t-> Valores del array srcBandAsArrayInt quitando los ceros:' )
        # print( srcBandAsArrayIntSinCeros )

    return srcBandAsArrayInt, nodata


# ==============================================================================
def calculaInterseccion(
        infoSourceDataset,
        coordVentana,
        imagenCompleta=False,
        LCLverbose=False,
    ):
    origenX_Imagen = infoSourceDataset['origenX']
    origenY_Imagen = infoSourceDataset['origenY']
    pixelX = infoSourceDataset['pixelX']
    pixelY = infoSourceDataset['pixelY']
    nPixelsX = infoSourceDataset['nPixelsX']
    nPixelsY = infoSourceDataset['nPixelsY']

    rasterMinX = origenX_Imagen
    rasterMaxX = origenX_Imagen + (nPixelsX * pixelX)
    rasterMinY = origenY_Imagen + (nPixelsY * pixelY)
    rasterMaxY = origenY_Imagen
    pixel_with = abs(pixelX)
    pixel_height = abs(pixelY)

    # Esto viene de: coordVentana = np.array([self.xminBloqueH30, self.yminBloqueH30, self.xmaxBloqueH30, self.ymaxBloqueH30], dtype=np.float32)
    #  Estas coordenadas de ventana ya estan ajustadas a un orgen en numero entero de pixeles de ortofoto
    #  Otra cosa es que la ortofoto tambien tenga su origen en un numero entero de sus pixeles
    xInfIzdaLas = coordVentana[0]
    yInfIzdaLas = coordVentana[1]
    xSupDchaLas = coordVentana[2]
    ySupDchaLas = coordVentana[3]
    # ySupIzdaLas = coordVentana[3]

    if False: # GLO.GLBLhuso29 or '_H29_' in GLO.MAINprocedimiento:
        print('\tclidcarto-> Revisando coordenadas del bloque Lidar y de la ortofoto (o raster que sea)')
        print('\t\t-> xInfIzdaLas, rasterMinX:', xInfIzdaLas, rasterMinX)
        print('\t\t-> xSupDchaLas, rasterMaxX:', xSupDchaLas, rasterMaxX)
        print('\t\t-> yInfIzdaLas, rasterMinY:', yInfIzdaLas, rasterMinY)
        print('\t\t-> ySupDchaLas, rasterMaxY:', ySupDchaLas, rasterMaxY)

    if xSupDchaLas < rasterMinX or xInfIzdaLas > rasterMaxX or ySupDchaLas < rasterMinY or yInfIzdaLas > rasterMaxY:
        if LCLverbose:
            print('\tclidcarto-> Cuadrado Lidar fuera de la imagen raster')
            print('\t\t-> xSupDchaLas, rasterMinX:', xSupDchaLas, rasterMinX)
            print('\t\t-> xInfIzdaLas, rasterMaxX:', xInfIzdaLas, rasterMaxX)
            print('\t\t-> ySupDchaLas, rasterMinY:', ySupDchaLas, rasterMinY)
            print('\t\t-> yInfIzdaLas, rasterMaxY:', yInfIzdaLas, rasterMaxY)
        haySolape = False
    else:
        haySolape = True

    if not haySolape:
        return [haySolape]

    # El punto de partida es el bloqueLidar expresado en pixeles del raster (redondeado a pixeles enteros)
    if imagenCompleta:
        bloqueLidarNumPixelsX = nPixelsX
        bloqueLidarNumPixelsY = nPixelsY
        bloqueLidarCoordMinX = rasterMinX
        bloqueLidarCoordMaxX = rasterMaxX
        bloqueLidarCoordMinY = rasterMinY
        bloqueLidarCoordMaxY = rasterMaxY
    else:
        # bloqueLidarNumPixelsX = math.floor((xSupDchaLas - xInfIzdaLas) / pixel_with)
        bloqueLidarNumPixelsX = math.ceil((xSupDchaLas - xInfIzdaLas) / pixel_with)
        # bloqueLidarNumPixelsY = math.floor((ySupDchaLas - yInfIzdaLas) / pixel_height)
        bloqueLidarNumPixelsY = math.ceil((ySupDchaLas - yInfIzdaLas) / pixel_height)
        # bloqueLidarCoordMinX = (xSupIzda - xInfIzdaLas)
        bloqueLidarCoordMinX = xInfIzdaLas
        # bloqueLidarCoordMaxX = xInfIzdaLas + (bloqueLidarNumPixelsX * pixelX)
        bloqueLidarCoordMaxX = xSupDchaLas

        # bloqueLidarCoordMinY = ySupIzdaLas + (bloqueLidarNumPixelsY * pixelY)
        bloqueLidarCoordMinY = yInfIzdaLas
        bloqueLidarCoordMaxY = ySupDchaLas

    if imagenCompleta:
        xOffRaster = 0
        yOffRaster = 0
        intersectNumPixelsX = bloqueLidarNumPixelsX
        intersectNumPixelsY = bloqueLidarNumPixelsY
        intersectMinX = rasterMinX
        intersectMaxX = rasterMaxX
        intersectMinY = rasterMinY
        intersectMaxY = rasterMaxY
    else:
        # xOffRaster, yOffRaster: medidos en pixeles
        if rasterMinX < bloqueLidarCoordMinX:
            xOffRaster = math.floor((bloqueLidarCoordMinX - rasterMinX) / pixel_with)
            intersectMinX = bloqueLidarCoordMinX
            if rasterMaxX > bloqueLidarCoordMaxX:
                intersectMaxX = bloqueLidarCoordMaxX
                intersectNumPixelsX = bloqueLidarNumPixelsX
            else:
                intersectMaxX = rasterMaxX
                intersectNumPixelsX = bloqueLidarNumPixelsX - math.floor(((bloqueLidarCoordMaxX - rasterMaxX) / pixel_with))
            # print('\tclidcarto-> Intersecccion->1a', intersectMinX, intersectMaxX)
        else:
            xOffRaster = 0
            intersectMinX = rasterMinX
            if rasterMaxX > bloqueLidarCoordMaxX:
                intersectMaxX = bloqueLidarCoordMaxX
                intersectNumPixelsX = bloqueLidarNumPixelsX - math.floor(((rasterMinX - bloqueLidarCoordMinX) / pixel_with))
            else:
                intersectMaxX = rasterMaxX
                intersectNumPixelsX = bloqueLidarNumPixelsX - math.floor(((bloqueLidarCoordMaxX - rasterMaxX + rasterMinX - bloqueLidarCoordMinX) / pixel_with))
            # print('\tclidcarto-> Intersecccion->1b', intersectMinX, intersectMaxX)

        if rasterMaxY > bloqueLidarCoordMaxY:
            yOffRaster = math.floor((rasterMaxY - bloqueLidarCoordMaxY) / pixel_height)
            intersectMaxY = bloqueLidarCoordMaxY
            if rasterMinY < bloqueLidarCoordMinY:
                intersectMinY = bloqueLidarCoordMinY
                intersectNumPixelsY = bloqueLidarNumPixelsY
            else:
                intersectMinY = rasterMinY
                intersectNumPixelsY = bloqueLidarNumPixelsY - math.floor(((rasterMinY - bloqueLidarCoordMinY) / pixel_with))
            # print('\tclidcarto-> Intersecccion->2a', intersectMinY, intersectMaxY)
        else:
            yOffRaster = 0
            intersectMaxY = rasterMaxY
            if rasterMinY < bloqueLidarCoordMinY:
                intersectNumPixelsY = bloqueLidarNumPixelsY - math.floor(((bloqueLidarCoordMaxY - rasterMaxY) / pixel_with))
                intersectMinY = bloqueLidarCoordMinY
            else:
                intersectNumPixelsY = bloqueLidarNumPixelsY - math.floor(((bloqueLidarCoordMaxY - rasterMaxY + rasterMinY - bloqueLidarCoordMinY) / pixel_with))
                intersectMinY = rasterMinY
            # print('\tclidcarto-> Intersecccion->2b', intersectMinY, intersectMaxY)
        xOffRaster = int(xOffRaster)
        yOffRaster = int(yOffRaster)

    if intersectNumPixelsX == 0 or intersectNumPixelsY == 0:
        haySolape = False


#     origenX_Imagen = infoSourceDataset['origenX']
#     origenY_Imagen = infoSourceDataset['origenY']
#     pixelX = infoSourceDataset['pixelX']
#     pixelY = infoSourceDataset['pixelY']
#     nPixelsX = infoSourceDataset['nPixelsX']
#     nPixelsY = infoSourceDataset['nPixelsY']
    if LCLverbose: # or GLO.GLBLhuso29 or '_H29_' in GLO.MAINprocedimiento:
        # print( '\tclidcarto-> Origen de la imagen:        ', origenX_Imagen, origenY_Imagen )
        # print( '\tclidcarto-> Nota: Arcgis dice que el origen esta 13 m a la dcha y 12 m arriba ?' )
        # print( '\tclidcarto-> Puede estar relacionado con la unidad angular que considera?' )
        # print( '\tclidcarto-> En cambio QGIS recoge estas mismas coordenadas en la extension de la capa' )
        print('\tclidcarto-> Coordenadas del raster y del bloqueLidar:')
        print('\t\t-> Coordenadas min imagen:  rasterMinX: %0.2f - rasterMinY: %0.2f' % (rasterMinX, rasterMinY))
        print('\t\t-> Coordenadas max imagen:  rasterMaxX: %0.2f - rasterMaxY: %0.2f' % (rasterMaxX, rasterMaxY))
        print('\t\t-> Coordenadas min lasFile/interseccion:  CoordMinX: %0.2f - CoordMinY: %0.2f' % (bloqueLidarCoordMinX, bloqueLidarCoordMinY))
        print('\t\t-> Coordenadas max lasFile/interseccion:  CoordMaxX: %0.2f - CoordMaxY: %0.2f' % (bloqueLidarCoordMaxX, bloqueLidarCoordMaxY))
        print('\tclidcarto-> Dimension del pixel de la imagen raster:')
        print(f'\t\t-> pixel_with:   {pixel_with} (= {pixelX})')
        print(f'\t\t-> pixel_height: {pixel_height} (= abs({pixelY}))')
        print('\tclidcarto-> Numero de pixeles de la imagen raster:')
        print(f'\t\t-> Num de pixels de la imagen {nPixelsX} x {nPixelsY}')
        print('\tclidcarto-> Numero de pixeles que corresponden al bloqueLidar (considerando pixeles de {pixel_with} x {pixel_height}):')
        print(f'\t\t-> bloqueLidarNumPixelsX: {bloqueLidarNumPixelsX}')
        print(f'\t\t-> bloqueLidarNumPixelsY: {bloqueLidarNumPixelsY}')

        print('\tclidcarto-> Intersecccion:')
        print(f'\t\t-> Num de pixels de la intersec -> Columnas (X): {intersectNumPixelsX}; Filas (Y): {intersectNumPixelsY}')
        print('\t\t-> Coordenadas min intersec: {:0.02} - {:0.02}'.format(intersectMinX, intersectMinY))
        print('\t\t-> Coordenadas max intersec: {:0.02} - {:0.02}'.format(intersectMaxX, intersectMaxY))
        print(f'\t\t-> Offset de intersec rpto imagen: {xOffRaster} - {yOffRaster}')

    return [haySolape, xOffRaster, yOffRaster, intersectNumPixelsX, intersectNumPixelsY, intersectMinX, intersectMinY, intersectMaxX, intersectMaxY]


# ==============================================================================
def infoRasterDataset(dataset, mostrar=True):
    geotransform = dataset.GetGeoTransform()
    if geotransform is None:
        print('clidcarto-> La imagen no esta georreferenciada:')
        origenX = 0
        origenY = 0
        pixelX = 1
        pixelY = 1
    else:
        origenX = geotransform[0]
        origenY = geotransform[3]
        pixelX = geotransform[1]
        pixelY = geotransform[5]
    nPixelsX = dataset.RasterXSize
    nPixelsY = dataset.RasterYSize
    nBandas = dataset.RasterCount

    if mostrar: # or GLO.GLBLhuso29 or '_H29_' in GLO.MAINprocedimiento:
        print('\tclidcarto-> Driver      :', dataset.GetDriver().ShortName, '/', dataset.GetDriver().LongName)
        getProj = dataset.GetProjection()
        if getProj is None or getProj == '':
            print('\tclidcarto-> Projection  : no hay info de SRC')
        else:
            print('\tclidcarto-> Projection  :', type(getProj), '->', getProj)
        # getProjRef = dataset.GetProjectionRef()
        # print( '\tclidcarto-> Projection [GetProjectionRef()]:', type(getProjRef), getProjRef)
        print('\tclidcarto-> Origen      :', origenX, origenY)
        print('\tclidcarto-> Metros pixel:', pixelX, pixelY)
        print('\tclidcarto-> Num pixels  :', nPixelsX, 'x', nPixelsY, 'metros')
        print('\tclidcarto-> Num bandas  :', nBandas)
        print('\tclidcarto-> Metadatos   :', dataset.GetMetadata())
    return {'origenX': origenX, 'origenY': origenY, 'pixelX': pixelX, 'pixelY': pixelY, 'nPixelsX': nPixelsX, 'nPixelsY': nPixelsY, 'nBandas': nBandas}


# ==============================================================================
def normalizarRgb8bits(inputArray, nombreCapa=''):
    # Capas de 16 bits, las divido por 255 y guardo como uint8
    inputArray = inputArray / 255.0
    return inputArray.astype(np.uint8)


# ==============================================================================
def normalizarInt8bits(inputArray, nombreCapa=''):
    # Valor de 8 bits, simplemente convertir a uint8
    return inputArray.astype(np.uint8)


# ==============================================================================
def normalizarNdv8bits(inputArray, nombreCapa=''):
    # Float de rango -1 a +1 -> Paso a rango 0-255: x127 +127 y convertir a uint8:
    inputArray = 127 + (127 * inputArray)
    return inputArray.astype(np.uint8)


# ==============================================================================
def normalizarPteAbs8bits(inputArray, nombreCapa=''):
    # Trunco los valores extremos {abs(pte)>9}, aplico logaritmo decimal del valor absoluto
    # Paso a rango 0-255: x255 y convertir a uint8:
    inputArray[inputArray >= 9] = 9
    inputArray[inputArray <= -9] = -9
    # Uso el logaritmo para acentuar las diferencias d ependeinte cercanas a ceo
    # A la pendiente nula se le asigna el valor 127; la mas negativa (-9 o menos): 0 y la mas positiva (9 o mas): 255
    inputArray = 255 * np.log10(np.abs(inputArray) + 1)
    return inputArray.astype(np.uint8)


# ==============================================================================
def normalizarPte8bits(inputArray, nombreCapa=''):
    # Uso el logaritmo para acentuar las diferencias de pendiente cercanas a cero
    # Trunco los valores extremos {abs(pte)>17},
    # aplico logaritmo decimal del valor absoluto
    # y repongo el signo para tener rango -1 a +1
    # Paso a rango 0-255: x127 +127 y convertir a int8:
    # print('clidcato-> Pre normalizando pte a 8bits:', nombreCapa, inputArray.dtype, 'Rango de valores:', np.min(inputArray), np.max(inputArray), inputArray[30:31, 20:25])
    inputArray[inputArray >= 17.8] = 17.8
    inputArray[inputArray <= -17.8] = -17.8
    # inputArray[np.abs(inputArray) < 0.1] = np.sign(inputArray[np.abs(inputArray) < 0.1]) * 0.1
    # A la pendiente nula se le asigna el valor 127; la mas negativa (-17 o menos): 0 y la mas positiva (17 o mas): 255
    inputArray = 127.5 + (np.sign(inputArray) * 100 * np.log10(np.abs(inputArray) + 1))
    # print('        -> post normalizando pte a 8bits:', nombreCapa)
    # print('           ', inputArray.astype(np.int8).dtype, inputArray.shape, 'Rango de valores:', np.min(inputArray), np.max(inputArray), inputArray[30:31, 20:25].astype(np.int8))
    return inputArray.astype(np.int8)


# ==============================================================================
def normalizarMse8bits(inputArray, nombreCapa=''):
    # Trunco los valores extremos (>18m), aplico log10 a ese (valor/2)+1 y x 255
    inputArray[inputArray >= 18] = 18
    inputArray[inputArray <= 1E-6] = 1E-6
    inputArray = 255 * np.log10((inputArray / 2) + 1)
    return inputArray.astype(np.uint8)


# ==============================================================================
def normalizarDif8bits(inputArray, nombreCapa=''):
    # Trunco los valores extremos (>90 dm), aplico log10 a ese (valor/10)+1 y x 255
    inputArray[inputArray >= 90] = 90
    inputArray[inputArray <= 0] = 0
    inputArray = 255 * np.log10((inputArray / 10.0) + 1)
    return inputArray.astype(np.uint8)


# ==============================================================================
def normalizarCota16bits(inputArray, nombreCapa=''):
    # Trunco los valores extremos (>1950) y x255x255/1950
    # El resultado discrimina 3 cm (1.950 / 65.025 = 0.03 m).
    inputArray[inputArray >= 1950] = 1950
    inputArray = 255 * 255 * inputArray / 1950
    return inputArray.astype(np.uint16)


# ==============================================================================
def normalizarCota8bits(inputArray, nombreCapa=''):
    # Trunco los valores extremos (>1530) y x255/1530
    # El resultado discrimina 6 m (1530 / 255 = 6 m).
    inputArray[inputArray >= 1530] = 1530
    inputArray = 255 * inputArray / 1530
    return inputArray.astype(np.uint8)


# ==============================================================================
def normalizarCotaAbsolutaTruncandoA1500m(inputArray, nombreCapa=''):
    # Trunco los valores extremos (>1500) y paso a 8 bits-> precision = 6 m.
    inputArray[inputArray >= 1500] = 1500
    return (inputArray / 6) .astype(np.uint8)


# ==============================================================================
def normalizar8bits(inputArray, nombreCapa=''):
    # Normalizo array de dos dimensiones (una capa)
    inputArrayMins = np.min(inputArray)
    inputArrayMaxs = np.max(inputArray)
    if (inputArrayMaxs - inputArrayMins).any() == 0:
        inputArray = np.zeros(inputArray.shape, dtype=np.uint8)
    else:
        inputArray = 255 * (inputArray - inputArrayMins) / (inputArrayMaxs - inputArrayMins)
    return inputArray.astype(np.uint8)


# ==============================================================================
def normalizar01(inputArray, nombreCapa=''):
    # Normalizo array de dos dimensiones (una capa)
    inputArrayMins = np.min(inputArray)
    inputArrayMaxs = np.max(inputArray)
    if (inputArrayMaxs - inputArrayMins).any() == 0:
        inputArray = np.zeros(inputArray.shape, dtype=np.uint8)
    else:
        inputArray = (inputArray - inputArrayMins) / (inputArrayMaxs - inputArrayMins)
    return inputArray


# ==============================================================================
def normalizar0std(inputArray, nombreCapa=''):
    nPixels = inputArray.shape[0] * inputArray.shape[1]
    nCanals = inputArray.shape[2]
    inputArrayFlatten = np.reshape(inputArray, (nPixels, nCanals))
    # Valor medio de todos los valores (x e y) de cada variable
    # inputArrayMeans = np.mean(inputArrayFlatten, axis=0, dtype=np.float32)
    inputArrayMins = np.min(inputArrayFlatten, axis=0, dtype=np.float32)
    inputArrayStds = np.std(inputArrayFlatten, axis=0, dtype=np.float32)
    # Le agrego dos dimensiones al array de std para poder restarlo: creo que no hace falta
    inputArrayStds = np.reshape(inputArrayStds, (1, 1, nCanals))
    inputArrayStds[inputArrayStds <= 1e-6] = 1.0  # Evito problemas de division por cero

    inputArray = (inputArray - inputArrayMins) / inputArrayStds
    return inputArray


# ==============================================================================
def normalizarCapas(tileRecorte, nombreCapas):
    # pte: Valorar que pasa con los noData en la normalizacion
    tileRecorteNormalizado = np.zeros(tileRecorte.shape, dtype=np.uint8)
    for numCapa in range(tileRecorte.shape[2]):
        if (
            nombreCapas[numCapa] == 'RedPtoMax'
            or nombreCapas[numCapa] == 'RedPtoMin'
            or nombreCapas[numCapa] == 'GreenPtoMax'
            or nombreCapas[numCapa] == 'GreenPtoMin'
            or nombreCapas[numCapa] == 'BluePtoMax'
            or nombreCapas[numCapa] == 'BluePtoMin'
            or nombreCapas[numCapa] == 'NirPtoMax'
            or nombreCapas[numCapa] == 'NirPtoMin'
            or nombreCapas[numCapa] == 'intSRetMed'
            or nombreCapas[numCapa] == 'intSRetMed1m'
        ):
            # Capas de 16 bits: las divido por 255 y guardo como uint8
            tileRecorteNormalizado[:, :, numCapa] = normalizarRgb8bits(tileRecorte[:, :, numCapa], nombreCapa=nombreCapas[numCapa])
        elif nombreCapas[numCapa] == 'ndviMed' or nombreCapas[numCapa] == 'ndwiMed':
            # Float de rango [-1, +1]: -> + 1 x 127 y convertir a uint8
            tileRecorteNormalizado[:, :, numCapa] = normalizarNdv8bits(tileRecorte[:, :, numCapa], nombreCapa=nombreCapas[numCapa])
        elif nombreCapas[numCapa] == 'ndviMed1m':
            # Float de rango [-1, +1]: -> + 1 x 127 y convertir a uint8
            tileRecorteNormalizado[:, :, numCapa] = normalizarNdv8bits(tileRecorte[:, :, numCapa], nombreCapa=nombreCapas[numCapa])
        elif (
            nombreCapas[numCapa] == 'pteXglobal'
            or nombreCapas[numCapa] == 'pteYglobal'
        ):
            # Pte en tanto x 1: Trunco los valores extremos {abs(pte)>9}, aplico logaritmo decimal del valor absoluto y repongo el signo para tener rango -1 a +1
            # Paso a rango 0-255: x127 +127 y convertir a uint8:
            tileRecorteNormalizado[:, :, numCapa] = normalizarPte8bits(tileRecorte[:, :, numCapa], nombreCapa=nombreCapas[numCapa])
        elif (
            nombreCapas[numCapa] == 'pteXx50MicroPlanoNubePuntual'
            or nombreCapas[numCapa] == 'pteYx50MicroPlanoNubePuntual'
        ):
            # Pte en tanto x 10: Debiera tener truncados los valores extremos {abs(pte)>100}, aplico logaritmo decimal del valor absoluto y repongo el signo para tener rango -1 a +1
            # Paso a rango 0-255: x127 +127 y convertir a uint8:
            tileRecorteNormalizado[:, :, numCapa] = normalizarPte8bits(tileRecorte[:, :, numCapa].astype(np.float32) / 50.0, nombreCapa=nombreCapas[numCapa])
        elif (nombreCapas[numCapa] == 'ecmrGlobal'):
            # Float positivo en m: Trunco los valores extremos (>18m), aplico log10 a ese (valor/2)+1 y x 255
            tileRecorteNormalizado[:, :, numCapa] = normalizarMse8bits(tileRecorte[:, :, numCapa], nombreCapa=nombreCapas[numCapa])
        elif (nombreCapas[numCapa] == 'mseByteMicroPlanoNubePuntual'):
            # Float positivo en m: Trunco los valores extremos (>18m), aplico log10 a ese (valor/2)+1 y x 255
            tileRecorteNormalizado[:, :, numCapa] = normalizarMse8bits(tileRecorte[:, :, numCapa].astype(np.float32) / 50.0, nombreCapa=nombreCapas[numCapa])
        elif nombreCapas[numCapa] == 'CotaMdf' or nombreCapas[numCapa] == 'cotaMin':
            # Float32 positivo en m: Trunco los valores extremos (>1530m) y x255/1530
            tileRecorteNormalizado[:, :, numCapa] = normalizarCota8bits(tileRecorte[:, :, numCapa], nombreCapa=nombreCapas[numCapa])
            # No guardo en 16 bits
            ##Float32 positivo en m: Trunco los valores extremos (>1950m) y x255x255/1950
            # tileRecorteNormalizado[:, :, numCapa] = normalizarCota16bits(tileRecorte[:, :, numCapa])
        elif nombreCapas[numCapa] == 'cotaAbsolutaDmMinSubCel':
            # uint16 en dm: Trunco a 1500 y divido por 6 para tener un rango de 0 a 250
            tileRecorteNormalizado[:, :, numCapa] = normalizarCotaAbsolutaTruncandoA1500m(
                tileRecorte[:, :, numCapa] / 10, nombreCapa=nombreCapas[numCapa]
            )
        elif (
            nombreCapas[numCapa] == 'DifCota'
            or nombreCapas[numCapa] == 'AltDmPlus20SobreMdt8bits'
            or nombreCapas[numCapa] == 'AltMaxSobreMdfResta'
            or nombreCapas[numCapa] == 'AltMaxSobreMdpMacro'
            or nombreCapas[numCapa] == 'AltMaxSobreMdpMicro'
            or nombreCapas[numCapa] == 'AltP95SobreMdf'
            or nombreCapas[numCapa] == 'AltMaxSobreMdf'
            or nombreCapas[numCapa] == 'AltMinSobreMdf'
            or nombreCapas[numCapa] == 'cotaRelDmMaxNubePuntual'
            or nombreCapas[numCapa] == 'cotaRelDmPlanoNubePuntual'
        ):
            # Dif de cota en m: trunco los valores extremos (>90), aplico log10 a ese (valor/10)+1 y x 255
            tileRecorteNormalizado[:, :, numCapa] = normalizarDif8bits(tileRecorte[:, :, numCapa], nombreCapa=nombreCapas[numCapa])
        elif nombreCapas[numCapa][:11].lower() == 'lateralidad':
            # float64: pendiente del plano ajustado a los saltos en las 8 direcciones principales
            # Esta pendiente se calcula con la funcion clidnv2y.detectarRugosidad{}. Me da igual el signo.
            # Trunco los valores extremos {abs(pte)>9}, aplico logaritmo decimal del valor absoluto
            # Paso a rango 0-255: x255 y convertir a uint8:
            tileRecorteNormalizado[:, :, numCapa] = normalizarPteAbs8bits(tileRecorte[:, :, numCapa], nombreCapa=nombreCapas[numCapa])
        elif (
            nombreCapas[numCapa][:4].lower() == 'rugosidadminmax'
            or nombreCapas[numCapa] == 'AltPlanoTejado1m'
        ):
            # rugosidadminmax es uint8: indice de rugosidad de 0 a 240: no necesita normalizar
            #     Este indice se calcula con la funcion clidnv2y.detectarRugosidad{}
            # AltPlanoTejado1m es uint8 -> no necesita normalizar
            tileRecorteNormalizado[:, :, numCapa] = tileRecorte[:, :, numCapa]
        else:
            print('clidcarto-> ATENCION normalizando a 8 bits de forma no normalizada. nombreCapas:', nombreCapas)
            tileRecorteNormalizado[:, :, numCapa] = normalizar8bits(tileRecorte[:, :, numCapa], nombreCapa=nombreCapas[numCapa])
    return tileRecorteNormalizado.astype(np.uint8)


# ==============================================================================
def crearTilesTargetReDepurados(
        myLasData,
        myLasHead,
        train_dir='train',
        fileCoordYear='0_0',
        LCLmantenerTilesGuardados=False,
    ):

    # ==========================================================================
    # Calculo dimensiones para tiles de subCeldas y de celdillas (metricos)
    GLBNtileSizeEnPixelsSubCelda = int(math.ceil(GLO.GLBLtileSizeMetros / GLO.GLBLmetrosSubCelda)) # -> 128 ($256)
    GLBNtileSizeEnPixelsCeldilla = int(math.ceil(GLO.GLBLtileSizeMetros / GLO.GLBLmetrosCeldilla)) # -> 256 ($512)
    GLBNtileSemiSolapePixelsSubCelda = int(math.floor(GLO.GLBLtileSemiSolapeMetros / GLO.GLBLmetrosSubCelda)) # -> 0 ($3)
    GLBNtileSemiSolapePixelsCeldilla = int(math.floor(GLO.GLBLtileSemiSolapeMetros / GLO.GLBLmetrosCeldilla)) # -> 0 ($6)
    GLBNtileKernelMetros = (GLO.GLBLtileSizeMetros - (2 * GLO.GLBLtileSemiSolapeMetros))
    GLBNtileKernelPixelsSubCelda = (GLBNtileSizeEnPixelsSubCelda - (2 * GLBNtileSemiSolapePixelsSubCelda))
    GLBNtileKernelPixelsCeldilla = (GLBNtileSizeEnPixelsCeldilla - (2 * GLBNtileSemiSolapePixelsSubCelda))

    nSubCeldasRasterRefY = myLasData.nCeldasY * GLBNsubCeldasPorCelda # -> 1000
    nSubCeldasRasterRefX = myLasData.nCeldasX * GLBNsubCeldasPorCelda # -> 1000
    nCeldillasRasterRefX = int(math.ceil(myLasHead.metrosBloqueX / GLO.GLBLmetrosCeldilla)) # -> 2000
    nCeldillasRasterRefY = int(math.ceil(myLasHead.metrosBloqueY / GLO.GLBLmetrosCeldilla)) # -> 2000
    numTilesRows = int(math.ceil(nSubCeldasRasterRefY / GLBNtileSizeEnPixelsSubCelda)) # -> 8 ($4)
    numTilesCols = int(math.ceil(nSubCeldasRasterRefX / GLBNtileSizeEnPixelsSubCelda)) # -> 8 ($4)

    margenXsobresalienteMetros = GLO.GLBLtileSemiSolapeMetros + (((numTilesCols * GLBNtileKernelMetros) - GLO.GLBLmetrosBloque) / 2) # -> 24 ($6)
    margenYsobresalienteMetros = GLO.GLBLtileSemiSolapeMetros + (((numTilesRows * GLBNtileKernelMetros) - GLO.GLBLmetrosBloque) / 2) # -> 24 ($6)
    margenXsobresalientePixelsScA = int(math.floor(margenXsobresalienteMetros / GLO.GLBLmetrosSubCelda))
    margenXsobresalientePixelsScB = int(math.ceil(margenXsobresalienteMetros / GLO.GLBLmetrosSubCelda))
    margenYsobresalientePixelsScA = int(math.floor(margenYsobresalienteMetros / GLO.GLBLmetrosSubCelda))
    margenYsobresalientePixelsScB = int(math.ceil(margenYsobresalienteMetros / GLO.GLBLmetrosSubCelda))
    margenXsobresalientePixelsCdA = int(math.floor(margenXsobresalienteMetros / GLO.GLBLmetrosCeldilla))
    margenXsobresalientePixelsCdB = int(math.ceil(margenXsobresalienteMetros / GLO.GLBLmetrosCeldilla))
    margenYsobresalientePixelsCdA = int(math.floor(margenYsobresalienteMetros / GLO.GLBLmetrosCeldilla))
    margenYsobresalientePixelsCdB = int(math.ceil(margenYsobresalienteMetros / GLO.GLBLmetrosCeldilla))

    # Creacion de directorios para los tiles exData
    if GLO.GLBLcrearTilesExDataMiniSubCelLasClass:
        subDirExDataMiniSubCelLasClass_2_345_6 = 'pngExDataMiniSubCelLasClass_2_345_6_reDepurada'
        trainPathExDataMiniSubCelLasClass_2_345_6 = os.path.join(
            GLO.MAINrutaOutput,
            train_dir,
            subDirExDataMiniSubCelLasClass_2_345_6
        )
        if not os.path.isdir(trainPathExDataMiniSubCelLasClass_2_345_6):
            numIntentosEscritura = 0
            while True:
                numIntentosEscritura += 1
                try:
                    os.makedirs(trainPathExDataMiniSubCelLasClass_2_345_6)
                    break
                except:
                    time.sleep(5)
                    if numIntentosEscritura > 5:
                        break
            print(
                'cartolider.{:006}-> Creando directorio exData: {}'.format(
                    GLO.MAINidProceso, trainPathExDataMiniSubCelLasClass_2_345_6
                )
            )
    else:
        trainPathExDataMiniSubCelLasClass_2_345_6 = ''

    subDirPngTargetLasClass_2_345_6 = 'pngTargetMiniSubCelLasClass_2_345_6_reDepurada/'
    subDirPngTargetLasClass02Binary = 'pngTargetMiniSubCelLasClass02Binary_reDepurada/'
    trainPathPngTargetTriClass = os.path.join(GLO.MAINrutaOutput, train_dir, subDirPngTargetLasClass_2_345_6)
    trainPathPngTargetBinClass = os.path.join(GLO.MAINrutaOutput, train_dir, subDirPngTargetLasClass02Binary)
    if GLO.GLBLformatoTilesAscInput:
        trainPathAscTargetTriClass = (trainPathPngTargetTriClass.replace('/png', '/asc')).replace('\png', '/asc')
        trainPathAscTargetBinClass = (trainPathPngTargetBinClass.replace('/png', '/asc')).replace('\png', '/asc')
    nombreCapaTargetTriClass = 'LasClass_2_345_6'
    nombreCapaTargetBinClass = 'LasClass02Binary'


#     if GLO.GLBLusarMiniSubCelPselEnVezDeTlp:
#         if GLO.GLBLusarFormatoDtypeMaxiMiniSubCel:
#             arrayCapaTargetOriClas = np.zeros(
#                 (
#                     myLasData.aSubCeldasPuntoMiniSubCelPsuePsel.shape[0],
#                     myLasData.aSubCeldasPuntoMiniSubCelPsuePsel.shape[1],
#                 ), dtype=np.uint8
#             )
#             histogramaLasClass = np.zeros(20, dtype=np.int32)
#             for nX in range(myLasData.aSubCeldasPuntoMiniSubCelPsuePsel.shape[0]):
#                 for nY in range(myLasData.aSubCeldasPuntoMiniSubCelPsuePsel.shape[1]):
#                     lasClassValue = myLasData.aSubCeldasPuntoMiniSubCelPsuePsel[nX, nY]['lasClassOriginal']
#                     arrayCapaTargetOriClas[nX, nY] = lasClassValue
#                     histogramaLasClass[lasClassValue] += 1
#             if GLO.GLBLverbose:
#                 print('clidcarto-> Controlando TargetClass-> histograma lasClassOriginal[:]:  {}'.format(histogramaLasClass))
#         else:
#             arrayCapaTargetOriClas = myLasData.aSubCeldasPuntoMiniSubCelPsel[:, :, 8:9]
#     else:
#         arrayCapaTargetOriClas = np.zeros(
#             (
#                 myLasData.aSubCeldasPuntoMiniSubCel_Tlp.shape[0],
#                 myLasData.aSubCeldasPuntoMiniSubCel_Tlp.shape[1],
#             ), dtype=np.uint8
#         )
#         for nX in range(myLasData.aSubCeldasPuntoMiniSubCel_Tlp.shape[0]):
#             for nY in range(myLasData.aSubCeldasPuntoMiniSubCel_Tlp.shape[1]):
#                 arrayCapaTargetOriClas[nX, nY] = myLasData.aSubCeldasPuntoMiniSubCel_Tlp[nX, nY]['lasClassOriginal']


    if GLO.GLBLreorganizaLasClassParaGenerarTilesCuaTrinarios_X_6_2_345:
        if GLO.GLBLusarMiniSubCelPselEnVezDeTlp:
            if GLO.GLBLusarFormatoDtypeMaxiMiniSubCel:
                arrayCapaTargetTriClas = np.zeros(
                    (
                        myLasData.aSubCeldasPuntoMiniSubCelPsuePsel.shape[0],
                        myLasData.aSubCeldasPuntoMiniSubCelPsuePsel.shape[1],
                    ), dtype=np.uint8
                )
                histogramaLasClass = np.zeros(20, dtype=np.int32)
                for nX in range(myLasData.aSubCeldasPuntoMiniSubCelPsuePsel.shape[0]):
                    for nY in range(myLasData.aSubCeldasPuntoMiniSubCelPsuePsel.shape[1]):
                        lasClassValue = myLasData.aSubCeldasPuntoMiniSubCelPsuePsel[nX, nY]['lasClass_2_345_6']
                        arrayCapaTargetTriClas[nX, nY] = lasClassValue
                        histogramaLasClass[lasClassValue] += 1
                if GLO.GLBLverbose:
                    print('clidcarto-> Controlando TargetClass-> histograma lasClass_2_345_6[:4]: {}'.format(histogramaLasClass[:4]))
            else:
                arrayCapaTargetTriClas = myLasData.aSubCeldasPuntoMiniSubCelPsel[:, :, 9:10]
        else:
            arrayCapaTargetTriClas = np.zeros(
                (
                    myLasData.aSubCeldasPuntoMiniSubCel_Tlp.shape[0],
                    myLasData.aSubCeldasPuntoMiniSubCel_Tlp.shape[1],
                ), dtype=np.uint8
            )
            for nX in range(myLasData.aSubCeldasPuntoMiniSubCel_Tlp.shape[0]):
                for nY in range(myLasData.aSubCeldasPuntoMiniSubCel_Tlp.shape[1]):
                    arrayCapaTargetTriClas[nX, nY] = myLasData.aSubCeldasPuntoMiniSubCel_Tlp[nX, nY]['lasClass_2_345_6']

    if GLO.GLBLreorganizaLasClassParaGenerarTilesBinariosMonoClase:
        arrayCapaTargetBinClas = arrayCapaTargetTriClas.copy()
        if GLO.GLBLreorganizaLasClassParaGenerarTilesBinariosMonoClase == 6: # La clase 6 (edificio) cambia en TriClass a 1
            arrayCapaTargetBinClas[arrayCapaTargetBinClas == 1] = 1
            arrayCapaTargetBinClas[arrayCapaTargetBinClas != 1] = 0
        elif GLO.GLBLreorganizaLasClassParaGenerarTilesBinariosMonoClase == 2: # La clase 2 (edificio) se mantiene en TriClass
            arrayCapaTargetBinClas[arrayCapaTargetBinClas == 2] = 1
            arrayCapaTargetBinClas[arrayCapaTargetBinClas != 2] = 0
        elif GLO.GLBLreorganizaLasClassParaGenerarTilesBinariosMonoClase == 3: # Incluye 3, 4 y 5, que en triClass se agrupan en la 3
            arrayCapaTargetBinClas[arrayCapaTargetBinClas == 3] = 1
            arrayCapaTargetBinClas[arrayCapaTargetBinClas != 3] = 0

    for trainPathPng in [
        trainPathPngTargetTriClass,
        trainPathPngTargetBinClass,
    ]:
        if not os.path.isdir(trainPathPng):
            os.makedirs(trainPathPng)
            print('\tclidcarto-> Creando directorio target png', trainPathPng)

    if GLO.GLBLformatoTilesAscInput:
        for trainPathPng in [
            trainPathPngTargetTriClass,
            trainPathPngTargetBinClass,
        ]:
            trainPathAsc = (trainPathPng.replace('/png', '/asc')).replace('\png', '/asc')
            if not os.path.isdir(trainPathAsc):
                os.makedirs(trainPathAsc)
                print('\tclidcarto-> Creando directorio target o train asc', trainPathAsc)
    # ======================================================================
    if GLO.GLBLverbose:
        print('clidcarto-> Se generan los {} x {} tiles.'.format(numTilesRows, numTilesCols))
    for nRow in range(numTilesRows):
        for nCol in range(numTilesCols):

            if nRow == 0:
                xInfIzdaTile = (myLasHead.xmin - margenXsobresalienteMetros)
                recorteIniY = 0
                recorteIniY1m = 0
            else:
                xInfIzdaTile = (
                    myLasHead.xmin
                    + (
                        GLO.GLBLtileSizeMetros
                        - margenXsobresalienteMetros
                        - GLO.GLBLtileSemiSolapeMetros
                    )
                    + ((nRow - 1) * GLBNtileKernelMetros)
                    - GLO.GLBLtileSemiSolapeMetros
                )
                recorteIniY = int(
                    (
                        GLBNtileSizeEnPixelsSubCelda
                        - margenYsobresalientePixelsScA
                        - GLBNtileSemiSolapePixelsSubCelda
                    )
                    + ((nRow - 1) * GLBNtileKernelPixelsSubCelda)
                    - GLBNtileSemiSolapePixelsSubCelda
                )
                recorteIniY1m = int(
                    (
                        GLBNtileSizeEnPixelsCeldilla
                        - margenYsobresalientePixelsCdA
                        - GLBNtileSemiSolapePixelsCeldilla
                    )
                    + ((nRow - 1) * GLBNtileKernelPixelsCeldilla)
                    - GLBNtileSemiSolapePixelsCeldilla
                 )
            if nCol == 0:
                yInfIzdaTile = (myLasHead.ymin - margenYsobresalienteMetros)
                recorteIniX = 0
                recorteIniX1m = 0
            else:
                yInfIzdaTile = (
                    myLasHead.ymin
                    + (
                        GLO.GLBLtileSizeMetros
                        - margenYsobresalienteMetros
                        - GLO.GLBLtileSemiSolapeMetros
                    )
                    + ((nCol - 1) * GLBNtileKernelMetros)
                    - GLO.GLBLtileSemiSolapeMetros
                )
                recorteIniX = int(
                    (
                        GLBNtileSizeEnPixelsSubCelda
                        - margenXsobresalientePixelsScA
                        - GLBNtileSemiSolapePixelsSubCelda
                    )
                    + ((nCol - 1) * GLBNtileKernelPixelsSubCelda)
                    - GLBNtileSemiSolapePixelsSubCelda
                )
                recorteIniX1m = int(
                    (
                        GLBNtileSizeEnPixelsCeldilla
                        - margenXsobresalientePixelsCdA
                        - GLBNtileSemiSolapePixelsCeldilla
                    )
                    + ((nCol - 1) * GLBNtileKernelPixelsCeldilla)
                    - GLBNtileSemiSolapePixelsCeldilla
                )

            if nRow == 0:
                iniY = margenYsobresalientePixelsScA
                iniY1m = margenYsobresalientePixelsCdA
            else:
                iniY = 0
                iniY1m = 0
            if nCol == 0:
                iniX = margenXsobresalientePixelsScA
                iniX1m = margenXsobresalientePixelsCdA
            else:
                iniX = 0
                iniX1m = 0

            if nRow == numTilesRows - 1:
                finY = int(GLBNtileSizeEnPixelsSubCelda - margenYsobresalientePixelsScB)
                finY1m = int(GLBNtileSizeEnPixelsCeldilla - margenYsobresalientePixelsCdB)
            else:
                finY = int(GLBNtileSizeEnPixelsSubCelda)
                finY1m = int(GLBNtileSizeEnPixelsCeldilla)
            if nCol == numTilesCols - 1:
                finX = int(GLBNtileSizeEnPixelsSubCelda - margenXsobresalientePixelsScB)
                finX1m = int(GLBNtileSizeEnPixelsCeldilla - margenXsobresalientePixelsCdB)
            else:
                finX = int(GLBNtileSizeEnPixelsSubCelda)
                finX1m = int(GLBNtileSizeEnPixelsCeldilla)

            if GLO.GLBLverbose:
                print('\tclidcarto-> tiles 2m:', nRow, nCol, '->', iniY, finY, iniX, finX,
                      '->1m', nRow, nCol, '->', iniY1m, finY1m, iniX1m, finX1m)
                print('\t\ttiles 2m recorte', recorteIniY, recorteIniY + finY - iniY,
                      recorteIniX, recorteIniX + finX - iniX,
                      '->1m recorte', recorteIniY1m, recorteIniY1m + finY1m - iniY1m,
                      recorteIniX1m, recorteIniX1m + finX1m - iniX1m)

#             # if grabarTarget:
#             tileRecorte0TargetOriClass = np.zeros((GLBNtileSizeEnPixelsSubCelda, GLBNtileSizeEnPixelsSubCelda), dtype=arrayCapaTargetOriClas.dtype)
#             targetOriClasRecorteShape = arrayCapaTargetOriClas[recorteIniY : recorteIniY + finY - iniY, recorteIniX : recorteIniX + finX - iniX].shape
#             funY = iniY + targetOriClasRecorteShape[0]
#             funX = iniX + targetOriClasRecorteShape[1]
#             if (
#                 tileRecorte0TargetOriClass[iniY:funY, iniX:funX].shape
#                 == arrayCapaTargetOriClas[recorteIniY : recorteIniY + finY - iniY, recorteIniX : recorteIniX + finX - iniX].shape
#             ):
#                 tileRecorte0TargetOriClass[iniY:funY, iniX:funX] = arrayCapaTargetOriClas[recorteIniY : recorteIniY + finY - iniY, recorteIniX : recorteIniX + finX - iniX]
#             # No normalizo el target, que tiene valores ASPRS o,
#             #  si GLBLreorganizaLasClassParaGenerarTilesCuaTrinarios_X_6_2_345, con valores simplificados:
#             #    0 (sin datos), 1 (edificio), 2 (suelo), 3 (vegetacion)
#             #    Ver clidnv1.buscarGuardarPuntosMiniSubCel{} ln 1680)
#             # tileRecorte0Normalizado = normalizarCapas(tileRecorte0TargetOriClass, nombreCapaT)

            if GLO.GLBLreorganizaLasClassParaGenerarTilesCuaTrinarios_X_6_2_345:
                tileRecorte0TargetTriClass = np.zeros((GLBNtileSizeEnPixelsSubCelda, GLBNtileSizeEnPixelsSubCelda), dtype=arrayCapaTargetTriClas.dtype)
                targetTriClasRecorteShape = arrayCapaTargetTriClas[recorteIniY : recorteIniY + finY - iniY, recorteIniX : recorteIniX + finX - iniX].shape
                funY = iniY + targetTriClasRecorteShape[0]
                funX = iniX + targetTriClasRecorteShape[1]
                if (
                    tileRecorte0TargetTriClass[iniY:funY, iniX:funX].shape
                    == arrayCapaTargetTriClas[recorteIniY : recorteIniY + finY - iniY, recorteIniX : recorteIniX + finX - iniX].shape
                ):
                    tileRecorte0TargetTriClass[iniY:funY, iniX:funX] = arrayCapaTargetTriClas[recorteIniY : recorteIniY + finY - iniY, recorteIniX : recorteIniX + finX - iniX]

            if GLO.GLBLreorganizaLasClassParaGenerarTilesBinariosMonoClase:
                tileRecorte0TargetBinClas = np.zeros((GLBNtileSizeEnPixelsSubCelda, GLBNtileSizeEnPixelsSubCelda), dtype=arrayCapaTargetBinClas.dtype)
                targetBinClasRecorteShape = arrayCapaTargetBinClas[recorteIniY : recorteIniY + finY - iniY, recorteIniX : recorteIniX + finX - iniX].shape
                funY = iniY + targetBinClasRecorteShape[0]
                funX = iniX + targetBinClasRecorteShape[1]
                if (
                    tileRecorte0TargetBinClas[iniY:funY, iniX:funX].shape
                    == arrayCapaTargetBinClas[recorteIniY : recorteIniY + finY - iniY, recorteIniX : recorteIniX + finX - iniX].shape
                ):
                    tileRecorte0TargetBinClas[iniY:funY, iniX:funX] = arrayCapaTargetBinClas[recorteIniY : recorteIniY + finY - iniY, recorteIniX : recorteIniX + finX - iniX]

            if GLO.GLBLcrearTilesTargetMiniSubCelSoloSiHayNoSueloSuficientes:
                if GLO.GLBLreorganizaLasClassParaGenerarTilesCuaTrinarios_X_6_2_345:
                    listaSelectedTargets = [1] # La clase 6 (edificios) pasa a clase 1 en con cuatriClass
                    minPorcentajePixeles = [GLO.GLBLminPctjEdificiosParaCrearTileTargetMiniSubCel]
                elif GLO.GLBLreorganizaLasClassParaGenerarTilesBinariosMonoClase:
                    listaSelectedTargets = [1] # Clase significativa (no 0)
                    # Uso GLBLminPctjEdificiosParaCrearTileTargetMiniSubCel, sea cual sea la clase significativa elegida
                    minPorcentajePixeles = [GLO.GLBLminPctjEdificiosParaCrearTileTargetMiniSubCel]
                else:
                    # Sin implementar (dejo esto para que no de error)
                    listaSelectedTargets = [1]
                    # Uso GLBLminPctjEdificiosParaCrearTileTargetMiniSubCel, sea cual sea la clase significativa elegida
                    minPorcentajePixeles = [GLO.GLBLminPctjEdificiosParaCrearTileTargetMiniSubCel]
                miHistograma = np.bincount(tileRecorte0TargetTriClass.flatten())
                if len(miHistograma) <= min(listaSelectedTargets):
                    if GLO.GLBLverbose:
                        print('\t\tclidcarto-> tiles 2m:', nRow, nCol,
                              '-> Sin valores target seleccionados:', listaSelectedTargets)
                    continue
                nPixelsSelectedTargets = []
                tieneSuficientesPixelesDeLasCLasesElegidas = False
                for nLasClass, minPctj in zip(listaSelectedTargets, minPorcentajePixeles):
                    if len(miHistograma) > nLasClass:
                        nPixelsSelectedTargets.append(miHistograma[nLasClass])
                        if miHistograma[nLasClass] >= minPctj * sum(miHistograma) / 100.0:
                            tieneSuficientesPixelesDeLasCLasesElegidas = True
                    else:
                        nPixelsSelectedTargets.append(0)
                if not tieneSuficientesPixelesDeLasCLasesElegidas:
                    if GLO.GLBLverbose:
                        print('\t\tclidcarto-> tiles 2m:', nRow, nCol,
                              '-> Insuficientes pixeles de las clases seleccionadas')
                    continue


            if GLO.GLBLformatoTilesPng:
                pngFileNameTargetTriClass = os.path.join(trainPathPngTargetTriClass, '%s_%s_%i_%i.png' % (fileCoordYear, 'Train', nRow, nCol))
                pngFileNameTargetBinClass = os.path.join(trainPathPngTargetBinClass, '%s_%s_%i_%i.png' % (fileCoordYear, 'Train', nRow, nCol))

                # No lo hago para lasClassOriginal; solo para TriCLass y/o BinClass
#                 # 'lasClassOriginal'
#                 # colorMode = 'P'
#                 # palette = []
#                 colorMode = 'L'
#                 myImageBN = Image.fromarray(np.rot90(tileRecorte0TargetOriClass), colorMode)
#                 # https://pillow.readthedocs.io/en/5.1.x/reference/Image.html#PIL.Image.Image.save
#                 #  https://pillow.readthedocs.io/en/5.1.x/handbook/image-file-formats.html#image-file-formats
#                 #   https://pillow.readthedocs.io/en/5.1.x/handbook/image-file-formats.html#png
#                 if os.path.exists(pngFileNameTargetOriClass) and not LCLmantenerTilesGuardados:
#                     os.remove(pngFileNameTargetOriClass)
#                 myImageBN.save(pngFileNameTargetOriClass)
#                 # ATENCION: No elegir el modo "P" (palette) porque reorganiza los valores de los pixeles y luego no se pueden interpretar
#                 # myImageConPaleta = myImageBN.convert("P", palette = Image.ADAPTIVE, colors = 25)
#                 # myImageConPaleta.save(pngFileNameTargetOriClass)
#                 if GLO.GLBLformatoTilesAscInput:
#                     capaTileRecorte = tileRecorte0TargetOriClass[:, :]
#                     nombreCapa = nombreCapaTargetOriClass
#                     ascFileNameScipyZoom = os.path.join(trainPathAscTargetOriClass, '%s_%s_%i_%i.asc' % (fileCoordYear, nombreCapa, nRow, nCol))
#                     crearASC(
#                         ascFileNameScipyZoom,
#                         capaTileRecorte,
#                         capaTileRecorte.shape,
#                         GLBNtileSizeEnPixelsSubCelda,
#                         GLBNtileSizeEnPixelsSubCelda,
#                         GLO.GLBLmetrosSubCelda,
#                         xInfIzdaTile,
#                         yInfIzdaTile,
#                         GLO.GLBLnoData,
#                         nTipoDato=2,
#                     )

                if GLO.GLBLreorganizaLasClassParaGenerarTilesCuaTrinarios_X_6_2_345:
                    #print('clidcarto->->-> guardando targetTrinario:', pngFileNameTargetTriClass)
                    colorMode = 'L'
                    myImageBN = Image.fromarray(np.rot90(tileRecorte0TargetTriClass), colorMode)
                    if os.path.exists(pngFileNameTargetTriClass) and not LCLmantenerTilesGuardados:
                        print('\t\tclidcarto->->-> Eliminando fichero triClass existente con pathlib:', pngFileNameTargetTriClass)
                        #os.remove(pngFileNameTargetTriClass)
                        (pathlib.Path(pngFileNameTargetTriClass)).unlink()
                        if os.path.exists(pngFileNameTargetTriClass):
                            print('\t\t\tNo se ha podido eliminar el fichero existente')
                    myImageBN.save(pngFileNameTargetTriClass)
                    if GLO.GLBLformatoTilesAscInput:
                        capaTileRecorte = tileRecorte0TargetTriClass[:, :]
                        nombreCapa = nombreCapaTargetTriClass
                        ascFileNameScipyZoom = os.path.join(trainPathAscTargetTriClass, '%s_%s_%i_%i.asc' % (fileCoordYear, nombreCapa, nRow, nCol))
                        crearASC(
                            ascFileNameScipyZoom,
                            capaTileRecorte,
                            capaTileRecorte.shape,
                            GLBNtileSizeEnPixelsSubCelda,
                            GLBNtileSizeEnPixelsSubCelda,
                            GLO.GLBLmetrosSubCelda,
                            xInfIzdaTile,
                            yInfIzdaTile,
                            GLO.GLBLnoData,
                            nTipoDato=2,
                        )

                if GLO.GLBLreorganizaLasClassParaGenerarTilesBinariosMonoClase:
                    colorMode = 'L'
                    myImageBN = Image.fromarray(np.rot90(tileRecorte0TargetBinClas), colorMode)
                    if os.path.exists(pngFileNameTargetBinClass) and not LCLmantenerTilesGuardados:
                        print('clidcarto-> Eliminando tile pngTargetBinClas previo: {}'.format(pngFileNameTargetBinClass))
                        os.remove(pngFileNameTargetBinClass)
                    myImageBN.save(pngFileNameTargetBinClass)
                    if GLO.GLBLformatoTilesAscInput:
                        capaTileRecorte = tileRecorte0TargetBinClas[:, :]
                        nombreCapa = nombreCapaTargetBinClass
                        ascFileNameScipyZoom = os.path.join(trainPathAscTargetBinClass, '%s_%s_%i_%i.asc' % (fileCoordYear, nombreCapa, nRow, nCol))
                        crearASC(
                            ascFileNameScipyZoom,
                            capaTileRecorte,
                            capaTileRecorte.shape,
                            GLBNtileSizeEnPixelsSubCelda,
                            GLBNtileSizeEnPixelsSubCelda,
                            GLO.GLBLmetrosSubCelda,
                            xInfIzdaTile,
                            yInfIzdaTile,
                            GLO.GLBLnoData,
                            nTipoDato=2,
                        )

                # Creacion de los tiles exData propiamente dichos
                if GLO.GLBLcrearTilesExDataMiniSubCelLasClass:
                    # No lo hago para tileRecorte0TargetOriClass; solo para TriCLass y/o BinClass
#                     lookupTable = [0 if (i == 0 or i == 12) else 1 for i in range(256)]
#                     # for lasClassNoData in [0, 12]:
#                     #     lookupTable[int(lasClassNoData)] = 0
#                     pngFileNameExData = os.path.join(
#                         trainPathExDataMiniSubCelLasClassOriginal,
#                         '%s_%s_%i_%i.png' % (fileCoordYear, 'Train', nRow, nCol)
#                     )
#                     # print('\t->->-> guardando exDataMiniSubCelLasClassOriginal:', pngFileNameExData)
#                     # Mapeo las 10 categorias de tileRecorteNormalizado a 1 y 0 (ceros las que se excluyen del entrenamiento):
#                     # Atencion: si uso colorMode = 'L' tengo que usar dtype=np.uint8
#                     colorMode = 'L'  # (8-bit pixels, black and white) -> lleva el valor max a 255 y el min a 0 -> No respeta los valores del array ->Espacio de color: Escala de grises
#                     tileRecorteExData = np.array(
#                         [lookupTable[val] for val in tileRecorte0TargetOriClass.flatten()],
#                         dtype=np.uint8
#                     ).reshape(tileRecorte0TargetOriClass.shape)
#                     myImageBN = Image.fromarray(np.rot90(tileRecorteExData), colorMode)
#                     if os.path.exists(pngFileNameExData) and not LCLmantenerTilesGuardados:
#                         print('\t\tclidcarto->->-> Eliminando fichero existente:', pngFileNameExData)
#                         os.remove(pngFileNameExData)
#                     myImageBN.save(pngFileNameExData)

                    # Solo se usan los miniSubCel que estan en alguna de las 3 clases (edificio, suelo, vegetacion)
                    lookupTable = [1 if (i in [1, 2, 3]) else 0 for i in range(256)]
                    # for lasClassNoData in [0, 12]:
                    #     lookupTable[int(lasClassNoData)] = 0
                    pngFileNameExData = os.path.join(
                        trainPathExDataMiniSubCelLasClass_2_345_6,
                        '%s_%s_%i_%i.png' % (fileCoordYear, 'Train', nRow, nCol)
                    )
                    # print('\t->->-> guardando exDataMiniSubCelLasClass_2_345_6:', pngFileNameExData)
                    # Mapeo las 10 categorias de tileRecorteNormalizado a 1 y 0 (ceros las que se excluyen del entrenamiento):
                    # Atencion: si uso colorMode = 'L' tengo que usar dtype=np.uint8
                    colorMode = 'L'  # (8-bit pixels, black and white) -> lleva el valor max a 255 y el min a 0 -> No respeta los valores del array ->Espacio de color: Escala de grises
                    if GLO.GLBLreorganizaLasClassParaGenerarTilesCuaTrinarios_X_6_2_345:
                        tileRecorteExData = np.array(
                            [lookupTable[val] for val in tileRecorte0TargetTriClass.flatten()],
                            dtype=np.uint8
                        ).reshape(tileRecorte0TargetTriClass.shape)
                    elif GLO.GLBLreorganizaLasClassParaGenerarTilesBinariosMonoClase:
                        tileRecorteExData = np.array(
                            [lookupTable[val] for val in tileRecorte0TargetBinClas.flatten()],
                            dtype=np.uint8
                        ).reshape(tileRecorte0TargetBinClas.shape)
                    myImageBN = Image.fromarray(np.rot90(tileRecorteExData), colorMode)
                    if os.path.exists(pngFileNameExData) and not LCLmantenerTilesGuardados:
                        print('\t\tclidcarto->->-> Eliminando fichero exData existente con pathlib:', pngFileNameExData)
                        #os.remove(pngFileNameExData)
                        (pathlib.Path(pngFileNameExData)).unlink()
                        if os.path.exists(pngFileNameExData):
                            print('\t\t\tNo se ha podido eliminar el fichero existente')
                    myImageBN.save(pngFileNameExData)

    tilesCreados = True
    print('clidcarto-> Ok tiles reDepurados creados')
    return tilesCreados


# ==============================================================================
def crearTilesInputTarget(
        myLasData,
        myLasHead,
        train_dir='train',
        fileCoordYear='0_0',
        grupoTiles='preVuelta2',
        LCLmantenerTilesGuardados=False,
        cartoRefUsoSingular=None,
        cartoRefLandCover=None,
        cartoRefNucleosUrbanos=None,
    ):

    # nXcentral = int(myLasData.aSubCeldasPuntoMiniSubCel_Tlp.shape[0] / 2)
    # nYcentral = int(myLasData.aSubCeldasPuntoMiniSubCel_Tlp.shape[0] / 2)

    # ==========================================================================
    # Calculo dimensiones para tiles de subCeldas y de celdillas (metricos)
    GLBNtileSizeEnPixelsSubCelda = int(math.ceil(GLO.GLBLtileSizeMetros / GLO.GLBLmetrosSubCelda)) # -> 128 ($256)
    GLBNtileSizeEnPixelsCeldilla = int(math.ceil(GLO.GLBLtileSizeMetros / GLO.GLBLmetrosCeldilla)) # -> 256 ($512)
    GLBNtileSemiSolapePixelsSubCelda = int(math.floor(GLO.GLBLtileSemiSolapeMetros / GLO.GLBLmetrosSubCelda)) # -> 0 ($3)
    GLBNtileSemiSolapePixelsCeldilla = int(math.floor(GLO.GLBLtileSemiSolapeMetros / GLO.GLBLmetrosCeldilla)) # -> 0 ($6)
    GLBNtileKernelMetros = (GLO.GLBLtileSizeMetros - (2 * GLO.GLBLtileSemiSolapeMetros))
    GLBNtileKernelPixelsSubCelda = (GLBNtileSizeEnPixelsSubCelda - (2 * GLBNtileSemiSolapePixelsSubCelda))
    GLBNtileKernelPixelsCeldilla = (GLBNtileSizeEnPixelsCeldilla - (2 * GLBNtileSemiSolapePixelsSubCelda))

    nSubCeldasRasterRefY = myLasData.nCeldasY * GLBNsubCeldasPorCelda # -> 1000
    nSubCeldasRasterRefX = myLasData.nCeldasX * GLBNsubCeldasPorCelda # -> 1000
    nCeldillasRasterRefX = int(math.ceil(myLasHead.metrosBloqueX / GLO.GLBLmetrosCeldilla)) # -> 2000
    nCeldillasRasterRefY = int(math.ceil(myLasHead.metrosBloqueY / GLO.GLBLmetrosCeldilla)) # -> 2000
    numTilesRows = int(math.ceil(nSubCeldasRasterRefY / GLBNtileSizeEnPixelsSubCelda)) # -> 8 ($4)
    numTilesCols = int(math.ceil(nSubCeldasRasterRefX / GLBNtileSizeEnPixelsSubCelda)) # -> 8 ($4)

    margenXsobresalienteMetros = GLO.GLBLtileSemiSolapeMetros + (((numTilesCols * GLBNtileKernelMetros) - GLO.GLBLmetrosBloque) / 2) # -> 24 ($6)
    margenYsobresalienteMetros = GLO.GLBLtileSemiSolapeMetros + (((numTilesRows * GLBNtileKernelMetros) - GLO.GLBLmetrosBloque) / 2) # -> 24 ($6)
    margenXsobresalientePixelsScA = int(math.floor(margenXsobresalienteMetros / GLO.GLBLmetrosSubCelda))
    margenXsobresalientePixelsScB = int(math.ceil(margenXsobresalienteMetros / GLO.GLBLmetrosSubCelda))
    margenYsobresalientePixelsScA = int(math.floor(margenYsobresalienteMetros / GLO.GLBLmetrosSubCelda))
    margenYsobresalientePixelsScB = int(math.ceil(margenYsobresalienteMetros / GLO.GLBLmetrosSubCelda))
    margenXsobresalientePixelsCdA = int(math.floor(margenXsobresalienteMetros / GLO.GLBLmetrosCeldilla))
    margenXsobresalientePixelsCdB = int(math.ceil(margenXsobresalienteMetros / GLO.GLBLmetrosCeldilla))
    margenYsobresalientePixelsCdA = int(math.floor(margenYsobresalienteMetros / GLO.GLBLmetrosCeldilla))
    margenYsobresalientePixelsCdB = int(math.ceil(margenYsobresalienteMetros / GLO.GLBLmetrosCeldilla))

    if GLO.GLBLverbose:
        print('\tclidcarto-> Se van a crear %i x %i tiles' % (numTilesRows, numTilesCols))
        print(
            '\t\tnSubCeldasRasterRefY: {}; nSubCeldasRasterRefX: {}'.format(
                nSubCeldasRasterRefY, nSubCeldasRasterRefX
            )
        )
        print('\t\tGLO.GLBLtileSizeMetros:', GLO.GLBLtileSizeMetros,
              'GLO.GLBLtileSemiSolapeMetros:', GLO.GLBLtileSemiSolapeMetros,
              'GLBNtileSemiSolapePixelsSubCelda:', GLBNtileSemiSolapePixelsSubCelda
        )
        print('\t\tGLBNtileKernelPixelsSubCelda:', GLBNtileKernelPixelsSubCelda,
              'GLBNtileKernelMetros:', GLBNtileKernelMetros,
          )
              
        print('\t\tGLBNtileSizeEnPixelsSubCelda 2m', GLBNtileSizeEnPixelsSubCelda,
              'GLBNtileSizeEnPixelsCeldilla 1m', GLBNtileSizeEnPixelsCeldilla
        )
        print(
            '\t\tmargenXsobresalienteMetros', margenXsobresalienteMetros, '=', margenXsobresalienteMetros, 'm;',
            'margenYsobresalienteMetros', margenYsobresalienteMetros, '=', margenYsobresalienteMetros, 'm;',
        )

    if margenXsobresalienteMetros < 0 or margenYsobresalienteMetros < 0:
        print(
            '\nclidcarto-> ATENCION: reducir GLBLtileSemiSolapeMetros ({:0.1f} m) para que los tiles cubran todo el bloque'.format(
                GLO.GLBLtileSemiSolapeMetros
            )
        )
        # sys.exit(0)
    elif GLO.GLBLtileSemiSolapeMetros % GLO.GLBLmetrosSubCelda != 0:
        print(
            '\nclidcarto-> ATENCION: cambiar GLBLtileSemiSolapeMetros ({:0.1f} m) para que el semi-solape sea un numero entero de subCeldas (subcelda: {} m)'.format(
                GLO.GLBLtileSemiSolapeMetros,
                GLO.GLBLmetrosSubCelda,
            )
        )
        # sys.exit(0)
    elif margenXsobresalienteMetros % GLO.GLBLmetrosSubCelda != 0 or margenYsobresalienteMetros  % GLO.GLBLmetrosSubCelda != 0:
        print(
            '\nclidcarto-> ATENCION: cambiar GLBLtileSemiSolapeMetros ({:0.1f} m) para que el margen exterior sea un numero entero de subCeldas (subcelda: {} m)'.format(
                GLO.GLBLtileSemiSolapeMetros,
                GLO.GLBLmetrosSubCelda,

            )
        )
        # sys.exit(0)
    # ==========================================================================

    # ==========================================================================
    # Nota: La version reDepurada se crea en crearTilesTargetReDepurados<>
    if GLO.GLBLcrearTilesConTodasLasClasesMiniSubCel:
        subDirExDataMiniSubCelLasClassOriginal = 'pngExDataMiniSubCelLasClassOriginal_noDepurada'
        trainPathExDataMiniSubCelLasClassOriginal = os.path.join(
            GLO.MAINrutaOutput,
            train_dir,
            subDirExDataMiniSubCelLasClassOriginal
        )
    # El exData para BinClass y para TriClass es en principio el mismo
    if GLO.GLBLdepurarTriClassDePuntosMiniSubCelNoCoherentesConCartoRef:
        subDirExDataMiniSubCelLasClass_2_345_6 = 'pngExDataMiniSubCelLasClass_2_345_6_siDepurada'
    else:
        subDirExDataMiniSubCelLasClass_2_345_6 = 'pngExDataMiniSubCelLasClass_2_345_6_noDepurada'
    trainPathExDataMiniSubCelLasClass_2_345_6 = os.path.join(
        GLO.MAINrutaOutput,
        train_dir,
        subDirExDataMiniSubCelLasClass_2_345_6
    )
    # ==========================================================================
    if GLO.GLBLdepurarTriClassDePuntosMiniSubCelNoCoherentesConCartoRef:
        subDirPngTargetLasClass_2_345_6 = 'pngTargetMiniSubCelLasClass_2_345_6_siDepurada/'
    else:
        subDirPngTargetLasClass_2_345_6 = 'pngTargetMiniSubCelLasClass_2_345_6_noDepurada/'
    if GLO.GLBLdepurarBinClassDePuntosMiniSubCelNoCoherentesConCartoRef:
        subDirPngTargetLasClass02Binary = 'pngTargetMiniSubCelLasClass02Binary_siDepurada/'
    else:
        subDirPngTargetLasClass02Binary = 'pngTargetMiniSubCelLasClass02Binary_noDepurada/'
    trainPathPngTargetOriClass = os.path.join(GLO.MAINrutaOutput, train_dir, 'pngTargetMiniSubCelLasClassAllClass_noDepurada/')
    trainPathPngTargetTriClass = os.path.join(GLO.MAINrutaOutput, train_dir, subDirPngTargetLasClass_2_345_6)
    trainPathPngTargetBinClass = os.path.join(GLO.MAINrutaOutput, train_dir, subDirPngTargetLasClass02Binary)
    # ==========================================================================

    trainPathPng1 = os.path.join(GLO.MAINrutaOutput, train_dir, 'pngInputVar_int_ndvi_ndwi/')
    trainPathPng2 = os.path.join(GLO.MAINrutaOutput, train_dir, 'pngInputVar_nirRedGreen_maxiSubCel/')
    trainPathPng3 = os.path.join(GLO.MAINrutaOutput, train_dir, 'pngInputVar_nirRedGreen_miniSubCel/')
    trainPathPng4 = os.path.join(GLO.MAINrutaOutput, train_dir, 'pngInputVar_planoNubePuntual_miniSubCel/')
    trainPathPng5 = os.path.join(GLO.MAINrutaOutput, train_dir, 'pngInputVar_cotasRelativas_miniSubCel/')
    trainPathPng6 = os.path.join(GLO.MAINrutaOutput, train_dir, 'pngInputVar_MdgEcmrPtes/')
    trainPathPng7 = os.path.join(GLO.MAINrutaOutput, train_dir, 'pngInputVar_miniSubCel_autovalores/')
    trainPathPng8 = os.path.join(GLO.MAINrutaOutput, train_dir, 'pngInputVar_Hmax_sMdf_sMdpmacro_sMdpMicro/')
    trainPathPng9 = os.path.join(GLO.MAINrutaOutput, train_dir, 'pngInputVar_RiC_Macro_Mesos_Micro_Megas/')
    trainPathPngInt1m = os.path.join(GLO.MAINrutaOutput, train_dir, 'png1mInputVar_int_ndvi_hTejado/')
    trainPathPngRiC1m = os.path.join(GLO.MAINrutaOutput, train_dir, 'png1mInputVar_RiC_macro_mesos_micro/')

    if LCLmantenerTilesGuardados:
        tilesEncontrados = True
        # Verifico si existen los 6 Png xq voy a generar los 6 (el modelo entrenado que uso para prediccion no tiene nada que ver con la generacion de tiles)
        SELEC_IMG = '012345'
        print('clidcarto-> Verificando si ya existen los tiles SELEC_IMG:', SELEC_IMG, 'GLO.GLBLformatoTilesAscInput:', GLO.GLBLformatoTilesAscInput)
        for nRow in range(numTilesRows):
            for nCol in range(numTilesCols):
                pngFileNameTargetOriClass = os.path.join(trainPathPngTargetOriClass, '%s_%s_%i_%i.png' % (fileCoordYear, 'Train', nRow, nCol))
                pngFileNameTargetTriClass = os.path.join(trainPathPngTargetTriClass, '%s_%s_%i_%i.png' % (fileCoordYear, 'Train', nRow, nCol))
                pngFileNameTargetBinClass = os.path.join(trainPathPngTargetBinClass, '%s_%s_%i_%i.png' % (fileCoordYear, 'Train', nRow, nCol))
                pngFileName1 = os.path.join(trainPathPng1, '%s_%s_%i_%i.png' % (fileCoordYear, 'Train', nRow, nCol))
                pngFileName2 = os.path.join(trainPathPng2, '%s_%s_%i_%i.png' % (fileCoordYear, 'Train', nRow, nCol))
                pngFileName3 = os.path.join(trainPathPng3, '%s_%s_%i_%i.png' % (fileCoordYear, 'Train', nRow, nCol))
                pngFileName4 = os.path.join(trainPathPng4, '%s_%s_%i_%i.png' % (fileCoordYear, 'Train', nRow, nCol))
                pngFileName5 = os.path.join(trainPathPng5, '%s_%s_%i_%i.png' % (fileCoordYear, 'Train', nRow, nCol))
                pngFileName6 = os.path.join(trainPathPng6, '%s_%s_%i_%i.png' % (fileCoordYear, 'Train', nRow, nCol))
                pngFileName7 = os.path.join(trainPathPng7, '%s_%s_%i_%i.png' % (fileCoordYear, 'Train', nRow, nCol))
                pngFileName8 = os.path.join(trainPathPng8, '%s_%s_%i_%i.png' % (fileCoordYear, 'Train', nRow, nCol))
                pngFileName9 = os.path.join(trainPathPng9, '%s_%s_%i_%i.png' % (fileCoordYear, 'Train', nRow, nCol))
                pngFileNameInt1m = os.path.join(trainPathPngInt1m, '%s_%s_%i_%i.png' % (fileCoordYear, 'Train', nRow, nCol))
                pngFileNameRiC1m = os.path.join(trainPathPngRiC1m, '%s_%s_%i_%i.png' % (fileCoordYear, 'Train', nRow, nCol))

                if (
                    (not os.path.exists(pngFileName1) and '0' in SELEC_IMG)
                    or (not os.path.exists(pngFileName2) and '1' in SELEC_IMG)
                    or (not os.path.exists(pngFileName3) and '2' in SELEC_IMG)
                    or (not os.path.exists(pngFileName4) and '3' in SELEC_IMG)
                    or (not os.path.exists(pngFileName5) and '4' in SELEC_IMG)
                    or (not os.path.exists(pngFileName6) and '5' in SELEC_IMG)
                ):
                    tilesEncontrados = False
                    print(
                        '\tNo encontrado alguno de los tiles inputs. Ficheros:',
                        '\n\t\t', pngFileName1, 'etc.',
                        '\n\t\t', pngFileName2, 'etc.',
                        '\n\t\t', pngFileName3, 'etc.',
                        '\n\t\t', pngFileName4, 'etc.',
                        '\n\t\t', pngFileName5, 'etc.',
                        '\n\t\t', pngFileName6, 'etc.',
                    )
                    break
                if tilesEncontrados and GLO.GLBLcrearTilesConTodasLasClasesMiniSubCel and not os.path.exists(pngFileNameTargetOriClass):
                    print('\tSe han encontrado los tiles input pero no los target pngFileNameTargetOriClass con todas las clases. Ficheros:',
                          '\n\t\t', pngFileNameTargetOriClass, 'etc.')
                    tilesEncontrados = False
                    break
                if tilesEncontrados and GLO.GLBLreorganizaLasClassParaGenerarTilesCuaTrinarios_X_6_2_345 and not os.path.exists(pngFileNameTargetTriClass):
                    print('\tSe han encontrado los tiles input pero no los target pngFileNameTargetTriClass con las clases agrupadas en 3/4. Ficheros:',
                          '\n\t\t', pngFileNameTargetTriClass, 'etc.')
                    tilesEncontrados = False
                    break
                if tilesEncontrados and GLO.GLBLreorganizaLasClassParaGenerarTilesBinariosMonoClase and not os.path.exists(pngFileNameTargetBinClass):
                    print('\tSe han encontrado los tiles input pero no los target pngFileNameTargetBinClass convertida a binario. Ficheros:',
                          '\n\t\t', pngFileNameTargetBinClass, 'etc.')
                    tilesEncontrados = False
                    break


                if GLO.GLBLformatoTilesAscInput:
                    if (
                        not os.path.exists((pngFileNameTargetOriClass.replace('/png', '/asc')).replace('\png', '/asc'))
                        or (not os.path.exists((pngFileName1.replace('/png', '/asc')).replace('\png', '/asc')) and '0' in SELEC_IMG)
                        or (not os.path.exists((pngFileName2.replace('/png', '/asc')).replace('\png', '/asc')) and '1' in SELEC_IMG)
                        or (not os.path.exists((pngFileName3.replace('/png', '/asc')).replace('\png', '/asc')) and '2' in SELEC_IMG)
                        or (not os.path.exists((pngFileName4.replace('/png', '/asc')).replace('\png', '/asc')) and '3' in SELEC_IMG)
                        or (not os.path.exists((pngFileName5.replace('/png', '/asc')).replace('\png', '/asc')) and '4' in SELEC_IMG)
                        or (not os.path.exists((pngFileName6.replace('/png', '/asc')).replace('\png', '/asc')) and '5' in SELEC_IMG)
                    ):
                        tilesEncontrados = False
                        break
                    if GLO.GLBLreorganizaLasClassParaGenerarTilesCuaTrinarios_X_6_2_345 and not os.path.exists((pngFileNameTargetTriClass.replace('/png', '/asc')).replace('\png', '/asc')):
                        tilesEncontrados = False
                        break
                    if GLO.GLBLreorganizaLasClassParaGenerarTilesBinariosMonoClase and not os.path.exists((pngFileNameTargetBinClass.replace('/png', '/asc')).replace('\png', '/asc')):
                        tilesEncontrados = False
                        break

                if not tilesEncontrados:
                    break
            if not tilesEncontrados:
                break
        if tilesEncontrados:
            print('\n{:_^80}'.format(''))
            print('clidcarto-> No es necesario crear tiles porque ya se han creado previamente.')
            print('{:=^80}'.format(''))
            return tilesEncontrados
        else:
            print('clidcarto-> Se crean los tiles porque no se han localizado todos.')
            if GLO.GLBLformatoTilesAscInput:
                print('\tEsto incluye a los ficheros Asc.')

    # ==========================================================================
    if GLO.GLBLformatoTilesNpz:
        trainPathNpzInput = os.path.join(GLO.MAINrutaOutput, train_dir, 'inputVariablesNpz/')
        trainPathNpzTarget = os.path.join(GLO.MAINrutaOutput, train_dir, 'inputVariablesNpz/')
        if not os.path.isdir(trainPathNpzInput):
            os.makedirs(trainPathNpzInput)
            print('cartolider-> Creando directorio train', trainPathNpzInput)
        if not os.path.isdir(trainPathNpzTarget):
            os.makedirs(trainPathNpzTarget)
            print('cartolider-> Creando directorio train', trainPathNpzTarget)
    else:
        trainPathNpzInput = ''
        trainPathNpzTarget = ''

    # Creacion de directorios para los tiles exData
    if GLO.GLBLcrearTilesConTodasLasClasesMiniSubCel and GLO.GLBLcrearTilesExDataMiniSubCelLasClass:
        if not os.path.isdir(trainPathExDataMiniSubCelLasClassOriginal):
            numIntentosEscritura = 0
            while True:
                numIntentosEscritura += 1
                try:
                    os.makedirs(trainPathExDataMiniSubCelLasClassOriginal)
                    break
                except:
                    time.sleep(5)
                    if numIntentosEscritura > 5:
                        break
            print(
                'cartolider.{:006}-> Creando directorio exData: {}'.format(
                    GLO.MAINidProceso, trainPathExDataMiniSubCelLasClassOriginal
                )
            )

    if GLO.GLBLreorganizaLasClassParaGenerarTilesCuaTrinarios_X_6_2_345 or GLO.GLBLreorganizaLasClassParaGenerarTilesBinariosMonoClase:
        # Los tiles reDepurados no se crean en esta funcion sino en 
        # Se crean cuando GLO.GLBLreDepurarMiniSubCelEnVueltaAjustesMdp
        if not os.path.isdir(trainPathExDataMiniSubCelLasClass_2_345_6):
            numIntentosEscritura = 0
            while True:
                numIntentosEscritura += 1
                try:
                    os.makedirs(trainPathExDataMiniSubCelLasClass_2_345_6)
                    break
                except:
                    time.sleep(5)
                    if numIntentosEscritura > 5:
                        break
            print(
                'cartolider.{:006}-> Creando directorio exData: {}'.format(
                    GLO.MAINidProceso, trainPathExDataMiniSubCelLasClass_2_345_6
                )
            )


    if GLO.GLBLformatoTilesPng:
        if GLO.GLBLcrearTilesTargetMiniSubCelLasClass:
            grabarTarget = True
        else:
            grabarTarget = False

        grabarCapa7, grabarCapa8, grabarCapa9 = False, False, False
        grabarCapaIm, grabarCapaRm = False, False
        # Valores por defecto para que de error el "Creando directorio train"
        trainPathPngTargetOriClass = os.path.join(GLO.MAINrutaOutput, train_dir)
        trainPathPngTargetTriClass = os.path.join(GLO.MAINrutaOutput, train_dir)
        trainPathPngTargetBinClass = os.path.join(GLO.MAINrutaOutput, train_dir)
        trainPathPng1 = os.path.join(GLO.MAINrutaOutput, train_dir)
        trainPathPng2 = os.path.join(GLO.MAINrutaOutput, train_dir)
        trainPathPng3 = os.path.join(GLO.MAINrutaOutput, train_dir)
        trainPathPng4 = os.path.join(GLO.MAINrutaOutput, train_dir)
        trainPathPng5 = os.path.join(GLO.MAINrutaOutput, train_dir)
        trainPathPng6 = os.path.join(GLO.MAINrutaOutput, train_dir)
        trainPathPng7 = os.path.join(GLO.MAINrutaOutput, train_dir)
        trainPathPng8 = os.path.join(GLO.MAINrutaOutput, train_dir)
        trainPathPng9 = os.path.join(GLO.MAINrutaOutput, train_dir)
        trainPathPngInt1m = os.path.join(GLO.MAINrutaOutput, train_dir)
        trainPathPngRiC1m = os.path.join(GLO.MAINrutaOutput, train_dir)
        trainPathAscTargetOriClass = os.path.join(GLO.MAINrutaOutput, train_dir)
        trainPathAscTargetTriClass = os.path.join(GLO.MAINrutaOutput, train_dir)
        trainPathAscTargetBinClass = os.path.join(GLO.MAINrutaOutput, train_dir)
        trainPathAsc1 = os.path.join(GLO.MAINrutaOutput, train_dir)
        trainPathAsc2 = os.path.join(GLO.MAINrutaOutput, train_dir)
        trainPathAsc3 = os.path.join(GLO.MAINrutaOutput, train_dir)
        trainPathAsc4 = os.path.join(GLO.MAINrutaOutput, train_dir)
        trainPathAsc5 = os.path.join(GLO.MAINrutaOutput, train_dir)
        trainPathAsc6 = os.path.join(GLO.MAINrutaOutput, train_dir)
        trainPathAscOtros = os.path.join(GLO.MAINrutaOutput, train_dir, 'ascInputOtros/')

        # ======================================================================
        if grupoTiles == 'preVuelta2':
        # ======================================================================
            # Lista de capas:
            # nombreCapas1 = ['intSRetMed', 'ndviMed', 'ndwiMed']        -> SubCelda
            # nombreCapas2 = ['NirPtoMax', 'RedPtoMax', 'GreenPtoMax']   -> SubCelda (ptoMax)
            # nombreCapas3 = ['NirPtoMin', 'RedPtoMin', 'GreenPtoMin']   -> pto MinSubCel
            # nombreCapas4 = ['mseByteMicroPlanoNubePuntual', 'pteXx50MicroPlanoNubePuntual', 'pteYx50MicroPlanoNubePuntual']   -> nube pto MinSubCel
            # nombreCapas5 = ['cotaAbsolutaDmMinSubCel', 'cotaRelDmMaxNubePuntual', 'cotaRelDmPlanoNubePuntual']                -> nube pto MinSubCel
            # nombreCapas6 = ['pteXglobal', 'pteYglobal', 'ecmrGlobal']   -> SubCelda
            # nombreCapas7 = ['anisotropy', 'planarity', 'sphericity']    -> matriz subCelda (no la uso)
            # ======================================================================
            # Esto requiere: GLO.GLBLcalcularSubCeldas and GLO.GLBLgrabarIndicesVegetacionNDVIetAlSubCelda
            grabarCapa1 = True
            grabarCapa2 = True
            grabarCapa3 = True
            grabarCapa4 = True
            grabarCapa5 = True
            grabarCapa6 = True
            grabarCapa7 = False

            # Creacion de las png target con la clase del punto miniSubCel
            trainPathPngTargetOriClass = os.path.join(GLO.MAINrutaOutput, train_dir, 'pngTargetMiniSubCelLasClassAllClass_noDepurada/')
            trainPathPngTargetTriClass = os.path.join(GLO.MAINrutaOutput, train_dir, subDirPngTargetLasClass_2_345_6)
            trainPathPngTargetBinClass = os.path.join(GLO.MAINrutaOutput, train_dir, subDirPngTargetLasClass02Binary)

            if GLO.GLBLformatoTilesAscInput:
                trainPathAscTargetOriClass = (trainPathPngTargetOriClass.replace('/png', '/asc')).replace('\png', '/asc')
                trainPathAscTargetTriClass = (trainPathPngTargetTriClass.replace('/png', '/asc')).replace('\png', '/asc')
                trainPathAscTargetBinClass = (trainPathPngTargetBinClass.replace('/png', '/asc')).replace('\png', '/asc')
            nombreCapaTargetOriClass = 'lasClassOriginal'
            nombreCapaTargetTriClass = 'LasClass_2_345_6'
            nombreCapaTargetBinClass = 'LasClass02Binary'

            # Tiles con la clase miniSubCel sin reagrupar ni reordenar (se crea en todo caso, aunque no la uso)
            if GLO.GLBLcrearTilesConTodasLasClasesMiniSubCel or GLO.GLBLcrearTilesTargetMiniSubCelSoloSiHayNoSueloSuficientes:
                if GLO.GLBLusarMiniSubCelPselEnVezDeTlp:
                    if GLO.GLBLusarFormatoDtypeMaxiMiniSubCel:
                        arrayCapaTargetOriClas = np.zeros(
                            (
                                myLasData.aSubCeldasPuntoMiniSubCelPsuePsel.shape[0],
                                myLasData.aSubCeldasPuntoMiniSubCelPsuePsel.shape[1],
                            ), dtype=np.uint8
                        )
                        histogramaLasClass = np.zeros(20, dtype=np.int32)
                        for nX in range(myLasData.aSubCeldasPuntoMiniSubCelPsuePsel.shape[0]):
                            for nY in range(myLasData.aSubCeldasPuntoMiniSubCelPsuePsel.shape[1]):
                                lasClassValue = myLasData.aSubCeldasPuntoMiniSubCelPsuePsel[nX, nY]['lasClassOriginal']
                                arrayCapaTargetOriClas[nX, nY] = lasClassValue
                                histogramaLasClass[lasClassValue] += 1
                        if GLO.GLBLverbose:
                            print('clidcarto-> Controlando TargetClass-> histograma lasClassOriginal[:]:  {}'.format(histogramaLasClass))
                    else:
                        arrayCapaTargetOriClas = myLasData.aSubCeldasPuntoMiniSubCelPsel[:, :, 8:9]
                else:
                    arrayCapaTargetOriClas = np.zeros(
                        (
                            myLasData.aSubCeldasPuntoMiniSubCel_Tlp.shape[0],
                            myLasData.aSubCeldasPuntoMiniSubCel_Tlp.shape[1],
                        ), dtype=np.uint8
                    )
                    for nX in range(myLasData.aSubCeldasPuntoMiniSubCel_Tlp.shape[0]):
                        for nY in range(myLasData.aSubCeldasPuntoMiniSubCel_Tlp.shape[1]):
                            arrayCapaTargetOriClas[nX, nY] = myLasData.aSubCeldasPuntoMiniSubCel_Tlp[nX, nY]['lasClassOriginal']

            # targetTiles con la clase miniSubCel reagrupada en cuatro clases: 0: Resto; 1: Edificios; 2: Suelo; 3: Vegetacion
            if GLO.GLBLreorganizaLasClassParaGenerarTilesCuaTrinarios_X_6_2_345:
                if GLO.GLBLusarMiniSubCelPselEnVezDeTlp:
                    if GLO.GLBLusarFormatoDtypeMaxiMiniSubCel:
                        arrayCapaTargetTriClas = np.zeros(
                            (
                                myLasData.aSubCeldasPuntoMiniSubCelPsuePsel.shape[0],
                                myLasData.aSubCeldasPuntoMiniSubCelPsuePsel.shape[1],
                            ), dtype=np.uint8
                        )
                        histogramaLasClass = np.zeros(20, dtype=np.int32)
                        for nX in range(myLasData.aSubCeldasPuntoMiniSubCelPsuePsel.shape[0]):
                            if GLO.GLBLverbose and nX % 200 == 0:
                                print(
                                    'clidcarto-> miniSubCelLasClass para nX: {:03} -> {}'.format(
                                        nX,
                                        myLasData.aSubCeldasPuntoMiniSubCelPsuePsel[nX, :20]['lasClass_2_345_6']
                                    )
                                )
                            for nY in range(myLasData.aSubCeldasPuntoMiniSubCelPsuePsel.shape[1]):
                                lasClassValue = myLasData.aSubCeldasPuntoMiniSubCelPsuePsel[nX, nY]['lasClass_2_345_6']
                                arrayCapaTargetTriClas[nX, nY] = lasClassValue
                                histogramaLasClass[lasClassValue] += 1
                        if GLO.GLBLverbose or True:
                            print('clidcarto-> Controlando TargetClass-> histograma lasClass_2_345_6[:4]: {}'.format(histogramaLasClass[:4]))
                    else:
                        arrayCapaTargetTriClas = myLasData.aSubCeldasPuntoMiniSubCelPsel[:, :, 9:10]
                else:
                    arrayCapaTargetTriClas = np.zeros(
                        (
                            myLasData.aSubCeldasPuntoMiniSubCel_Tlp.shape[0],
                            myLasData.aSubCeldasPuntoMiniSubCel_Tlp.shape[1],
                        ), dtype=np.uint8
                    )
                    for nX in range(myLasData.aSubCeldasPuntoMiniSubCel_Tlp.shape[0]):
                        for nY in range(myLasData.aSubCeldasPuntoMiniSubCel_Tlp.shape[1]):
                            arrayCapaTargetTriClas[nX, nY] = myLasData.aSubCeldasPuntoMiniSubCel_Tlp[nX, nY]['lasClass_2_345_6']

            # targetTiles con la clase miniSubCel reagrupada en dos clases: 0: Resto; 1: la clase seleccionada (GLBLreorganizaLasClassParaGenerarTilesBinariosMonoClase)
            if GLO.GLBLreorganizaLasClassParaGenerarTilesBinariosMonoClase:
                arrayCapaTargetBinClas = arrayCapaTargetTriClas.copy()
                if GLO.GLBLreorganizaLasClassParaGenerarTilesBinariosMonoClase == 6: # La clase 6 (edificio) cambia en TriClass a 1
                    arrayCapaTargetBinClas[arrayCapaTargetBinClas == 1] = 1
                    arrayCapaTargetBinClas[arrayCapaTargetBinClas != 1] = 0
                elif GLO.GLBLreorganizaLasClassParaGenerarTilesBinariosMonoClase == 2: # La clase 2 (edificio) se mantiene en TriClass
                    arrayCapaTargetBinClas[arrayCapaTargetBinClas == 2] = 1
                    arrayCapaTargetBinClas[arrayCapaTargetBinClas != 2] = 0
                elif GLO.GLBLreorganizaLasClassParaGenerarTilesBinariosMonoClase == 3: # Incluye 3, 4 y 5, que en triClass se agrupan en la 3
                    arrayCapaTargetBinClas[arrayCapaTargetBinClas == 3] = 1
                    arrayCapaTargetBinClas[arrayCapaTargetBinClas != 3] = 0


            # Estas variables son de la subCelda
            # preVuelta2
            trainSubDir1 = 'pngInputVar_int_ndvi_ndwi'
            trainPathPng1 = os.path.join(GLO.MAINrutaOutput, train_dir, 'pngInputVar_int_ndvi_ndwi/')
            if GLO.GLBLformatoTilesAscInput:
                trainPathAsc1 = (trainPathPng1.replace('/png', '/asc')).replace('\png', '/asc')
            nombreCapas1 = ['intSRetMed', 'ndviMed', 'ndwiMed']
            arrayCapas1 = np.concatenate(
                (
                    myLasData.aSubCeldasIntSRetMed[..., np.newaxis].astype(np.float64),
                    myLasData.aSubCeldasNDVIMed[..., np.newaxis].astype(np.float64),
                    myLasData.aSubCeldasNDWIMed[..., np.newaxis].astype(np.float64),
                ),
                axis=2,
            )
            print('clidcarto->', trainSubDir1, 'arrayCapas1.dtype:', arrayCapas1.dtype, arrayCapas1.min(), arrayCapas1.max())
            # print(myLasData.aSubCeldasNDVIMed[10:12, 10:12])
            # print('clidcarto-> mostrando ndvi en origen:')
            # print('clidcarto-> mostrando ndvi en destino:')
            # print(arrayCapas1[10:12, 10:12, 1])

            # Estas variables son del maxiSubCel
            # preVuelta2
            trainSubDir2 = 'pngInputVar_nirRedGreen_maxiSubCel'
            trainPathPng2 = os.path.join(GLO.MAINrutaOutput, train_dir, 'pngInputVar_nirRedGreen_maxiSubCel/')
            if GLO.GLBLformatoTilesAscInput:
                trainPathAsc2 = (trainPathPng2.replace('/png', '/asc')).replace('\png', '/asc')
            nombreCapas2 = ['NirPtoMax', 'RedPtoMax', 'GreenPtoMax']
            if GLO.GLBLusarMiniSubCelPselEnVezDeTlp:
                if GLO.GLBLusarFormatoDtypeMaxiMiniSubCel:
                    # arrayCapas2 = np.concatenate((myLasData.aSubCeldasPuntoMaxiSubCelPsuePsel[:, :]['nir'],
                    #                              myLasData.aSubCeldasPuntoMaxiSubCelPsuePsel[:, :]['red'],
                    #                              myLasData.aSubCeldasPuntoMaxiSubCelPsuePsel[:, :]['green']),
                    #                              axis=2)
                    arrayCapas2 = np.zeros(
                        (myLasData.aSubCeldasPuntoMaxiSubCelPsuePsel.shape[0], myLasData.aSubCeldasPuntoMaxiSubCelPsuePsel.shape[1], 3), dtype=np.uint16
                    )
                    for nX in range(myLasData.aSubCeldasPuntoMaxiSubCelPsuePsel.shape[0]):
                        for nY in range(myLasData.aSubCeldasPuntoMaxiSubCelPsuePsel.shape[1]):
                            arrayCapas2[nX, nY][0] = myLasData.aSubCeldasPuntoMaxiSubCelPsuePsel[nX, nY]['nir']
                            arrayCapas2[nX, nY][1] = myLasData.aSubCeldasPuntoMaxiSubCelPsuePsel[nX, nY]['red']
                            arrayCapas2[nX, nY][2] = myLasData.aSubCeldasPuntoMaxiSubCelPsuePsel[nX, nY]['green']
                else:
                    arrayCapas2 = np.concatenate(
                        (
                            myLasData.aSubCeldasPuntoMaxiSubCelPsel[:, :, 7:8],
                            myLasData.aSubCeldasPuntoMaxiSubCelPsel[:, :, 4:5],
                            myLasData.aSubCeldasPuntoMaxiSubCelPsel[:, :, 5:6],
                        ),
                        axis=2,
                    )
            else:
                arrayCapas2 = np.zeros((myLasData.aSubCeldasPuntoMaxiSubCel_Tlp.shape[0], myLasData.aSubCeldasPuntoMaxiSubCel_Tlp.shape[1], 3), dtype=np.uint16)
                for nX in range(myLasData.aSubCeldasPuntoMaxiSubCel_Tlp.shape[0]):
                    for nY in range(myLasData.aSubCeldasPuntoMaxiSubCel_Tlp.shape[1]):
                        arrayCapas2[nX, nY][0] = myLasData.aSubCeldasPuntoMaxiSubCel_Tlp[nX, nY]['nir']
                        arrayCapas2[nX, nY][1] = myLasData.aSubCeldasPuntoMaxiSubCel_Tlp[nX, nY]['red']
                        arrayCapas2[nX, nY][2] = myLasData.aSubCeldasPuntoMaxiSubCel_Tlp[nX, nY]['green']
            print('clidcarto->', trainSubDir2, 'arrayCapas2.dtype:', arrayCapas2.dtype, arrayCapas2.min(), arrayCapas2.max())

            # Las siguientes variables son del miniSubCel
            # preVuelta2
            trainSubDir3 ='pngInputVar_nirRedGreen_miniSubCel'
            trainPathPng3 = os.path.join(GLO.MAINrutaOutput, train_dir, 'pngInputVar_nirRedGreen_miniSubCel/')
            if GLO.GLBLformatoTilesAscInput:
                trainPathAsc3 = (trainPathPng3.replace('/png', '/asc')).replace('\png', '/asc')
            nombreCapas3 = ['NirPtoMin', 'RedPtoMin', 'GreenPtoMin']
            if GLO.GLBLusarFormatoDtypeMaxiMiniSubCel:
                if GLO.GLBLusarMiniSubCelPselEnVezDeTlp:
                    aSubCeldasPuntoMiniSubCel_ = myLasData.aSubCeldasPuntoMiniSubCelPsuePsel
                else:
                    aSubCeldasPuntoMiniSubCel_ = myLasData.aSubCeldasPuntoMiniSubCel_Tlp
                arrayCapas3 = np.zeros(
                    (
                        aSubCeldasPuntoMiniSubCel_.shape[0],
                        aSubCeldasPuntoMiniSubCel_.shape[1],
                        3
                    ), dtype=np.uint16
                )
                for nX in range(aSubCeldasPuntoMiniSubCel_.shape[0]):
                    for nY in range(aSubCeldasPuntoMiniSubCel_.shape[1]):
                        arrayCapas3[nX, nY][0] = aSubCeldasPuntoMiniSubCel_[nX, nY]['nir']
                        arrayCapas3[nX, nY][1] = aSubCeldasPuntoMiniSubCel_[nX, nY]['red']
                        arrayCapas3[nX, nY][2] = aSubCeldasPuntoMiniSubCel_[nX, nY]['green']
            else:
                arrayCapas3 = np.concatenate(
                    (
                        myLasData.aSubCeldasPuntoMiniSubCelPsel[:, :, 7:8],
                        myLasData.aSubCeldasPuntoMiniSubCelPsel[:, :, 4:5],
                        myLasData.aSubCeldasPuntoMiniSubCelPsel[:, :, 5:6],
                    ),
                    axis=2,
                )
            print('clidcarto->', trainSubDir3, 'arrayCapas3.dtype:', arrayCapas3.dtype, arrayCapas3.min(), arrayCapas3.max())

            # preVuelta2
            trainSubDir4 = 'pngInputVar_planoNubePuntual_miniSubCel'
            trainPathPng4 = os.path.join(GLO.MAINrutaOutput, train_dir, 'pngInputVar_planoNubePuntual_miniSubCel/')
            if GLO.GLBLformatoTilesAscInput:
                trainPathAsc4 = (trainPathPng4.replace('/png', '/asc')).replace('\png', '/asc')
            nombreCapas4 = ['mseByteMicroPlanoNubePuntual', 'pteXx50MicroPlanoNubePuntual', 'pteYx50MicroPlanoNubePuntual']
            # Elijo dtype=np.int16 para que admita los valores de pte~X10 (-127 a 127) y de mseX50 (0 a 255)
            # No hay problema de eficiencia porque al normalizar lo paso todo a 0-255 (uint8).
            if GLO.GLBLusarFormatoDtypeMaxiMiniSubCel:
                if GLO.GLBLusarMiniSubCelPselEnVezDeTlp:
                    aSubCeldasPuntoMiniSubCel_ = myLasData.aSubCeldasPuntoMiniSubCelPsuePsel
                else:
                    aSubCeldasPuntoMiniSubCel_ = myLasData.aSubCeldasPuntoMiniSubCel_Tlp
                arrayCapas4 = np.zeros(
                    (
                        aSubCeldasPuntoMiniSubCel_.shape[0],
                        aSubCeldasPuntoMiniSubCel_.shape[1],
                        3
                    ), dtype=np.int16
                )
                for nX in range(aSubCeldasPuntoMiniSubCel_.shape[0]):
                    for nY in range(aSubCeldasPuntoMiniSubCel_.shape[1]):
                        arrayCapas4[nX, nY][0] = aSubCeldasPuntoMiniSubCel_[nX, nY]['mseByteMicroPlanoNubePuntual']
                        arrayCapas4[nX, nY][1] = aSubCeldasPuntoMiniSubCel_[nX, nY]['pteXx50MicroPlanoNubePuntual']
                        arrayCapas4[nX, nY][2] = aSubCeldasPuntoMiniSubCel_[nX, nY]['pteYx50MicroPlanoNubePuntual']
                        # ATENCION: Si quiero ver el numero de puntos de cada enjambre, cambiar la anterior linea por esta siguiente:
                        # En San Rafael el numero de puntos suele estar entre 4 y 7
                        # Hay pocas subceldas con menos de 3. Se nota algo el borde de celdas, que explora un circulo cortado.
                        #arrayCapas4[nX, nY][2] = aSubCeldasPuntoMiniSubCel_[nX, nY]['nPuntosEnjambre']
            else:
                # A extinguir
                arrayCapas4 = np.concatenate(
                    (
                        myLasData.aSubCeldasPuntoMiniSubCelPsel[:, :, 16:17],
                        myLasData.aSubCeldasPuntoMiniSubCelPsel[:, :, 17:18],
                        myLasData.aSubCeldasPuntoMiniSubCelPsel[:, :, 18:19],
                    ),
                    axis=2,
                )
            print('clidcarto->', trainSubDir4, 'arrayCapas4.dtype:', arrayCapas4.dtype, arrayCapas4.min(), arrayCapas1.max())

            # # ==================================================================
            # #Obtencion de cotaMinBloque
            # if GLO.GLBLusarMiniSubCelPselEnVezDeTlp:
            #     if GLO.GLBLusarFormatoDtypeMaxiMiniSubCel:
            #         arrayCotasMin = myLasData.aSubCeldasPuntoMiniSubCelPsuePsel[:, :]['z']
            #         arrayCotasMin = arrayCotasMin[arrayCotasMin != GLO.GLBLnoData]
            #         arrayCotasMin = arrayCotasMin[arrayCotasMin != 0]
            #         if arrayCotasMin.shape[0]:
            #             cotaMinLas = np.min(arrayCotasMin)
            #         else:
            #             print('clidcarto-> Atencion: Revisar cotaMinLas')
            #             cotaMinLas = 0
            #     else:
            #         arrayCotasMin = myLasData.aSubCeldasPuntoMiniSubCelPsel[:, :, 2:3]
            #         arrayCotasMin = arrayCotasMin[arrayCotasMin != GLO.GLBLnoData]
            #         arrayCotasMin = arrayCotasMin[arrayCotasMin != 0]
            #         if arrayCotasMin.shape[0]:
            #             cotaMinLas = np.min(arrayCotasMin)
            #         else:
            #             print('clidcarto-> Atencion: Revisar cotaMinLas')
            #             cotaMinLas = 0
            # else:
            #     arrayCotasMin = myLasData.aSubCeldasPuntoMiniSubCel_Tlp[:, :]['z']
            #     arrayCotasMin = arrayCotasMin[arrayCotasMin != GLO.GLBLnoData]
            #     arrayCotasMin = arrayCotasMin[arrayCotasMin != 0]
            #     if arrayCotasMin.shape[0]:
            #         cotaMinLas = np.min(arrayCotasMin)
            #     else:
            #         print('clidcarto-> Atencion: Revisar cotaMinLas')
            #         cotaMinLas = 0
            # cotaMinBloque = (cotaMinLas * myLasHead.headDict['zscale']) + myLasHead.headDict['zoffset']
            # print('clidcarto-> cotaMinBloque:', cotaMinBloque)
            # # ==================================================================

            # ==================================================================
            # preVuelta2
            trainSubDir5 = 'pngInputVar_cotasRelativas_miniSubCel'
            trainPathPng5 = os.path.join(GLO.MAINrutaOutput, train_dir, 'pngInputVar_cotasRelativas_miniSubCel/')
            if GLO.GLBLformatoTilesAscInput:
                trainPathAsc5 = (trainPathPng5.replace('/png', '/asc')).replace('\png', '/asc')
            nombreCapas5 = ['cotaAbsolutaDmMinSubCel', 'cotaRelDmMaxNubePuntual', 'cotaRelDmPlanoNubePuntual']
            # Elijo dtype=np.int16 (-327678 a +32767) porque asi admite el uint8 de cotaRelDmMaxNubePuntual
            # y el int8 cotaRelDmPlanoNubePuntual (cabe la posibilidad de que el planoNubePuntual este por debajo del pto).
            # Ademas admite valores de cotaAbsolutaDmMinSubCel muy amplios.
            # Esto es raro si es miniSubCel, pero lo calculo para todos los puntos (se guarda tb en aSubCeldasPuntoMaxiSubCel*** y extrVars)
            if GLO.GLBLusarFormatoDtypeMaxiMiniSubCel:
                if GLO.GLBLusarMiniSubCelPselEnVezDeTlp:
                    aSubCeldasPuntoMiniSubCel_ = myLasData.aSubCeldasPuntoMiniSubCelPsuePsel
                else:
                    aSubCeldasPuntoMiniSubCel_ = myLasData.aSubCeldasPuntoMiniSubCel_Tlp
                arrayCapas5 = np.zeros(
                    (
                        aSubCeldasPuntoMiniSubCel_.shape[0],
                        aSubCeldasPuntoMiniSubCel_.shape[1],
                        3
                    ), dtype=np.int16
                )
                for nX in range(aSubCeldasPuntoMiniSubCel_.shape[0]):
                    for nY in range(aSubCeldasPuntoMiniSubCel_.shape[1]):
                        # miTileZlas = aSubCeldasPuntoMiniSubCel_[nX, nY]['z']
                        # if miTileZlas != 0:
                        #     miTileZ = (miTileZlas * myLasHead.headDict['zscale']) + myLasHead.headDict['zoffset']
                        #     arrayCapas5[nX, nY][0] = 10 * (miTileZ - cotaMinBloque)
                        # else:
                        #     arrayCapas5[nX, nY][0] = 0
                        arrayCapas5[nX, nY][0] = 10 * (
                            (
                                aSubCeldasPuntoMiniSubCel_[nX, nY]['z']
                                * myLasHead.headDict['zscale']
                            ) + myLasHead.headDict['zoffset']
                        )
                        arrayCapas5[nX, nY][1] = aSubCeldasPuntoMiniSubCel_[nX, nY]['cotaRelDmMaxNubePuntual']
                        arrayCapas5[nX, nY][2] = aSubCeldasPuntoMiniSubCel_[nX, nY]['cotaRelDmPlanoNubePuntual']
            else:
                # A extinguir
                arrayCapas5 = np.concatenate(
                    (
                        np.int16(10 * (myLasData.aSubCeldasPuntoMiniSubCelPsel[:, :, 2:3])),
                        np.int16(myLasData.aSubCeldasPuntoMiniSubCelPsel[:, :, 21:22]),
                        np.int16(myLasData.aSubCeldasPuntoMiniSubCelPsel[:, :, 22:23]),
                    ),
                    axis=2,
                )
            print('clidcarto->', trainSubDir5, 'arrayCapas5.dtype:', arrayCapas5.dtype, arrayCapas5.min(), arrayCapas5.max())

            # preVuelta2
            trainSubDir6 = 'pngInputVar_MdgEcmrPtes'
            trainPathPng6 = os.path.join(GLO.MAINrutaOutput, train_dir, 'pngInputVar_MdgEcmrPtes/')
            if GLO.GLBLformatoTilesAscInput:
                trainPathAsc6 = (trainPathPng6.replace('/png', '/asc')).replace('\png', '/asc')
            nombreCapas6 = ['pteXglobal', 'pteYglobal', 'ecmrGlobal']
            arrayCapas6 = np.concatenate(
                (
                    myLasData.aSubCeldasMdgAjuste[:, :, 1:2],
                    myLasData.aSubCeldasMdgAjuste[:, :, 2:3],
                    myLasData.aSubCeldasMdgAjuste[:, :, 3:4],
                ),
                axis=2,
            )
            print('clidcarto->', trainSubDir6, 'arrayCapas6.dtype:', arrayCapas6.dtype, arrayCapas6.min(), arrayCapas6.max())

            # ======================================================================
            if GLO.GLBLcalcularAutovaloresDeCadaPunto:
                # Esta no la uso porque no me salen valores validos
                # preVuelta2
                trainPathPng7 = os.path.join(GLO.MAINrutaOutput, train_dir, 'pngInputVar_miniSubCel_autovalores/')
                if GLO.GLBLformatoTilesAscInput:
                    trainPathAsc7 = (trainPathPng7.replace('/png', '/asc')).replace('\png', '/asc')
                nombreCapas7 = ['anisotropy', 'planarity', 'sphericity']
                if GLO.GLBLusarMiniSubCelPselEnVezDeTlp:
                    if GLO.GLBLusarFormatoDtypeMaxiMiniSubCel:
                        arrayCapas7 = np.zeros(
                            (
                                myLasData.aSubCeldasPuntoMiniSubCelPsuePsel.shape[0],
                                myLasData.aSubCeldasPuntoMiniSubCelPsuePsel.shape[1],
                                3
                            ), dtype=np.int16
                        )
                        for nX in range(myLasData.aSubCeldasPuntoMiniSubCelPsuePsel.shape[0]):
                            for nY in range(myLasData.aSubCeldasPuntoMiniSubCelPsuePsel.shape[1]):
                                arrayCapas7[nX, nY][0] = myLasData.aSubCeldasPuntoMiniSubCelPsuePsel[nX, nY]['anisotropy']
                                arrayCapas7[nX, nY][1] = myLasData.aSubCeldasPuntoMiniSubCelPsuePsel[nX, nY]['planarity']
                                arrayCapas7[nX, nY][2] = myLasData.aSubCeldasPuntoMiniSubCelPsuePsel[nX, nY]['sphericity']
                    else:
                        arrayCapas7 = np.concatenate(
                            (
                                myLasData.aSubCeldasPuntoMiniSubCelPsel[:, :, 23:24],
                                myLasData.aSubCeldasPuntoMiniSubCelPsel[:, :, 24:25],
                                myLasData.aSubCeldasPuntoMiniSubCelPsel[:, :, 25:26],
                            ),
                            axis=2,
                        )
                else:
                    arrayCapas7 = np.zeros(
                        (
                            myLasData.aSubCeldasPuntoMiniSubCel_Tlp.shape[0],
                            myLasData.aSubCeldasPuntoMiniSubCel_Tlp.shape[1],
                            3
                        ), dtype=np.uint16
                    )
                    for nX in range(myLasData.aSubCeldasPuntoMiniSubCel_Tlp.shape[0]):
                        for nY in range(myLasData.aSubCeldasPuntoMiniSubCel_Tlp.shape[1]):
                            arrayCapas7[nX, nY][0] = myLasData.aSubCeldasPuntoMiniSubCel_Tlp[nX, nY]['anisotropy']
                            arrayCapas7[nX, nY][1] = myLasData.aSubCeldasPuntoMiniSubCel_Tlp[nX, nY]['planarity']
                            arrayCapas7[nX, nY][2] = myLasData.aSubCeldasPuntoMiniSubCel_Tlp[nX, nY]['sphericity']
        # ======================================================================


        # ======================================================================
        elif grupoTiles == 'postVuelta2':
        # ======================================================================
            grabarCapa1, grabarCapa2 = False, False
            grabarCapa3, grabarCapa4 = False, False
            grabarCapa5, grabarCapa6 = False, False
            if GLO.GLBLgrabarIndicesVegetacionNDVIetAlSubCelda:
                grabarCapa1 = True
            if GLO.GLBLcalcularSubCeldas:
                grabarCapa2 = True
            if GLO.GLBLcalcularMdg and GLO.GLBLcalcularSubCeldas:
                grabarCapa6 = True
            if GLO.GLBLcalcularMdp and GLO.GLBLcalcularSubCeldas:
                if GLO.GLBLcrearTilesLateralidadInterSubCeldasMinMin:
                    grabarCapa4 = True
                if GLO.GLBLcrearTilesRugosidadInterSubCeldas:
                    grabarCapa5 = True
            if GLO.GLBLgrabarHiperFormas and GLO.GLBLcrearTilesPlanosTejadoSubCeldas:
                grabarCapa3 = True
            # Capas opcionales, que por el momento no genero
            if GLO.GLBLcalcularMdp and GLO.GLBLcalcularSubCeldas:
                if GLO.GLBLgrabarMdfMinMax:
                    grabarCapa7 = True
                if GLO.GLBLgrabarHmaxSobreMdfSobreMdpmacroSobreMdpMicro:
                    grabarCapa8 = True
            if GLO.GLBLgrabarHiperFormas and GLO.GLBLguardarCapaRugosidadInterCeldillasSubCeldas:
                if GLO.GLBLgrabarRiCMacroMesosMicroMegas:
                    # ->Estas 4 capas que se calculan en clidnv4.py por ahora no las uso,
                    #  porque ya tengo las que se calculan en clidnv2y.py, que tienen en cuenta la lateralidad
                    grabarCapa9 = True
            if GLO.GLBLgrabarIndicesVegetacionNDVIetAlMetricos and GLO.GLBLguardarPlanosTejadoMetrico:
                grabarCapaIm = True
            if GLO.GLBLguardarCapaRugosidadInterCeldillasMetrico:
                grabarCapaRm = True

            if grabarCapa1:
                # postVuelta2
                trainPathPng1 = os.path.join(GLO.MAINrutaOutput, train_dir, 'pngInputVar_int_ndvi_ndwi/')
                if GLO.GLBLformatoTilesAscInput:
                    trainPathAsc1 = (trainPathPng1.replace('/png', '/asc')).replace('\png', '/asc')
                nombreCapas1 = ['intSRetMed', 'ndviMed', 'ndwiMed']
                arrayCapas1 = np.concatenate(
                    (
                        myLasData.aSubCeldasIntSRetMed[..., np.newaxis].astype(np.float64),
                        myLasData.aSubCeldasNDVIMed[..., np.newaxis].astype(np.float64),
                        myLasData.aSubCeldasNDWIMed[..., np.newaxis].astype(np.float64),
                    ),
                    axis=2,
                )
    
            if grabarCapa2:
                # postVuelta2
                trainPathPng2 = os.path.join(GLO.MAINrutaOutput, train_dir, 'pngInputVar_nirRedGreen_maxiSubCel/')
                if GLO.GLBLformatoTilesAscInput:
                    trainPathAsc2 = (trainPathPng2.replace('/png', '/asc')).replace('\png', '/asc')
                nombreCapas2 = ['NirPtoMax', 'RedPtoMax', 'GreenPtoMax']
                if GLO.GLBLusarMiniSubCelPselEnVezDeTlp:
                    if GLO.GLBLusarFormatoDtypeMaxiMiniSubCel:
                        # arrayCapas2 = np.concatenate((myLasData.aSubCeldasPuntoMaxiSubCelPsuePsel[:, :]['nir'],
                        #                              myLasData.aSubCeldasPuntoMaxiSubCelPsuePsel[:, :]['red'],
                        #                              myLasData.aSubCeldasPuntoMaxiSubCelPsuePsel[:, :]['green']),
                        #                              axis=2)
                        arrayCapas2 = np.zeros(
                            (myLasData.aSubCeldasPuntoMaxiSubCelPsuePsel.shape[0], myLasData.aSubCeldasPuntoMaxiSubCelPsuePsel.shape[1], 3), dtype=np.uint16
                        )
                        for nX in range(myLasData.aSubCeldasPuntoMaxiSubCelPsuePsel.shape[0]):
                            for nY in range(myLasData.aSubCeldasPuntoMaxiSubCelPsuePsel.shape[1]):
                                arrayCapas2[nX, nY][0] = myLasData.aSubCeldasPuntoMaxiSubCelPsuePsel[nX, nY]['nir']
                                arrayCapas2[nX, nY][1] = myLasData.aSubCeldasPuntoMaxiSubCelPsuePsel[nX, nY]['red']
                                arrayCapas2[nX, nY][2] = myLasData.aSubCeldasPuntoMaxiSubCelPsuePsel[nX, nY]['green']
                    else:
                        arrayCapas2 = np.concatenate(
                            (
                                myLasData.aSubCeldasPuntoMaxiSubCelPsel[:, :, 7:8],
                                myLasData.aSubCeldasPuntoMaxiSubCelPsel[:, :, 4:5],
                                myLasData.aSubCeldasPuntoMaxiSubCelPsel[:, :, 5:6],
                            ),
                            axis=2,
                        )
                else:
                    arrayCapas2 = np.zeros((myLasData.aSubCeldasPuntoMaxiSubCel_Tlp.shape[0], myLasData.aSubCeldasPuntoMaxiSubCel_Tlp.shape[1], 3), dtype=np.uint16)
                    for nX in range(myLasData.aSubCeldasPuntoMaxiSubCel_Tlp.shape[0]):
                        for nY in range(myLasData.aSubCeldasPuntoMaxiSubCel_Tlp.shape[1]):
                            arrayCapas2[nX, nY][0] = myLasData.aSubCeldasPuntoMaxiSubCel_Tlp[nX, nY]['nir']
                            arrayCapas2[nX, nY][1] = myLasData.aSubCeldasPuntoMaxiSubCel_Tlp[nX, nY]['red']
                            arrayCapas2[nX, nY][2] = myLasData.aSubCeldasPuntoMaxiSubCel_Tlp[nX, nY]['green']

            if grabarCapa3:
                # postVuelta2
                trainPathPng3 = os.path.join(GLO.MAINrutaOutput, train_dir, 'pngInputVar_hTejado_hMaxSmdf_Mdf/')
                if GLO.GLBLformatoTilesAscInput:
                    trainPathAsc3 = (trainPathPng3.replace('/png', '/asc')).replace('\png', '/asc')
                # nombreCapas3 = ['AltP95SobreMdf',
                nombreCapas3 = [
                    'AltPlanoTejado',
                    'AltMaxSobreMdf',
                    'cotaMdf',
                ]
    
                print('clidcarto-> myLasData.aSubCeldasPlanoTejado', myLasData.aSubCeldasPlanoTejado.shape)
                print('clidcarto-> myLasData.aSubCeldasAltMaxSobreMdf', myLasData.aSubCeldasAltMaxSobreMdf.shape)
                print('clidcarto-> myLasData.aSubCeldasMdfCotaPlus', myLasData.aSubCeldasMdfCotaPlus.shape)
                # arrayCapas3 = np.concatenate( ( myLasData.aSubCeldasAlt95SobreMdf[..., np.newaxis].astype(np.float64),
                # arrayCapas3 = np.concatenate( ( myLasData.aSubCeldasMdfCotaPlus[..., np.newaxis].astype(np.float64),
                arrayCapas3 = np.concatenate(
                    (
                        myLasData.aSubCeldasPlanoTejado[..., np.newaxis].astype(np.float64),
                        myLasData.aSubCeldasAltMaxSobreMdf[..., np.newaxis].astype(np.float64),
                        myLasData.aSubCeldasMdfCotaPlus[..., np.newaxis].astype(np.float64),
                    ),
                    axis=2,
                )

            if grabarCapa4:
                # postVuelta2
                trainPathPng4 = os.path.join(GLO.MAINrutaOutput, train_dir, 'pngInputVar_latMacroMesosMicro/')
                if GLO.GLBLformatoTilesAscInput:
                    trainPathAsc4 = (trainPathPng4.replace('/png', '/asc')).replace('\png', '/asc')
                nombreCapas4 = ['LateralidadMinMinMacro', 'LateralidadMinMinMesos', 'LateralidadMinMinMicro']
                arrayCapas4 = np.concatenate(
                    (
                        myLasData.aSubCeldasLateralidadMinMinMacro[..., np.newaxis].astype(np.float64),
                        myLasData.aSubCeldasLateralidadMinMinMesos[..., np.newaxis].astype(np.float64),
                        myLasData.aSubCeldasLateralidadMinMinMicro[..., np.newaxis].astype(np.float64),
                    ),
                    axis=2,
                )
    
            if grabarCapa5:
                # postVuelta2
                trainPathPng5 = os.path.join(GLO.MAINrutaOutput, train_dir, 'pngInputVar_rugMacroMesosMicro/')
                if GLO.GLBLformatoTilesAscInput:
                    trainPathAsc5 = (trainPathPng5.replace('/png', '/asc')).replace('\png', '/asc')
                nombreCapas5 = ['RugosidadMinMaxMacro', 'RugosidadMinMaxMesos', 'RugosidadMinMaxMicro']
                arrayCapas5 = np.concatenate(
                    (
                        myLasData.aSubCeldasRugosidadMinMaxMacroInterSubCeldas[..., np.newaxis].astype(np.float64),
                        myLasData.aSubCeldasRugosidadMinMaxMesosInterSubCeldas[..., np.newaxis].astype(np.float64),
                        myLasData.aSubCeldasRugosidadMinMaxMicroInterSubCeldas[..., np.newaxis].astype(np.float64),
                    ),
                    axis=2,
                )
    
            if grabarCapa6:
                # postVuelta2
                trainPathPng6 = os.path.join(GLO.MAINrutaOutput, train_dir, 'pngInputVar_MdgEcmrPtes/')  # ok
                if GLO.GLBLformatoTilesAscInput:
                    trainPathAsc6 = (trainPathPng6.replace('/png', '/asc')).replace('\png', '/asc')
                nombreCapas6 = ['pteXglobal', 'pteYglobal', 'ecmrGlobal']
                arrayCapas6 = np.concatenate(
                    (
                        myLasData.aSubCeldasMdgAjuste[:, :, 1:2],
                        myLasData.aSubCeldasMdgAjuste[:, :, 2:3],
                        myLasData.aSubCeldasMdgAjuste[:, :, 3:4],
                    ),
                    axis=2,
                )
    
            # En principio sin uso:
            if grabarCapa7:
                # postVuelta2
                trainPathPng7 = os.path.join(GLO.MAINrutaOutput, train_dir, 'pngInputVar_Mdf_Min_Max/')
                # Estas seguramente no las voy a usar:
                nombreCapas7 = ['cotaMdf', 'cotaMin', 'cotaMax']
                arrayCapas7 = np.concatenate(
                    (
                        myLasData.aSubCeldasMdfCotaPlus[..., np.newaxis].astype(np.float64),
                        myLasData.aSubCeldasCotaMinAA[..., np.newaxis].astype(np.float64),
                        myLasData.aSubCeldasCotaMaxAA[..., np.newaxis].astype(np.float64),
                    ),
                    axis=2,
                )
                # myLasData.aSubCeldasPuntoMaxiSubCel_Tlp[:,:]['cotaDmPlus20SobreMdt8bits'].astype(np.float64) ),
    
            if grabarCapa8:
                # postVuelta2
                trainPathPng8 = os.path.join(GLO.MAINrutaOutput, train_dir, 'pngInputVar_Hmax_sMdf_sMdpmacro_sMdpMicro/')
                nombreCapas8 = ['AltMaxSobreMdfResta', 'AltMaxSobreMdpMacro', 'AltMaxSobreMdpMicro']
                arrayCapas8 = np.concatenate(
                    (
                        (myLasData.aSubCeldasCotaMaxAA[..., np.newaxis].astype(np.float64) - myLasData.aSubCeldasMdfCotaPlus[..., np.newaxis].astype(np.float64)),
                        (myLasData.aSubCeldasCotaMaxAA[..., np.newaxis].astype(np.float64) - myLasData.aSubCeldasMdpCotaMacro[..., np.newaxis].astype(np.float64)),
                        (myLasData.aSubCeldasCotaMaxAA[..., np.newaxis].astype(np.float64) - myLasData.aSubCeldasMdpCotaMicro[..., np.newaxis].astype(np.float64)),
                    ),
                    axis=2,
                )
    
            if grabarCapa9:
                # postVuelta2
                trainPathPng9 = os.path.join(GLO.MAINrutaOutput, train_dir, 'pngInputVar_RiC_Macro_Mesos_Micro_Megas/')
                # ->Estas 4 capas que se calculan en clidnv4.py por ahora no las uso,
                #  porque ya tengo las que se calculan en clidnv2y.py, que tienen en cuenta la lateralidad
                nombreCapas9 = ['rugoInterCeldillasMacro', 'rugoInterCeldillasMesos', 'rugoInterCeldillasMicro', 'rugoInterCeldillasEscarpe']
                arrayCapas9 = np.concatenate(
                    (
                        myLasData.aSubCeldasRugosidadMacroInterCeldillas[..., np.newaxis].astype(np.float64),
                        myLasData.aSubCeldasRugosidadMesosInterCeldillas[..., np.newaxis].astype(np.float64),
                        myLasData.aSubCeldasRugosidadMicroInterCeldillas[..., np.newaxis].astype(np.float64),
                        myLasData.aSubCeldasRugosidadMegasInterCeldillas[..., np.newaxis].astype(np.float64),
                    ),
                    axis=2,
                )

            if grabarCapaIm:
                # postVuelta2
                trainPathPngInt1m = os.path.join(GLO.MAINrutaOutput, train_dir, 'png1mInputVar_int_ndvi_hTejado/')
                nombreCapasInt1m = ['intSRetMed1m', 'ndviMed1m', 'AltPlanoTejado1m']
                arrayCapasInt1m = np.concatenate(
                    (
                        myLasData.aMetricoIntSRet[..., np.newaxis],
                        myLasData.aMetricoNDVIMed[..., np.newaxis],
                        myLasData.aMetricoPlanoTejado[..., np.newaxis]), axis=2
                )
    
            if grabarCapaRm:
                # postVuelta2
                trainPathPngRiC1m = os.path.join(GLO.MAINrutaOutput, train_dir, 'png1mInputVar_RiC_macro_mesos_micro/')
                nombreCapasRiC1m = ['RugosidadMacro1m', 'RugosidadMesos1m', 'RugosidadMicro1m']
                arrayCapasRiC1m = np.concatenate(
                    (
                        myLasData.aMetricoRugosidadMacroInterCeldillas[..., np.newaxis],
                        myLasData.aMetricoRugosidadMesosInterCeldillas[..., np.newaxis],
                        myLasData.aMetricoRugosidadMicroInterCeldillas[..., np.newaxis],
                    ),
                    axis=2,
                )
        # ======================================================================

        # ======================================================================
        for trainPathPng in [
            trainPathPngTargetOriClass,
            trainPathPngTargetTriClass,
            trainPathPngTargetBinClass,
            trainPathPng1,
            trainPathPng2,
            trainPathPng3,
            trainPathPng4,
            trainPathPng5,
            trainPathPng6,
            trainPathPng7,
            trainPathPng8,
            trainPathPng9,
            trainPathPngInt1m,
            trainPathPngRiC1m,
        ]:
            if not os.path.isdir(trainPathPng):
                os.makedirs(trainPathPng)
                print('\tclidcarto-> Creando directorio target o train png', trainPathPng)

        if GLO.GLBLformatoTilesAscInput:
            for trainPathPng in [
                trainPathPngTargetOriClass,
                trainPathPngTargetTriClass,
                trainPathPngTargetBinClass,
                trainPathPng1,
                trainPathPng2,
                trainPathPng3,
                trainPathPng4,
                trainPathPng5,
                trainPathPng6,
            ]:
                trainPathAsc = (trainPathPng.replace('/png', '/asc')).replace('\png', '/asc')
                if not os.path.isdir(trainPathAsc):
                    os.makedirs(trainPathAsc)
                    print('\tclidcarto-> Creacion indiscriminada de directorios target o train asc', trainPathAsc)
            if not os.path.isdir(trainPathAscOtros):
                os.makedirs(trainPathAscOtros)
                print('\tclidcarto-> Creando directorio', trainPathAscOtros)
        # ======================================================================


    if GLO.GLBLverbose:
        print('clidcarto-> Se generan los {} x {} tiles.'.format(numTilesRows, numTilesCols))
    for nRow in range(numTilesRows):
        for nCol in range(numTilesCols):

            if GLO.GLBLcrearTilesInputSoloSiHayTilesTargetDeCartoRef:
                # Si el tile no ha dado lugar a un tile Target de cartoRef,
                # no genero tile miniSubCel (input ni target)
                if GLO.GLBLcrearTilesTargetDeCartoRefSingUse and not cartoRefUsoSingular is None:
                    trainPathTargetSingUsePng = os.path.join(
                        GLO.MAINrutaOutput,
                        train_dir,
                        'png{}/'.format(cartoRefUsoSingular.tilesTargetPathTroncal)
                    )
                    pngFileNameTargetSingUse = os.path.join(
                        trainPathTargetSingUsePng,
                        '%s_%s_%i_%i.png' % (fileCoordYear, 'Train', nRow, nCol)
                    )
                    if not os.path.exists(pngFileNameTargetSingUse):
                        if GLO.GLBLverbose:
                            print('\t-> Se salta el tile {}-{} porque no existe el equivalente en cartoRef singUse.'.format(nRow, nCol))
                        continue
                if GLO.GLBLcrearTilesTargetDeCartoRefNucleos and not cartoRefNucleosUrbanos is None:
                    trainPathTargetSingUsePng = os.path.join(
                        GLO.MAINrutaOutput,
                        train_dir,
                        'png{}/'.format(cartoRefNucleosUrbanos.tilesTargetPathTroncal)
                    )
                    pngFileNameTargetSingUse = os.path.join(
                        trainPathTargetSingUsePng,
                        '%s_%s_%i_%i.png' % (fileCoordYear, 'Train', nRow, nCol)
                    )
                    if not os.path.exists(pngFileNameTargetSingUse):
                        if GLO.GLBLverbose:
                            print('\t-> Se salta el tile {}-{} porque no existe el equivalente en cartoRef nucleos.'.format(nRow, nCol))
                        continue
                if GLO.GLBLcrearTilesTargetDeCartoRefLandCover and not cartoRefLandCover is None:
                    trainPathTargetSingUsePng = os.path.join(
                        GLO.MAINrutaOutput,
                        train_dir,
                        'png{}/'.format(cartoRefLandCover.tilesTargetPathTroncal)
                    )
                    pngFileNameTargetSingUse = os.path.join(
                        trainPathTargetSingUsePng,
                        '%s_%s_%i_%i.png' % (fileCoordYear, 'Train', nRow, nCol)
                    )
                    if not os.path.exists(pngFileNameTargetSingUse):
                        if GLO.GLBLverbose:
                            print('\t-> Se salta el tile {}-{} porque no existe el equivalente en cartoRef landCover.'.format(nRow, nCol))
                        continue

            if nRow == 0:
                xInfIzdaTile = (myLasHead.xmin - margenXsobresalienteMetros)
                recorteIniY = 0
                recorteIniY1m = 0
            else:
                xInfIzdaTile = (
                    myLasHead.xmin
                    + (
                        GLO.GLBLtileSizeMetros
                        - margenXsobresalienteMetros
                        - GLO.GLBLtileSemiSolapeMetros
                    )
                    + ((nRow - 1) * GLBNtileKernelMetros)
                    - GLO.GLBLtileSemiSolapeMetros
                )
                recorteIniY = int(
                    (
                        GLBNtileSizeEnPixelsSubCelda
                        - margenYsobresalientePixelsScA
                        - GLBNtileSemiSolapePixelsSubCelda
                    )
                    + ((nRow - 1) * GLBNtileKernelPixelsSubCelda)
                    - GLBNtileSemiSolapePixelsSubCelda
                )
                recorteIniY1m = int(
                    (
                        GLBNtileSizeEnPixelsCeldilla
                        - margenYsobresalientePixelsCdA
                        - GLBNtileSemiSolapePixelsCeldilla
                    )
                    + ((nRow - 1) * GLBNtileKernelPixelsCeldilla)
                    - GLBNtileSemiSolapePixelsCeldilla
                 )
            if nCol == 0:
                yInfIzdaTile = (myLasHead.ymin - margenYsobresalienteMetros)
                recorteIniX = 0
                recorteIniX1m = 0
            else:
                yInfIzdaTile = (
                    myLasHead.ymin
                    + (
                        GLO.GLBLtileSizeMetros
                        - margenYsobresalienteMetros
                        - GLO.GLBLtileSemiSolapeMetros
                    )
                    + ((nCol - 1) * GLBNtileKernelMetros)
                    - GLO.GLBLtileSemiSolapeMetros
                )
                recorteIniX = int(
                    (
                        GLBNtileSizeEnPixelsSubCelda
                        - margenXsobresalientePixelsScA
                        - GLBNtileSemiSolapePixelsSubCelda
                    )
                    + ((nCol - 1) * GLBNtileKernelPixelsSubCelda)
                    - GLBNtileSemiSolapePixelsSubCelda
                )
                recorteIniX1m = int(
                    (
                        GLBNtileSizeEnPixelsCeldilla
                        - margenXsobresalientePixelsCdA
                        - GLBNtileSemiSolapePixelsCeldilla
                    )
                    + ((nCol - 1) * GLBNtileKernelPixelsCeldilla)
                    - GLBNtileSemiSolapePixelsCeldilla
                )

            if nRow == 0:
                iniY = margenYsobresalientePixelsScA
                iniY1m = margenYsobresalientePixelsCdA
            else:
                iniY = 0
                iniY1m = 0
            if nCol == 0:
                iniX = margenXsobresalientePixelsScA
                iniX1m = margenXsobresalientePixelsCdA
            else:
                iniX = 0
                iniX1m = 0

            if nRow == numTilesRows - 1:
                finY = int(GLBNtileSizeEnPixelsSubCelda - margenYsobresalientePixelsScB)
                finY1m = int(GLBNtileSizeEnPixelsCeldilla - margenYsobresalientePixelsCdB)
            else:
                finY = int(GLBNtileSizeEnPixelsSubCelda)
                finY1m = int(GLBNtileSizeEnPixelsCeldilla)
            if nCol == numTilesCols - 1:
                finX = int(GLBNtileSizeEnPixelsSubCelda - margenXsobresalientePixelsScB)
                finX1m = int(GLBNtileSizeEnPixelsCeldilla - margenXsobresalientePixelsCdB)
            else:
                finX = int(GLBNtileSizeEnPixelsSubCelda)
                finX1m = int(GLBNtileSizeEnPixelsCeldilla)

            if GLO.GLBLverbose:
                print('\tclidcarto-> tiles 2m:', nRow, nCol, '->', iniY, finY, iniX, finX,
                      '->1m', nRow, nCol, '->', iniY1m, finY1m, iniX1m, finX1m)
                print('\t\ttiles 2m recorte', recorteIniY, recorteIniY + finY - iniY,
                      recorteIniX, recorteIniX + finX - iniX,
                      '->1m recorte', recorteIniY1m, recorteIniY1m + finY1m - iniY1m,
                      recorteIniX1m, recorteIniX1m + finX1m - iniX1m)
                print('\t\tgrabarCapa1-6: {} {} {} {} {} {}'.format(grabarCapa1, grabarCapa2, grabarCapa3, grabarCapa4, grabarCapa5, grabarCapa6))


            # if grabarTarget:
            if GLO.GLBLcrearTilesConTodasLasClasesMiniSubCel or GLO.GLBLcrearTilesTargetMiniSubCelSoloSiHayNoSueloSuficientes:
                tileRecorte0TargetOriClass = np.zeros((GLBNtileSizeEnPixelsSubCelda, GLBNtileSizeEnPixelsSubCelda), dtype=arrayCapaTargetOriClas.dtype)
                targetOriClasRecorteShape = arrayCapaTargetOriClas[recorteIniY : recorteIniY + finY - iniY, recorteIniX : recorteIniX + finX - iniX].shape
                funY = iniY + targetOriClasRecorteShape[0]
                funX = iniX + targetOriClasRecorteShape[1]
                if (
                    tileRecorte0TargetOriClass[iniY:funY, iniX:funX].shape
                    == arrayCapaTargetOriClas[recorteIniY : recorteIniY + finY - iniY, recorteIniX : recorteIniX + finX - iniX].shape
                ):
                    tileRecorte0TargetOriClass[iniY:funY, iniX:funX] = arrayCapaTargetOriClas[recorteIniY : recorteIniY + finY - iniY, recorteIniX : recorteIniX + finX - iniX]
                # No normalizo el target, que tiene valores ASPRS o,
                #  si GLBLreorganizaLasClassParaGenerarTilesCuaTrinarios_X_6_2_345, con valores simplificados:
                #    0 (sin datos), 1 (edificio), 2 (suelo), 3 (vegetacion)
                #    Ver clidnv1.buscarGuardarPuntosMiniSubCel{} ln 1680)
                # tileRecorte0Normalizado = normalizarCapas(tileRecorte0TargetOriClass, nombreCapaT)

                if GLO.GLBLcrearTilesTargetMiniSubCelSoloSiHayNoSueloSuficientes:
                    listaSelectedTargets = [6]
                    minPorcentajePixeles = [GLO.GLBLminPctjEdificiosParaCrearTileTargetMiniSubCel]
                    miHistograma = np.bincount(tileRecorte0TargetOriClass.flatten())
                    if len(miHistograma) <= min(listaSelectedTargets):
                        if GLO.GLBLverbose:
                            print('\t\tclidcarto-> tiles 2m:', nRow, nCol,
                                  '-> Sin valores target seleccionados:', listaSelectedTargets)
                        continue
                    nPixelsSelectedTargets = []
                    tieneSuficientesPixelesDeLasCLasesElegidas = False
                    for nLasClass, minPctj in zip(listaSelectedTargets, minPorcentajePixeles):
                        if len(miHistograma) > nLasClass:
                            nPixelsSelectedTargets.append(miHistograma[nLasClass])
                            if miHistograma[nLasClass] >= minPctj * sum(miHistograma) / 100.0:
                                tieneSuficientesPixelesDeLasCLasesElegidas = True
                        else:
                            nPixelsSelectedTargets.append(0)
                    if not tieneSuficientesPixelesDeLasCLasesElegidas:
                        if GLO.GLBLverbose:
                            print('\t\tclidcarto-> tiles 2m:', nRow, nCol,
                                  '-> Insuficientes pixeles de las clases seleccionadas')
                        continue

            if grabarTarget:
                if GLO.GLBLreorganizaLasClassParaGenerarTilesCuaTrinarios_X_6_2_345:
                    tileRecorte0TargetTriClass = np.zeros((GLBNtileSizeEnPixelsSubCelda, GLBNtileSizeEnPixelsSubCelda), dtype=arrayCapaTargetTriClas.dtype)
                    targetTriClasRecorteShape = arrayCapaTargetTriClas[recorteIniY : recorteIniY + finY - iniY, recorteIniX : recorteIniX + finX - iniX].shape
                    funY = iniY + targetTriClasRecorteShape[0]
                    funX = iniX + targetTriClasRecorteShape[1]
                    if (
                        tileRecorte0TargetTriClass[iniY:funY, iniX:funX].shape
                        == arrayCapaTargetTriClas[recorteIniY : recorteIniY + finY - iniY, recorteIniX : recorteIniX + finX - iniX].shape
                    ):
                        tileRecorte0TargetTriClass[iniY:funY, iniX:funX] = arrayCapaTargetTriClas[recorteIniY : recorteIniY + finY - iniY, recorteIniX : recorteIniX + finX - iniX]

                if GLO.GLBLreorganizaLasClassParaGenerarTilesBinariosMonoClase:
                    tileRecorte0TargetBinClas = np.zeros((GLBNtileSizeEnPixelsSubCelda, GLBNtileSizeEnPixelsSubCelda), dtype=arrayCapaTargetBinClas.dtype)
                    targetBinClasRecorteShape = arrayCapaTargetBinClas[recorteIniY : recorteIniY + finY - iniY, recorteIniX : recorteIniX + finX - iniX].shape
                    funY = iniY + targetBinClasRecorteShape[0]
                    funX = iniX + targetBinClasRecorteShape[1]
                    if (
                        tileRecorte0TargetBinClas[iniY:funY, iniX:funX].shape
                        == arrayCapaTargetBinClas[recorteIniY : recorteIniY + finY - iniY, recorteIniX : recorteIniX + finX - iniX].shape
                    ):
                        tileRecorte0TargetBinClas[iniY:funY, iniX:funX] = arrayCapaTargetBinClas[recorteIniY : recorteIniY + finY - iniY, recorteIniX : recorteIniX + finX - iniX]

            if grabarCapa1:
                tileRecorte1 = np.zeros((GLBNtileSizeEnPixelsSubCelda, GLBNtileSizeEnPixelsSubCelda, arrayCapas1.shape[2]), dtype=arrayCapas1.dtype)
                shapeRecorte = arrayCapas1[recorteIniY : recorteIniY + finY - iniY, recorteIniX : recorteIniX + finX - iniX].shape
                funY = iniY + shapeRecorte[0]
                funX = iniX + shapeRecorte[1]
                if (
                    tileRecorte1[iniY:funY, iniX:funX].shape
                    == arrayCapas1[recorteIniY : recorteIniY + finY - iniY, recorteIniX : recorteIniX + finX - iniX].shape
                ):
                    tileRecorte1[iniY:funY, iniX:funX, :] = arrayCapas1[recorteIniY : recorteIniY + finY - iniY, recorteIniX : recorteIniX + finX - iniX, :]
                tileRecorte1Normalizado = normalizarCapas(tileRecorte1, nombreCapas1)

                # print('tileRecorte1Normalizado.dtype:', tileRecorte1Normalizado.dtype)
                # print('\nclidcarto-> comparar tile (0-1) con el de su dcha (1-1). ndvi->', nRow, nCol, 'tileRecorte1:')
                # print(nRow, nCol, 'Pixeles de la izda:\n', tileRecorte1[0:5, 127:128, 1])
                # print(nRow, nCol, 'Pixeles de la dcha:\n', tileRecorte1[-6:-1, 127:128, 1])
                # print('clidcarto-> ndvi->', nRow, nCol, 'tileRecorte1Normalizado:')
                # print('Sin normalizar:', tileRecorte1[10:12, 10:12, 1])
                # print('Normalizado:   ', tileRecorte1Normalizado[10:12, 10:12, 1])
                # print('Pixeles de la izda:', tileRecorte1Normalizado[0:5, 127:128, 1])
                # print('Pixeles de la dcha:', tileRecorte1Normalizado[-6:-1, 127:128, 1])


            if grabarCapa2:
                tileRecorte2 = np.zeros((GLBNtileSizeEnPixelsSubCelda, GLBNtileSizeEnPixelsSubCelda, arrayCapas2.shape[2]), dtype=arrayCapas2.dtype)
                shapeRecorte = arrayCapas2[recorteIniY : recorteIniY + finY - iniY, recorteIniX : recorteIniX + finX - iniX].shape
                funY = iniY + shapeRecorte[0]
                funX = iniX + shapeRecorte[1]
                if (
                    tileRecorte2[iniY:funY, iniX:funX].shape
                    == arrayCapas2[recorteIniY : recorteIniY + finY - iniY, recorteIniX : recorteIniX + finX - iniX].shape
                ):
                    tileRecorte2[iniY:funY, iniX:funX, :] = arrayCapas2[recorteIniY : recorteIniY + finY - iniY, recorteIniX : recorteIniX + finX - iniX, :]
                tileRecorte2Normalizado = normalizarCapas(tileRecorte2, nombreCapas2)

            if grabarCapa3:
                tileRecorte3 = np.zeros((GLBNtileSizeEnPixelsSubCelda, GLBNtileSizeEnPixelsSubCelda, arrayCapas3.shape[2]), dtype=arrayCapas3.dtype)
                shapeRecorte = arrayCapas3[recorteIniY : recorteIniY + finY - iniY, recorteIniX : recorteIniX + finX - iniX].shape
                funY = iniY + shapeRecorte[0]
                funX = iniX + shapeRecorte[1]
                if (
                    tileRecorte3[iniY:funY, iniX:funX].shape
                    == arrayCapas3[recorteIniY : recorteIniY + finY - iniY, recorteIniX : recorteIniX + finX - iniX].shape
                ):
                    tileRecorte3[iniY:funY, iniX:funX, :] = arrayCapas3[recorteIniY : recorteIniY + finY - iniY, recorteIniX : recorteIniX + finX - iniX, :]
                tileRecorte3Normalizado = normalizarCapas(tileRecorte3, nombreCapas3)

            if grabarCapa4:
                tileRecorte4 = np.zeros((GLBNtileSizeEnPixelsSubCelda, GLBNtileSizeEnPixelsSubCelda, arrayCapas4.shape[2]), dtype=arrayCapas4.dtype)
                shapeRecorte = arrayCapas4[recorteIniY : recorteIniY + finY - iniY, recorteIniX : recorteIniX + finX - iniX].shape
                funY = iniY + shapeRecorte[0]
                funX = iniX + shapeRecorte[1]
                if (
                    tileRecorte4[iniY:funY, iniX:funX].shape
                    == arrayCapas4[recorteIniY : recorteIniY + finY - iniY, recorteIniX : recorteIniX + finX - iniX].shape
                ):
                    tileRecorte4[iniY:funY, iniX:funX, :] = arrayCapas4[recorteIniY : recorteIniY + finY - iniY, recorteIniX : recorteIniX + finX - iniX, :]
                tileRecorte4Normalizado = normalizarCapas(tileRecorte4, nombreCapas4)

            if grabarCapa5:
                tileRecorte5 = np.zeros((GLBNtileSizeEnPixelsSubCelda, GLBNtileSizeEnPixelsSubCelda, arrayCapas5.shape[2]), dtype=arrayCapas5.dtype)
                shapeRecorte = arrayCapas5[recorteIniY : recorteIniY + finY - iniY, recorteIniX : recorteIniX + finX - iniX].shape
                funY = iniY + shapeRecorte[0]
                funX = iniX + shapeRecorte[1]
                if (
                    tileRecorte5[iniY:funY, iniX:funX].shape
                    == arrayCapas5[recorteIniY : recorteIniY + finY - iniY, recorteIniX : recorteIniX + finX - iniX].shape
                ):
                    tileRecorte5[iniY:funY, iniX:funX, :] = arrayCapas5[recorteIniY : recorteIniY + finY - iniY, recorteIniX : recorteIniX + finX - iniX, :]
                tileRecorte5Normalizado = normalizarCapas(tileRecorte5, nombreCapas5)

            if grabarCapa6:
                tileRecorte6 = np.zeros((GLBNtileSizeEnPixelsSubCelda, GLBNtileSizeEnPixelsSubCelda, arrayCapas6.shape[2]), dtype=arrayCapas6.dtype)
                shapeRecorte = arrayCapas6[recorteIniY : recorteIniY + finY - iniY, recorteIniX : recorteIniX + finX - iniX].shape
                funY = iniY + shapeRecorte[0]
                funX = iniX + shapeRecorte[1]
                if (
                    tileRecorte6[iniY:funY, iniX:funX].shape
                    == arrayCapas6[recorteIniY : recorteIniY + finY - iniY, recorteIniX : recorteIniX + finX - iniX].shape
                ):
                    tileRecorte6[iniY:funY, iniX:funX, :] = arrayCapas6[recorteIniY : recorteIniY + finY - iniY, recorteIniX : recorteIniX + finX - iniX, :]
                tileRecorte6Normalizado = normalizarCapas(tileRecorte6, nombreCapas6)

            if grabarCapa7:
                tileRecorte7 = np.zeros((GLBNtileSizeEnPixelsSubCelda, GLBNtileSizeEnPixelsSubCelda, arrayCapas7.shape[2]), dtype=arrayCapas7.dtype)
                shapeRecorte = arrayCapas7[recorteIniY : recorteIniY + finY - iniY, recorteIniX : recorteIniX + finX - iniX].shape
                funY = iniY + shapeRecorte[0]
                funX = iniX + shapeRecorte[1]
                if (
                    tileRecorte7[iniY:funY, iniX:funX].shape
                    == arrayCapas7[recorteIniY : recorteIniY + finY - iniY, recorteIniX : recorteIniX + finX - iniX].shape
                ):
                    tileRecorte7[iniY:funY, iniX:funX, :] = arrayCapas7[recorteIniY : recorteIniY + finY - iniY, recorteIniX : recorteIniX + finX - iniX, :]
                tileRecorte7Normalizado = normalizarCapas(tileRecorte7, nombreCapas7)

            if grabarCapa8:
                tileRecorte8 = np.zeros((GLBNtileSizeEnPixelsSubCelda, GLBNtileSizeEnPixelsSubCelda, arrayCapas8.shape[2]), dtype=arrayCapas8.dtype)
                shapeRecorte = arrayCapas8[recorteIniY : recorteIniY + finY - iniY, recorteIniX : recorteIniX + finX - iniX].shape
                funY = iniY + shapeRecorte[0]
                funX = iniX + shapeRecorte[1]
                if (
                    tileRecorte8[iniY:funY, iniX:funX].shape
                    == arrayCapas8[recorteIniY : recorteIniY + finY - iniY, recorteIniX : recorteIniX + finX - iniX].shape
                ):
                    tileRecorte8[iniY:funY, iniX:funX, :] = arrayCapas8[recorteIniY : recorteIniY + finY - iniY, recorteIniX : recorteIniX + finX - iniX, :]
                tileRecorte8Normalizado = normalizarCapas(tileRecorte8, nombreCapas8)

            if grabarCapa9:
                tileRecorte9 = np.zeros((GLBNtileSizeEnPixelsSubCelda, GLBNtileSizeEnPixelsSubCelda, arrayCapas9.shape[2]), dtype=arrayCapas9.dtype)
                shapeRecorte = arrayCapas9[recorteIniY : recorteIniY + finY - iniY, recorteIniX : recorteIniX + finX - iniX].shape
                funY = iniY + shapeRecorte[0]
                funX = iniX + shapeRecorte[1]
                if (
                    tileRecorte9[iniY:funY, iniX:funX].shape
                    == arrayCapas9[recorteIniY : recorteIniY + finY - iniY, recorteIniX : recorteIniX + finX - iniX].shape
                ):
                    tileRecorte9[iniY:funY, iniX:funX, :] = arrayCapas9[recorteIniY : recorteIniY + finY - iniY, recorteIniX : recorteIniX + finX - iniX, :]
                tileRecorte9Normalizado = normalizarCapas(tileRecorte9, nombreCapas9)

            if grabarCapaIm:
                tileRecorteInt1m = np.zeros((GLO.GLBLtileSizeMetros, GLO.GLBLtileSizeMetros, arrayCapasInt1m.shape[2]), dtype=arrayCapasInt1m.dtype)
                shapeRecorte = arrayCapasInt1m[recorteIniY1m : recorteIniY1m + finY1m - iniY1m, recorteIniX1m : recorteIniX1m + finX1m - iniX1m].shape
                funY1m = iniY1m + shapeRecorte[0]
                funX1m = iniX1m + shapeRecorte[1]
                if (
                    tileRecorteInt1m[iniY1m:funY1m, iniX1m:funX1m].shape
                    == arrayCapasInt1m[recorteIniY1m : recorteIniY1m + finY1m - iniY1m, recorteIniX1m : recorteIniX1m + finX1m - iniX1m].shape
                ):
                    tileRecorteInt1m[iniY1m:funY1m, iniX1m:funX1m, :] = arrayCapasInt1m[
                        recorteIniY1m : recorteIniY1m + finY1m - iniY1m, recorteIniX1m : recorteIniX1m + finX1m - iniX1m, :
                    ]
                # No hay interpolacion porque mi array corresponde a celdas de metrosSubCelda x metrosSubCelda
                tileRecorte1NormalizaInt1m = normalizarCapas(tileRecorteInt1m, nombreCapasInt1m)

            if grabarCapaRm:
                tileRecorteRiC1m = np.zeros((GLO.GLBLtileSizeMetros, GLO.GLBLtileSizeMetros, arrayCapasRiC1m.shape[2]), dtype=arrayCapasRiC1m.dtype)
                shapeRecorte = arrayCapasRiC1m[recorteIniY1m : recorteIniY1m + finY1m - iniY1m, recorteIniX1m : recorteIniX1m + finX1m - iniX1m].shape
                funY1m = iniY1m + shapeRecorte[0]
                funX1m = iniX1m + shapeRecorte[1]
                if (
                    tileRecorteRiC1m[iniY1m:funY1m, iniX1m:funX1m].shape
                    == arrayCapasRiC1m[recorteIniY1m : recorteIniY1m + finY1m - iniY1m, recorteIniX1m : recorteIniX1m + finX1m - iniX1m].shape
                ):
                    tileRecorteRiC1m[iniY1m:funY1m, iniX1m:funX1m, :] = arrayCapasRiC1m[
                        recorteIniY1m : recorteIniY1m + finY1m - iniY1m, recorteIniX1m : recorteIniX1m + finX1m - iniX1m, :
                    ]
                # No hay interpolacion porque mi array corresponde a celdas de metrosSubCelda x metrosSubCelda
                tileRecorte1NormalizaRiC1m = normalizarCapas(tileRecorteRiC1m, nombreCapasRiC1m)

            if GLO.GLBLformatoTilesNpz:
                # Guardo como npz todas las variables en un solo fichero con un array uint8
                npzFileName = os.path.join(trainPathNpzInput, '%s_%s_%i_%i.npz' % (fileCoordYear, 'Train', nRow, nCol))
                if GLO.GLBLcalcularSubCeldas:
                    np.savez_compressed(npzFileName, rgb=tileRecorte1Normalizado, pte=tileRecorte2Normalizado)

            # Si quiero representar la imagen la giro 90 grados levogiros: np.rot90(array)
            # Se puede hacer de varias formas:
            # tileRecorte_Normalizado = np.rot90(tileRecorte_Normalizado)
            # tileRecorte_Normalizado = np.flip(tileRecorte_Normalizado.transpose(1, 0, 2), axis=0)
            # Para revertir el giro:
            # tileRecorte_Normalizado = np.rot90(tileRecorte_Normalizado, 3)

            # if nRow == 1 and nCol == 5:
            #    import matplotlib.pyplot as plt
            #    plt.imshow(tileRecorte_[:, :, 0])
            #    print('ccccccccccccccccccc')
            #    plt.show()
            #    plt.imshow(tileRecorte_Normalizado[:, :, 0])
            #    print('ddddddddddddd')
            #    plt.show()

            if GLO.GLBLformatoTilesPng:
                pngFileNameTargetOriClass = os.path.join(trainPathPngTargetOriClass, '%s_%s_%i_%i.png' % (fileCoordYear, 'Train', nRow, nCol))
                pngFileNameTargetTriClass = os.path.join(trainPathPngTargetTriClass, '%s_%s_%i_%i.png' % (fileCoordYear, 'Train', nRow, nCol))
                pngFileNameTargetBinClass = os.path.join(trainPathPngTargetBinClass, '%s_%s_%i_%i.png' % (fileCoordYear, 'Train', nRow, nCol))
                pngFileName1 = os.path.join(trainPathPng1, '%s_%s_%i_%i.png' % (fileCoordYear, 'Train', nRow, nCol))
                pngFileName2 = os.path.join(trainPathPng2, '%s_%s_%i_%i.png' % (fileCoordYear, 'Train', nRow, nCol))
                pngFileName3 = os.path.join(trainPathPng3, '%s_%s_%i_%i.png' % (fileCoordYear, 'Train', nRow, nCol))
                pngFileName4 = os.path.join(trainPathPng4, '%s_%s_%i_%i.png' % (fileCoordYear, 'Train', nRow, nCol))
                pngFileName5 = os.path.join(trainPathPng5, '%s_%s_%i_%i.png' % (fileCoordYear, 'Train', nRow, nCol))
                pngFileName6 = os.path.join(trainPathPng6, '%s_%s_%i_%i.png' % (fileCoordYear, 'Train', nRow, nCol))
                pngFileName7 = os.path.join(trainPathPng7, '%s_%s_%i_%i.png' % (fileCoordYear, 'Train', nRow, nCol))
                pngFileName8 = os.path.join(trainPathPng8, '%s_%s_%i_%i.png' % (fileCoordYear, 'Train', nRow, nCol))
                pngFileName9 = os.path.join(trainPathPng9, '%s_%s_%i_%i.png' % (fileCoordYear, 'Train', nRow, nCol))
                pngFileNameInt1m = os.path.join(trainPathPngInt1m, '%s_%s_%i_%i.png' % (fileCoordYear, 'Train', nRow, nCol))
                pngFileNameRiC1m = os.path.join(trainPathPngRiC1m, '%s_%s_%i_%i.png' % (fileCoordYear, 'Train', nRow, nCol))

#                 if GLO.GLBLverbose:
#                     print('\tclidcarto-> Creando tilesPng.')
#                     print('\t\tpngFileNameTargetOriClass: {}'.format(pngFileNameTargetOriClass))
#                     print('\t\tpngFileNameTargetBinClass: {}'.format(pngFileNameTargetBinClass))
#                     print('\t\tpngFileName1:              {}'.format(pngFileName1))
#                     print('\t\tpngFileName2:              {}'.format(pngFileName2))
#                     print('\t\tpngFileName3:              {}'.format(pngFileName3))
#                     print('\t\tpngFileName4:              {}'.format(pngFileName4))
#                     print('\t\tpngFileName5:              {}'.format(pngFileName5))
#                     print('\t\tpngFileName6:              {}'.format(pngFileName6))

                # colorMode
                # -> https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.fromarray
                #   -> https://pillow.readthedocs.io/en/stable/handbook/concepts.html#concept-modes
                #   -> https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.Image.convert
                #     -> https://pillow.readthedocs.io/en/stable/reference/Image.html?highlight=Image.ADAPTIVE#palettes
                #  The mode of an image defines the type and depth of a pixel in the image.
                #  Each pixel uses the full range of the bit depth.
                #  So a 1-bit pixel has a range of 0-1, an 8-bit pixel has a range of 0-255 and so on.
                #  1 (1-bit pixels, black and white, stored with one pixel per byte)
                #  L (8-bit pixels, black and white) -> Se refiere a niveles de gris
                #  P (8-bit pixels, mapped to any other mode using a color palette) (reduce el num de niveles de gris)
                #  RGB (3x8-bit pixels, true color)
                #  RGBA (4x8-bit pixels, true color with transparency mask)
                # The Python Imaging Library uses a Cartesian pixel coordinate system, with (0,0) in the upper left corner.
                # Note that the coordinates refer to the implied pixel corners;
                # the centre of a pixel addressed as (0, 0) actually lies at (0.5, 0.5).
                '''
                >>> myImage = Image.fromarray(b, 'L')
                >>> myImage.save('d:/_ws/borrarImagen.png')
                >>> a = np.random.rand(256, 256)
                >>> b= np.uint8(a*255)
                >>> myImage1 = Image.fromarray(b, 'L') # Imagen con 256 niveles de gris (8bit)
                >>> myImage1.save('d:/_ws/borrarImagen1.png')
                >>> myImage2 = Image.fromarray(b, '1') # Imagen en blanco y negro (1bit)
                >>> myImage2.save('d:/_ws/borrarImagen2.png')
                >>> myImageP = myImage1.convert('P', palette = Image.ADAPTIVE, colors = 10) # Imagen con 10 niveles de gris (8bit)
                >>> myImageP.save('d:/_ws/borrarImagenP.png')
                '''

                if grabarTarget:
                    if GLO.GLBLcrearTilesConTodasLasClasesMiniSubCel:
                        # 'lasClassOriginal'
                        # colorMode = 'P'
                        # palette = []
                        colorMode = 'L'
                        myImageBN = Image.fromarray(np.rot90(tileRecorte0TargetOriClass), colorMode)
                        # https://pillow.readthedocs.io/en/5.1.x/reference/Image.html#PIL.Image.Image.save
                        #  https://pillow.readthedocs.io/en/5.1.x/handbook/image-file-formats.html#image-file-formats
                        #   https://pillow.readthedocs.io/en/5.1.x/handbook/image-file-formats.html#png
                        if os.path.exists(pngFileNameTargetOriClass) and not LCLmantenerTilesGuardados:
                            print('clidcarto-> Eliminando tile pngTargetOriClas previo: {}'.format(pngFileNameTargetOriClass))
                            os.remove(pngFileNameTargetOriClass)
                        myImageBN.save(pngFileNameTargetOriClass)
                        # ATENCION: No elegir el modo "P" (palette) porque reorganiza los valores de los pixeles y luego no se pueden interpretar
                        # myImageConPaleta = myImageBN.convert("P", palette = Image.ADAPTIVE, colors = 25)
                        # myImageConPaleta.save(pngFileNameTargetOriClass)
                        if GLO.GLBLformatoTilesAscTargetMiniSubCelLasClass:
                            capaTileRecorte = tileRecorte0TargetOriClass[:, :]
                            nombreCapa = nombreCapaTargetOriClass
                            ascFileNameScipyZoom = os.path.join(trainPathAscTargetOriClass, '%s_%s_%i_%i.asc' % (fileCoordYear, nombreCapa, nRow, nCol))
                            crearASC(
                                ascFileNameScipyZoom,
                                capaTileRecorte,
                                capaTileRecorte.shape,
                                GLBNtileSizeEnPixelsSubCelda,
                                GLBNtileSizeEnPixelsSubCelda,
                                GLO.GLBLmetrosSubCelda,
                                xInfIzdaTile,
                                yInfIzdaTile,
                                GLO.GLBLnoData,
                                nTipoDato=2,
                            )
                        # Creacion de los tiles exData propiamente dichos para tiles con lasClass original sin reagrupar
                        if GLO.GLBLcrearTilesExDataMiniSubCelLasClass:
                            lookupTable = [0 if (i == 0 or i == 12) else 1 for i in range(256)]
                            # for lasClassNoData in [0, 12]:
                            #     lookupTable[int(lasClassNoData)] = 0
                            pngFileNameExData = os.path.join(
                                trainPathExDataMiniSubCelLasClassOriginal,
                                '%s_%s_%i_%i.png' % (fileCoordYear, 'Train', nRow, nCol)
                            )
                            # print('\t->->-> guardando exDataMiniSubCelLasClassOriginal:', pngFileNameExData)
                            # Mapeo las 10 categorias de tileRecorteNormalizado a 1 y 0 (ceros las que se excluyen del entrenamiento):
                            # Atencion: si uso colorMode = 'L' tengo que usar dtype=np.uint8
                            colorMode = 'L'  # (8-bit pixels, black and white) -> lleva el valor max a 255 y el min a 0 -> No respeta los valores del array ->Espacio de color: Escala de grises
                            tileRecorteExData = np.array(
                                [lookupTable[val] for val in tileRecorte0TargetOriClass.flatten()],
                                dtype=np.uint8
                            ).reshape(tileRecorte0TargetOriClass.shape)
                            myImageBN = Image.fromarray(np.rot90(tileRecorteExData), colorMode)
                            if os.path.exists(pngFileNameExData) and not LCLmantenerTilesGuardados:
                                print('\t\tclidcarto->->-> Eliminando fichero exData existente con pathlib:', pngFileNameExData)
                                #os.remove(pngFileNameExData)
                                (pathlib.Path(pngFileNameExData)).unlink()
                                if os.path.exists(pngFileNameExData):
                                    print('\t\t\tNo se ha podido eliminar el fichero existente')
                            myImageBN.save(pngFileNameExData)


                    if GLO.GLBLreorganizaLasClassParaGenerarTilesCuaTrinarios_X_6_2_345:
                        # print('clidcarto->->-> guardando targetTrinario:', pngFileNameTargetTriClass)
                        colorMode = 'L'
                        myImageBN = Image.fromarray(np.rot90(tileRecorte0TargetTriClass), colorMode)
                        if os.path.exists(pngFileNameTargetTriClass) and not LCLmantenerTilesGuardados:
                            print('\t\tclidcarto->->-> Eliminando fichero triLasClass existente con pathlib:', pngFileNameTargetTriClass)
                            #os.remove(pngFileNameTargetTriClass)
                            (pathlib.Path(pngFileNameTargetTriClass)).unlink()
                            if os.path.exists(pngFileNameTargetTriClass):
                                print('\t\t\tNo se ha podido eliminar el fichero existente')
                        myImageBN.save(pngFileNameTargetTriClass)
                        if GLO.GLBLformatoTilesAscInput:
                            capaTileRecorte = tileRecorte0TargetTriClass[:, :]
                            nombreCapa = nombreCapaTargetTriClass
                            ascFileNameScipyZoom = os.path.join(trainPathAscTargetTriClass, '%s_%s_%i_%i.asc' % (fileCoordYear, nombreCapa, nRow, nCol))
                            crearASC(
                                ascFileNameScipyZoom,
                                capaTileRecorte,
                                capaTileRecorte.shape,
                                GLBNtileSizeEnPixelsSubCelda,
                                GLBNtileSizeEnPixelsSubCelda,
                                GLO.GLBLmetrosSubCelda,
                                xInfIzdaTile,
                                yInfIzdaTile,
                                GLO.GLBLnoData,
                                nTipoDato=2,
                            )

                    if GLO.GLBLreorganizaLasClassParaGenerarTilesBinariosMonoClase:
                        colorMode = 'L'
                        myImageBN = Image.fromarray(np.rot90(tileRecorte0TargetBinClas), colorMode)
                        if os.path.exists(pngFileNameTargetBinClass) and not LCLmantenerTilesGuardados:
                            print('clidcarto-> Eliminando tile pngTargetBinClas previo: {}'.format(pngFileNameTargetBinClass))
                            os.remove(pngFileNameTargetBinClass)
                        myImageBN.save(pngFileNameTargetBinClass)
                        if GLO.GLBLformatoTilesAscInput:
                            capaTileRecorte = tileRecorte0TargetBinClas[:, :]
                            nombreCapa = nombreCapaTargetBinClass
                            ascFileNameScipyZoom = os.path.join(trainPathAscTargetBinClass, '%s_%s_%i_%i.asc' % (fileCoordYear, nombreCapa, nRow, nCol))
                            crearASC(
                                ascFileNameScipyZoom,
                                capaTileRecorte,
                                capaTileRecorte.shape,
                                GLBNtileSizeEnPixelsSubCelda,
                                GLBNtileSizeEnPixelsSubCelda,
                                GLO.GLBLmetrosSubCelda,
                                xInfIzdaTile,
                                yInfIzdaTile,
                                GLO.GLBLnoData,
                                nTipoDato=2,
                            )

                    # Creacion de los tiles exData propiamente dichos para tiles cuatrinarios y binarios (se usa el mismo para ambos)
                    if GLO.GLBLreorganizaLasClassParaGenerarTilesCuaTrinarios_X_6_2_345 or GLO.GLBLreorganizaLasClassParaGenerarTilesBinariosMonoClase:
                        if GLO.GLBLcrearTilesExDataMiniSubCelLasClass:
                            # Solo se usan los miniSubCel que estan en alguna de las 3 clases (edificio, suelo, vegetacion)
                            lookupTable = [1 if (i in [1, 2, 3]) else 0 for i in range(256)]
                            # for lasClassNoData in [0, 12]:
                            #     lookupTable[int(lasClassNoData)] = 0
                            pngFileNameExData = os.path.join(
                                trainPathExDataMiniSubCelLasClass_2_345_6,
                                '%s_%s_%i_%i.png' % (fileCoordYear, 'Train', nRow, nCol)
                            )
                            # print('\t->->-> guardando exDataMiniSubCelLasClass_2_345_6:', pngFileNameExData)
                            # Mapeo las 10 categorias de tileRecorteNormalizado a 1 y 0 (ceros las que se excluyen del entrenamiento):
                            # Atencion: si uso colorMode = 'L' tengo que usar dtype=np.uint8
                            colorMode = 'L'  # (8-bit pixels, black and white) -> lleva el valor max a 255 y el min a 0 -> No respeta los valores del array ->Espacio de color: Escala de grises
                            if GLO.GLBLreorganizaLasClassParaGenerarTilesCuaTrinarios_X_6_2_345:
                                tileRecorteExData = np.array(
                                    [lookupTable[val] for val in tileRecorte0TargetTriClass.flatten()],
                                    dtype=np.uint8
                                ).reshape(tileRecorte0TargetTriClass.shape)
                            elif GLO.GLBLreorganizaLasClassParaGenerarTilesBinariosMonoClase:
                                tileRecorteExData = np.array(
                                    [lookupTable[val] for val in tileRecorte0TargetBinClas.flatten()],
                                    dtype=np.uint8
                                ).reshape(tileRecorte0TargetBinClas.shape)
                            myImageBN = Image.fromarray(np.rot90(tileRecorteExData), colorMode)
                            if os.path.exists(pngFileNameExData) and not LCLmantenerTilesGuardados:
                                print('\t\tclidcarto->->-> Eliminando fichero exData existente con pathlib:', pngFileNameExData)
                                #os.remove(pngFileNameExData)
                                (pathlib.Path(pngFileNameExData)).unlink()
                                if os.path.exists(pngFileNameExData):
                                    print('\t\t\tNo se ha podido eliminar el fichero existente')
                            myImageBN.save(pngFileNameExData)


                colorMode = 'RGB'  # ATENCION: Creo q lleva el rango a 0-255. Eso ya lo he hecho yo para cada capa de forma independeinte con normalizar8bits{}
                # print('clidcarto->->-> grabarCapa1->', grabarCapa1, 'pngFileName1->', pngFileName1)
                if grabarCapa1:
                    # grupoTiles='preVuelta2'  -> nombreCapas1 = ['intSRetMed', 'ndviMed', 'ndwiMed'] -> '%train_dir%/pngInputVar_int_ndvi_ndwi/'
                    # grupoTiles='postVuelta2' -> nombreCapas1 = ['IntSRetMed', 'ndviMed', 'ndwiMed'] -> '%train_dir%/pngInputVar_int_ndvi_ndwi/'
                    if os.path.exists(pngFileName1) and not LCLmantenerTilesGuardados:
                        print('clidcarto-> Eliminando tile pngFileName1 previo: {}'.format(pngFileName1))
                        os.remove(pngFileName1)
                    tileRecorte1NormalizadoImg = Image.fromarray(np.rot90(tileRecorte1Normalizado), colorMode)
                    # print('clidcarto-> tileRecorte1Normalizado dtype', tileRecorte1Normalizado.dtype)
                    # print('clidcarto-> tileRecorte1Normalizado shape', tileRecorte1Normalizado.shape)
                    # print('clidcarto-> tileRecorte1Normalizado A ', tileRecorte1Normalizado[10, 10])
                    # print('clidcarto-> tileRecorte1Normalizado B ', (np.rot90(tileRecorte1Normalizado))[-10, 10])
                    # print('clidcarto-> tileRecorte1Normalizado B ', (np.rot90(tileRecorte1Normalizado))[-11, 10])
                    # print('clidcarto-> tileRecorte1NormalizadoImg', tileRecorte1NormalizadoImg.getpixel((256-11, 10)))
                    tileRecorte1NormalizadoImg.save(pngFileName1)
                    if GLO.GLBLformatoTilesAscInput:
                        for numCapa in range(tileRecorte1.shape[2]):
                            if GLO.GLBLnormalizarTilesAscInput:
                                capaTileRecorte = tileRecorte1Normalizado[:, :, numCapa]
                                nTipoDato = 3
                            else:
                                capaTileRecorte = tileRecorte1[:, :, numCapa]
                                nTipoDato = 5
                            nombreCapa = nombreCapas1[numCapa]
                            ascFileNameScipyZoom = os.path.join(trainPathAsc1, '%s_%s_%i_%i.asc' % (fileCoordYear, nombreCapa, nRow, nCol))
                            crearASC(
                                ascFileNameScipyZoom,
                                capaTileRecorte,
                                capaTileRecorte.shape,
                                GLBNtileSizeEnPixelsSubCelda,
                                GLBNtileSizeEnPixelsSubCelda,
                                GLO.GLBLmetrosSubCelda,
                                xInfIzdaTile,
                                yInfIzdaTile,
                                GLO.GLBLnoData,
                                nTipoDato=nTipoDato,
                            )

                if grabarCapa2:
                    # grupoTiles='preVuelta2'  -> nombreCapas2 = ['NirPtoMax', 'RedPtoMax', 'GreenPtoMax'] -> '%train_dir%/pngInputVar_nirRedGreen_maxiSubCel/'
                    # grupoTiles='postVuelta2' -> nombreCapas2 = ['NirPtoMax', 'RedPtoMax', 'GreenPtoMax'] -> '%train_dir%/pngInputVar_nirRedGreen_maxiSubCel/'
                    if os.path.exists(pngFileName2) and not LCLmantenerTilesGuardados:
                        print('clidcarto-> Eliminando tile pngFileName2 previo: {}'.format(pngFileName2))
                        os.remove(pngFileName2)
                    Image.fromarray(np.rot90(tileRecorte2Normalizado), colorMode).save(pngFileName2)
                    if GLO.GLBLformatoTilesAscInput:
                        for numCapa in range(tileRecorte2.shape[2]):
                            if GLO.GLBLnormalizarTilesAscInput:
                                capaTileRecorte = tileRecorte2Normalizado[:, :, numCapa]
                                nTipoDato = 3
                            else:
                                capaTileRecorte = tileRecorte2[:, :, numCapa]
                                nTipoDato = 4
                            nombreCapa = nombreCapas2[numCapa]
                            ascFileNameScipyZoom = os.path.join(trainPathAsc2, '%s_%s_%i_%i.asc' % (fileCoordYear, nombreCapa, nRow, nCol))
                            crearASC(
                                ascFileNameScipyZoom,
                                capaTileRecorte,
                                capaTileRecorte.shape,
                                GLBNtileSizeEnPixelsSubCelda,
                                GLBNtileSizeEnPixelsSubCelda,
                                GLO.GLBLmetrosSubCelda,
                                xInfIzdaTile,
                                yInfIzdaTile,
                                GLO.GLBLnoData,
                                nTipoDato=nTipoDato,
                            )

                if grabarCapa3:
                    # grupoTiles='preVuelta2'  -> nombreCapas3 = ['NirPtoMin', 'RedPtoMin', 'GreenPtoMin'] -> '%train_dir%/pngInputVar_nirRedGreen_miniSubCel/'
                    # grupoTiles='postVuelta2' -> nombreCapas7 = ['AltPlanoTejado', 'AltMaxSobreMdf', 'AltMinSobreMdf',] -> '%train_dir%/pngInputVar_hTejado_hMaxSmdf_Mdf/'
                    if os.path.exists(pngFileName3) and not LCLmantenerTilesGuardados:
                        print('clidcarto-> Eliminando tile pngFileName3 previo: {}'.format(pngFileName3))
                        os.remove(pngFileName3)
                    Image.fromarray(np.rot90(tileRecorte3Normalizado), colorMode).save(pngFileName3)
                    if GLO.GLBLformatoTilesAscInput:
                        for numCapa in range(tileRecorte3.shape[2]):
                            if GLO.GLBLnormalizarTilesAscInput:
                                capaTileRecorte = tileRecorte3Normalizado[:, :, numCapa]
                                nTipoDato = 3
                            else:
                                capaTileRecorte = tileRecorte3[:, :, numCapa]
                                nTipoDato = 0
                            nombreCapa = nombreCapas3[numCapa]
                            ascFileNameScipyZoom = os.path.join(trainPathAsc3, '%s_%s_%i_%i.asc' % (fileCoordYear, nombreCapa, nRow, nCol))
                            crearASC(
                                ascFileNameScipyZoom,
                                capaTileRecorte,
                                capaTileRecorte.shape,
                                GLBNtileSizeEnPixelsSubCelda,
                                GLBNtileSizeEnPixelsSubCelda,
                                GLO.GLBLmetrosSubCelda,
                                xInfIzdaTile,
                                yInfIzdaTile,
                                GLO.GLBLnoData,
                                nTipoDato=nTipoDato,
                            )

                if grabarCapa4:
                    # grupoTiles='preVuelta2'  -> nombreCapas4 = ['mseByteMicroPlanoNubePuntual', 'pteXx50MicroPlanoNubePuntual', 'pteYx50MicroPlanoNubePuntual'] -> '%train_dir%/pngInputVar_planoNubePuntual_miniSubCel/')
                    # grupoTiles='postVuelta2' -> nombreCapas4 = ['LateralidadMinMinMacro', 'LateralidadMinMinMesos', 'LateralidadMinMinMicro'] -> '%train_dir%/pngInputVar_latMacroMesosMicro/'
                    if os.path.exists(pngFileName4) and not LCLmantenerTilesGuardados:
                        print('clidcarto-> Eliminando tile pngFileName4 previo: {}'.format(pngFileName4))
                        os.remove(pngFileName4)
                    Image.fromarray(np.rot90(tileRecorte4Normalizado), colorMode).save(pngFileName4)
                    if GLO.GLBLformatoTilesAscInput:
                        for numCapa in range(tileRecorte4.shape[2]):
                            if GLO.GLBLnormalizarTilesAscInput:
                                capaTileRecorte = tileRecorte4Normalizado[:, :, numCapa]
                                nTipoDato = 3
                            else:
                                capaTileRecorte = tileRecorte4[:, :, numCapa]
                                nTipoDato = 5
                            nombreCapa = nombreCapas4[numCapa]
                            ascFileNameScipyZoom = os.path.join(trainPathAsc4, '%s_%s_%i_%i.asc' % (fileCoordYear, nombreCapa, nRow, nCol))
                            crearASC(
                                ascFileNameScipyZoom,
                                capaTileRecorte,
                                capaTileRecorte.shape,
                                GLBNtileSizeEnPixelsSubCelda,
                                GLBNtileSizeEnPixelsSubCelda,
                                GLO.GLBLmetrosSubCelda,
                                xInfIzdaTile,
                                yInfIzdaTile,
                                GLO.GLBLnoData,
                                nTipoDato=nTipoDato,
                            )

                if grabarCapa5:
                    # grupoTiles='preVuelta2'  -> nombreCapas5 = ['cotaAbsolutaDmMinSubCel', 'cotaRelDmMaxNubePuntual', 'cotaRelDmPlanoNubePuntual'] -> '%train_dir%/pngInputVar_cotasRelativas_miniSubCel/'
                    # grupoTiles='postVuelta2' -> nombreCapas5 = ['RugosidadMinMaxMacro', 'RugosidadMinMaxMesos', 'RugosidadMinMaxMicro'] -> '%train_dir%/pngInputVar_rugMacroMesosMicro/'
                    if os.path.exists(pngFileName5) and not LCLmantenerTilesGuardados:
                        print('clidcarto-> Eliminando tile pngFileName5 previo: {}'.format(pngFileName5))
                        os.remove(pngFileName5)
                    Image.fromarray(np.rot90(tileRecorte5Normalizado), colorMode).save(pngFileName5)
                    if GLO.GLBLformatoTilesAscInput:
                        for numCapa in range(tileRecorte5.shape[2]):
                            if GLO.GLBLnormalizarTilesAscInput:
                                capaTileRecorte = tileRecorte5Normalizado[:, :, numCapa]
                                nTipoDato = 3
                            else:
                                capaTileRecorte = tileRecorte5[:, :, numCapa]
                                nTipoDato = 5
                            nombreCapa = nombreCapas5[numCapa]
                            ascFileNameScipyZoom = os.path.join(trainPathAsc5, '%s_%s_%i_%i.asc' % (fileCoordYear, nombreCapa, nRow, nCol))
                            crearASC(
                                ascFileNameScipyZoom,
                                capaTileRecorte,
                                capaTileRecorte.shape,
                                GLBNtileSizeEnPixelsSubCelda,
                                GLBNtileSizeEnPixelsSubCelda,
                                GLO.GLBLmetrosSubCelda,
                                xInfIzdaTile,
                                yInfIzdaTile,
                                GLO.GLBLnoData,
                                nTipoDato=nTipoDato,
                            )

                if grabarCapa6:
                    # grupoTiles='preVuelta2'  -> nombreCapas6 = ['pteXglobal', 'pteYglobal', 'ecmrGlobal'] -> '%train_dir%/pngInputVar_ecmrGlobal_MdgPtes/'
                    # grupoTiles='postVuelta2' -> nombreCapas3 = ['pteXglobal', 'pteYglobal', 'ecmrGlobal'] -> '%train_dir%/pngInputVar_mse_pteX_pteY/'
                    if os.path.exists(pngFileName6) and not LCLmantenerTilesGuardados:
                        print('clidcarto-> Eliminando tile pngFileName6 previo: {}'.format(pngFileName6))
                        os.remove(pngFileName6)
                    Image.fromarray(np.rot90(tileRecorte6Normalizado), colorMode).save(pngFileName6)
                    if GLO.GLBLformatoTilesAscInput:
                        for numCapa in range(tileRecorte6.shape[2]):
                            if GLO.GLBLnormalizarTilesAscInput:
                                capaTileRecorte = tileRecorte6Normalizado[:, :, numCapa]
                                nTipoDato = 3
                            else:
                                capaTileRecorte = tileRecorte6[:, :, numCapa]
                                nTipoDato = 5
                            nombreCapa = nombreCapas6[numCapa]
                            ascFileNameScipyZoom = os.path.join(trainPathAsc6, '%s_%s_%i_%i.asc' % (fileCoordYear, nombreCapa, nRow, nCol))
                            crearASC(
                                ascFileNameScipyZoom,
                                capaTileRecorte,
                                capaTileRecorte.shape,
                                GLBNtileSizeEnPixelsSubCelda,
                                GLBNtileSizeEnPixelsSubCelda,
                                GLO.GLBLmetrosSubCelda,
                                xInfIzdaTile,
                                yInfIzdaTile,
                                GLO.GLBLnoData,
                                nTipoDato=nTipoDato,
                            )

                if grabarCapa7:
                    # grupoTiles='preVuelta2'  -> nombreCapas7 = ['anisotropy', 'planarity', 'sphericity'] -> '%train_dir%/pngInputVar_miniSubCel_autovalores/'
                    # grupoTiles='postVuelta2' -> nombreCapas7 = ['cotaMin', 'DifCota', 'AltDmPlus20SobreMdt8bits']
                    if os.path.exists(pngFileName7) and not LCLmantenerTilesGuardados:
                        print('clidcarto-> Eliminando tile pngFileName7 previo: {}'.format(pngFileName7))
                        os.remove(pngFileName7)
                    Image.fromarray(np.rot90(tileRecorte7Normalizado), colorMode).save(pngFileName7)
                    if GLO.GLBLformatoTilesAscInput:
                        for numCapa in range(tileRecorte7.shape[2]):
                            if GLO.GLBLnormalizarTilesAscInput:
                                capaTileRecorte = tileRecorte7Normalizado[:, :, numCapa]
                                nTipoDato = 3
                            else:
                                capaTileRecorte = tileRecorte7[:, :, numCapa]
                                nTipoDato = 5
                            nombreCapa = nombreCapas7[numCapa]
                            ascFileNameScipyZoom = os.path.join(trainPathAscOtros, '%s_%s_%i_%i.asc' % (fileCoordYear, nombreCapa, nRow, nCol))
                            crearASC(
                                ascFileNameScipyZoom,
                                capaTileRecorte,
                                capaTileRecorte.shape,
                                GLBNtileSizeEnPixelsSubCelda,
                                GLBNtileSizeEnPixelsSubCelda,
                                GLO.GLBLmetrosSubCelda,
                                xInfIzdaTile,
                                yInfIzdaTile,
                                GLO.GLBLnoData,
                                nTipoDato=nTipoDato,
                            )

                if grabarCapa8:
                    # ['AltMaxSobreMdfResta', 'AltMaxSobreMdpMacro', 'AltMaxSobreMdpMicro']
                    if os.path.exists(pngFileName8) and not LCLmantenerTilesGuardados:
                        print('clidcarto-> Eliminando tile pngFileName9 previo: {}'.format(pngFileName9))
                        os.remove(pngFileName8)
                    Image.fromarray(np.rot90(tileRecorte8Normalizado), colorMode).save(pngFileName8)
                    if GLO.GLBLformatoTilesAscInput:
                        for numCapa in range(tileRecorte8.shape[2]):
                            if GLO.GLBLnormalizarTilesAscInput:
                                capaTileRecorte = tileRecorte8Normalizado[:, :, numCapa]
                                nTipoDato = 3
                            else:
                                capaTileRecorte = tileRecorte8[:, :, numCapa]
                                nTipoDato = 5
                            nombreCapa = nombreCapas8[numCapa]
                            ascFileNameScipyZoom = os.path.join(trainPathAscOtros, '%s_%s_%i_%i.asc' % (fileCoordYear, nombreCapa, nRow, nCol))
                            crearASC(
                                ascFileNameScipyZoom,
                                capaTileRecorte,
                                capaTileRecorte.shape,
                                GLBNtileSizeEnPixelsSubCelda,
                                GLBNtileSizeEnPixelsSubCelda,
                                GLO.GLBLmetrosSubCelda,
                                xInfIzdaTile,
                                yInfIzdaTile,
                                GLO.GLBLnoData,
                                nTipoDato=nTipoDato,
                            )

                if grabarCapa9:
                    # ['rugoInterCeldillasMacro', 'rugoInterCeldillasMesos', 'rugoInterCeldillasMicro', 'rugoInterCeldillasEscarpe']
                    if GLO.GLBLguardarCapaRugosidadInterCeldillasSubCeldas:
                        if os.path.exists(pngFileName9) and not LCLmantenerTilesGuardados:
                            print('clidcarto-> Eliminando tile pngFileName9_ previo: {}'.format(pngFileName9))
                            os.remove(pngFileName9)
                        Image.fromarray(np.rot90(tileRecorte9Normalizado), colorMode).save(pngFileName9)
                        if GLO.GLBLformatoTilesAscInput:
                            for numCapa in range(tileRecorte9.shape[2]):
                                if GLO.GLBLnormalizarTilesAscInput:
                                    capaTileRecorte = tileRecorte9Normalizado[:, :, numCapa]
                                    nTipoDato = 3
                                else:
                                    capaTileRecorte = tileRecorte9[:, :, numCapa]
                                    nTipoDato = 5
                                nombreCapa = nombreCapas9[numCapa]
                                ascFileNameScipyZoom = os.path.join(trainPathAscOtros, '%s_%s_%i_%i.asc' % (fileCoordYear, nombreCapa, nRow, nCol))
                                crearASC(
                                    ascFileNameScipyZoom,
                                    capaTileRecorte,
                                    capaTileRecorte.shape,
                                    GLBNtileSizeEnPixelsSubCelda,
                                    GLBNtileSizeEnPixelsSubCelda,
                                    GLO.GLBLmetrosSubCelda,
                                    xInfIzdaTile,
                                    yInfIzdaTile,
                                    GLO.GLBLnoData,
                                    nTipoDato=nTipoDato,
                                )

                if grabarCapaIm:
                    # ['intSRetMed1m', 'ndviMed1m', 'AltPlanoTejado1m']
                    if os.path.exists(pngFileNameInt1m) and not LCLmantenerTilesGuardados:
                        print('clidcarto-> Eliminando tile pngFileNameInt1m previo: {}'.format(pngFileNameInt1m))
                        os.remove(pngFileNameInt1m)
                    Image.fromarray(np.rot90(tileRecorte1NormalizaInt1m), colorMode).save(pngFileNameInt1m)
                    if GLO.GLBLformatoTilesAscInput:
                        for numCapa in range(tileRecorteInt1m.shape[2]):
                            if GLO.GLBLnormalizarTilesAscInput:
                                capaTileRecorte = tileRecorte1NormalizaInt1m[:, :, numCapa]
                                nTipoDato = 3
                            else:
                                capaTileRecorte = tileRecorteInt1m[:, :, numCapa]
                                nTipoDato = 5
                            nombreCapa = nombreCapasInt1m[numCapa]
                            ascFileNameScipyZoom = os.path.join(trainPathAscOtros, '%s_%s_%i_%i.asc' % (fileCoordYear, nombreCapa, nRow, nCol))
                            crearASC(
                                ascFileNameScipyZoom,
                                capaTileRecorte,
                                capaTileRecorte.shape,
                                GLO.GLBLtileSizeMetros,
                                GLO.GLBLtileSizeMetros,
                                GLO.GLBLmetrosCeldilla,
                                xInfIzdaTile,
                                yInfIzdaTile,
                                GLO.GLBLnoData,
                                nTipoDato=nTipoDato,
                            )

                if grabarCapaRm:
                    if os.path.exists(pngFileNameRiC1m) and not LCLmantenerTilesGuardados:
                        print('clidcarto-> Eliminando tile pngFileNameRiC1m previo: {}'.format(pngFileNameRiC1m))
                        os.remove(pngFileNameRiC1m)
                    Image.fromarray(np.rot90(tileRecorte1NormalizaRiC1m), colorMode).save(pngFileNameRiC1m)
                    # ['RugosidadMacro1m', 'RugosidadMesos1m', 'RugosidadMicro1m']
                    if GLO.GLBLformatoTilesAscInput:
                        for numCapa in range(tileRecorteRiC1m.shape[2]):
                            if GLO.GLBLnormalizarTilesAscInput:
                                capaTileRecorte = tileRecorte1NormalizaRiC1m[:, :, numCapa]
                                nTipoDato = 3
                            else:
                                capaTileRecorte = tileRecorteRiC1m[:, :, numCapa]
                                nTipoDato = 5
                            nombreCapa = nombreCapasRiC1m[numCapa]
                            ascFileNameScipyZoom = os.path.join(trainPathAscOtros, '%s_%s_%i_%i.asc' % (fileCoordYear, nombreCapa, nRow, nCol))
                            crearASC(
                                ascFileNameScipyZoom,
                                capaTileRecorte,
                                capaTileRecorte.shape,
                                GLO.GLBLtileSizeMetros,
                                GLO.GLBLtileSizeMetros,
                                GLO.GLBLmetrosCeldilla,
                                xInfIzdaTile,
                                yInfIzdaTile,
                                GLO.GLBLnoData,
                                nTipoDato=nTipoDato,
                            )

            # Scipy normaliza la imagen al crearla (usa PIL)
            # scipy.misc.toimage(tileRecorte).save(pngFileName)
            # scipy.misc.toimage(tileRecorteNormalizado, cmin=0.0, cmax=...).save(pngFileName)
    tilesCreados = True
    print('\n{:_^80}'.format(''))
    print('clidcarto-> Ok tiles creados: {}'.format(grupoTiles))
    print('{:=^80}'.format(''))
    return tilesCreados


# ==============================================================================
if __name__ == "__main__":
    # import cartolidar
    pass
