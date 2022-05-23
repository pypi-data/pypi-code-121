## @package segmentation.main
#  @subsection description How to run
#  The segmentation code is ran like this:
#
#  > python3 -m segmentation <npoints> <fibrasdir> <idsubj> <atlasdir> <atlasInformation> <result_path>
#   
#
import sys
import os
from pathlib import Path
from subprocess import run


## Variable that saves the absolute path of the file, so the executable /main can be run. It is not entered by the user.
## Variable que guarda la ruta absoluta del archivo, para poder correr el ejecutable /main. No es ingresado por el usuario.
pathname = os.path.dirname(__file__)
## Number of points at which the segmentation is done.
## Es el número de puntos a los que se hace la segmentación.
npoints = sys.argv[1]
## Path to the .bundles file that corresponds to the fascicles.
## Ruta al archivo .bundles que corresponde a los fascículos.
fibrasdir = sys.argv[2]
## ID of the subject that the fascicles belong to.
## ID del sujeto a quien pertenecen los fascículos.
idsubj = sys.argv[3]
## Path to the folder that contains the .bundles and .bundlesdata files of the atlas.
## Ruta al directorio que contiene los archivos .bundles y .bundlesdata del atlas.
atlasdir=sys.argv[4]
## Path to the .txt file that contains the atlas' information.
## Ruta al archivo .txt que contiene la información del atlas.
atlasInformation = sys.argv[5]
## Output directory path for the segmented fascicles of the subject.
## Directorio de salida para los fascículos segmentados del sujeto.
result_path = sys.argv[6]

run(["./main", npoints, fibrasdir, idsubj, atlasdir, atlasInformation, seg_resul, id_seg_result])




