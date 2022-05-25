#!/usr/bin/python
# -*- coding: UTF-8 -*-
'''
Module included in cartolidar project 
cartolidar: tools for Lidar processing focused on Spanish PNOA datasets

clidtwins_config (ancillary to clidtwins) is used for clidtwins configuration.
It creates global object GLO with configuration parameters as properties.
GLO can be imported from clidtwins module to read configuration parameters.
clidtwins_config requires clidconfig module (clidax package of cartolidar).

clidtwins provides classes and functions that can be used to search for
areas similar to a reference one in terms of dasometric Lidar variables (DLVs).
DLVs (Daso Lidar Vars): vars that characterize forest or land cover structure.

@author:     Jose Bengoa
@copyright:  2022 @clid
@license:    GNU General Public License v3 (GPLv3)
@contact:    cartolidar@gmail.com
'''

import os
import sys
import pathlib
from configparser import RawConfigParser
import unicodedata
try:
    import psutil
    psutilOk = True
except:
    psutilOk = False


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
    print(f'clidtwins_config-> __name__:     <{__name__}>')
    print(f'clidtwins_config-> __package__ : <{__package__ }>')
# ==============================================================================

# Acceso a un modulo del package clidax
try:
    from cartolidar.clidax import clidconfig
except:
    if __verbose__ > 2:
        print(f'qlidtwins-> Se importa clidconfig desde clidtwins_config del directorio local {os.getcwd()}/clidtools')
        print('\tNo hay vesion de cartolidar instalada en site-packages.')
    from clidax import clidconfig


# ==============================================================================
# El idProceso sirve para dar nombres unicos a los ficheros de configracion y
# asi poder lanzar trabajos paralelos con distintas configuraciones.
# Sin embargo, qlidtwins no esta pensada para lanzar trabajos en paralelo.
# Mantengo el idProceso por si acaso
if '--idProceso' in sys.argv and len(sys.argv) > sys.argv.index('--idProceso') + 1:
    MAIN_idProceso = sys.argv[sys.argv.index('--idProceso') + 1]
else:
    # MAIN_idProceso = random.randint(1, 999998)
    MAIN_idProceso = 0
    sys.argv.append('--idProceso')
    sys.argv.append(MAIN_idProceso)
# ==============================================================================


# ==============================================================================
def infoUsuario():
    if psutilOk:
        try:
            USERusuario = psutil.users()[0].name
        except:
            USERusuario = psutil.users()
        if not isinstance(USERusuario, str) or USERusuario == '':
            USERusuario = 'PC1'
        return USERusuario
    else:
        return 'SinUsuario'


# ==============================================================================
def leerConfig(LOCL_configDictPorDefecto, LOCL_configFileNameCfg, LOCL_verbose=False, LOCL_verboseAll=False):
    if LOCL_verbose:
        print('\n{:_^80}'.format(''))
        print('clidtwins_config-> Fichero de configuracion:  {}'.format(LOCL_configFileNameCfg))
    # ==========================================================================
    if not os.path.exists(LOCL_configFileNameCfg):
        if LOCL_verbose:
            print('\t  clidtwins_config-> Fichero no encontrado: se crea con valores por defecto')
        # En ausencia de fichero de configuracion, uso valores por defecto y los guardo en un nuevo fichero cfg
        config = RawConfigParser()
        config.optionxform = str  # Avoid change to lowercase
    
        for nombreParametroDeConfiguracion in LOCL_configDictPorDefecto.keys():
            grupoParametroConfiguracion = LOCL_configDictPorDefecto[nombreParametroDeConfiguracion][1]
            if not grupoParametroConfiguracion in config.sections():
                if LOCL_verboseAll:
                    print('\t\tclidtwins_config-> grupoParametros nuevo:', grupoParametroConfiguracion)
                config.add_section(grupoParametroConfiguracion)
        # Puedo agregar otras secciones:
        config.add_section('Custom')
    
        if LOCL_verboseAll:
            print('\t\tclidtwins_config-> Lista de parametros de configuracion por defecto:')
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
            if LOCL_verboseAll:
                print('\t\t\t-> {}: {} (tipo {})-> {}'.format(nombreParametroDeConfiguracion, valorParametroConfiguracion, tipoParametroConfiguracion, descripcionParametroConfiguracion))
    
        # try:
        if True:
            with open(LOCL_configFileNameCfg, mode='w+') as configfile:
                config.write(configfile)
        # except:
        #     print('\nclidtwins_config-> ATENCION, revisar caracteres no admitidos en el fichero de configuracion:', LOCL_configFileNameCfg)
        #     print('\tEjemplos: vocales acentuadas, ennes, cedillas, flecha dchea (->), etc.')
    
    # Asigno los parametros de configuracion a varaible globales:
    config = RawConfigParser()
    config.optionxform = str  # Avoid change to lowercase
    
    
    # Confirmo que se ha creado correctamente el fichero de configuracion
    if not os.path.exists(LOCL_configFileNameCfg):
        print('\nclidtwins_config-> ATENCION: fichero de configuracion no encontrado ni creado:', LOCL_configFileNameCfg)
        print('\t-> Revisar derechos de escritura en la ruta en la que esta la aplicacion')
        sys.exit(0)
    
    try:
        LOCL_configDict = {}
        config.read(LOCL_configFileNameCfg)
        if LOCL_verbose:
            print('\t-> clidtwins_config-> Parametros de configuracion (guardados en {}):'.format(LOCL_configFileNameCfg))
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
                if LOCL_verboseAll:
                    print('\t\t-> parametro {:<35} -> {}'.format(nombreParametroDeConfiguracion, LOCL_configDict[nombreParametroDeConfiguracion]))
    
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
                if LOCL_verbose:
                    print('\t-> AVISO: el parametro <{}> no esta en el fichero de configuacion; se adopta valor por defecto: <{}>'.format(nombreParametroDeConfiguracion, valorParametroConfiguracion))
    
        config_ok = True
    except:
        print('clidtwins_config-> Error al leer la configuracion del fichero:', LOCL_configFileNameCfg)
        config_ok = False
        sys.exit(0)
    # print('\t\tclidtwins_config-> LOCL_configDict:', LOCL_configDict)

    if LOCL_verbose:
        print('{:=^80}\n'.format(''))
    return LOCL_configDict


# ==============================================================================
def foo0():
    pass

# # ==============================================================================
# class myClass(object):
#     pass
#
# GLO = myClass()
# GLO.GLBLverbose = None
# GLO.GLBLaccionPrincipalPorDefecto = None
# GLO.GLBLrutaAscRaizBasePorDefecto = None
# GLO.GLBLrasterPixelSizePorDefecto = None
# GLO.GLBLradioClusterPixPorDefecto = None
# GLO.GLBLrutaCompletaMFEPorDefecto = None
# GLO.GLBLcartoMFEcampoSpPorDefecto = None
# GLO.GLBLpatronVectrNamePorDefecto = None
# GLO.GLBLtesteoVectrNamePorDefecto = None
# GLO.GLBLpatronLayerNamePorDefecto = None
# GLO.GLBLtesteoLayerNamePorDefecto = None
# GLO.GLBLnPatronDasoVarsPorDefecto = None
#
# GLO.GLBLlistaDasoVarsFileTypes = None
# GLO.GLBLlistaDasoVarsNickNames = None
# GLO.GLBLlistaDasoVarsRangoLinf = None
# GLO.GLBLlistaDasoVarsRangoLsup = None
# GLO.GLBLlistaDasoVarsNumClases = None
# GLO.GLBLlistaDasoVarsMovilidad = None
# GLO.GLBLlistLstDasoVarsPorDefecto = None
# GLO.GLBLlistTxtDasoVarsPorDefecto = None
#
# GLO.GLBLmenuInteractivoPorDefecto = None
# GLO.GLBLmarcoPatronTestPorDefecto = None
# GLO.GLBLnivelSubdirExplPorDefecto = None
# GLO.GLBLoutRasterDriverPorDefecto = None
# GLO.GLBLoutputSubdirNewPorDefecto = None
# GLO.GLBLcartoMFErecortePorDefecto = None
# GLO.GLBLvarsTxtFileNamePorDefecto = None
# GLO.GLBLambitoTiffNuevoPorDefecto = None
# GLO.GLBLnoDataTiffProviPorDefecto = None
# GLO.GLBLnoDataTiffFilesPorDefecto = None
# GLO.GLBLnoDataTipoDMasaPorDefecto = None
# GLO.GLBLumbralMatriDistPorDefecto = None
#
# GLO.GLBLaccionPrincipal = None
# GLO.GLBLrutaAscRaizBase = None
# GLO.GLBLrasterPixelSize = None
# GLO.GLBLradioClusterPix = None
# GLO.GLBLrutaCompletaMFE = None
# GLO.GLBLcartoMFEcampoSp = None
# GLO.GLBLpatronVectrName = None
# GLO.GLBLpatronLayerName = None
# GLO.GLBLtesteoVectrName = None
# GLO.GLBLtesteoLayerName = None
# GLO.GLBLnPatronDasoVars = None
#
# GLO.GLBLlistaDasoVarsFileTypes = None
# GLO.GLBLlistaDasoVarsNickNames = None
# GLO.GLBLlistaDasoVarsRangoLinf = None
# GLO.GLBLlistaDasoVarsRangoLsup = None
# GLO.GLBLlistaDasoVarsNumClases = None
# GLO.GLBLlistaDasoVarsMovilidad = None
# GLO.GLBLlistLstDasoVars = None
# GLO.GLBLlistTxtDasoVars = None
#
# GLO.GLBLmenuInteractivo = None
# GLO.GLBLmarcoPatronTest = None
# GLO.GLBLnivelSubdirExpl = None
# GLO.GLBLoutRasterDriver = None
# GLO.GLBLoutputSubdirNew = None
# GLO.GLBLcartoMFErecorte = None
# GLO.GLBLvarsTxtFileName = None
# GLO.GLBLambitoTiffNuevo = None
# GLO.GLBLnoDataTiffProvi = None
# GLO.GLBLnoDataTiffFiles = None
# GLO.GLBLnoDataTipoDMasa = None
# GLO.GLBLumbralMatriDist = None
#
# GLO.GLBLmarcoCoordMiniX = 0
# GLO.GLBLmarcoCoordMaxiX = 0
# GLO.GLBLmarcoCoordMiniY = 0
# GLO.GLBLmarcoCoordMaxiY = 0
#
# GLO.configFileNameCfg = None


# ==============================================================================
def leerConfigDictPorDefecto():
    ''''Dict de parametros de configuracion con valores por defecto.
    Estructura:
        GRAL_configDict[nombreParametroDeConfiguracion] = [valorParametro, grupoParametros, tipoVariable, descripcionParametro]
    '''
    configDictPorDefecto = {
        'GLBLverbose': [2, 'General', 'bool', 'Mostrar info de ejecucion en consola'],
        # 'MAINprocedimiento': ['', 'General', 'str', ''],
        # 'GLBLsoloRoquedosParaEntrenamiento': ['', 'General', 'str', ''],
    
        'GLBLaccionPrincipalPorDefecto': ['2', 'dasoLidar', 'bool', '1. Verificar analog�a con un determinado patron dasoLidar; 2. Generar raster con presencia de un determinado patron dasoLidar.'],
    
        # Ruta de los lasFiles para Leon:
        'GLBLrutaAscRaizBasePorDefecto': ['K:/calendula/NW', 'dasoLidar', 'str', 'Ruta de los ASC para el dasolidar cluster en JCyL'],
        'GLBLrutaAscRaizBasePorDefecto': ['', 'dasoLidar', 'str', 'Ruta de los ASC para el dasolidar cluster en JCyL'],
        'GLBLrutaAscRaizBasePorDefecto': ['O:/Sigmena/usuarios/COMUNES/Bengoa/Lidar/cartoLidar/Sg_PinoSilvestre', 'dasoLidar', 'str', 'Ruta de los ASC para el dasolidar cluster en JCyL'],
    
        # 'GLBLpatronVectrNamePorDefecto': [r'O:/Sigmena/usuarios/COMUNES/Bengoa/Lidar/cartoLidar/Le_roble/vector/zonaEnsayoTolosana.shp', 'dasoLidar', 'str', 'Nombre del dataset (shp o gpkg) de referencia (patron) para caracterizacion dasoLidar'],
        # 'GLBLpatronVectrNamePorDefecto': [r'O:/Sigmena/usuarios/COMUNES/Bengoa/Lidar/cartoLidar/Le_roble/vector/perimetrosDeReferencia.gpkg', 'dasoLidar', 'str', 'Nombre del dataset (shp o gpkg) de referencia (patron) para caracterizacion dasoLidar'],
        'GLBLpatronVectrNamePorDefecto': [r'O:/Sigmena/usuarios/COMUNES/Bengoa/Lidar/cartoLidar/Le_roble/vector/recintos_roble.gpkg', 'dasoLidar', 'str', 'Nombre del dataset (shp o gpkg) de referencia (patron) para caracterizacion dasoLidar'],
        'GLBLpatronVectrNamePorDefecto': [r'O:/Sigmena/usuarios/COMUNES/Bengoa/Lidar/cartoLidar/Sg_PinoSilvestre/poligonos Riaza1.shp', 'dasoLidar', 'str', 'Nombre del dataset (shp o gpkg) de referencia (patron) para caracterizacion dasoLidar'],
    
        # 'GLBLtesteoVectrNamePorDefecto': [r'O:/Sigmena/usuarios/COMUNES/Bengoa/Lidar/cartoLidar/Le_roble/vector/MUP_rodales_zonaEstudio.shp', 'dasoLidar', 'str', 'Nombre del dataset (shp o gpkg) cuya semejanza con el de entrada se chequea con dasoLidar.'],
        # 'GLBLtesteoVectrNamePorDefecto': [r'O:/Sigmena/usuarios/COMUNES/Bengoa/Lidar/cartoLidar/Le_roble/vector/testeo_roble.shp', 'dasoLidar', 'str', 'Nombre del dataset (shp o gpkg) de contraste (testeo) para verificar su analogia con el patron dasoLidar'],
        'GLBLtesteoVectrNamePorDefecto': [r'O:/Sigmena/usuarios/COMUNES/Bengoa/Lidar/cartoLidar/Le_roble/vector/recintos_roble.gpkg', 'dasoLidar', 'str', 'Nombre del dataset (shp o gpkg) de contraste (testeo) para verificar su analogia con el patron dasoLidar'],
        'GLBLtesteoVectrNamePorDefecto': [r'O:/Sigmena/usuarios/COMUNES/Bengoa/Lidar/cartoLidar/Sg_PinoSilvestre/poligonos Riaza2.shp', 'dasoLidar', 'str', 'Nombre del dataset (shp o gpkg) cuya semejanza con el de entrada se chequea con dasoLidar.'],
    
        # 'GLBLpatronLayerNamePorDefecto': [r'robleAlto1', 'dasoLidar', 'str', 'Nombre del layer de referencia (patron) para caracterizacion dasoLidar (solo si el dataset es gpkg; para shp layer=capa=dataset).'],
        # 'GLBLtesteoLayerNamePorDefecto': [r'robleAlto2', 'dasoLidar', 'str', 'Nombre del layer cuya semejanza con el de entrada se chequea con dasoLidar (solo si el dataset es gpkg; para shp layer=capa=dataset).'],
        'GLBLpatronLayerNamePorDefecto': [r'', 'dasoLidar', 'str', 'Nombre del layer de referencia (patron) para caracterizacion dasoLidar (solo si el dataset es gpkg; para shp layer=capa=dataset).'],
        'GLBLtesteoLayerNamePorDefecto': [r'', 'dasoLidar', 'str', 'Nombre del layer cuya semejanza con el de entrada se chequea con dasoLidar (solo si el dataset es gpkg; para shp layer=capa=dataset).'],
    
        'GLBLrasterPixelSizePorDefecto': [10, 'General', 'uint8', 'Lado del pixel dasometrico en metros (pte ver diferencia con GLBLmetrosCelda)'],
        'GLBLradioClusterPixPorDefecto': [3, 'dasoLidar', 'uint8', 'Numero de anillos de pixeles que tiene el cluster, ademas del central'],
    
        # 'GLBLrutaCompletaMFEPorDefecto': ['O:/Sigmena/Carto/VEGETACI/MFE/MFE50/MFE50AD/24_MFE50AD_etrs89.shp', 'dasoLidar', 'str', 'Nombre (con ruta y extension) del fichero con la capa MFE'],
        'GLBLrutaCompletaMFEPorDefecto': ['O:/Sigmena/Carto/VEGETACI/MFE/MFE50/MFE50AD/40_MFE50AD_etrs89.shp', 'dasoLidar', 'str', 'Nombre (con ruta y extension) del fichero con la capa MFE'],
        'GLBLcartoMFEcampoSpPorDefecto': ['SP1', 'dasoLidar', 'str', 'Nombre del campo con el codigo numerico de la especie principal o tipo de bosque en la capa MFE'],
    
        'GLBLnPatronDasoVarsPorDefecto': [0, 'dasoLidar', 'int', 'Si es distinto de cero, numero de dasoVars con las que se caracteriza el patron (n primeras dasoVars)'],
    
        'GLBLnClasesDasoVarsPorDefecto': [5, 'dasoLidar', 'int', 'Numero de clases por defecto para todas las variables si no se especifica para cada variable.'],
        'GLBLtrasferDasoVarsPorDefecto': [25, 'dasoLidar', 'int', 'Porcentaje de movilidad admisible interclases si no se especifica para cada variable.'],

            'GLBLlistaDasoVarsFileTypes': [
            'CeldasAlt95SobreMdk,FccRptoAmdk_PrimeRets_MasDe0500,FccRptoAmdk_PrimeRets_MasDe0300,FccRptoAmdk_PrimeRets_0025_0150,FccRptoAmdk_TodosRets_200cm_50%HD,MFE25,TMasa',
            # 'CeldasAlt95SobreMdk,FccRptoAmdk_PrimeRets_MasDe0500,FccRptoAmdk_PrimeRets_MasDe0300,FccRptoAmdk_PrimeRets_0025_0150,MFE,TipoMasa',
            'dasoLidar', 'list_str', 'Lista de tipos de fichero para el dasoLidar'
        ],
        'GLBLlistaDasoVarsNickNames': [
            'Alt95,FCC5m,FCC3m,FCmat,FCsub,MFE25,TMasa',
            # 'Alt95,FCC5m,FCC3m,FCmat,MFE25,TMasa',
            'dasoLidar', 'list_str', 'Lista de variables para el dasoLidar'
        ],
        'GLBLlistaDasoVarsRangoLinf': [
            '0,0,0,0,0,0,0',
            # '0,0,0,0,0,0',
            'dasoLidar', 'list_int', 'Lista de variables para el dasoLidar'
        ],
        'GLBLlistaDasoVarsRangoLsup': [
            '36,100,100,100,100,255,255',
            # '36,100,100,100,255,255',
            'dasoLidar', 'list_int', 'Lista de variables para el dasoLidar'
        ],
        'GLBLlistaDasoVarsNumClases': [
            '18,5,5,5,5,255,255',
            # '18,5,5,5,255,255',
            'dasoLidar', 'list_int', 'Lista de variables para el dasoLidar'
        ],
        'GLBLlistaDasoVarsMovilidad': [
            '40,25,30,35,35,0,0',
            # '25,20,20,25,0,0',
            'dasoLidar', 'list_int', 'Lista de factores de movilidad admitidas entre clases del histograma de la variable dasoVar (0-100)'
        ],
        'GLBLlistaDasoVarsPonderado': [
            '10,8,5,4,3,0,0',
            'dasoLidar', 'list_int', 'Peso de cada variable para poderar las discrepancias respecto al modelo o patron (0-10).'
        ],
    
        'GLBLmenuInteractivoPorDefecto': [0, 'General', 'bool', 'Preguntar en tiempo de ejecucion para confirmar opciones'],
        'GLBLmarcoPatronTestPorDefecto': [1, 'dasoLidar', 'bool', 'Zona de analisis definida por la envolvente de los poligonos de referencia (patron) y de chequeo (testeo)'],
        'GLBLnivelSubdirExplPorDefecto': [3, 'General', 'bool', 'Explorar subdirectorios de rutaAscRaizBase'],
        'GLBLoutRasterDriverPorDefecto': ['GTiff', 'dasoLidar', 'str', 'Formato de fichero raster de salida para el dasolidar'],
        'GLBLoutputSubdirNewPorDefecto': ['dasoLayers', 'dasoLidar', 'str', 'Subdirectorio de GLBLrutaAscRaizBasePorDefecto donde se guardan los resultados'],
        'GLBLcartoMFErecortePorDefecto': ['mfe50rec', 'dasoLidar', 'str', 'Nombre del fichero en el que se guarda la version recortada raster del MFE'],
        'GLBLvarsTxtFileNamePorDefecto': ['rangosDeDeferencia.txt', 'dasoLidar', 'str', 'Nombre de fichero en el que se guardan los rangos calculados para todas las variables'],
        ''
        'GLBLambitoTiffNuevoPorDefecto': ['loteAsc', 'general', 'str', 'Principalmente para merge: ambito geografico del nuevo raster creado (uno predeterminado o el correspondiente a los ASC)'],
    
        'GLBLnoDataTiffProviPorDefecto': [-8888, 'dasoLidar', 'int', 'NoData temporal para los ficheros raster de salida para el dasolidar'],
        'GLBLnoDataTiffFilesPorDefecto': [-9999, 'dasoLidar', 'int', 'NoData definitivo para los ficheros raster de salida para el dasolidar'],
        'GLBLnoDataTipoDMasaPorDefecto': [255, 'dasoLidar', 'int', 'NoData definitivo para el raster de salida con el tipo de masa para el dasolidar'],
        'GLBLumbralMatriDistPorDefecto': [20, 'dasoLidar', 'int', 'Umbral de distancia por debajo del cual se considera que una celda es parecida a otra enla matriz de distancias entre dasoVars'],

        'GLBLmarcoCoordMiniXPorDefecto': [0, 'dasoLidar', 'int', 'Limite inferior X para delimitar la zona de analisis'],
        'GLBLmarcoCoordMaxiXPorDefecto': [0, 'dasoLidar', 'int', 'Limite superior X para delimitar la zona de analisis'],
        'GLBLmarcoCoordMiniYPorDefecto': [0, 'dasoLidar', 'int', 'Limite inferior Y para delimitar la zona de analisis'],
        'GLBLmarcoCoordMaxiYPorDefecto': [0, 'dasoLidar', 'int', 'Limite superior Y para delimitar la zona de analisis'],

    }
    return configDictPorDefecto


# ==============================================================================
def readSppMatch():
    sppMatch = [
        [21, 22, 7], # Ps Pu
        [21, 23, 3], # Ps Pp
        [21, 24, 2], # Ps Ph
        [21, 25, 6], # Ps Pn
        [21, 26, 5], # Ps Pt
        [21, 28, 3], # Ps Pr
        [22, 23, 3], # Pu Pp
        [22, 24, 2], # Pu Ph
        [22, 25, 5], # Pu Pn
        [22, 26, 4], # Pu Pt
        [22, 28, 3], # Pu Pr
        [23, 24, 4], # Pp Ph
        [23, 25, 4], # Pp Pn
        [23, 26, 5], # Pp Pt
        [23, 28, 2], # Pp Pr
        [24, 25, 3], # Ph Pn
        [24, 26, 3], # Ph Pt
        [24, 28, 2], # Ph Pr
        [25, 26, 5], # Pn Pt
        [25, 28, 4], # Pn Pr
        [26, 28, 5], # Pt Pr
        [41, 42, 9], # Qr Qt
        [41, 43, 5], # Qr Qp
        [41, 44, 4], # Qr Qf
        [41, 45, 3], # Qr Qi
        [41, 46, 3], # Qr Qs
        [42, 43, 5], # Qt Qp
        [42, 44, 4], # Qt Qf
        [42, 45, 3], # Qt Qi
        [42, 46, 3], # Qt Qs
        [43, 44, 7], # Qp Qf
        [43, 45, 5], # Qp Qi
        [43, 46, 3], # Qp Qs
        [44, 45, 7], # Qf Qi
        [44, 46, 5], # Qf Qs
        [45, 46, 7], # Qi Qs
        ]
    return sppMatch


# ==============================================================================
def checkGLO(GLO):
    GLO.GLBLinputVectorMfePathName = os.path.dirname(GLO.GLBLrutaCompletaMFEPorDefecto)
    inputVectorMfeFilePathName, GLO.GLBLinputVectorMfeFileExt = os.path.splitext(GLO.GLBLrutaCompletaMFEPorDefecto)
    GLO.GLBLinputVectorMfeFileName = os.path.basename(inputVectorMfeFilePathName)
    if GLO.GLBLinputVectorMfeFileExt.lower() == '.shp':
        GLO.GLBLinputVectorDriverNameMFE = 'ESRI Shapefile'
    elif GLO.GLBLinputVectorMfeFileExt.lower() == '.gpkg':
        GLO.GLBLinputVectorDriverNameMFE = 'ESRI Shapefile'
    else:
        GLO.GLBLinputVectorDriverNameMFE = ''
        print(f'clidtwins_config-> No se ha identificado bien el driver de esta extension: {GLO.GLBLinputVectorMfeFileExt} (fichero: {GLO.GLBLrutaCompletaMFEPorDefecto})')
        sys.exit(0)

    # ==============================================================================
    if (
        len(GLO.GLBLlistaDasoVarsNickNames) < len(GLO.GLBLlistaDasoVarsFileTypes) 
        or len(GLO.GLBLlistaDasoVarsRangoLinf) < len(GLO.GLBLlistaDasoVarsFileTypes)
        or len(GLO.GLBLlistaDasoVarsRangoLsup) < len(GLO.GLBLlistaDasoVarsFileTypes)
        or len(GLO.GLBLlistaDasoVarsNumClases) < len(GLO.GLBLlistaDasoVarsFileTypes)
        or len(GLO.GLBLlistaDasoVarsMovilidad) < len(GLO.GLBLlistaDasoVarsFileTypes)
        or len(GLO.GLBLlistaDasoVarsPonderado) < len(GLO.GLBLlistaDasoVarsFileTypes)
        
    ):
        print(
            '\nclidtwins_config-> ATENCION: revisar lista de variables en el fichero de parametros de configuracion:',
            len(GLO.GLBLlistaDasoVarsFileTypes),
            len(GLO.GLBLlistaDasoVarsNickNames),
            len(GLO.GLBLlistaDasoVarsRangoLinf),
            len(GLO.GLBLlistaDasoVarsRangoLsup),
            len(GLO.GLBLlistaDasoVarsNumClases),
            len(GLO.GLBLlistaDasoVarsMovilidad),
            len(GLO.GLBLlistaDasoVarsPonderado),
        )
        print('\t', type(GLO.GLBLlistaDasoVarsFileTypes), len(GLO.GLBLlistaDasoVarsFileTypes), GLO.GLBLlistaDasoVarsFileTypes)
        print('\t', type(GLO.GLBLlistaDasoVarsNickNames), len(GLO.GLBLlistaDasoVarsNickNames), GLO.GLBLlistaDasoVarsNickNames)
        print('\t', type(GLO.GLBLlistaDasoVarsRangoLinf), len(GLO.GLBLlistaDasoVarsRangoLinf), GLO.GLBLlistaDasoVarsRangoLinf)
        print('\t', type(GLO.GLBLlistaDasoVarsRangoLinf), len(GLO.GLBLlistaDasoVarsRangoLsup), GLO.GLBLlistaDasoVarsRangoLinf)
        print('\t', type(GLO.GLBLlistaDasoVarsNumClases), len(GLO.GLBLlistaDasoVarsNumClases), GLO.GLBLlistaDasoVarsNumClases)
        print('\t', type(GLO.GLBLlistaDasoVarsMovilidad), len(GLO.GLBLlistaDasoVarsMovilidad), GLO.GLBLlistaDasoVarsMovilidad)
        print('\t', type(GLO.GLBLlistaDasoVarsPonderado), len(GLO.GLBLlistaDasoVarsPonderado), GLO.GLBLlistaDasoVarsPonderado)
        print(f'Corregir o eliminar el fichero almacenado ({GLO.configFileNameCfg}).')
        sys.exit(0)

    nBandasPrevistasOutput = len(GLO.GLBLlistaDasoVarsFileTypes)
    GLO.GLBLlistTxtDasoVarsPorDefecto = []
    for nVar in range(nBandasPrevistasOutput):
        GLO.GLBLlistTxtDasoVarsPorDefecto.append(
            '{},{},{},{},{},{},{}'.format(
                GLO.GLBLlistaDasoVarsFileTypes[nVar],
                GLO.GLBLlistaDasoVarsNickNames[nVar],
                GLO.GLBLlistaDasoVarsRangoLinf[nVar],
                GLO.GLBLlistaDasoVarsRangoLsup[nVar],
                GLO.GLBLlistaDasoVarsNumClases[nVar],
                GLO.GLBLlistaDasoVarsMovilidad[nVar],
                GLO.GLBLlistaDasoVarsPonderado[nVar],
            )
        )

    GLO.GLBLlistLstDasoVarsPorDefecto = []
    for nVar in range(nBandasPrevistasOutput):
        GLO.GLBLlistLstDasoVarsPorDefecto.append(
            [
                GLO.GLBLlistaDasoVarsFileTypes[nVar],
                GLO.GLBLlistaDasoVarsNickNames[nVar],
                GLO.GLBLlistaDasoVarsRangoLinf[nVar],
                GLO.GLBLlistaDasoVarsRangoLsup[nVar],
                GLO.GLBLlistaDasoVarsNumClases[nVar],
                GLO.GLBLlistaDasoVarsMovilidad[nVar],
                GLO.GLBLlistaDasoVarsPonderado[nVar],
            ]
        )

    # # Partiendo del formato listTxtDasoVars (lista de textos emulando listas):
    # GLO.GLBLlistLstDasoVarsPorDefecto = []
    # for nVar in range(nBandasPrevistasOutput):
    #     for numLista, txtListaDasovar in enumerate(GLO.GLBLlistTxtDasoVarsPorDefecto):
    #         if nVar == 0 or nVar == 1:
    #             # FileTypes y NickNames
    #             listDasoVar = [item.strip() for item in txtListaDasovar.split(',')]
    #         elif nVar == 2 or nVar == 3:
    #             # RangoLinf y RangoLinf
    #             listDasoVar = [float(item.strip()) for item in txtListaDasovar.split(',')]
    #         else:
    #             # NumClases, Movilidad y Ponderado
    #             listDasoVar = [int(item.strip()) for item in txtListaDasovar.split(',')]
    #         GLO.GLBLlistLstDasoVarsPorDefecto.append(listDasoVar)

        # print('clidtwins_config->', nVar, type(GLO.GLBLlistaDasoVarsMovilidad[nVar]), GLO.GLBLlistaDasoVarsMovilidad[nVar], end=' -> ')
        # GLO.GLBLlistaDasoVarsRangoLinf[nVar] = int(GLO.GLBLlistaDasoVarsRangoLinf[nVar])
        # GLO.GLBLlistaDasoVarsRangoLsup[nVar] = int(GLO.GLBLlistaDasoVarsRangoLsup[nVar])
        # GLO.GLBLlistaDasoVarsNumClases[nVar] = int(GLO.GLBLlistaDasoVarsNumClases[nVar])
        # GLO.GLBLlistaDasoVarsMovilidad[nVar] = int(GLO.GLBLlistaDasoVarsMovilidad[nVar])
        # print(type(GLO.GLBLlistaDasoVarsMovilidad[nVar]), GLO.GLBLlistaDasoVarsMovilidad[nVar])
    # ==========================================================================
    GLO.GLBLverbose = GLO.GLBLverbose
    GLO.GLBLaccionPrincipalPorDefecto = int(GLO.GLBLaccionPrincipalPorDefecto)
    GLO.GLBLrutaAscRaizBasePorDefecto = str(GLO.GLBLrutaAscRaizBasePorDefecto)
    GLO.GLBLrasterPixelSizePorDefecto = int(GLO.GLBLrasterPixelSizePorDefecto)
    GLO.GLBLradioClusterPixPorDefecto = int(GLO.GLBLradioClusterPixPorDefecto)
    GLO.GLBLrutaCompletaMFEPorDefecto = str(GLO.GLBLrutaCompletaMFEPorDefecto)
    GLO.GLBLcartoMFEcampoSpPorDefecto = str(GLO.GLBLcartoMFEcampoSpPorDefecto)
    GLO.GLBLpatronVectrNamePorDefecto = str(GLO.GLBLpatronVectrNamePorDefecto)
    GLO.GLBLpatronLayerNamePorDefecto = GLO.GLBLpatronLayerNamePorDefecto
    GLO.GLBLtesteoVectrNamePorDefecto = str(GLO.GLBLtesteoVectrNamePorDefecto)
    GLO.GLBLtesteoLayerNamePorDefecto = GLO.GLBLtesteoLayerNamePorDefecto
    GLO.GLBLnPatronDasoVarsPorDefecto = int(GLO.GLBLnPatronDasoVarsPorDefecto)
    
    GLO.GLBLlistaDasoVarsFileTypes = list(GLO.GLBLlistaDasoVarsFileTypes)
    GLO.GLBLlistaDasoVarsNickNames = list(GLO.GLBLlistaDasoVarsNickNames)
    GLO.GLBLlistaDasoVarsRangoLinf = list(GLO.GLBLlistaDasoVarsRangoLinf)
    GLO.GLBLlistaDasoVarsRangoLsup = list(GLO.GLBLlistaDasoVarsRangoLsup)
    GLO.GLBLlistaDasoVarsNumClases = list(GLO.GLBLlistaDasoVarsNumClases)
    GLO.GLBLlistaDasoVarsMovilidad = list(GLO.GLBLlistaDasoVarsMovilidad)
    GLO.GLBLlistLstDasoVarsPorDefecto = list(GLO.GLBLlistLstDasoVarsPorDefecto)
    GLO.GLBLlistTxtDasoVarsPorDefecto = list(GLO.GLBLlistTxtDasoVarsPorDefecto)
    
    GLO.GLBLmenuInteractivoPorDefecto = int(GLO.GLBLmenuInteractivoPorDefecto)
    GLO.GLBLmarcoPatronTestPorDefecto = int(GLO.GLBLmarcoPatronTestPorDefecto)
    GLO.GLBLnivelSubdirExplPorDefecto = int(GLO.GLBLnivelSubdirExplPorDefecto)
    GLO.GLBLoutRasterDriverPorDefecto = str(GLO.GLBLoutRasterDriverPorDefecto)
    GLO.GLBLoutputSubdirNewPorDefecto = str(GLO.GLBLoutputSubdirNewPorDefecto)
    GLO.GLBLcartoMFErecortePorDefecto = str(GLO.GLBLcartoMFErecortePorDefecto)
    GLO.GLBLvarsTxtFileNamePorDefecto = str(GLO.GLBLvarsTxtFileNamePorDefecto)
    GLO.GLBLambitoTiffNuevoPorDefecto = str(GLO.GLBLambitoTiffNuevoPorDefecto)
    GLO.GLBLnoDataTiffProviPorDefecto = int(GLO.GLBLnoDataTiffProviPorDefecto)
    GLO.GLBLnoDataTiffFilesPorDefecto = int(GLO.GLBLnoDataTiffFilesPorDefecto)
    GLO.GLBLnoDataTipoDMasaPorDefecto = int(GLO.GLBLnoDataTipoDMasaPorDefecto)
    GLO.GLBLumbralMatriDistPorDefecto = int(GLO.GLBLumbralMatriDistPorDefecto)
    # ==========================================================================
    
    # ==========================================================================
    sppMatch = readSppMatch()
    GLO.GLBLdictProximidadInterEspecies = {}
    for (codeEsp1, codeEsp2, proximidadInterEsp) in sppMatch:
        binomioEspeciesA = f'{codeEsp1}_{codeEsp2}'
        binomioEspeciesB = f'{codeEsp2}_{codeEsp1}'
        GLO.GLBLdictProximidadInterEspecies[binomioEspeciesA] = proximidadInterEsp
        GLO.GLBLdictProximidadInterEspecies[binomioEspeciesB] = proximidadInterEsp
    # print('GLBLdictProximidadInterEspecies:')
    # for binomioSpp in GLO.GLBLdictProximidadInterEspecies:
    #     print(binomioSpp, GLO.GLBLdictProximidadInterEspecies[binomioSpp])
    # ==========================================================================

    return GLO


# ==============================================================================
def readGLO():
    configFileNameCfg = clidconfig.getConfigFileName(MAIN_idProceso)
    configDictPorDefecto = leerConfigDictPorDefecto()
    # Se guardan los parametros de configuracion en un diccionario:
    GRAL_configDict = leerConfig(configDictPorDefecto, configFileNameCfg)
    # Se crea un objeto de la clase VariablesGlobales para almacenar los
    # parametros de configuracion guardados en GRAL_configDict como atributos
    GLO = clidconfig.VariablesGlobales(GRAL_configDict)
    GLO.configFileNameCfg = configFileNameCfg
    checkGLO(GLO)


    if __verbose__ > 2:
        print('clidtwins_config-> GLO:')
        for myParameter in dir(GLO):
            if not myParameter.startswith('__'):
                print('\t', myParameter)
                if hasattr(GLO, myParameter) and (
                    'listaDasoVars' in myParameter
                    or 'listLstDasoVars' in myParameter
                    or 'listTxtDasoVars' in myParameter
                ):
                    
                    print('\t\t->', getattr(GLO, myParameter))
        quit()
    return GLO


# ==============================================================================
GLO = readGLO()


# ==============================================================================
if __name__ == "__main__":
    pass
