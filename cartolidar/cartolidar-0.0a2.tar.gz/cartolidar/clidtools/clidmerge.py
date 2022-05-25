#!/usr/bin/python
# -*- coding: UTF-8 -*-
'''
Created on 10/02/2022
@author: benmarjo
'''
# -*- coding: latin-1 -*-

import os
import sys
import pathlib
import time
import unicodedata
import warnings
import math
# import random

import numpy as np
import numpy.ma as ma
from scipy.spatial import KDTree
from scipy.spatial import distance_matrix
# import matplotlib as mpl
import matplotlib.pyplot as plt
# import matplotlib.colors as mcolors
# from PIL import Image, ImageDraw
# import Image
# import ImageDraw
from configparser import RawConfigParser
# try:
#     from configparser import RawConfigParser
# except ImportError:  # Python 2
#     from ConfigParser import RawConfigParser
try:
    import psutil
    psutilOk = True
except:
    psutilOk = False

# Para que acceda a osgeo he incluido la ruta: C/OSGeo4W64/apps/Python27/Lib/site-packages
# en Project->Properties->pydev - PYTHONPATH->External libraries
try:
    import gdal, ogr, osr, gdalnumeric, gdalconst
    gdalOk = True
except:
    gdalOk = False
    print('clidpar-> No se ha podido cargar gdal directamente, se intenta de la carpeta osgeo')
if not gdalOk:
    # Esto daba error en casa
    try:
        from osgeo import gdal, ogr, osr, gdalnumeric, gdalconst
        gdalOk = True
    except:
        gdalOk = False
        print('clidpar-> Tampoco se ha podido cargar desde la carpeta osgeo')
        sys.exit(0)


# ==============================================================================
# Agrego el idProceso para poder lanzar trabajos paralelos con distinta configuracion
# En principio con clidpar no ejecuto trabajos en paralelo con distinta configuracion
# Mantengo el procedimiento por si acaso
# GRAL_idProceso = random.randint(1, 999998)
GRAL_idProceso = 0
sys.argv.append('idProceso')
sys.argv.append(GRAL_idProceso)
# ==============================================================================
from clidax import clidraster
# from clidax import clidconfig
# from clidax import clidcarto
# ==============================================================================

# ==============================================================================
def mergeBloquesASC(
        LCLrutaAscRaizFull,
        LCLexplorarNivelDeSubdirs,
        LCLlistaDasoVarsFileTypes,
    ):
    global GLO
    global ARGSconvertirAltAcm16Bit
    global ARGSconvertirAltAdm8Bit
    global GLBLconvertirAlt
    global ARGSsubLoteTiff

    # ==========================================================================
    miOutputDir = os.path.join(LCLrutaAscRaizFull, GLO.GLBLsubdirOutputParaMergeAsc)
    if not os.path.exists(miOutputDir):
        if GLO.GLBLverbose:
            print('\nNo existe directorio %s -> Se crea automaticamente' % (miOutputDir))
        try:
            os.makedirs(miOutputDir)
        except:
            print('\nATENCION: No se ha podido crear el directorio {}'.format(miOutputDir))
            print('\tRevisar derechos de escritura en esa ruta')
            sys.exit(0)
    else:
        if GLO.GLBLverbose:
            print('\nEl directorio %s ya existe -> Se agregan los tif a este directorio' % (miOutputDir))
    # ==========================================================================


    if MAIN_ENTORNO == 'calendula' or len(LCLlistaDasoVarsFileTypes) == 1:
        miTipoDeFicheroMerge = LCLlistaDasoVarsFileTypes[0]
        LCLlistaDasoVarsFileTypes = LCLlistaDasoVarsFileTypes[:1]
    else:
        print('\nTipos de fichero que se pueden integrar:')
        for num, prop in enumerate(LCLlistaDasoVarsFileTypes):
            print(num, prop)
        selec = input('Indica el tipo de fichero asc a integrar: (pulsar "x" para todos)')
        try:
            if selec != 'x':
                miTipoDeFicheroMerge = 'x'
                print('Se procesan todos los ficheros de tipo: {}'.format(LCLlistaDasoVarsFileTypes))
            else:
                AUX_numTipoFichero = int(selec)
                miTipoDeFicheroMerge = LCLlistaDasoVarsFileTypes[AUX_numTipoFichero]
                LCLlistaDasoVarsFileTypes = [miTipoDeFicheroMerge]
                print('Se procesan los ficheros de tipo %s' % miTipoDeFicheroMerge)
        except:
            miTipoDeFicheroMerge = LCLlistaDasoVarsFileTypes[0]
            LCLlistaDasoVarsFileTypes = LCLlistaDasoVarsFileTypes[:1]
            print('Tipo no identificado; se procesan los ficheros de tipo %s' % miTipoDeFicheroMerge)


    if MAIN_ENTORNO == 'windows' and ARGSconvertirAltAcm16Bit == GLO.convertirAltPorDefecto and ARGSconvertirAltAdm8Bit == GLO.convertirAltPorDefecto:
        transformarAllturasPorDefecto = '2'
        print('Transformar alturas:')
        print('0. No, dejarlas en metros (float32).')
        print('1. Transformar a dm (8 bits).')
        print('2. Transformar a cm (16 bits).')
        selec = input('Elije opcion ({}): '.format(transformarAllturasPorDefecto))
        if selec == '':
            selec = transformarAllturasPorDefecto
        if selec == '1':
            ARGSconvertirAltAdm8Bit = True
            ARGSconvertirAltAcm16Bit = False
        elif selec == '2':
            ARGSconvertirAltAdm8Bit = False
            ARGSconvertirAltAcm16Bit = True
        else:
            ARGSconvertirAltAdm8Bit = False
            ARGSconvertirAltAcm16Bit = False
        if (ARGSdasoVar.lower()).startswith('alt') and (ARGSconvertirAltAdm8Bit or ARGSconvertirAltAcm16Bit):
            GLBLconvertirAlt = True
        else:
            GLBLconvertirAlt = False
        print('\nOpcion elegida: ARGSconvertirAltAdm8Bit: {}; ARGSconvertirAltAcm16Bit: {}'.format(ARGSconvertirAltAdm8Bit, ARGSconvertirAltAcm16Bit))


    if LCLlistaDasoVarsFileTypes[0][:3] == 'Fcc':
        tipoDatoPorDefecto = '6'
    elif 'alt' in (LCLlistaDasoVarsFileTypes[0]).lower():
        tipoDatoPorDefecto = '1'
    # elif LCLlistaDasoVarsFileTypes[0][:9] == 'CeldasAlt' or LCLlistaDasoVarsFileTypes[0][:12] == 'SubCeldasAlt':
    #     tipoDatoPorDefecto = '1'
    elif LCLlistaDasoVarsFileTypes[0][:20] == 'planoBasal_intercept' or LCLlistaDasoVarsFileTypes[0][:16] == 'SubCeldasMdkCota':
        tipoDatoPorDefecto = '1'
    else:
        tipoDatoPorDefecto = '1'

    # ==========================================================================
    nBandasOutput = 1
    '''
    Pixel data types
    GDT_Unknown  Unknown or unspecified type
    GDT_Byte     Eight bit unsigned integer
    GDT_UInt16   Sixteen bit unsigned integer
    GDT_Int16    Sixteen bit signed integer
    GDT_UInt32   Thirty two bit unsigned integer
    GDT_Int32    Thirty two bit signed integer
    GDT_Float32  Thirty two bit floating point
    GDT_Float64  Sixty four bit floating point
    GDT_CInt16   Complex Int16
    GDT_CInt32   Complex Int32
    GDT_CFloat32 Complex Float32
    GDT_CFloat64 Complex Float64
    '''
    # Creo la capa raster de destino y asigno su rasterband 1
    if MAIN_ENTORNO == 'calendula':
        selec = tipoDatoPorDefecto
    else:
        print('\nTipo de dato del tif:')
        print('1. GDT_Float32')
        print('2. GDT_UInt32')
        print('3. GDT_Int32')
        print('4. GDT_UInt16')
        print('5. GDT_Int16')
        print('6. GDT_Byte')
        selec = input('Elije tipo ({})'.format(tipoDatoPorDefecto))
        if selec == '':
            selec = tipoDatoPorDefecto
    if selec == '1':
        outputGdalDatatype = gdal.GDT_Float32
        outputNpDatatype = np.float32
        dataType = 'Float32'
        noDataPrevisto = -9999
        noDataProvisional = -99999
    elif selec == '2':
        outputGdalDatatype = gdal.GDT_UInt32
        outputNpDatatype = np.uint32
        dataType = 'UInt32'
        noDataPrevisto = 9999
        noDataProvisional = 99999
    elif selec == '3':
        outputGdalDatatype = gdal.GDT_Int32
        outputNpDatatype = np.int32
        dataType = 'Int32'
        noDataPrevisto = -9999
        noDataProvisional = -99999
    elif selec == '4':
        outputGdalDatatype = gdal.GDT_UInt16
        outputNpDatatype = np.uint16
        dataType = 'UInt16'
        noDataPrevisto = 9999
        noDataProvisional = 65535
    elif selec == '5':
        outputGdalDatatype = gdal.GDT_Int16
        outputNpDatatype = np.int16
        dataType = 'Int16'
        noDataPrevisto = -9999
        noDataProvisional = -32768
    elif selec == '6':
        outputGdalDatatype = gdal.GDT_Byte
        outputNpDatatype = np.int8
        dataType = 'Byte'
        noDataPrevisto = 255
        noDataProvisional = 1
    else:
        outputGdalDatatype = gdal.GDT_Float32
        outputNpDatatype = np.uint8
        dataType = 'Float32'
        noDataPrevisto = -9999
        noDataProvisional = -99999

    if (ARGSdasoVar.lower()).startswith('alt') and ARGSconvertirAltAdm8Bit:
        outputGdalDatatype = gdal.GDT_Byte
        outputNpDatatype = np.int8
        dataType = 'Byte'
        noDataDestinoTiff = 255
        print('\n\nSe convierten las alturas a dm y cambia el tipo de dato a:')
        print('\tTipo dato Gdal: ', outputGdalDatatype)
        print('\tTipo dato numpy:', outputNpDatatype)
    elif (ARGSdasoVar.lower()).startswith('alt') and ARGSconvertirAltAcm16Bit:
        outputGdalDatatype = gdal.GDT_Int16
        outputNpDatatype = np.int16
        dataType = 'Int16'
        noDataDestinoTiff = -32768
        print('\n\nSe convierten las alturas a cm y cambia el tipo de dato a:')
        print('\tTipo dato Gdal: ', outputGdalDatatype)
        print('\tTipo dato numpy:', outputNpDatatype)
    else:
        noDataDestinoTiff = noDataPrevisto
        print('\n\nTipode datos de la capa tiff que se genera:')
        print('\tTipo dato Gdal: ', outputGdalDatatype)
        print('\tTipo dato numpy:', outputNpDatatype)


    print('\nTipo de compresion del tif:')
    if MAIN_ENTORNO == 'calendula':
        if GLO.GLBLoutputDriverName == "GTiff":
            outputOptions = ['COMPRESS=LZW']
            outputOptions.append('BIGTIFF=YES')
        else:
            outputOptions = []
    else:
        print('1. Sin comprimir')
        print('2. LZW')
        selec = input('Elije tipo (2)')
        if selec == '1':
            outputOptions = []
        else:
            outputOptions = ['COMPRESS=LZW']
        print('Tipo elegido:', outputOptions)
        outputOptions.append('BIGTIFF=YES')

    # outputOptions.append('TFW=YES')
    # outputOptions.append('TILED=YES')
    # outputOptions.append('BLOCKXSIZE=128') #Creo que por defecto 256
    # outputOptions.append('BLOCKYSIZE=128') #Creo que por defecto 256
    # outputOptions.append('PHOTOMETRIC=MINISBLACK')
    # PHOTOMETRIC=PALETTE only compatible with Byte or UInt16
    if dataType == 'Byte':
        outputOptions.append('PHOTOMETRIC=PALETTE')
    # outputOptions.append('PHOTOMETRIC=RGB')
    # outputOptions.append('PHOTOMETRIC=MINISWHITE') #Creo que esta es la opcion por defecto

    # Con mas de 8 bits no se ve nada
    # Con 8 bits se ve negro con: DEFECTO, PALETTE, RGB, MINISWHITE y blanco con MINISBLACK

    if MAIN_ENTORNO == 'calendula':
        if ARGStipoOutput == '':
            nTipoOutput = 0
        else:
            try:
                nTipoOutput = int(ARGStipoOutput)
            except:
                nTipoOutput = 0
        if nTipoOutput == 4:
            GLO.GLBLambitoDelOutputTiff = ARGSsubLoteTiff
        elif nTipoOutput == 5:
            GLO.GLBLambitoDelOutputTiff = 'subLoteAsc_{}'.format(ARGSsubLoteTiff)
        else:
            GLO.GLBLambitoDelOutputTiff = ''

    elif MAIN_ENTORNO == 'windows':
        print('\nTipo de integracion:')
        print('0. Integrar los asc en un tif con extension de la envolvente de todos los asc')
        print('1. Integrar los ficheros asc en un nuevo tif de CyL')
        print('2. Integrar los ficheros asc en un nuevo tif de la mitad oeste de CyL')
        print('3. Integrar los ficheros asc en un nuevo tif de la mitad este de CyL')
        print('4. Integrar los ficheros asc en un nuevo tif de un marco en un cuadrante de CyL (pte)')
        print('5. Integrar los asc en un tif con extension de un cuarto de la envolvente de todos los asc')
        print('6. Integrar los ficheros asc en un tif creado previamente')
        print('7. Integrar los ficheros asc en un tif igual a uno de referencia (mismas dimensiones y resolucion)')
        print('8. Integrar los ficheros asc en tif individuales')
        print('9. Integrar un solo fichero asc en un fichero tif individual')
        selec = input('Elije opcion (0): ')
        try:
            nTipoOutput = int(selec)
        except:
            nTipoOutput = 0

        if nTipoOutput == 4:
            print('\n0. Elegir cuadrante:')
            print('1. CE')
            print('2. NE')
            print('3. NW')
            print('4. SE')
            print('5. SW')
            print('6. XX')
            print('5. NE')
            print('7. LE')
            selec2 = input('Elije opcion (2): ')
            try:
                nCuadrante = int(selec2)
            except:
                nCuadrante = 2
            print('\nOpcion elegida: {}'.format(nCuadrante))
            if nCuadrante == 1:
                GLO.GLBLambitoDelOutputTiff = 'CyL_marcoCE'
            elif nCuadrante == 2:
                GLO.GLBLambitoDelOutputTiff = 'CyL_marcoNE'
            elif nCuadrante == 3:
                GLO.GLBLambitoDelOutputTiff = 'CyL_marcoNW'
            elif nCuadrante == 4:
                GLO.GLBLambitoDelOutputTiff = 'CyL_marcoSE'
            elif nCuadrante == 5:
                GLO.GLBLambitoDelOutputTiff = 'CyL_marcoSW'
            elif nCuadrante == 6:
                GLO.GLBLambitoDelOutputTiff = 'CyL_marcoXX'
            elif nCuadrante == 7:
                GLO.GLBLambitoDelOutputTiff = 'CyL_marcoLE'
            else:
                GLO.GLBLambitoDelOutputTiff = 'CyL_marcoXX'

        elif nTipoOutput == 5:
            print('\nElegir subLote:')
            print('1. NE')
            print('2. NW')
            print('3. SE')
            print('4. SW')
            selec2 = input('Elije opcion (4): ')
            try:
                nCuadrante = int(selec2)
            except:
                nCuadrante = 4
            print('\nOpcion elegida: {}'.format(nCuadrante))
            if nCuadrante == 1:
                ARGSsubLoteTiff = 'NE'
            elif nCuadrante == 2:
                ARGSsubLoteTiff = 'NW'
            elif nCuadrante == 3:
                ARGSsubLoteTiff = 'SE'
            elif nCuadrante == 4:
                ARGSsubLoteTiff = 'SW'
            else:
                ARGSsubLoteTiff = 'SW'
            GLO.GLBLambitoDelOutputTiff = 'subLoteAsc_{}'.format(ARGSsubLoteTiff)

    print('\nSe crea un nuevo fichero tif para cada tipo de fichero.')
    if nTipoOutput == 0:
        GLO.GLBLambitoDelOutputTiff = 'LoteAsc'
    elif nTipoOutput == 1:
        GLO.GLBLambitoDelOutputTiff = 'CyL'
    elif nTipoOutput == 2:
        GLO.GLBLambitoDelOutputTiff = 'CyL_w'
    elif nTipoOutput == 3:
        GLO.GLBLambitoDelOutputTiff = 'CyL_e'
    elif nTipoOutput == 4:
        pass
    elif nTipoOutput == 5:
        pass
    elif nTipoOutput == 6:
        # Integrar los ficheros asc en un tif creado previamente
        GLO.GLBLambitoDelOutputTiff = 'rasterDest_CyL'
    elif nTipoOutput == 7:
        # Integrar los ficheros asc en un tif igual a uno de referencia (mismas dimensiones y resolucion)
        # Si finalmente no lo utilizo, quitar esto
        GLO.GLBLambitoDelOutputTiff = 'rasterRefe_CyL'
    elif nTipoOutput == 8:
        GLO.GLBLambitoDelOutputTiff = 'FicherosTiffIndividuales'
    elif nTipoOutput == 9:
        GLO.GLBLambitoDelOutputTiff = 'ConvertirSoloUnFicheroASC'
    else:
        sys.exit(0)


    for AUX_numTipoFichero in range(len(LCLlistaDasoVarsFileTypes)):
        print(
            '\nSe procesan los ficheros de tipo: xxx_xxxx_{}.asc \n\tde las carpetas que hay en la ruta: {}'.format(
                LCLlistaDasoVarsFileTypes[AUX_numTipoFichero],
                LCLrutaAscRaizFull
            )
        )
        if LCLexplorarNivelDeSubdirs > 0:
            print('\nSe procesan {} nivel(es) de subdirectorios'.format(LCLexplorarNivelDeSubdirs))

        integrarFicherosAscTipoFich(
            LCLlistaDasoVarsFileTypes,
            AUX_numTipoFichero,
            LCLrutaAscRaizFull,
            LCLexplorarNivelDeSubdirs,
            miOutputDir,
            GLO.GLBLambitoDelOutputTiff,
            ARGSsubLoteTiff,
            GLO.GLBLoutputDriverName,
            nBandasOutput,
            outputGdalDatatype,
            outputNpDatatype,
            noDataPrevisto,
            noDataProvisional,
            noDataDestinoTiff,
            outputOptions,
        )


# ==============================================================================
def mergePlusMDE():
    # Pendiente implementar los argumentos que paso a esta funcion
    # Por el momento esta preparada para el mdt y tirando de MAINmiRutaRaiz/data/carto

    # MAINmiRutaRaiz = '/scratch/jcyl_spi_1/jcyl_spi_1_1/'
    MAINmiRutaRaiz = MAIN_RAIZ_DIR
    MAINrutaCarto = os.path.join(MAINmiRutaRaiz, 'data/carto/')
    # nombreCapaInputVector = 'malla2k.gpkg'
    # nombreCapaInputVector = 'CuadrantesLidarPNOA2.shp'
    # nombreCapaInputVector = 'corte.shp'

    MDTSprefijo = 'mdt'
    MDTSprefijo = 'mds'

    grupoBloques = 'bordeCyL'
    grupoBloques = 'multiCuadrante'
    grupoBloques = 'monoCuadrante'

    if MDTSprefijo == 'mdt':
        MDTSdir = 'Klass'
        MDTStxt = 'SubCeldasMdkCotaItp'
    elif MDTSprefijo == 'mds':
        MDTSdir = 'Cielo'
        MDTStxt = 'SubCeldasMdcCotaMax'

    MAINrutaMdt02 = f'E:/calendula/{MDTSprefijo}02_{grupoBloques}'
    MAINrutaMdtAux = f'E:/calendula/{MDTSprefijo}Aux'

    print('clidpar-> MAINmiRutaRaiz', MAINmiRutaRaiz)
    print('clidpar-> MAIN_PROJ_DIR ', MAIN_PROJ_DIR)
    print('clidpar-> MAINrutaCarto ', MAINrutaCarto)
    print('clidpar-> MAINrutaMdt02 ', MAINrutaMdt02)
    print('clidpar-> MAINrutaMdtAux', MAINrutaMdtAux)

    # Ver: https://gdal.org/python/
    #      https://gdal.org/tutorials/warp_tut.html
    #      http://pcjericks.github.io/py-gdalogr-cookbook/layers.html
    # https://www.youtube.com/watch?v=1jHhQKJOQ5M
    # https://stackoverflow.com/questions/48706402/python-perform-gdalwarp-in-memory-with-gdal-bindings
    # https://gis.stackexchange.com/questions/257257/how-to-use-gdal-warp-cutline-option
    # https://gis.stackexchange.com/questions/361213/how-to-merge-rasters-with-gdal-merge-py
    print('Iniciando componerMDE', MAIN_PROJ_DIR)

    myListaBloquesFile = os.path.join(MAIN_PROJ_DIR, 'listaBloquesCuadrantes.cfg')

    if not os.path.exists(myListaBloquesFile):
        print(f'No se encuentra {myListaBloquesFile}')
        sys.exit(0)
    config = RawConfigParser()
    config.optionxform = str  # Avoid change to lowercase
    try:
        config.read(myListaBloquesFile)
        print('clidpar-> Leyendo: {}'.format(myListaBloquesFile))
    except (Exception) as thisError: # Raised when a generated error does not fall into any category.
        print('cartolidar-> Error leyendo: {}'.format(myListaBloquesFile))
        print('\t-> Puede ser debido a que hay alguna linea repetida (campo clave).')
        print('\t-> Error exception: {}'.format(thisError))

    for miSeccion in config.sections():
        print('Seccion:', miSeccion)
        # if miSeccion != 'multiCuadrante' and miSeccion != 'bordeCyL':
        if miSeccion != grupoBloques:
            continue
        nBloqueProcesado = 0
        for nBloqueTotal, miBloque in enumerate(config.options(miSeccion)):
            miYearCuads = config.get(miSeccion, miBloque).split(',')
            # print('\t->', type(miYearCuads), miYearCuads, len(miYearCuads))
            print(f'{nBloqueTotal}/{nBloqueProcesado}-> {miSeccion} {miBloque}-> {miYearCuads} ({len(miYearCuads)})')
            miYear1 = miYearCuads[0]
            miCuad1 = miYearCuads[1]
            if len(miYearCuads) > 3:
                miYear2 = miYearCuads[2]
                miCuad2 = miYearCuads[3]
            else:
                miYear2 = '0000'
                miCuad2 = ''

            disponibleCuad1 = True
            disponibleCuad2 = True
            targetRasterFileNameCuad1 = f'E:/calendula\{miCuad1.upper()}\Mde/02mCell/{MDTSdir}\{miBloque}_{miYear1}_{MDTStxt}.asc'
            if not os.path.exists(targetRasterFileNameCuad1):
                print(f'clidpar-> Atencion: No se encuentra el fichero {targetRasterFileNameCuad1}')
                disponibleCuad1 = False
            if miSeccion == 'multiCuadrante':
                targetRasterFileNameCuad2 = f'E:/calendula\{miCuad2.upper()}\Mde/02mCell/{MDTSdir}\{miBloque}_{miYear2}_{MDTStxt}.asc'
                if not os.path.exists(targetRasterFileNameCuad2):
                    # print(f'clidpar-> Atencion: No se encuentra el fichero {targetRasterFileNameCuad2} -> Se continua con el siguiente.')
                    disponibleCuad2 = False

            if not disponibleCuad1 and not disponibleCuad2:
                continue
            if not disponibleCuad1 and (miSeccion == 'monoCuadrante' or miSeccion == 'bordeCyL'):
                continue

            if miSeccion == 'multiCuadrante':
                nombreCapaInputVectorCuad1 = f'cuadrante{miCuad1.upper()}.shp'
                nombreConPathCapaInputVectorCuad1 = os.path.join(MAINrutaCarto, 'MallasBloques', nombreCapaInputVectorCuad1)
                nombreCapaInputVectorCuad2 = f'cuadrante{miCuad2.upper()}.shp'
                nombreConPathCapaInputVectorCuad2 = os.path.join(MAINrutaCarto, 'MallasBloques', nombreCapaInputVectorCuad2)
            elif miSeccion == 'bordeCyL':
                nombreCapaInputVectorCuad1 = 'auton_ign_e25_etrs89.shp'
                nombreConPathCapaInputVectorCuad1 = os.path.join(MAINrutaCarto, 'MallasBloques', nombreCapaInputVectorCuad1)

            if miSeccion == 'multiCuadrante':
                if disponibleCuad1 and disponibleCuad2:
                    targetRasterFileNewCuad1 = os.path.basename(targetRasterFileNameCuad1).replace('.asc', f'_{miCuad1}.tiff')
                    targetRasterFileNewWithPathCuad1 = os.path.join(MAINrutaMdtAux, os.path.basename(targetRasterFileNewCuad1))
                    targetRasterFileNewCuad2 = targetRasterFileNameCuad2.replace('.asc', f'_{miCuad2}.tiff')
                    targetRasterFileNewWithPathCuad2 = os.path.join(MAINrutaMdtAux, os.path.basename(targetRasterFileNewCuad2))
                    targetRasterFileNewInteg = '{}02_{}'.format(MDTSprefijo, os.path.basename(targetRasterFileNameCuad1).replace(f'_{miYear1}', '').replace(f'_{MDTStxt}', '').replace('.asc', '.tiff'))
                    targetRasterFileNewWithPathInteg = os.path.join(MAINrutaMdt02, os.path.basename(targetRasterFileNewInteg))
                    if os.path.exists(targetRasterFileNewWithPathInteg):
                        print('\t-> Ya se ha generado', targetRasterFileNewWithPathInteg)
                        continue
                    else:
                        print('\t-> Se va a generar', targetRasterFileNewWithPathInteg)
                elif disponibleCuad1 and not disponibleCuad2:
                    targetRasterFileNewCuad1 = '{}02_{}'.format(MDTSprefijo, os.path.basename(targetRasterFileNameCuad1).replace(f'_{miYear1}', '').replace(f'_{MDTStxt}', '').replace('.asc', '.tiff'))
                    targetRasterFileNewWithPathCuad1 = os.path.join(MAINrutaMdt02, os.path.basename(targetRasterFileNewCuad1))
                    if os.path.exists(targetRasterFileNewWithPathCuad1):
                        print('\t-> Ya se ha generado', targetRasterFileNewWithPathCuad1)
                        continue
                    else:
                        print('\t-> Se va a generar', targetRasterFileNewWithPathCuad1)
                elif disponibleCuad2 and not disponibleCuad1:
                    targetRasterFileNewCuad2 = '{}02_{}'.format(MDTSprefijo, os.path.basename(targetRasterFileNameCuad2).replace(f'_{miYear2}', '').replace(f'_{MDTStxt}', '').replace('.asc', '.tiff'))
                    targetRasterFileNewWithPathCuad2 = os.path.join(MAINrutaMdt02, os.path.basename(targetRasterFileNewCuad2))
                    if os.path.exists(targetRasterFileNewWithPathCuad2):
                        print('\t-> Ya se ha generado', targetRasterFileNewWithPathCuad2)
                        continue
                    else:
                        print('\t-> Se va a generar', targetRasterFileNewWithPathCuad2)

            elif miSeccion == 'bordeCyL' or miSeccion == 'monoCuadrante':
                targetRasterFileNewCuad1 = '{}02_{}'.format(MDTSprefijo, os.path.basename(targetRasterFileNameCuad1).replace(f'_{miYear1}', '').replace(f'_{MDTStxt}', '').replace('.asc', '.tiff'))
                targetRasterFileNewWithPathCuad1 = os.path.join(MAINrutaMdt02, os.path.basename(targetRasterFileNewCuad1))
                if os.path.exists(targetRasterFileNewWithPathCuad1):
                    print('\t-> Ya se ha generado', targetRasterFileNewWithPathCuad1)
                    continue
                else:
                    print('\t-> Se va a generar', targetRasterFileNewWithPathCuad1)
                if miCuad2 != '':
                    print(f'\t-> ATENCION: el bloque {miBloque} no deberia tener miCuad2 ({miCuad2}) -> {miYearCuads}')
                    
            if miSeccion != 'monoCuadrante' and disponibleCuad1:
                try:
                    # Load as a gdal image to get geoTrans
                    targetRasterDatasetCuad1 = gdal.Open(targetRasterFileNameCuad1, gdalconst.GA_ReadOnly)
                    if targetRasterDatasetCuad1 is None:
                        print('\tclidpar-> Error abriendo raster', targetRasterFileNameCuad1)
                        return False
                    # Also load the source data as a gdalnumeric array
                    # srcArrayCuad1 = gdalnumeric.LoadFile(targetRasterFileNameCuad1)
                    print('\tclidpar-> Capa leida ok:', targetRasterFileNameCuad1)
                except:
                    print('clidpar-> ATENCION: error al leer {}'.format(targetRasterFileNameCuad1))
        
            if miSeccion == 'multiCuadrante' and disponibleCuad2:
                try:
                    # Load as a gdal image to get geoTrans
                    targetRasterDatasetCuad2 = gdal.Open(targetRasterFileNameCuad2, gdalconst.GA_ReadOnly)
                    if targetRasterDatasetCuad2 is None:
                        print('\tclidpar-> Error abriendo raster', targetRasterFileNameCuad2)
                        return False
                    # Also load the source data as a gdalnumeric array
                    # srcArrayCuad2 = gdalnumeric.LoadFile(targetRasterFileNameCuad2)
                    print('\tclidpar-> Capa leida ok:', targetRasterFileNameCuad2)
                except:
                    print('clidpar-> ATENCION: error al leer {}'.format(targetRasterFileNameCuad2))

            # geoTrans = targetRasterDatasetCuad1.GetGeoTransform()
            # cartoRasterOrigenX = geoTrans[0]
            # cartoRasterOrigenY = geoTrans[3]
            # cartoRasterPixelX = geoTrans[1]
            # cartoRasterPixelY = geoTrans[5]
            # cartoRasterNumCeldasX = targetRasterDatasetCuad1.RasterXSize
            # cartoRasterNumCeldasY = targetRasterDatasetCuad1.RasterYSize
            # print('cartoRasterOrigenX: {}'.format(cartoRasterOrigenX))
            # print('cartoRasterOrigenY: {}'.format(cartoRasterOrigenY))
            # print('cartoRasterPixelX: {}'.format(cartoRasterPixelX))
            # print('cartoRasterPixelY: {}'.format(cartoRasterPixelY))
            # print('cartoRasterNumCeldasX: {}'.format(cartoRasterNumCeldasX))
            # print('cartoRasterNumCeldasY: {}'.format(cartoRasterNumCeldasY))

            if miSeccion != 'monoCuadrante' and disponibleCuad1:
                print(f'Se crea el nuevo fichero raster1 ({miSeccion}): {targetRasterFileNewWithPathCuad1}')
                dsClipCuad1 = gdal.Warp(
                    targetRasterFileNewWithPathCuad1,
                    targetRasterDatasetCuad1,
                    dstSRS='EPSG:25830',
                    cutlineDSName = nombreConPathCapaInputVectorCuad1,
                    cropToCutline = False, # requiere que el source tenga SRS
                    dstNodata = np.nan,
                    # outputType=gdal.GDT_Float32,
                    # xRes=2, yRes=2
                )
            if miSeccion == 'multiCuadrante' and disponibleCuad2:
                print('\t-> Se crea el nuevo fichero raster1 ({miSeccion}): {targetRasterFileNewWithPathCuad2}')
                dsClipCuad2 = gdal.Warp(
                    targetRasterFileNewWithPathCuad2,
                    targetRasterDatasetCuad2,
                    dstSRS='EPSG:25830',
                    cutlineDSName = nombreConPathCapaInputVectorCuad2,
                    cropToCutline = False, # requiere que el source tenga SRS
                    dstNodata = np.nan,
                    # outputType=gdal.GDT_Float32,
                    # xRes=2, yRes=2
                )

            # Si miSeccion == 'bordeCyL' o miSeccion == 'multiCuadrante' y falta el bloque de uno de los cuadrantes
            # El bloque recortado (incompleto) ya se ha creado en MAINrutaMdt02, en vez de MAINrutaMdtAux
            if miSeccion == 'multiCuadrante' and disponibleCuad1 and disponibleCuad2:
                listaFiles = [targetRasterFileNewWithPathCuad1, targetRasterFileNewWithPathCuad2]
                g = gdal.Warp(
                    targetRasterFileNewWithPathInteg, listaFiles, format="GTiff",
                    options=["COMPRESS=LZW", "TILED=YES"]
                )
            if miSeccion == 'monoCuadrante' and disponibleCuad1:
                listaFiles = [targetRasterFileNameCuad1]
                g = gdal.Warp(
                    targetRasterFileNewWithPathCuad1, listaFiles, format="GTiff",
                    options=["COMPRESS=LZW", "TILED=YES"]
                )

            nBloqueProcesado += 1


# ==============================================================================
def integrarFicherosAscTipoFich(
    LCLlistaDasoVarsFileTypes,
    AUX_numTipoFichero,
    LCLrutaAscRaizFull,
    LCLexplorarNivelDeSubdirs,
    miOutputDir,
    PAR_ambitoTiffNuevo,
    PAR_subLoteTiff,
    LCLoutputDriverName,
    nBandasOutput,
    outputGdalDatatype,
    outputNpDatatype,
    noDataPrevisto,
    noDataProvisional,
    noDataDestinoTiff,
    outputOptions,
):
    txtTipoFichero = LCLlistaDasoVarsFileTypes[AUX_numTipoFichero]
    if PAR_ambitoTiffNuevo t == 'ConvertirSoloUnFicheroASC':
        # nTipoOutput == 9
        print('Se procesa un unico fichero:')
        LCLrutaAscRaizFull = 'D:/cartolidout2/Ajustes/Final'
        inputAscName0 = '286_4524_2019_SubCeldasMdfCotaPlus.asc'
        LCLlistaDasoVarsFileTypes = [inputAscName0[14:-4]]
        AUX_numTipoFichero = 0
        print('\nFichero de entrada: %s' % (inputAscName0))
        mergedUniCellAllDasoVarsFileNameSinPath = inputAscName0.replace('.asc', '.tif')
        infiles = [[LCLrutaAscRaizFull, inputAscName0]]
        # Creo un tif con un solo fichero de entrada
        cargarRasterEnMemoria = True
        clidraster.crearRasterTiff(
            # LCLrutaAscRaizFull,
            [infiles],
            miOutputDir,
            mergedUniCellAllDasoVarsFileNameSinPath,
            nBandasOutput,
            LCLlistaDasoVarsFileTypes,
            LCLlistaDasoVarsFileTypes, # Redundante porque no lo uso con mergeBloques<>

            PAR_rasterPixelSize=0,
            PAR_outRasterDriver=LCLoutputDriverName,
            PAR_noDataTiffProvi=noDataProvisional,
            PAR_noDataMergeTiff=noDataDestinoTiff,
            outputOptions=outputOptions,
            nInputVars=1,
            outputGdalDatatype=outputGdalDatatype,
            outputNpDatatype=outputNpDatatype,

            LCLconvertirAlt=GLBLconvertirAlt,
            integrarFicherosAsc=True,
            AUX_numTipoFichero=AUX_numTipoFichero,
            PAR_ambitoTiffNuevo=PAR_ambitoTiffNuevo,
            PAR_subLoteTiff=PAR_subLoteTiff,
        )
        return

    rasterEnElQueSeEscribe = None
    rasterQueSeUsaComoDeferencia = None

    if PAR_ambitoTiffNuevo == 'rasterDest_CyL':
        # nTipoOutput == 6:
        # Integrar los ficheros asc en un tif creado previamente
        LCLexplorarNivelDeSubdirs = 0
        rasterEnElQueSeEscribe = '{}_{}.tif'.format(txtTipoFichero, PAR_ambitoTiffNuevo)
        rasterQueSeUsaComoDeferencia = rasterEnElQueSeEscribe
        mergedUniCellAllDasoVarsFileNameSinPath = rasterEnElQueSeEscribe
        selec = input('\nFichero destino: (por defecto: %s) ' % mergedUniCellAllDasoVarsFileNameSinPath)
        if selec != '':
            mergedUniCellAllDasoVarsFileNameSinPath = selec
        print('Los ficheros asc se integran en el fichero', mergedUniCellAllDasoVarsFileNameSinPath)
    elif PAR_ambitoTiffNuevo == 'rasterRefe_CyL':
        # nTipoOutput == 7:
        # Integrar los ficheros asc en un tif igual a uno de referencia (mismas dimensiones y resolucion)
        # Si finalmente no lo utilizo, quitar esto
        LCLexplorarNivelDeSubdirs = 0
        rasterQueSeUsaComoDeferencia = 'O:/Sigmena/usuarios/COMUNES/Bengoa/SIC/ClasificaCubiertas/ITACYL_2015_12/clasificacion_2015_diciembre_CyL.img'
        mergedUniCellAllDasoVarsFileNameSinPath = '{}_{}.tif'.format(txtTipoFichero, PAR_ambitoTiffNuevo)
        selec = input('\nFichero de referencia: (por defecto: %s) ' % rasterQueSeUsaComoDeferencia)
        if selec != '':
            rasterQueSeUsaComoDeferencia = selec
        print('Los ficheros asc se integran en un tif igual al fichero', rasterQueSeUsaComoDeferencia)
        selec = input('\nFichero destino: (por defecto: %s) ' % mergedUniCellAllDasoVarsFileNameSinPath)
        if selec != '':
            mergedUniCellAllDasoVarsFileNameSinPath = selec

    listaDirsExcluidos = ['patron']
    dirIterator = iter(os.walk(LCLrutaAscRaizFull))
    # dirpath, dirnames, filenames = next(dirIterator)
    print('Directorios excluidos:')
    for dirExcluido in listaDirsExcluidos:
        print('\t', os.path.join(LCLrutaAscRaizFull, dirExcluido))
    dirpathPrevio = os.path.abspath(os.path.join(LCLrutaAscRaizFull, '..'))
    # dirpathPrevio = LCLrutaAscRaizFull
    for dirpathOk, dirnames, filenames in dirIterator:  # get second element onwards
        dirpathPadre1 = os.path.abspath(os.path.join(dirpathOk, '..'))
        # dirpathPadre1 = dirpathOk
        if dirpathOk.endswith('aIntegraTiff'):
            continue

        subDirExplorado = dirpathOk.replace(LCLrutaAscRaizFull, '')
        if dirpathOk == LCLrutaAscRaizFull:
            nivelDeSubdir = 0
        elif not '/' in subDirExplorado and not '\\' in subDirExplorado:
            nivelDeSubdir = 0
        else:
            nivelDeSubdir = subDirExplorado.count('/') + subDirExplorado.count('\\')
        print('\nnivelExplorado:  {}'.format(nivelDeSubdir))
        print('\tdirpathOk:       {}'.format(dirpathOk))
        print('\tdirnames:        {}'.format(dirnames))
        print('\tnumFiles:        {}'.format(len(filenames)))
        print('\tdirpathPrevio: {}'.format(dirpathPrevio))
        print('\tdirpathPadre1:   {}'.format(dirpathPadre1))
        dirpathPrevio = dirpathPadre1
        if nivelDeSubdir > LCLexplorarNivelDeSubdirs:
            if GLO.GLBLverbose:
                print('\nSe ha alcanzado el nivel de directorios maximo')
            continue
        infiles = []
        excluirDirectorio = False
        for dirExcluido in listaDirsExcluidos:
            if dirpathOk == os.path.join(LCLrutaAscRaizFull, dirExcluido):
                excluirDirectorio = True
                break
        if excluirDirectorio:
            print('\nDirectorio excluido:', dirpathOk)
            continue
        # print('\tNumero de ficheros en el directorio:', len(filenames))
        if len(filenames) == 0:
            print('\t-> No hay ficheros; se pasa al siguiente directorio')
            continue
        print('Buscando ficheros tipo {}... '.format(txtTipoFichero), end=' -> ')
        # filenamesSeleccionados = [filename for filename in filenames if filename[14:-4].upper() == txtTipoFichero.upper() and filename[-4:].upper() == '.ASC']
        idInputDir = os.path.basename(dirpathOk)
        filenamesSeleccionados = [filename for filename in filenames if txtTipoFichero.upper() in filename.upper() and filename[-4:].upper() == '.ASC']
        print('localizados: {} ficheros'.format(len(filenamesSeleccionados)))
        if filenamesSeleccionados:
            print('\n{:_^80}'.format(''))
            print('\nEncontrados {} ficheros. Primeros 5 files:'.format(len(filenamesSeleccionados)))
            for nFile, pathAndfilename in enumerate(filenamesSeleccionados[:5]):
                print('\t\t', nFile, pathAndfilename)
            for filenameSel in filenamesSeleccionados:
                infiles.append([dirpathOk, filenameSel])
        else:
            print('\t-> No se ha localizado ningun fichero con ese patron:', txtTipoFichero)
        if len(infiles) == 0:
            print('\t-> Se pasa al siguiente directotrio')
            continue
        # Cambio el outputDir general por uno especifico de directorio
        mergedUniCellAllDasoVarsFileNameSinPath = '{}_{}_{}.tif'.format(ARGSdasoVar, idInputDir, PAR_ambitoTiffNuevo)
        print('Fichero de salida:\n\t{}'.format(mergedUniCellAllDasoVarsFileNameSinPath))
        miOutputDir = os.path.join(dirpathOk, 'aIntegraTiff/')
        if not os.path.exists(miOutputDir):
            print('No existe directorio %s -> Se crea automaticamente' % (miOutputDir))
            try:
                os.makedirs(miOutputDir)
            except:
                print('No se ha podido crear el directorio %s' % (miOutputDir))
                sys.exit(0)
        else:
            print('El directorio %s ya existe -> Se agregan los tif a este directorio' % (miOutputDir))

        # Si LCLexplorarNivelDeSubdirs = 0, por aqui solo pasa una vez,
        #   tras recopilar los asc files en el directorio LCLrutaAscRaizFull
        clidraster.crearRasterTiff(
            # LCLrutaAscRaizFull,
            [infiles],
            miOutputDir,
            mergedUniCellAllDasoVarsFileNameSinPath,
            nBandasOutput,
            LCLlistaDasoVarsFileTypes,
            LCLlistaDasoVarsFileTypes,

            PAR_rasterPixelSize=0,
            PAR_outRasterDriver=LCLoutputDriverName,
            PAR_noDataTiffProvi=noDataProvisional,
            PAR_noDataMergeTiff=noDataDestinoTiff,
            outputOptions=outputOptions,
            nInputVars=1,
            outputGdalDatatype=outputGdalDatatype,
            outputNpDatatype=outputNpDatatype,

            rasterQueSeUsaComoDeferencia=rasterQueSeUsaComoDeferencia,
            rasterEnElQueSeEscribe=rasterEnElQueSeEscribe,
            LCLconvertirAlt=GLBLconvertirAlt,
            integrarFicherosAsc=True,
            AUX_numTipoFichero=AUX_numTipoFichero,
            PAR_ambitoTiffNuevo=PAR_ambitoTiffNuevo,
            PAR_subLoteTiff=PAR_subLoteTiff,
        )


# ==============================================================================
def renombrarFicheros():
    # miInputDir = 'E:/calendula/mdt02_multiCuadrante'
    # miInputDir = 'E:/calendula/mdt02_monoCuadrante'
    # miInputDir = 'E:/calendula/mdt02_bordeCyL'
    # miInputDir = 'E:/calendula/mds02_bordeCyL'
    # miInputDir = 'E:/calendula/mds02_multiCuadrante'
    miInputDir = 'E:/calendula/mds02_monoCuadrante'
    print('\nclidpar-> Recorriendo la ruta: {}'.format(miInputDir))
    # tipoFichero = '_SubCeldasMdkCotaItp'
    tipoFichero = '_SubCeldasMdcCotaMax'
    miExtension = 'tiff'
    miYear1 = '2017'
    miYear2 = '2019'
    dirIterator = iter(os.walk(miInputDir))
    # dirpath, dirnames, filenames = next(dirIterator)
    for dirpath, dirnames, filenames in dirIterator:
        print('\nNumero de ficheros en', dirpath, '->', len(filenames))
        print('Buscando ficheros tipo {}... '.format(tipoFichero), end=' -> ')
        filenamesSeleccionados = [filename for filename in filenames if filename[-25:-5].upper() == tipoFichero.upper() and filename[-len(miExtension):].upper() == miExtension.upper()]
        print('localizados: {} ficheros'.format(tipoFichero, len(filenamesSeleccionados)))
        if filenamesSeleccionados:
            for nFile, filenameSel in enumerate(filenamesSeleccionados):
                filenameNew = filenameSel.replace(f'_{miYear1}', '').replace(f'_{miYear2}', '').replace(f'{tipoFichero}', '')
                print('\t\t', nFile, os.path.join(dirpath, filenameSel), '->', filenameNew)
                os.rename(os.path.join(dirpath, filenameSel), os.path.join(dirpath, filenameNew))



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
    # ==========================================================================
    # Valorar si uso el modulo csv de miPandas
    #     csv.reader(entrada, delimiter = ',')
    # ==========================================================================

    # Esta lista incluye un unico tipoDeFichero y solo se usa en mergeBloquesASC<>
    # La lista de tipos de fichero que se usa en creaDasoLayer<> incluye varios 
    # tipos de ficheros/variables (parametro de configuracion GLBLlistaDasoVarsFileTypes)

    # Este argumento se usa con un solo valor y solo para mergeBloquesASC<>
    LCLlistaDasoVarsFileTypes = [ARGStiposDeFichero]
    menuPrincipal(
        ARGSopcionElegida,
        ARGSrutaAscRaizBase,
        ARGSsubPath,
        ARGSexplorarNivelDeSubdirs,
        LCLlistaDasoVarsFileTypes,
        # ARGScodCuadrante,
    )
    # ==========================================================================
    print('\nEjecucion terminada ok.')




'''
    # ==========================================================================
    # ====================== Argumentos en linea de comandos ===================
    # ==========================================================================
    # AVISO: Los argumentos en linea de comandos prevalecen sobre los parametros de configuracion:
    # -o ARGSopcionElegida          => GLO.accionPrincipalPorDefecto    -> Para todas las funciones
    # -p ARGSrutaAscRaizBase        => GLO.rutaAscRaizBasePorDefecto            -> Para mergeBloques y creaDasoLayer
    # -s ARGSsubPath                => GLO.subPathPorDefecto                -> Solo para mergeBloques
    # -f ARGStiposDeFichero         => GLO.tipoDeFicheroPorDefecto          -> Solo para mergeBloques
    # -d ARGSdasoVar                => GLO.dasoVarPorDefecto                -> Solo para mergeBloques
    # -a ARGSconvertirAltAdm8Bit    => GLO.convertirAltPorDefecto           -> Solo para mergeBloques
    # -A ARGSconvertirAltAcm16Bit   => GLO.convertirAltPorDefecto           -> Solo para mergeBloques
    # -t ARGStipoOutput             => GLO.tipoOutputPorDefecto             -> Solo para mergeBloques
    # -u ARGSsubLoteTiff            => GLO.GLBLsubLoteTiffPorDefecto        -> Solo para mergeBloques
    # -l ARGSexplorarNivelDeSubdirs => GLO.GLBLexplorarNivelDeSubdirs       -> Para mergeBloques y creaDasoLayer
    # ==========================================================================
    if len(sys.argv) > 1 and sys.argv[1] != 'idProceso':
        try:
            ARGSopcionElegida = int(sys.argv[1])
        except:
            print('qlidtwins-> ARGSopcionElegida error')
            ARGSopcionElegida = 0
    else:
        if MAIN_ENTORNO == 'calendula':
            ARGSopcionElegida = 1 # 1.- Unir ficheros asc (2x2 km) en una sola capa (merge).
            # ARGSopcionElegida = 2 # 2.- Cortar ficheros asc (2x2 km) compartidos por cuadrantes y unir en un solo fichero (merge).
        else:
            ARGSopcionElegida = GLO.GLBLaccionPrincipalPorDefecto
    
    if len(sys.argv) > 2 and sys.argv[2] != 'idProceso' and sys.argv[1] != 'idProceso':
        ARGSrutaAscRaizBase = sys.argv[2]
    else:
        ARGSrutaAscRaizBase = GLO.rutaAscRaizBasePorDefecto
    
    if len(sys.argv) > 3 and sys.argv[3] != 'idProceso' and sys.argv[2] != 'idProceso':
        ARGSsubPath = sys.argv[3]
    else:
        ARGSsubPath = GLO.subPathPorDefecto
    
    # Este argumento se usa en linea de comandos con un solo valor y solo para mergeBloquesASC<>
    if len(sys.argv) > 4 and sys.argv[4] != 'idProceso' and sys.argv[3] != 'idProceso':
        ARGStiposDeFichero = sys.argv[4]
    else:
        ARGStiposDeFichero = GLO.tipoDeFicheroPorDefecto
    
    if len(sys.argv) > 5 and sys.argv[5] != 'idProceso' and sys.argv[4] != 'idProceso':
        ARGSdasoVar = sys.argv[5]
    else:
        ARGSdasoVar = GLO.dasoVarPorDefecto
    
    if len(sys.argv) > 6 and sys.argv[6] != 'idProceso' and sys.argv[5] != 'idProceso':
        if sys.argv[6] == '1':
            ARGSconvertirAltAdm8Bit = True
            ARGSconvertirAltAcm16Bit = False
        elif sys.argv[6] == '2' or sys.argv[6] == 'True' or (sys.argv[6]).upper() == 'SI':
            ARGSconvertirAltAdm8Bit = False
            ARGSconvertirAltAcm16Bit = True
        else:
            ARGSconvertirAltAdm8Bit = False
            ARGSconvertirAltAcm16Bit = False
    else:
        ARGSconvertirAltAdm8Bit = GLO.convertirAltPorDefecto
        ARGSconvertirAltAcm16Bit = GLO.convertirAltPorDefecto
    if (ARGSdasoVar.lower()).startswith('alt') and (ARGSconvertirAltAdm8Bit or ARGSconvertirAltAcm16Bit):
        GLBLconvertirAlt = True
    else:
        GLBLconvertirAlt = False
    
    if len(sys.argv) > 7 and sys.argv[7] != 'idProceso' and sys.argv[6] != 'idProceso':
        ARGStipoOutput = sys.argv[7]
    else:
        ARGStipoOutput = GLO.tipoOutputPorDefecto
    # ARGSsubLoteTiff tiene dos posibles significados:
    #  Si ARGStipoOutput == 4:
    #    Cuadrante de CyL: 
    #    Valores: CE, NE, NW, SE, SW, XX, LE
    #  Si ARGStipoOutput == 5:
    #    SubLote del lote de asc, que suele ser un cuadrante
    #    Valores: NE, NW, SE, SW
    
    if len(sys.argv) > 8 and sys.argv[8] != 'idProceso' and sys.argv[7] != 'idProceso':
        ARGSsubLoteTiff = sys.argv[8]
    else:
        ARGSsubLoteTiff = GLO.GLBLsubLoteTiffPorDefecto
    
    if len(sys.argv) > 9 and sys.argv[9] != 'idProceso' and sys.argv[8] != 'idProceso':
        try:
            ARGSexplorarNivelDeSubdirs = int(sys.argv[9])
            if ARGSexplorarNivelDeSubdirs > 5:
                ARGSexplorarNivelDeSubdirs = 5
                print('\nqlidtwins-> AVISO: no esta implementada la exploracion de mas de 4 niveles de subdirectorios.\n')
        except:
            ARGSexplorarNivelDeSubdirs = GLO.explorarNivelDeSubdirs
    else:
        ARGSexplorarNivelDeSubdirs = GLO.explorarNivelDeSubdirs
    # ==========================================================================
'''

'''
# ==========================================================================
# ================= Parametrosde configuracion por defecto =================
# ======================== GRAL_configDictPorDefecto =======================
# ==========================================================================
# Dict de parametrosde configuracion con valores por defecto. Estructura:
#     GRAL_configDict[nombreParametroDeConfiguracion] = [valorParametro, grupoParametros, tipoVariable, descripcionParametro]
GRAL_configDictPorDefecto = {
    'GLBLverboseAll': [GRAL_verbose, 'General', 'bool', 'Mostrar info de ejecucion en consola'],

    'GLBLejecucionInteractiva': [0, 'General', 'bool', 'Preguntar en tiempo de ejecucion para confirmar opciones'],
    'GLBLaccionPrincipalPorDefecto': [4, 'General', 'int', 'Opcion por defecto en menu principal'],

    # 'GLBLmetrosCelda': [10, 'General', 'uint8', 'Lado del pixel dasometrico en metros'],
    # 'METROS_PIXEL': [10, 'General', 'uint8', 'Lado del pixel dasometrico en metros (pte ver diferencia con GLBLmetrosCelda)'],

    # 'GLBLrutaAscRaizParaMergeAscCalendula': ['/scratch/jcyl_spi_1/jcyl_spi_1_1', 'General', 'uint8', 'Ruta de los ASC en Calendula'],
    'GLBLrutaAscRaizParaMergeAscCalendula': ['/LUSTRE/SCRATCH/jcyl_spi_1/jcyl_spi_1_1', 'General', 'str', 'Ruta de los ASC en Calendula'],
    'GLBLrutaAscRaizParaMergeAscJCyL': ['K:/calendula/NW', 'General', 'str', 'Ruta de los ASC en JCyL'],
    'GLBLrutaAscRaizParaMergeAscCasa': ['D:/_clid', 'General', 'str', 'Ruta de los ASC en Casa'],

    'GLBLsubdirOutputParaMergeAsc': ['aIntegraTiff', 'General', 'str', 'Subdirectorio de rutaAscRaizBase donde se guardan los resultados'],

    'subPathPorDefecto': ['AltSobreTerreno/10mCell/Alt95SobreMdk', 'Merge', 'str', 'SubPath de ficheros ASC para el Merge'],
    'tipoDeFicheroPorDefecto': ['CeldasAlt95SobreMdk', 'Merge', 'str', 'Tipo de fichero ASC para el Merge'],

    'GLBLambitoDelOutputTiff': ['LoteAsc', 'Merge', 'str', 'Principalmente para merge: ambito geografico del nuevo raster creado (uno predeterminado o el correspondiente a los ASC)'],
    'GLBLsubLoteTiffPorDefecto': ['', 'Merge', 'str', 'SubLote principalmente para el Merge (en dasolidar es residual)'],

    # 'subPathPorDefecto': ['AltSobreTerreno/02mCell/AltMaxSobreMdk', 'Merge', 'str', 'SubPath de ficheros ASC para el Merge'],
    # 'tipoDeFicheroPorDefecto': ['SubCeldasAltMaxSobreMdk', 'Merge', 'str', 'Tipo de fichero ASC para el Merge'],
    # 'dasoVarPorDefecto': ['AltMax02', 'Merge', 'str', 'Nombre de la variable para el Merge'],
    #
    # 'subPathPorDefecto': ['cartolidout_NW_CREAR_LAZ_LeonRobledales/Fcc/10mCell', 'Merge', 'str', 'Ruta de los ASC en JCyL'],
    # 'tipoDeFicheroPorDefecto': ['FccRptoAmdk_PrimeRets_MasDe0300', 'Merge', 'str', 'Ruta de los ASC en JCyL'],
    # 'dasoVarPorDefecto': ['Fcc', 'Merge', 'str', 'Ruta de los ASC en JCyL'],
    #
    # 'subPathPorDefecto': ['cartolidout_NW_CREAR_LAZ_LeonRobledales/Fcc/10mCell', 'Merge', 'str', 'Ruta de los ASC en JCyL'],
    # 'tipoDeFicheroPorDefecto': ['FccRptoAmdk_PrimeRets_MasDe', 'Merge', 'str', 'Ruta de los ASC en JCyL'],
    # 'dasoVarPorDefecto': ['Fcc', 'Merge', 'str', 'Ruta de los ASC en JCyL'],
    #
    # 'subPathPorDefecto': ['cartolidout_NW_CREAR_LAZ_LeonRobledales/Fcc/10mCell', 'Merge', 'str', 'Ruta de los ASC en JCyL'],
    # 'tipoDeFicheroPorDefecto': ['FccRptoAmdb_PrimeRets_MasDe', 'Merge', 'str', 'Ruta de los ASC en JCyL'],
    # 'dasoVarPorDefecto': ['Fcc', 'Merge', 'str', 'Ruta de los ASC en JCyL'],
    #
    # 'subPathPorDefecto': ['cartolidout_NW_CREAR_LAZ_LeonRobledales/Fcc/10mCell', 'Merge', 'str', 'Ruta de los ASC en JCyL'],
    # 'tipoDeFicheroPorDefecto': ['FccRptoAmdk_TodosRets_', 'Merge', 'str', 'Ruta de los ASC en JCyL'],
    # 'dasoVarPorDefecto': ['Fcc', 'Merge', 'str', 'Ruta de los ASC en JCyL'],
    #
    # 'subPathPorDefecto': ['cartolidout_NW_CREAR_LAZ_LeonRobledales/Fcc/10mCell/FccRangos', 'Merge', 'str', 'Ruta de los ASC en JCyL'],
    # 'tipoDeFicheroPorDefecto': ['FccRptoAmdk_TodosRets_', 'Merge', 'str', 'Ruta de los ASC en JCyL'],
    # 'dasoVarPorDefecto': ['Fcc', 'Merge', 'str', 'Ruta de los ASC en JCyL'],
    #
    # 'subPathPorDefecto': ['cartolidout_NW_CREAR_LAZ_LeonRobledales/Mde/02mCell/Klass', 'Merge', 'str', 'Ruta de los ASC en JCyL'],
    # 'tipoDeFicheroPorDefecto': ['SubCeldasMdkCotaItp', 'Merge', 'str', 'Ruta de los ASC en JCyL'],
    # 'dasoVarPorDefecto': ['Mdt', 'Merge', 'str', 'Ruta de los ASC en JCyL'],
    #
    # 'subPathPorDefecto': ['cartolidout_NW_CREAR_LAZ_LeonRobledales/Mde/02mCell/Cielo', 'Merge', 'str', 'Ruta de los ASC en JCyL'],
    # 'tipoDeFicheroPorDefecto': ['SubCeldasMdcCotaMax', 'Merge', 'str', 'Ruta de los ASC en JCyL'],
    # 'dasoVarPorDefecto': ['Mds', 'Merge', 'str', 'Ruta de los ASC en JCyL'],
    #
    # 'subPathPorDefecto': ['cartolidout_NW_CREAR_LAZ_LeonRobledales/HiperCubo/02mCell/Rugosidad', 'Merge', 'str', 'Ruta de los ASC en JCyL'],
    # 'tipoDeFicheroPorDefecto': ['SubCeldasRugosidadMegasInterCeldillas', 'Merge', 'str', 'Ruta de los ASC en JCyL'],
    # 'dasoVarPorDefecto': ['RugMegas', 'Merge', 'str', 'Ruta de los ASC en JCyL'],
    #
    # 'subPathPorDefecto': ['cartolidout_NW_CREAR_LAZ_LeonRobledales/HiperCubo/02mCell/Rugosidad', 'Merge', 'str', 'Ruta de los ASC en JCyL'],
    # 'tipoDeFicheroPorDefecto': ['SubCeldasRugosidadMicroInterCeldillas', 'Merge', 'str', 'Ruta de los ASC en JCyL'],
    # 'dasoVarPorDefecto': ['RugMicro', 'Merge', 'str', 'Ruta de los ASC en JCyL'],
    #
    # 'subPathPorDefecto': ['cartolidout_NW_CREAR_LAZ_LeonRobledales/HiperCubo/02mCell/Rugosidad', 'Merge', 'str', 'Ruta de los ASC en JCyL'],
    # 'tipoDeFicheroPorDefecto': ['SubCeldasRugosidadMesosInterCeldillas', 'Merge', 'str', 'Ruta de los ASC en JCyL'],
    # 'dasoVarPorDefecto': ['RugMesos', 'Merge', 'str', 'Ruta de los ASC en JCyL'],
    #
    # 'subPathPorDefecto': ['cartolidout_NW_CREAR_LAZ_LeonRobledales/HiperCubo/02mCell/Rugosidad', 'Merge', 'str', 'Ruta de los ASC en JCyL'],
    # 'tipoDeFicheroPorDefecto': ['SubCeldasRugosidadMacroInterCeldillas', 'Merge', 'str', 'Ruta de los ASC en JCyL'],
    # 'dasoVarPorDefecto': ['RugMacro', 'Merge', 'str', 'Ruta de los ASC en JCyL'],
    #
    # 'subPathPorDefecto': ['cartolidout_NW_CREAR_LAZ_LeonRobledales/AltSobreTerreno/02mCell/AltMaxSobreMdk', 'Merge', 'str', 'Ruta de los ASC en JCyL'],
    # 'tipoDeFicheroPorDefecto': ['SubCeldasAltMaxSobreMdk', 'Merge', 'str', 'Ruta de los ASC en JCyL'],
    # 'dasoVarPorDefecto': ['AltMx', 'Merge', 'str', 'Ruta de los ASC en JCyL'],
    #
    # 'subPathPorDefecto': ['cartolidout_NW_CREAR_LAZ_LeonRobledales/NumPtos/10mCell/SinSolapeRt1', 'Merge', 'str', 'Ruta de los ASC en JCyL'],
    # 'tipoDeFicheroPorDefecto': ['numPuntosPrimRetSinSolape', 'Merge', 'str', 'Ruta de los ASC en JCyL'],
    # 'dasoVarPorDefecto': ['Npt', 'Merge', 'str', 'Ruta de los ASC en JCyL'],
    #
    # 'subPathPorDefecto': ['cartolidout_NW_CREAR_LAZ_LeonRobledales/RGBI/02mCell/NDVI', 'Merge', 'str', 'Ruta de los ASC en JCyL'],
    # 'tipoDeFicheroPorDefecto': ['SubCeldasNDVI', 'Merge', 'str', 'Ruta de los ASC en JCyL'],
    # 'dasoVarPorDefecto': ['Ndv', 'Merge', 'str', 'Ruta de los ASC en JCyL'],
    #
    # 'subPathPorDefecto': ['cartolidout_NW_CREAR_LAZ_LeonRobledales/Pasadas/DifEntrePasadas', 'Merge', 'str', 'Ruta de los ASC en JCyL'],
    # 'tipoDeFicheroPorDefecto': ['zMediaPtsTodosDiferenciaEntrePasadas', 'Merge', 'str', 'Ruta de los ASC en JCyL'],
    # 'dasoVarPorDefecto': ['AjustePasadas', 'Merge', 'str', 'Ruta de los ASC en JCyL'],
    #

    'dasoVarPorDefecto': ['Alt95', 'Merge', 'str', 'Nombre de la variable para el Merge'],

    'convertirAltPorDefecto': ['', 'Merge', 'str', 'Convertir alturas de metros a cm para el Merge'],
    'tipoOutputPorDefecto': ['', 'Merge', 'str', 'Tipo de variable de salida para el Merge'],
}
# ==========================================================================
'''
