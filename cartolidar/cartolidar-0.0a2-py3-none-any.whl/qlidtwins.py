#!/usr/bin/python
# -*- coding: UTF-8 -*-
'''
Utility included in cartolidar project 
cartolidar: tools for Lidar processing focused on Spanish PNOA datasets

qlidtwins is an example that uses clidtwins within the cartolidar configuration.
clidtwins provides classes and functions that can be used to search for
areas similar to a reference one in terms of dasometric Lidar variables (DLVs).
DLVs (Daso Lidar Vars): vars that characterize forest or land cover structure.

@author:     Jose Bengoa
@copyright:  2022 @clid
@license:    GNU General Public License v3 (GPLv3)
@contact:    cartolidar@gmail.com
'''

import sys
import os
from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
# import random

__version__ = '0.0a2'
__date__ = '2016-2022'
__updated__ = '2022-05-18'
# No se importa nada con: from qlidtwins import *
__all__ = []

# ==============================================================================
# Verbose provisional para la version alpha
if '-vvv' in sys.argv:
    __verbose__ = 3
elif '-vv' in sys.argv:
    __verbose__ = 2
elif '-v' in sys.argv or '--verbose' in sys.argv:
    __verbose__ = 2
else:
    # En eclipse se adopta el valor indicado en Run Configurations -> Arguments
    __verbose__ = 2
if __verbose__ > 2:
    print(f'qlidtwins-> __name__:     <{__name__}>')
    print(f'qlidtwins-> __package__ : <{__package__ }>')
# ==============================================================================
if '-e' in sys.argv and len(sys.argv) > sys.argv.index('-e') + 1:
    # TRNS_LEER_EXTRA_ARGS = sys.argv[sys.argv.index('-e') + 1]
    TRNS_LEER_EXTRA_ARGS = True
elif '--extraArguments' in sys.argv and len(sys.argv) > sys.argv.index('--extraArguments') + 1:
    # TRNS_LEER_EXTRA_ARGS = sys.argv[sys.argv.index('--extraArguments') + 1]
    TRNS_LEER_EXTRA_ARGS = True
else:
    TRNS_LEER_EXTRA_ARGS = False
# ==============================================================================

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
try:
    from cartolidar.clidtools.clidtwins_config import GLO
    from cartolidar.clidtools.clidtwins import DasoLidarSource
except ModuleNotFoundError:
    if __verbose__ > 2:
        print(f'qlidtwins-> Se importa clidtwins desde qlidtwins del directorio local {os.getcwd()}/clidtools')
        print('\tNo hay vesion de cartolidar instalada en site-packages.')
    from clidtools.clidtwins_config import GLO
    from clidtools.clidtwins import DasoLidarSource
# except ModuleNotFoundError:
#     sys.stderr.write(f'\nATENCION: qlidtwins.py requiere los paquetes de cartolidar clidtools y clidax.\n')
#     sys.stderr.write(f'          Para lanzar el modulo qlidtwins.py desde linea de comandos ejecutar:\n')
#     sys.stderr.write(f'              $ python -m cartolidar\n')
#     sys.stderr.write(f'          Para ver las opciones de qlidtwins en linea de comandos:\n')
#     sys.stderr.write(f'              $ python qlidtwins -h\n')
#     sys.exit(0)
except Exception as e:
    program_name = 'qlidtwins'
    indent = len(program_name) * " "
    sys.stderr.write(f'{program_name}-> {repr(e)}\n')
    sys.stderr.write(f'{indent}   For help use:\n')
    sys.stderr.write(f'{indent}     help with only the arguments only: python {program_name}.py -h\n')
    sys.stderr.write(f'{indent}     help with main & extra arguments:  python {program_name}.py -e 1 -h')
    sys.exit(0)
# ==============================================================================

# ==============================================================================
try:
    from cartolidar.clidax.clidaux import Bar
except:
    if __verbose__ > 2:
        print(f'qlidtwins-> Se importa clidaux desde clidax del directorio local {os.getcwd()}/clidtools')
        print('\tNo hay vesion de cartolidar instalada en site-packages.')
    from clidax.clidaux import Bar

bar = Bar('Procesando', max=100)
for i in range(100):
    bar.next()
bar.finish()
# ==============================================================================



# ==============================================================================
# ============================ Constantes globales =============================
# ==============================================================================
TESTRUN = 0
PROFILE = 0
TRNS_preguntarPorArgumentosEnLineaDeComandos = __verbose__ > 1
# ==============================================================================


# ==============================================================================
# Gestion de errores de argumentos en linea de comandos con argparse
class CLIError(Exception):
    '''Generic exception to raise and log different fatal errors.'''
    def __init__(self, msg):
        super(CLIError).__init__(type(self))
        self.msg = "E: %s" % msg
    def __str__(self):
        return self.msg
    def __unicode__(self):
        return self.msg


# ==============================================================================
def checkRun():
    '''Chequeo de la forma de ejecucion provisional para la version alpha'''
    if __verbose__ > 1:
        print(f'\nqlidtwins-> __verbose__: {__verbose__}')
        if __verbose__ > 2:
            print(f'\nqlidtwins-> sys.argv: {sys.argv}')
    # ==========================================================================
    tipoEjecucion = 0
    try:
        if len(sys.argv) == 0:
            print(f'\nqlidtwins-> Revisar esta forma de ejecucion. sys.argv: <{sys.argv}>')
            sys.exit(0)
        elif sys.argv[0].endswith('__main__.py') and 'cartolidar' in sys.argv[0]:
            tipoEjecucion = 1
            if __verbose__ > 1:
                print('\nqlidtwins.py se ejecuta lanzando el paquete cartolidar desde linea de comandos:')
                print('\t  python -m cartolidar')
        elif sys.argv[0].endswith('qlidtwins.py'):
            tipoEjecucion = 2
            if __verbose__ > 1:
                print('\nqlidtwins.py se ha lanzado desde linea de comandos:')
                print('\t  python qlidtwins.py')
        elif sys.argv[0] == '':
            tipoEjecucion = 3
            if __verbose__ > 1:
                # Al importar el modulo no se pueden incluir el argumento -v (ni ningun otro)
                print('\nqlidtwins se esta importando desde el interprete interactivo:')
                print('\t>>> from cartolidar import qlidtwins')
                print('o, si esta accesible (en el path):')
                print('\t>>> import qlidtwins')
        else:
            tipoEjecucion = 4
            if __verbose__ > 1 or True:
                print(f'\nqlidtwins.py se esta importando desde el modulo: {sys.argv[0]}')
    except:
        print('\nqlidtwins-> Revisar MAIN_idProceso:')
        print(f'MAIN_idProceso: <{MAIN_idProceso}> type: {type(MAIN_idProceso)}')
        print(f'sys.argv:       <{sys.argv}>')
        print(f'sys.argv[0]:    <{sys.argv[0]}>')
    # ==========================================================================

    print('\nqlidtwins-> Info transitoria a quitar de aqui:')
    print(f'\tqlidtwins-> __name__:     <{__name__}>')
    print(f'\tqlidtwins-> __package__ : <{__package__ }>')
    print(f'\tqlidtwins-> sys.argv:     <{sys.argv}>')

    if sys.argv[0] == '':
        if __verbose__ > 1:
            print('\nAVISO: clidqins.py es un modulo escrito para ejecutarse desde linea de comandos:')
            print('\t  python -m cartolidar')
            print('o bien:')
            print('\t  python qlidtwins.py')
            print('\nSin embargo, se esta importando desde el interprete interactivo de python y')
            print('no se pueden incluir argumentos en linea de comandos.')
            print(f'Se usa fichero de configuracion: {GLO.configFileNameCfg}')
            print('(si existe) o configuracion por defecto (en caso contrario).')
            if __verbose__ > 1:
                selec = input('\r\nLanzar el modulo como si se ejecutara desde linea de comandos (S/n): ')
            else:
                selec = 's'
        else:
            selec = 's'
    elif len(sys.argv) == 3 and TRNS_preguntarPorArgumentosEnLineaDeComandos:
        # if sys.argv[0].endswith('__main__.py') and 'cartolidar' in sys.argv[0]:
        #     # Tb cumple 'qlidtwins' in __name__
        #     # __name__:    <cartolidar.qlidtwins>
        #     # __package__: <cartolidar>
        #     if __verbose__ > 1:
        #         print('\nqlidtwins.py se ejecuta lanzando el paquete cartolidar desde linea de comandos:')
        #         print('\t  python -m cartolidar')        print('\nAVISO: no se han introducido argumentos en linea de comandos')
        print('\t-> Para obtener ayuda sobre estos argumentos escribir:')
        print('\t\tpython {} -h'.format(os.path.basename(sys.argv[0])))
        selec = input('\nContinuar con la configuracion por defecto? (S/n): ')
    else:
        selec = 's'

    if (
        'qlidtwins' in __name__
        or len(sys.argv) == 3 and TRNS_preguntarPorArgumentosEnLineaDeComandos
    ):
        try:
            if selec.upper() == 'N':
                sys.argv.append("-h")
                print('')
                # print('Fin')
                # sys.exit(0)
        except (Exception) as thisError: # Raised when a generated error does not fall into any category.
            print(f'\nqlidtwins-> ATENCION: revisar codigo. selec: {type(selec)}´<{selec}>')
            print(f'\tRevisar error: {thisError}')
            sys.exit(0)
        print('{:=^80}'.format(''))

    return tipoEjecucion

# ==============================================================================
def testRun():
    if TESTRUN:
        import doctest
        doctest.testmod()
    if PROFILE:
        import cProfile
        import pstats
        profile_filename = 'qlidtwins_profile.txt'
        cProfile.run('leerArgumentosEnLineaDeComandos()', profile_filename)
        statsfile = open("profile_stats.txt", "wb")
        p = pstats.Stats(profile_filename, stream=statsfile)
        stats = p.strip_dirs().sort_stats('cumulative')
        stats.print_stats()
        statsfile.close()
        sys.exit(0)


# ==============================================================================
def leerArgumentosEnLineaDeComandos(argv=None):
    '''Command line options.
    These arguments take precedence over configuration file
    and over default parameters.
    '''

    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    program_name = os.path.basename(sys.argv[0])
    program_version = 'v{}'.format(__version__)
    program_build_date = str(__updated__)
    program_version_message = '{} {} ({})'.format(program_name, program_version, program_build_date)
    # program_shortdesc = __import__('__main__').__doc__.split("\n")[1]
    # program_shortdesc = __import__('__main__').__doc__
    program_shortdesc = '''  qlidtwins searchs for similar areas to a reference one in terms of
  lidar variables that characterize forest structure (dasoLidar variables).
  Utility included in cartolidar suite.'''

    program_license = '''{}

  Created by @clid {}.
  Licensed GNU General Public License v3 (GPLv3) https://fsf.org/
  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.
'''.format(program_shortdesc, str(__date__))

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
        parser.add_argument('-V', '--version',
                            action='version',
                            version=program_version_message,)
        parser.add_argument('-v', '--verbose',
                            dest='verbose',
                            action='count', # Cuenta el numero de veces que aparece la v (-v, -vv, -vvv, etc.)
                            # action="store_true",
                            help='set verbosity level [default: %(default)s]',
                            default = GLO.GLBLverbose,)
        parser.add_argument('-e', '--extraArguments',
                            dest='extraArguments',
                            # action='count', # Cuenta el numero de veces que aparece la e (-e, -ee, etc.)
                            action="store_false",
                            help='Activates extra arguments in command line. Default: %(default)s',
                            default = TRNS_LEER_EXTRA_ARGS,)
        optionsHelp = 'Opciones del menu principal cuando se ejecuta con python -m cartolidar'
        parser.add_argument('-o',  # '--option',
                            dest='menuOption',
                            type=int,
                            help=f'{optionsHelp}. Default: %(default)s',
                            default = '0',)

        parser.add_argument('-a',  # '--action',
                            dest='mainAction',
                            type=int,
                            help='Accion a ejecutar: \n1. Verificar analogia con un determinado patron dasoLidar; \n2. Generar raster con presencia de un determinado patron dasoLidar. Default: %(default)s',
                            default = GLO.GLBLaccionPrincipalPorDefecto,)

        parser.add_argument('-i',  # '--inputpath',
                            dest='rutaAscRaizBase',
                            help='Ruta (path) en la que estan los ficheros de entrada con las variables dasolidar. Default: %(default)s',
                            default = GLO.GLBLrutaAscRaizBasePorDefecto,)

        parser.add_argument('-m',  # '--mfepath',
                            dest='rutaCompletaMFE',
                            help='Nombre (con ruta y extension) del fichero con la capa MFE. Default: %(default)s',
                            default = GLO.GLBLrutaCompletaMFEPorDefecto,)
        parser.add_argument('-f',  # '--mfefield',
                            dest='cartoMFEcampoSp',
                            help='Nombre del campo con el codigo numerico de la especie principal o tipo de bosque en la capa MFE. Default: %(default)s',
                            default = GLO.GLBLcartoMFEcampoSpPorDefecto,)

        parser.add_argument('-p',  # '--patron',
                            dest='patronVectrName',
                            help='Nombre del poligono de referencia (patron) para caracterizacion dasoLidar. Default: %(default)s',
                            default = GLO.GLBLpatronVectrNamePorDefecto,)
        parser.add_argument('-l',  # '--patronLayer',
                            dest='patronLayerName',
                            help='Nombre del layer del gpkg (en su caso) de referencia (patron) para caracterizacion dasoLidar. Default: %(default)s',
                            default = GLO.GLBLpatronLayerNamePorDefecto,)
        parser.add_argument('-t',  # '--testeo',
                            dest='testeoVectrName',
                            help='Nombre del poligono de contraste (testeo) para verificar su analogia con el patron dasoLidar. Default: %(default)s',
                            default = GLO.GLBLtesteoVectrNamePorDefecto,)
        parser.add_argument('-y',  # '--testeoLayer',
                            dest='testeoLayerName',
                            help='Nombre del layer del gpkg (en su caso) de contraste (testeo) para verificar su analogia con el patron dasoLidar. Default: %(default)s',
                            default = GLO.GLBLtesteoLayerNamePorDefecto,)

        # ======================================================================
        listaExtraArgs = (
            'menuInteractivo', 'marcoCoordMiniX', 'marcoCoordMaxiX', 'marcoCoordMiniY',
            'marcoCoordMaxiY', 'marcoPatronTest', 'nPatronDasoVars', 'rasterPixelSize',
            'radioClusterPix', 'nivelSubdirExpl', 'outRasterDriver', 'outputSubdirNew',
            'cartoMFErecorte', 'varsTxtFileName', 'ambitoTiffNuevo', 'noDataTiffProvi',
            'noDataTiffFiles', 'noDataTipoDMasa', 'umbralMatriDist')
        if TRNS_LEER_EXTRA_ARGS:
            parser.add_argument('-0',  # '--menuInteractivo',
                                dest='menuInteractivo',
                                type=int,
                                help='La aplicacion pregunta en tiempo de ejecucion para elegir o confirmar opciones. Default: %(default)s',
                                default = GLO.GLBLmenuInteractivoPorDefecto,)

            parser.add_argument('-1',  # '--marcoCoordMiniX',
                                dest='marcoCoordMiniX',
                                type=float,
                                help='Limite inferior X para delimitar la zona de analisis. Default: %(default)s',
                                default = GLO.GLBLmarcoCoordMiniXPorDefecto,)
            parser.add_argument('-2',  # '--marcoCoordMaxiX',
                                dest='marcoCoordMaxiX',
                                type=float,
                                help='Limite superior X para delimitar la zona de analisis. Default: %(default)s',
                                default = GLO.GLBLmarcoCoordMaxiXPorDefecto,)
            parser.add_argument('-3',  # '--marcoCoordMiniY',
                                dest='marcoCoordMiniY',
                                type=float,
                                help='Limite inferior Y para delimitar la zona de analisis. Default: %(default)s',
                                default = GLO.GLBLmarcoCoordMiniYPorDefecto,)
            parser.add_argument('-4',  # '--marcoCoordMaxiY',
                                dest='marcoCoordMaxiY',
                                type=float,
                                help='Limite superior Y para delimitar la zona de analisis. Default: %(default)s',
                                default = GLO.GLBLmarcoCoordMaxiYPorDefecto,)
            parser.add_argument('-Z',  # '--marcoPatronTest',
                                dest='marcoPatronTest',
                                type=int,
                                help='Zona de analisis definida por la envolvente de los poligonos de referencia (patron) y de chequeo (testeo). Default: %(default)s',
                                default = GLO.GLBLmarcoPatronTestPorDefecto,)

            parser.add_argument('-X',  # '--pixelsize',
                                dest='rasterPixelSize',
                                type=int,
                                help='Lado del pixel dasometrico en metros (pte ver diferencia con GLBLmetrosCelda). Default: %(default)s',
                                default = GLO.GLBLrasterPixelSizePorDefecto,)
            parser.add_argument('-C',  # '--clustersize',
                                dest='radioClusterPix',
                                type=int,
                                help='Numero de anillos de pixeles que tiene el cluster, ademas del central. Default: %(default)s',
                                default = GLO.GLBLradioClusterPixPorDefecto,)

            parser.add_argument('-N',  # '--numvars',
                                dest='nPatronDasoVars',
                                type=int,
                                help='Si es distinto de cero, numero de dasoVars con las que se caracteriza el patron (n primeras dasoVars). Default: %(default)s',
                                default = GLO.GLBLnPatronDasoVarsPorDefecto,)
            parser.add_argument('-L',  # '--level',
                                dest='nivelSubdirExpl',
                                type=int,
                                help='nivel de subdirectorios a explorar para buscar ficheros de entrada con las variables dasolidar. Default: %(default)s',
                                default = GLO.GLBLnivelSubdirExplPorDefecto,)
            parser.add_argument('-D',  # '--outrasterdriver',
                                dest='outRasterDriver',
                                type=int,
                                help='Nombre gdal del driver para el formato de fichero raster de salida para el dasolidar. Default: %(default)s',
                                default = GLO.GLBLoutRasterDriverPorDefecto,)
            parser.add_argument('-S',  # '--outsubdir',
                                dest='outputSubdirNew',
                                type=int,
                                help='Subdirectorio de GLBLrutaAscRaizBasePorDefecto donde se guardan los resultados. Default: %(default)s',
                                default = GLO.GLBLoutputSubdirNewPorDefecto,)
            parser.add_argument('-M',  # '--clipMFEfilename',
                                dest='cartoMFErecorte',
                                type=int,
                                help='Nombre del fichero en el que se guarda la version recortada raster del MFE. Default: %(default)s',
                                default = GLO.GLBLcartoMFErecortePorDefecto,)
            parser.add_argument('-R',  # '--rangovarsfilename',
                                dest='varsTxtFileName',
                                help='Nombre de fichero en el que se guardan los intervalos calculados para todas las variables. Default: %(default)s',
                                default = GLO.GLBLvarsTxtFileNamePorDefecto,)
    
            parser.add_argument('-A',  # '--ambitoTiffNuevo',
                                dest='ambitoTiffNuevo',
                                help='Tipo de ambito para el rango de coordenadas (loteASC, CyL, CyL_nw, etc). Default: %(default)s',
                                default = GLO.GLBLambitoTiffNuevoPorDefecto,)
    
            parser.add_argument('-P',  # '--noDataTiffProvi',
                                dest='noDataTiffProvi',
                                help='NoData temporal para los ficheros raster de salida para el dasolidar. Default: %(default)s',
                                default = GLO.GLBLnoDataTiffProviPorDefecto,)
            parser.add_argument('-T',  # '--noDataTiffFiles',
                                dest='noDataTiffFiles',
                                help='NoData definitivo para los ficheros raster de salida para el dasolidar. Default: %(default)s',
                                default = GLO.GLBLnoDataTiffFilesPorDefecto,)
            parser.add_argument('-O',  # '--noDataTipoDMasa',
                                dest='noDataTipoDMasa',
                                help='NoData definitivo para el raster de salida con el tipo de masa para el dasolidar. Default: %(default)s',
                                default = GLO.GLBLnoDataTipoDMasaPorDefecto,)
            parser.add_argument('-U',  # '--umbralMatriDist',
                                dest='umbralMatriDist',
                                help='Umbral de distancia por debajo del cual se considera que una celda es parecida a otra enla matriz de distancias entre dasoVars. Default: %(default)s',
                                default = GLO.GLBLumbralMatriDistPorDefecto,)

        parser.add_argument('--idProceso',
                            dest='idProceso',
                            type=int,
                            help='Numero aleatorio para identificar el proceso que se esta ejecutando (se asigna automaticamente; no usar este argumento)',)

        # Argumentos posicionales:
        # Opcionales
        parser.add_argument(dest='listTxtDasoVars',
                            help='Lista de variables dasoLidar:'
                            'Secuencia de cadenas de texto (uno por variable), del tipo:'
                            '"texto1", "texto2", etc. de forma que cada elementos de esta secuencia sea:'
                            '    Opcion a: identificadores de DLVs (FileTypeId). P. ej. alt95 fcc05 fcc03 (no llevan comas ni comillas)' 
                            '    Opcion b: una secuencia de cinco elementos separados por comas del tipo:'
                            '        "FileTypeId, NickName, RangoLinf, RangoLsup, NumClases, Movilidad(0-100), Ponderacion(0-10)"'
                            '        Ejemplo: ["alt95,hDom,0,36,18,40,10", "fcc05,FCC,0,100,5,30,8"]'
                            '[default: %(default)s]',
                            default = GLO.GLBLlistTxtDasoVarsPorDefecto,
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
        # args, unknown = parser.parse_known_args()
        # print(f'\nqlidtwins-> Argumentos ignorados: {unknown}')

    except KeyboardInterrupt:
        # handle keyboard interrupt
        print('qlidtwins-> Revisar error en argumentos en linea de comandos (1).')
        program_name = 'qlidtwins'
        indent = len(program_name) * " "
        sys.stderr.write(f'{indent}   For help use:\n')
        sys.stderr.write(f'{indent}     help with only the main arguments:  python {program_name}.py -h\n')
        sys.stderr.write(f'{indent}     help with main and extra arguments: python {program_name}.py -e 1 -h')
        sys.exit(0)

    except Exception as e:
        print('qlidtwins-> Revisar error en argumentos en linea de comandos (2).')
        if TESTRUN:
            raise(e)
        program_name = 'qlidtwins'
        indent = len(program_name) * " "
        sys.stderr.write(f'{program_name}-> {repr(e)}\n')
        sys.stderr.write(f'{indent}   For help use:\n')
        sys.stderr.write(f'{indent}     help with only the main arguments:  python {program_name}.py -h\n')
        sys.stderr.write(f'{indent}     help with main and extra arguments: python {program_name}.py -e 1 -h')
        sys.exit(0)


    # ==========================================================================
    # Si no TRNS_LEER_EXTRA_ARGS, ArgumentParser no asigna
    # el valor por defecto a estos argumentos extras en linea de comandos.
    # Se asignan los valores del archivo cfg o por defecto.
    if not 'menuInteractivo' in dir(args):
        args.menuInteractivo = GLO.GLBLmenuInteractivoPorDefecto
    if not 'marcoCoordMiniX' in dir(args):
        args.marcoCoordMiniX = GLO.GLBLmarcoCoordMiniXPorDefecto
    if not 'marcoCoordMaxiX' in dir(args):
        args.marcoCoordMaxiX = GLO.GLBLmarcoCoordMaxiXPorDefecto
    if not 'marcoCoordMiniY' in dir(args):
        args.marcoCoordMiniY = GLO.GLBLmarcoCoordMiniYPorDefecto
    if not 'marcoCoordMaxiY' in dir(args):
        args.marcoCoordMaxiY = GLO.GLBLmarcoCoordMaxiYPorDefecto
    if not 'marcoPatronTest' in dir(args):
        args.marcoPatronTest = GLO.GLBLmarcoPatronTestPorDefecto
    if not 'nPatronDasoVars' in dir(args):
        args.nPatronDasoVars = GLO.GLBLnPatronDasoVarsPorDefecto
    if not 'rasterPixelSize' in dir(args):
        args.rasterPixelSize = GLO.GLBLrasterPixelSizePorDefecto
    if not 'radioClusterPix' in dir(args):
        args.radioClusterPix = GLO.GLBLradioClusterPixPorDefecto
    if not 'nivelSubdirExpl' in dir(args):
        args.nivelSubdirExpl = GLO.GLBLnivelSubdirExplPorDefecto
    if not 'outRasterDriver' in dir(args):
        args.outRasterDriver = GLO.GLBLoutRasterDriverPorDefecto
    if not 'outputSubdirNew' in dir(args):
        args.outputSubdirNew = GLO.GLBLoutputSubdirNewPorDefecto
    if not 'cartoMFErecorte' in dir(args):
        args.cartoMFErecorte = GLO.GLBLcartoMFErecortePorDefecto
    if not 'varsTxtFileName' in dir(args):
        args.varsTxtFileName = GLO.GLBLvarsTxtFileNamePorDefecto
    if not 'ambitoTiffNuevo' in dir(args):
        args.ambitoTiffNuevo = GLO.GLBLambitoTiffNuevoPorDefecto
    if not 'noDataTiffProvi' in dir(args):
        args.noDataTiffProvi = GLO.GLBLnoDataTiffProviPorDefecto
    if not 'noDataTiffFiles' in dir(args):
        args.noDataTiffFiles = GLO.GLBLnoDataTiffFilesPorDefecto
    if not 'noDataTipoDMasa' in dir(args):
        args.noDataTipoDMasa = GLO.GLBLnoDataTipoDMasaPorDefecto
    if not 'umbralMatriDist' in dir(args):
        args.umbralMatriDist = GLO.GLBLumbralMatriDistPorDefecto

    for myExtraArg in listaExtraArgs:
        if not myExtraArg in dir(args):
            print('qlidtwins-> Revisar codigo para que lea todos los argumentos extras por defecto.')
            sys.exit(0)
    return args


# ==============================================================================
def saveArgs(args):
    # argsFileName = sys.argv[0].replace('.py', '.args')
    argsFileName = (GLO.configFileNameCfg).replace('.cfg', '.args')
    # try:
    if True:
        with open(argsFileName, mode='w+') as argsFileControl:
            if 'mainAction' in dir(args):
                argsFileControl.write(f'-a={args.mainAction}\n')
            if 'rutaAscRaizBase' in dir(args):
                argsFileControl.write(f'-i={args.rutaAscRaizBase}\n')
            if 'rutaCompletaMFE' in dir(args):
                argsFileControl.write(f'-m={args.rutaCompletaMFE}\n')
            if 'cartoMFEcampoSp' in dir(args):
                argsFileControl.write(f'-f={args.cartoMFEcampoSp}\n')
            if 'patronVectrName' in dir(args):
                argsFileControl.write(f'-p={args.patronVectrName}\n')
            if 'patronLayerName' in dir(args):
                argsFileControl.write(f'-l={args.patronLayerName}\n')
            if 'testeoVectrName' in dir(args):
                argsFileControl.write(f'-t={args.testeoVectrName}\n')
            if 'testeoLayerName' in dir(args):
                argsFileControl.write(f'-y={args.testeoLayerName}\n')
            if 'verbose' in dir(args):
                argsFileControl.write(f'-v={__verbose__}\n')

            if 'menuInteractivo' in dir(args):
                argsFileControl.write(f'-0={args.menuInteractivo}\n')

            if 'marcoCoordMiniX' in dir(args):
                argsFileControl.write(f'-Z={args.marcoCoordMiniX}\n')
            if 'marcoCoordMaxiX' in dir(args):
                argsFileControl.write(f'-Z={args.marcoCoordMaxiX}\n')
            if 'marcoCoordMiniY' in dir(args):
                argsFileControl.write(f'-Z={args.marcoCoordMiniY}\n')
            if 'marcoCoordMaxiY' in dir(args):
                argsFileControl.write(f'-Z={args.marcoCoordMaxiY}\n')
            if 'marcoPatronTest' in dir(args):
                argsFileControl.write(f'-Z={args.marcoPatronTest}\n')

            if 'rasterPixelSize' in dir(args):
                argsFileControl.write(f'-X={args.rasterPixelSize}\n')
            if 'radioClusterPix' in dir(args):
                argsFileControl.write(f'-C={args.radioClusterPix}\n')
            if 'nPatronDasoVars' in dir(args):
                argsFileControl.write(f'-N={args.nPatronDasoVars}\n')
            if 'nivelSubdirExpl' in dir(args):
                argsFileControl.write(f'-L={args.nivelSubdirExpl}\n')
            if 'outRasterDriver' in dir(args):
                argsFileControl.write(f'-D={args.outRasterDriver}\n')
            if 'outputSubdirNew' in dir(args):
                argsFileControl.write(f'-S={args.outputSubdirNew}\n')
            if 'cartoMFErecorte' in dir(args):
                argsFileControl.write(f'-M={args.cartoMFErecorte}\n')
            if 'varsTxtFileName' in dir(args):
                argsFileControl.write(f'-R={args.varsTxtFileName}\n')
            if 'ambitoTiffNuevo' in dir(args):
                argsFileControl.write(f'-A={args.ambitoTiffNuevo}\n')
            if 'noDataTiffProvi' in dir(args):
                argsFileControl.write(f'-P={args.noDataTiffProvi}\n')
            if 'noDataTiffFiles' in dir(args):
                argsFileControl.write(f'-T={args.noDataTiffFiles}\n')
            if 'noDataTipoDMasa' in dir(args):
                argsFileControl.write(f'-O={args.noDataTipoDMasa}\n')
            if 'umbralMatriDist' in dir(args):
                argsFileControl.write(f'-U={args.umbralMatriDist}\n')

            for miDasoVar in args.listTxtDasoVars:
                argsFileControl.write(f'{miDasoVar}\n')
    # except:
    #     if __verbose__ > 1:
    #         print(f'\nqlidtwins-> No se ha podido crear el fichero de argumentos para linea de comandos: {argsFileName}')


# ==============================================================================
def creaConfigDict(
        args,
        tipoEjecucion=0,
    ):
    """
    Se crea el diccionario usando los argumentos leidos en linea de comandos
    o, en su defecto, los valores por defecto del fichero de configuracion
    o, en su defecto, los valores por defecto del modulo clidtwins_config.py
    """

    cfgDict = {}
    # Parametros de configuracion principales
    cfgDict['mainAction'] = args.mainAction
    if args.rutaAscRaizBase == '':
        cfgDict['rutaAscRaizBase'] = os.path.dirname(os.path.abspath(__file__))
    else:
        cfgDict['rutaAscRaizBase'] = args.rutaAscRaizBase

    cfgDict['rutaCompletaMFE'] = args.rutaCompletaMFE
    cfgDict['cartoMFEcampoSp'] = args.cartoMFEcampoSp

    cfgDict['patronVectrName'] = args.patronVectrName
    if args.patronLayerName == 'None':
        cfgDict['patronLayerName'] = None
    else:
        cfgDict['patronLayerName'] = args.patronLayerName
    cfgDict['testeoVectrName'] = args.testeoVectrName
    if args.testeoLayerName == 'None':
        cfgDict['testeoLayerName'] = None
    else:
        cfgDict['testeoLayerName'] = args.testeoLayerName


    if __verbose__ > 2:
        print(f'qlidtwins-> args.listTxtDasoVars de tipos {type(args.listTxtDasoVars)} -> {args.listTxtDasoVars}')
        print(f'\tEl primer argumento posicional tiene {len((args.listTxtDasoVars[0]).split(","))} elementos: {(args.listTxtDasoVars[0]).split(",")}')

    # args.listTxtDasoVars es una lista de cadenas (argumentos posicionales)
    if len((args.listTxtDasoVars[0]).split(',')) == 1:
        # Los argumentos posicionales son simplificados, solo incluyen FileTypeId
        # Los textos de la lista de textos se usa directamente son los FileTypeId
        # cfgDict['listLstDasoVars'] = args.listTxtDasoVars
        cfgDict['listaTxtDasoVarsFileTypes'] = args.listTxtDasoVars
        if __verbose__ > 2 and (tipoEjecucion == 1 or tipoEjecucion == 2):
            print(f'\nqlidtwins-> Los argumentos posicionales (listTxtDasoVars) son una secuencia de FileTypeId')
    else:
        args_listLstDasoVars = []
        # Argumentos posicionales completos: FileTypeId,NickName,RangoLinf,RangoLsup,NumClases,Movilidad,Ponderacion
        # La lista de textos se convierte a lista de listas y el primer elemento de esas listas es FileTypeId
        for numDasoVar, txtListaDasovar in enumerate(args.listTxtDasoVars):
            # Los argumentos posicionales son completos:
            # "FileTypeId, NickName, RangoLinf, RangoLsup, NumClases, Movilidad(0-100), Ponderacion(0-10)"
            listDasoVar = [item.strip() for item in txtListaDasovar.split(',')]
            if len(listDasoVar) <= 5:
                print(f'\nqlidtwins-> ATENCION: el argumento posicional (listTxtDasoVars) debe ser una')
                print(f'\t Secuencia (uno por variable) de cadenas de texto separados por espacios del tipo:')
                print(f'\t     texto1 texto2 ...')
                print(f'\t Los elementos de esta secuencia deben ser:')
                print(f'\t     Opcion a: identificadores de DLVs (FileTypeId). P. ej. alt95 fcc05 fcc03') 
                print(f'\t     Opcion b: una secuencia de cinco elementos separados por comas (sin espacios) del tipo:')
                print(f'\t         FileTypeId,NickName,RangoLinf,RangoLsup,NumClases,Movilidad,Ponderacion')
                print(f'\t         Ejemplo: {GLO.GLBLlistTxtDasoVarsPorDefecto}')
                print(f'\t-> La variable {numDasoVar} ({listDasoVar[0]}) solo tiene {len(listDasoVar)} elementos: {listDasoVar}')
                sys.exit(0)
            listDasoVar[2] = int(listDasoVar[2])
            listDasoVar[3] = int(listDasoVar[3])
            listDasoVar[4] = int(listDasoVar[4])
            listDasoVar[5] = int(listDasoVar[5])
            if len(listDasoVar) > 6:
                listDasoVar[6] = int(listDasoVar[6])
            else:
                listDasoVar.append(10)
            args_listLstDasoVars.append(listDasoVar)
        # La lista de textos se ha convertido a lista de listas
        cfgDict['listLstDasoVars'] = args_listLstDasoVars
    # ==========================================================================

    # ==========================================================================
    # Parametros de configuracion extra
    try:
        cfgDict['menuInteractivo'] = args.menuInteractivo
        cfgDict['marcoCoordMiniX'] = args.marcoCoordMiniX
        cfgDict['marcoCoordMaxiX'] = args.marcoCoordMaxiX
        cfgDict['marcoCoordMiniY'] = args.marcoCoordMiniY
        cfgDict['marcoCoordMaxiY'] = args.marcoCoordMaxiY
        cfgDict['marcoPatronTest'] = args.marcoPatronTest
        cfgDict['nPatronDasoVars'] = args.nPatronDasoVars
        cfgDict['rasterPixelSize'] = args.rasterPixelSize
        cfgDict['radioClusterPix'] = args.radioClusterPix
        cfgDict['nivelSubdirExpl'] = args.nivelSubdirExpl
        cfgDict['outRasterDriver'] = args.outRasterDriver
        cfgDict['outputSubdirNew'] = args.outputSubdirNew
        cfgDict['cartoMFErecorte'] = args.cartoMFErecorte
        cfgDict['varsTxtFileName'] = args.varsTxtFileName
        cfgDict['ambitoTiffNuevo'] = args.ambitoTiffNuevo
        cfgDict['noDataTiffProvi'] = args.noDataTiffProvi
        cfgDict['noDataTiffFiles'] = args.noDataTiffFiles
        cfgDict['noDataTipoDMasa'] = args.noDataTipoDMasa
        cfgDict['umbralMatriDist'] = args.umbralMatriDist
    except Exception as e:
        print(f'qlidtwins-> args: {list(myArgs for myArgs in dir(args) if not myArgs.startswith("__"))}')
        program_name = 'qlidtwins'
        indent = len(program_name) * " "
        sys.stderr.write(f'{program_name}-> {repr(e)}\n')
        if os.path.exists(GLO.configFileNameCfg):
            if 'object has no attribute' in repr(e):
                argumentoNoEncontrado = repr(e)[repr(e).index('object has no attribute') + len('object has no attribute') + 2: -3]
                sys.stderr.write(f'{indent}   Revisar si {GLO.configFileNameCfg} incluye el argumento {argumentoNoEncontrado}\n')
                sys.stderr.write(f'{indent}     {GLO.configFileNameCfg} debe incluir todos los parametros preceptivos (main & extra).\n')
            else:
                sys.stderr.write(f'{indent}   Revisar si el fichero de configuracion {GLO.configFileNameCfg} incluye todos los parametros preceptivos (main & extra).\n')
        else:
            sys.stderr.write(f'{indent}   Error desconocido al leer los parametros de configuracion en linea de argumentos y por defecto.\n')
        sys.stderr.write(f'{indent}   For help use:\n')
        sys.stderr.write(f'{indent}     help with only the main arguments:  python {program_name}.py -h\n')
        sys.stderr.write(f'{indent}     help with main and extra arguments: python {program_name}.py -e 1 -h')
        sys.exit(0)
    # ==========================================================================

    # cfgDict['marcoCoordMiniX'] = 318000
    # cfgDict['marcoCoordMaxiX'] = 322000
    # cfgDict['marcoCoordMiniY'] = 4734000
    # cfgDict['marcoCoordMaxiY'] = 4740000

    return cfgDict


# ==============================================================================
def mostrarConfiguracion(cfgDict):
    # configFileNameCfg = getConfigFileName()
    configFileNameCfg = GLO.configFileNameCfg

    print('\n{:_^80}'.format(''))
    if len(sys.argv) == 3:
        if os.path.exists(configFileNameCfg):
            infoConfiguracionUsada = f' (valores leidos del fichero de configuracion, {configFileNameCfg})'
        else:
            infoConfiguracionUsada = ' (valores "de fabrica" incluidos en codigo, clidtwins_config.py)'
    else:
        infoConfiguracionUsada = ' (valores leidos en linea de comandos o, si no van en linea de comandos, valores por defecto)'
    print(f'Parametros de configuracion principales{infoConfiguracionUsada}:')

    accionesPrincipales = [
        '1. Verificar analogia con un determinado patron dasoLidar.',
        '2. Generar raster con presencia de un determinado patron dasoLidar.'
    ]
    print('\t--> Accion: {}'.format(accionesPrincipales[cfgDict['mainAction'] - 1]))
    if 'listLstDasoVars' in cfgDict.keys():
        print('\t--> Listado de dasoVars [codigo fichero, nombre, limite inf, limite sup, num clases, movilidad_interclases (0-100), ponderacion (0-10)]:')
        for numDasoVar, listDasoVar in enumerate(cfgDict['listLstDasoVars']):
            print('\t\tVariable {}: {}'.format(numDasoVar, listDasoVar))
    elif 'listaTxtDasoVarsFileTypes' in cfgDict.keys():
        print('\t--> Listado de FileTypeId (identificadores de dasoVars:')
        for numDasoVar, FileTypeId in enumerate(cfgDict['listaTxtDasoVarsFileTypes']):
            print('\t\tVariable {}: {}'.format(numDasoVar, FileTypeId))
    print('\t--> Rango de coordenadas UTM:')

    if cfgDict['marcoPatronTest']:
        print('\t\tSe adopta la envolvente de los shapes de referenia (patron) y chequeo (testeo).')
        print('\t\tVer valores mas adelante.')
    elif (
        cfgDict['marcoCoordMiniX'] == 0
        or cfgDict['marcoCoordMaxiX'] == 0
        or cfgDict['marcoCoordMiniY'] == 0
        or cfgDict['marcoCoordMaxiY'] == 0
        ):
        print('\t\tNo se han establecido coordenadas para la zona de estudio.')
        print('\t\tSe adopta la envolvente de los ficheros con variables dasoLidar.')
    else:
        print(
            '\t\tX {:07f} - {:07f} -> {:04.0f} m:'.format(
                cfgDict['marcoCoordMiniX'], cfgDict['marcoCoordMaxiX'],
                cfgDict['marcoCoordMaxiX'] - cfgDict['marcoCoordMiniX']
            )
        )
        print(
            '\t\tY {:07f} - {:07f} -> {:04.0f} m:'.format(
                cfgDict['marcoCoordMiniY'], cfgDict['marcoCoordMaxiY'],
                cfgDict['marcoCoordMaxiY'] - cfgDict['marcoCoordMiniY']
            )
        )
    print('\t--> Ruta base (raiz) y ficheros:')
    print('\t\trutaAscRaizBase: {}'.format(cfgDict['rutaAscRaizBase']))
    print('\t\tpatronVectrName: {}'.format(cfgDict['patronVectrName']))
    print('\t\tpatronLayerName: {} {}'.format(cfgDict['patronLayerName'], type(cfgDict['patronLayerName'])))
    print('\t\ttesteoVectrName: {}'.format(cfgDict['testeoVectrName']))
    print('\t\ttesteoLayerName: {}'.format(cfgDict['testeoLayerName']))
    print('\t--> Cartografia de cubiertas (MFE):')
    print('\t\trutaCompletaMFE: {}'.format(cfgDict['rutaCompletaMFE']))
    print('\t\tcartoMFEcampoSp: {}'.format(cfgDict['cartoMFEcampoSp']))
    print('{:=^80}'.format(''))

    if __verbose__ > 1:
        print('\n{:_^80}'.format(''))
        print('__verbose__: {}'.format(__verbose__))
        if __verbose__ > 2:
            print('->> qlidtwins-> args:', args)
            # print('\t->> dir(args):', dir(args))
        print('->> Lista de dasoVars en formato para linea de comandos:')
        print('\t{}'.format(args.listTxtDasoVars))
        print('{:=^80}'.format(''))

        if TRNS_LEER_EXTRA_ARGS:
            infoConfiguracionUsada = ' (valores leidos en linea de comandos o, si no van en linea de comandos, valores por defecto)'
        else:
            if os.path.exists(configFileNameCfg):
                infoConfiguracionUsada = f' (valores leidos del fichero de configuracion, {configFileNameCfg})'
            else:
                infoConfiguracionUsada = ' (valores "de fabrica" incluidos en codigo, clidtwins_config.py)'
        print('\n{:_^80}'.format(''))
        print(f'Parametros de configuracion adicionales{infoConfiguracionUsada}:')
        print('\t--> menuInteractivo: {}'.format(cfgDict['menuInteractivo']))

        print('\t--> marcoCoordMiniX: {}'.format(cfgDict['marcoCoordMiniX']))
        print('\t--> marcoCoordMaxiX: {}'.format(cfgDict['marcoCoordMaxiX']))
        print('\t--> marcoCoordMiniY: {}'.format(cfgDict['marcoCoordMiniY']))
        print('\t--> marcoCoordMaxiY: {}'.format(cfgDict['marcoCoordMaxiY']))
        print('\t--> marcoPatronTest: {}'.format(cfgDict['marcoPatronTest']))
        print('\t--> nPatronDasoVars: {}'.format(cfgDict['nPatronDasoVars']))
        print('\t--> rasterPixelSize: {}'.format(cfgDict['rasterPixelSize']))
        print('\t--> radioClusterPix: {}'.format(cfgDict['radioClusterPix']))
        print('\t--> nivelSubdirExpl: {}'.format(cfgDict['nivelSubdirExpl']))
        print('\t--> outRasterDriver: {}'.format(cfgDict['outRasterDriver']))
        print('\t--> outputSubdirNew: {}'.format(cfgDict['outputSubdirNew']))
        print('\t--> cartoMFErecorte: {}'.format(cfgDict['cartoMFErecorte']))
        print('\t--> varsTxtFileName: {}'.format(cfgDict['varsTxtFileName']))
        print('\t--> ambitoTiffNuevo: {}'.format(cfgDict['ambitoTiffNuevo']))
        print('\t--> noDataTiffProvi: {}'.format(cfgDict['noDataTiffProvi']))
        print('\t--> noDataTiffFiles: {}'.format(cfgDict['noDataTiffFiles']))
        print('\t--> noDataTipoDMasa: {}'.format(cfgDict['noDataTipoDMasa']))
        print('\t--> umbralMatriDist: {}'.format(cfgDict['umbralMatriDist']))
        print('{:=^80}'.format(''))


# ==============================================================================
def clidtwinsUseCase(cfgDict):
    if __verbose__:
        print('\n{:_^80}'.format(''))
        if __verbose__ > 1:
            print('qlidtwins-> Creando objeto de la clase DasoLidarSource...')

    myDasolidar = DasoLidarSource(LCL_verbose=__verbose__)

    if __verbose__:
        print('{:=^80}'.format(''))
        print('\n{:_^80}'.format(''))
        if __verbose__ > 1:
            print('qlidtwins-> Ejecutando setRangeUTM...')

    myDasolidar.setRangeUTM(
        LCL_marcoCoordMiniX=cfgDict['marcoCoordMiniX'],
        LCL_marcoCoordMaxiX=cfgDict['marcoCoordMaxiX'],
        LCL_marcoCoordMiniY=cfgDict['marcoCoordMiniY'],
        LCL_marcoCoordMaxiY=cfgDict['marcoCoordMaxiY'],
    )

    if __verbose__:
        print('{:=^80}'.format(''))
        print('\n{:_^80}'.format(''))
        print('qlidtwins-> Ejecutando searchSourceFiles...')

    if (
        'listLstDasoVars' in cfgDict.keys()
        and type(cfgDict['listLstDasoVars'][0]) == list
    ):
        # los argumentos listaDasoVars son completos 
        myDasolidar.searchSourceFiles(
            LCL_listLstDasoVars=cfgDict['listLstDasoVars'],
            LCL_nPatronDasoVars=cfgDict['nPatronDasoVars'],  # opcional
            LCL_rutaAscRaizBase=cfgDict['rutaAscRaizBase'],
            LCL_nivelSubdirExpl=cfgDict['nivelSubdirExpl'],  # opcional
            LCL_outputSubdirNew=cfgDict['outputSubdirNew'],  # opcional
        )
    elif (
        'listaTxtDasoVarsFileTypes' in cfgDict.keys()
        and type(cfgDict['listaTxtDasoVarsFileTypes'][0]) == str
    ):
        # Los argumentos posicionales listaDasoVars solo tienen los FileTypeId
        myDasolidar.searchSourceFiles(
            LCL_listaTxtDasoVarsFileTypes=cfgDict['listaTxtDasoVarsFileTypes'],
            LCL_nPatronDasoVars=cfgDict['nPatronDasoVars'],  # opcional
            LCL_rutaAscRaizBase=cfgDict['rutaAscRaizBase'],
            LCL_nivelSubdirExpl=cfgDict['nivelSubdirExpl'],  # opcional
            LCL_outputSubdirNew=cfgDict['outputSubdirNew'],  # opcional
        )

    elif (
        # Esta situacion no debe darse, porque si los argumentos posicionales son de tipo
        # FileTypeId se guardan como listaTxtDasoVarsFileTypes y no como listLstDasoVars
        'listLstDasoVars' in cfgDict.keys()
        and type(cfgDict['listLstDasoVars'][0]) == str
    ):
        myDasolidar.searchSourceFiles(
            LCL_listaTxtDasoVarsFileTypes=cfgDict['listLstDasoVars'],
            LCL_nPatronDasoVars=cfgDict['nPatronDasoVars'],  # opcional
            LCL_rutaAscRaizBase=cfgDict['rutaAscRaizBase'],
            LCL_nivelSubdirExpl=cfgDict['nivelSubdirExpl'],  # opcional
            LCL_outputSubdirNew=cfgDict['outputSubdirNew'],  # opcional
        )
    else:
        print(f'\nqlidtwins-> Revisar los argumentos pasados en linea de comandos. sys.argv: <{sys.argv}>')
        sys.exit(0)

    if __verbose__:
        print('{:=^80}'.format(''))
        print('\n{:_^80}'.format(''))
        print('qlidtwins-> Ejecutando createMultiDasoLayerRasterFile...')
    myDasolidar.createMultiDasoLayerRasterFile(
        LCL_rutaCompletaMFE=cfgDict['rutaCompletaMFE'],
        LCL_cartoMFEcampoSp=cfgDict['cartoMFEcampoSp'],

        LCL_rasterPixelSize=cfgDict['rasterPixelSize'],
        # LCL_outRasterDriver=cfgDict['outRasterDriver'],
        # LCL_cartoMFErecorte=cfgDict['cartoMFErecorte'],
        # LCL_varsTxtFileName=cfgDict['varsTxtFileName'],
    )

    if __verbose__:
        print('{:=^80}'.format(''))
        print('\n{:_^80}'.format(''))
        print('qlidtwins-> Ejecutando analyzeMultiDasoLayerRasterFile...')
    myDasolidar.analyzeMultiDasoLayerRasterFile(
        LCL_patronVectrName=cfgDict['patronVectrName'],
        LCL_patronLayerName=cfgDict['patronLayerName'],
    )

    if __verbose__:
        print('{:=^80}'.format(''))

    if cfgDict['mainAction'] == 0 or cfgDict['menuInteractivo']:
        # Sin uso por el momento, probablemente quite esta opcion
        pass
    elif cfgDict['mainAction'] == 1:
        if __verbose__:
            print('\n{:_^80}'.format(''))
            print('qlidtwins-> Ejecutando chequearCompatibilidadConTesteoShape...')
        myDasolidar.chequearCompatibilidadConTesteoVector(
            LCL_testeoVectrName=cfgDict['testeoVectrName'],
            LCL_testeoLayerName=cfgDict['testeoLayerName'],
            )
    elif cfgDict['mainAction'] == 2:
        if __verbose__:
            print('\n{:_^80}'.format(''))
            print('qlidtwins-> Ejecutando generarRasterCluster...')
        myDasolidar.generarRasterCluster(
            LCL_radioClusterPix=cfgDict['radioClusterPix'],
        )

    if __verbose__ and cfgDict['mainAction']:
        print('{:=^80}'.format(''))

    print('\nqlidtwins-> Fin.')


# ==============================================================================
if __name__ == '__main__' or 'qlidtwins' in __name__:

    tipoEjecucion = checkRun()
    testRun()

    args = leerArgumentosEnLineaDeComandos()
    saveArgs(args)
    cfgDict = creaConfigDict(args, tipoEjecucion=tipoEjecucion)
    if __verbose__ or True:
        mostrarConfiguracion(cfgDict)

    clidtwinsUseCase(cfgDict)
