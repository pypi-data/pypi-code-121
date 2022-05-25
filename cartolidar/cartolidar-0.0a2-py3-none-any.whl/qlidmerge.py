#!/usr/bin/python
# encoding: utf-8
'''
qlidmerge:  utility included in cartolidar package 
cartolidar: processes files with lidar data from PNOA (Spain)

qlidmerge reads individual asc files and merges them in one layer
selecting the right part of each file for blocks that
are placed in more than one PNOA regional lidar zones. 

@author:     Jose Bengoa
@copyright:  2022 clid
@license:    GNU General Public License v3 (GPLv3)
@contact:    benmarjo@jcyl.es
@deffield    updated: 2022-05-03
'''
# -*- coding: latin-1 -*-

import sys
import os
from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
import pathlib
import time
import warnings
import math
# import random

# try:
#     from configparser import RawConfigParser
# except ImportError:  # Python 2
#     from ConfigParser import RawConfigParser
try:
    import psutil
    psutilOk = True
except:
    psutilOk = False

DEBUG = 0
TESTRUN = 0
PROFILE = 0

# ==============================================================================
# Agrego el idProceso para poder lanzar trabajos paralelos con distinta configuracion
# En principio con clidpar no ejecuto trabajos en paralelo con distinta configuracion
# Mantengo el procedimiento por si acaso
# GRAL_idProceso = random.randint(1, 999998)
GRAL_idProceso = 0
sys.argv.append('--idProceso')
sys.argv.append(GRAL_idProceso)
# ==============================================================================
# from clidtools import clidmerge_config as GLOBAL
from clidtools.clidmerge_config import GLO
from clidax import clidconfig
from clidax import clidcarto
# ==============================================================================


__all__ = []
__version__ = '0.0.dev1'
__date__ = '2022-05-03'
__updated__ = '2022-05-03'


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
def leerArgumentosEnLineaDeComandos(argv=None):
    '''Command line options.'''

    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    program_name = os.path.basename(sys.argv[0])
    program_version = 'v{}'.format(__version__)
    program_build_date = str(__updated__)
    program_version_message = '{} {} ({})'.format(program_name, program_version, program_build_date)
    program_shortdesc = __import__('__main__').__doc__.split("\n")[1]
    program_license = '''{}

  Created by Jose Bengoa on {}.

  Licensed GNU General Public License v3 (GPLv3)
  https://fsf.org/

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.

USAGE
'''.format(program_shortdesc, str(__date__))

    # print('qlidmerge-> sys.argv:', sys.argv)

    # ==========================================================================
    # https://docs.python.org/es/3/howto/argparse.html
    # https://docs.python.org/3/library/argparse.html
    # https://ellibrodepython.com/python-argparse
    try:
        # Setup argument parser
        parser = ArgumentParser(
            description=program_license,
            formatter_class=RawDescriptionHelpFormatter,
            fromfile_prefix_chars='@',
            )

        # Opciones:
        parser.add_argument('-v', '--verbose',
                            dest='verbose',
                            # action='count', # Cuenta el numero de veces que aparece la v (-v, -vv, -vvv, etc.)
                            action="store_true",
                            help='set verbosity level [default: %(default)s]')
        parser.add_argument('-V', '--version',
                            action='version',
                            version=program_version_message)
        parser.add_argument('-I', '--idProceso',
                            dest='nPatronDasoVars',
                            type=int,
                            help='Si es distinto de cero, numero de dasoVars con las que se caracteriza el patron (n primeras dasoVars). [default: %(default)s]',
                            default = GLO.GLBLnPatronDasoVarsPorDefecto,)

        parser.add_argument('-a', '--action',
                            dest='accionPrincipal',
                            type=int,
                            help='Accion a ejecutar: \n1. Verificar analogía con un determinado patron dasoLidar; \n2. Generar raster con presencia de un determinado patron dasoLidar.',
                            default = GLO.GLBLaccionPrincipalPorDefecto,)
        parser.add_argument('-i', '--inputpath',
                            dest='rutaAscRaizBase',
                            help='ruta en la que estan los ficheros de entrada con las variables dasolidar. [default: %(default)s]',
                            default = GLO.GLBLrutaAscRaizBasePorDefecto,)
        parser.add_argument('-l', '--level',
                            dest='nivelSubdirExpl',
                            type=int,
                            help='nivel de subdirectorios a explorar para buscar ficheros de entrada con las variables dasolidar. [default: %(default)s]',
                            default = GLO.GLBLnivelSubdirExplPorDefecto,)
        parser.add_argument('-x', '--pixelsize',
                            dest='rasterPixelSize',
                            type=int,
                            help='Lado del pixel dasometrico en metros (pte ver diferencia con GLBLmetrosCelda). [default: %(default)s]',
                            default = GLO.GLBLrasterPixelSizePorDefecto,)
        parser.add_argument('-c', '--clustersize',
                            dest='radioClusterPix',
                            type=int,
                            help='Numero de anillos de pixeles que tiene el cluster, ademas del central. [default: %(default)s]',
                            default = GLO.GLBLradioClusterPixPorDefecto,)
        parser.add_argument('-m', '--mfepath',
                            dest='rutaCompletaMFE',
                            help='Nombre (con ruta y extension) del fichero con la capa MFE. [default: %(default)s]',
                            default = GLO.GLBLrutaCompletaMFEPorDefecto,)
        parser.add_argument('-f', '--mfefield',
                            dest='campoEspecieMFE',
                            help='Nombre del campo con el codigo numerico de la especie o tipo de bosque principal en la capa MFE. [default: %(default)s]',
                            default = GLO.GLBLcampoEspecieMFEPorDefecto,)
        parser.add_argument('-p', '--patron',
                            dest='patronShapeName',
                            help='Nombre del poligono de referencia (patron) para caracterizacion dasoLidar. [default: %(default)s]',
                            default = GLO.GLBLpatronShapeNamePorDefecto,)
        parser.add_argument('-t', '--testeo',
                            dest='testeoShapeName',
                            help='Nombre del poligono de contraste (testeo) para verificar su analogia con el patron dasoLidar. [default: %(default)s]',
                            default = GLO.GLBLtesteoShapeNamePorDefecto,)
        parser.add_argument('-n', '--numvars',
                            dest='nPatronDasoVars',
                            type=int,
                            help='Si es distinto de cero, numero de dasoVars con las que se caracteriza el patron (n primeras dasoVars). [default: %(default)s]',
                            default = GLO.GLBLnPatronDasoVarsPorDefecto,)

        # Argumentos posicionales:
        # Opcionales
        parser.add_argument(dest='listadoDasoVars',
                            help='Lista de variables dasoLidar [default: %(default)s]',
                            default = GLO.GLBLlistaTxtDasoVarsAll,
                            nargs='*') # Admite entre 0 y n valores
        # Obligatorios:
        # parser.add_argument('uniParam',
        #                     help='Un parametro unico.',)
        # parser.add_argument(dest='paths',
        #                     help='paths to folder(s) with source file(s)',
        #                     metavar='path',
        #                     nargs='+') # Admite entre 0 y n valores

        # Process arguments
        args = parser.parse_args()

        print('\n-->> args: ', args)
        print('-->> verbose:        ', args.verbose)
        print('-->> accionPrincipal:', args.accionPrincipal)
        print('-->> rutaAscRaizBase:', args.rutaAscRaizBase)
        print('-->> nivelSubdirExpl:', args.nivelSubdirExpl)
        print('-->> rutaAscRaizBase:', args.rasterPixelSize)
        print('-->> rutaAscRaizBase:', args.radioClusterPix)
        print('-->> rutaAscRaizBase:', args.rutaCompletaMFE)
        print('-->> rutaAscRaizBase:', args.campoEspecieMFE)
        print('-->> rutaAscRaizBase:', args.patronShapeName)
        print('-->> rutaAscRaizBase:', args.testeoShapeName)
        print('-->> rutaAscRaizBase:', args.nPatronDasoVars)
        print('-->> txtlistaVars:   ', args.listadoDasoVars)
        print('-->> listaVars:')
        listadoDasoVars = []
        for txtListaDasovar in args.listadoDasoVars:
            listDasoVar = [item.strip() for item in txtListaDasovar.split(',')]
            listadoDasoVars.append(listDasoVar)
            print('\t', listDasoVar)

        return args
    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return None
    except Exception as e:
        if DEBUG or TESTRUN:
            raise(e)
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        return None


# ==============================================================================
def menuPrincipal(
        LCLopcionElegida,
        LCLrutaAscRaizBase,
        LCLsubPath,
        LCLexplorarNivelDeSubdirs,
        LCLlistaDasoVarsFileTypes,
        # LCLcodCuadrante,
    ):

    if LCLopcionElegida == 0 or GLO.GLBLejecucionInteractiva:
        print('\n{:_^80}'.format(''))
        if MAIN_ENTORNO != 'windows':
            print('clidpar-> Ejecucion interactivo, no permitida fuera de Windows.')
            sys.exit(0)
        print('clidpar-> Elegir opcion:')
        print('\t 1.- Unir ficheros asc (2x2 km) en una sola capa (mergeBloquesASC).')
        print('\t 2.- Cortar ficheros asc (2x2 km) compartidos por cuadrantes y unir en un solo fichero (mergePlusMDE).')
        print('\t 3.- Renombrar ficheros tiff con nombre incorrecto.')
        print('\t 4.- Identificar patrones dasometricos y buscar zonas analogas.')
        selec = input('Elige opcion ({}) -> '.format(GLO.GLBLopcionPrincipalPorDefecto))
        try:
            LCLopcionElegida = int(selec)
        except:
            LCLopcionElegida = GLO.GLBLopcionPrincipalPorDefecto
        print(
            'Opcion selecionada: %i:' % LCLopcionElegida,
        )
        if LCLopcionElegida <= 0 or LCLopcionElegida > 4:
            print('clidclas-> Opcion no valida: {}'.format(LCLopcionElegida))
            sys.exit(0)
    
    # if LCLcodCuadrante == '':
    #     codCuadrantePorDefecto = 3
    #     print('\nclidpar-> No hay indicacion de cuadrante en linea de comandos. Elegir cuadrante')
    #     print('1. CE')
    #     print('2. NE')
    #     print('3. NW')
    #     print('4. SE')
    #     print('5. SW')
    #     print('6. XX')
    #     print('7. LE')
    #     selec2 = input('Elige opcion ({}) -> '.format(codCuadrantePorDefecto))
    #     try:
    #         nCuadrante = int(selec2)
    #     except:
    #         nCuadrante = codCuadrantePorDefecto
    #     if nCuadrante <= 0 or nCuadrante > 7:
    #         print('clidclas-> Opcion no valida: {}'.format(nCuadrante))
    #         sys.exit(0)
    #
    #     if nCuadrante == 1:
    #         LCLcodCuadrante = 'CE'
    #     elif nCuadrante == 2:
    #         LCLcodCuadrante = 'NE'
    #     elif nCuadrante == 3:
    #         LCLcodCuadrante = 'NW'
    #     elif nCuadrante == 4:
    #         LCLcodCuadrante = 'SE'
    #     elif nCuadrante == 5:
    #         LCLcodCuadrante = 'SW'
    #     elif nCuadrante == 6:
    #         LCLcodCuadrante = 'XX'
    #     elif nCuadrante == 7:
    #         LCLcodCuadrante = 'LE'
    #     else:
    #         LCLcodCuadrante = 'XX'
    #     print('clidpar-> Cuadrante elegido: {}'.format(LCLcodCuadrante))
    # else:
    #     print('clidpar-> Cuadrante elegido en linea de comandos: {}'.format(LCLcodCuadrante))

    # ==========================================================================
    if LCLopcionElegida == 4:
        LCLsubPath = ''
    if LCLsubPath != '':
        LCLrutaAscRaizFull = os.path.join(LCLrutaAscRaizBase, LCLsubPath)
    else:
        LCLrutaAscRaizFull = LCLrutaAscRaizBase
    print('clidpar-> LCLrutaAscRaizFull: {}'.format(LCLrutaAscRaizFull))
    if MAIN_ENTORNO == 'windows' and GLO.GLBLejecucionInteractiva:
        selec = input('\nRuta de las carpetas con ficheros .asc (por defecto: %s): ' % LCLrutaAscRaizFull)
        if selec != '':
            LCLrutaAscRaizFull = ''
            for letra in selec:
                letraSinBackslash = letra if letra != '\\' else '/'
                LCLrutaAscRaizFull += letraSinBackslash
        else:
            LCLrutaAscRaizFull = LCLrutaAscRaizFull
        print('{:=^80}'.format(''))
    # ==========================================================================

    if LCLopcionElegida == 1:
        mergeBloquesASC(
            LCLrutaAscRaizFull,
            LCLexplorarNivelDeSubdirs,
            LCLlistaDasoVarsFileTypes
        )
    elif LCLopcionElegida == 2:
        mergePlusMDE()
    elif LCLopcionElegida == 3:
        renombrarFicheros()
    elif LCLopcionElegida == 4:
        creaDasoLayer(LCLrutaAscRaizFull, LCLexplorarNivelDeSubdirs)


# ==============================================================================
def fooMain0():
    # Variables globales
    pass
# ==============================================================================
# ======================== Variables globales GRAL =========================
# ==========================================================================
# GRAL_idProceso -> Se define antes de importar clidconfig y clidcarto
# GRAL_configDictPorDefecto -> Se define mas adelante
GRAL_verbose = False
GRAL_nombreUsuario = infoUsuario()
GRAL_configFileNameCfg = sys.argv[0].replace('.py', '%06i.cfg' % GRAL_idProceso)
# ==========================================================================

# ==========================================================================
# ======================== Variables globales MAIN =========================
# ==========================================================================
# Directorio que depende del entorno:
MAIN_HOME_DIR = str(pathlib.Path.home())
# Directorios de la aplicacion:
MAIN_FILE_DIR = os.path.dirname(os.path.abspath(__file__))
MAIN_PROJ_DIR = os.path.abspath(os.path.join(MAIN_FILE_DIR, '..'))
# Cuando estoy en un modulo dentro de un paquete (subdirectorio):
# MAIN_PROJ_DIR = os.path.abspath(os.path.join(MAIN_FILE_DIR, '..'))  # Equivale a FILE_DIR = pathlib.Path(__file__).parent
MAIN_RAIZ_DIR = os.path.abspath(os.path.join(MAIN_PROJ_DIR, '..'))
MAIN_MDLS_DIR = os.path.join(MAIN_RAIZ_DIR, 'data')
# Directorio desde el que se lanza la app (estos dos coinciden):
MAIN_BASE_DIR = os.path.abspath('.')
MAIN_THIS_DIR = os.getcwd()
# ==========================================================================
# Unidad de disco si MAIN_ENTORNO = 'windows'
MAIN_DRIVE = os.path.splitdrive(MAIN_FILE_DIR)[0]  # 'D:' o 'C:'
# ==========================================================================
if MAIN_FILE_DIR[:12] == '/LUSTRE/HOME':
    MAIN_ENTORNO = 'calendula'
    MAIN_PC = 'calendula'
elif MAIN_FILE_DIR[:8] == '/content':
    MAIN_ENTORNO = 'colab'
    MAIN_PC = 'colab'
else:
    MAIN_ENTORNO = 'windows'
    try:
        if GRAL_nombreUsuario == 'benmarjo':
            MAIN_PC = 'JCyL'
        else:
            MAIN_PC = 'Casa'
    except:
        MAIN_ENTORNO = 'calendula'
        MAIN_PC = 'calendula'
# ==========================================================================

# ==========================================================================
# ========================== Inicio de aplicacion ==========================
# ==========================================================================
print('\n{:_^80}'.format(''))
print('Arrancando qlidmerge')
print('\t-> ENTORNO:          {}'.format(MAIN_ENTORNO))
print('\t-> MAIN_PC:          {}'.format(MAIN_PC))
print('\t-> Usuario:          {}'.format(GRAL_nombreUsuario))
print('\t-> Modulo principal: {}'.format(sys.argv[0])) # = __file__
if GRAL_verbose:
    print('\t-> sys.argv: {}'.format(sys.argv))
print('{:=^80}'.format(''))
# ==========================================================================


# ==========================================================================
def fooMain1():
    pass

# ==============================================================================
if __name__ == "__main__":
    if DEBUG:
        sys.argv.append("-h")
    if TESTRUN:
        import doctest
        doctest.testmod()
    if PROFILE:
        import cProfile
        import pstats
        profile_filename = 'qlidmerge_profile.txt'
        cProfile.run('leerArgumentosEnLineaDeComandos()', profile_filename)
        statsfile = open("profile_stats.txt", "wb")
        p = pstats.Stats(profile_filename, stream=statsfile)
        stats = p.strip_dirs().sort_stats('cumulative')
        stats.print_stats()
        statsfile.close()
        sys.exit(0)

    # ==========================================================================
    # ===================== Argumentos en linea de comandos ====================
    # ============ Prevalecen sobre los parametros de configuracion ============
    # ==========================================================================
    args = leerArgumentosEnLineaDeComandos()
    if args is None:
        print('qlidmerge-> Revisar error en argumentos en linea')
        sys.exit(0)
    GLO.GLBLverbose = args.verbose
    GLO.GLBLaccionPrincipal = args.accionPrincipal
    GLO.GLBLrutaAscRaizBase = args.rutaAscRaizBase
    GLO.GLBLnivelSubdirExpl = args.nivelSubdirExpl
    GLO.GLBLrasterPixelSize = args.rasterPixelSize
    GLO.GLBLradioClusterPix = args.radioClusterPix
    GLO.GLBLrutaCompletaMFE = args.rutaCompletaMFE
    GLO.GLBLcampoEspecieMFE = args.campoEspecieMFE
    GLO.GLBLpatronShapeName = args.patronShapeName
    GLO.GLBLtesteoShapeName = args.testeoShapeName
    GLO.GLBLnPatronDasoVars = args.nPatronDasoVars
    GLO.GLBLlistadoDasoVars = args.listadoDasoVars
    # ==========================================================================

    # ==========================================================================
    # ============================ Inicio diferido =============================
    # ==========================================================================
    # Inicio diferido en Calendula
    print('\n{:_^80}'.format(''))
    if MAIN_ENTORNO != 'windows' or (GLO.GLBLaccionPrincipal != 0 and not GLO.GLBLejecucionInteractiva):
        print('clidpar-> Ejecucion automatizada, sin intervencion de usuario')
        esperar = 60 * 60 * 0.001
        print(
            '\tIniciando clidpar-> Hora: {}'.format(
                time.asctime(time.localtime(time.time()))
            )
        )
        print(
            '\tEjecucion diferida hasta: {}'.format(
                time.asctime(time.localtime(time.time() + esperar))
            )
        )
        print('\tEsperando {} minutos ({} horas) ...'.format(int(esperar/60), round(esperar/3600,2)))
        time.sleep(esperar)
        timeInicio = time.asctime(time.localtime(time.time()))
        print('\tInicio efectivo:        {}'.format(str(timeInicio)))
    else:
        print('clidpar-> Ejecucion interactiva, con intervencion de usuario. ARGSopcioGLBLaccionPrincipalnElegida:', GLO.GLBLaccionPrincipal, GLO.GLBLejecucionInteractiva)
    print('{:=^80}'.format(''))
    # ==========================================================================
