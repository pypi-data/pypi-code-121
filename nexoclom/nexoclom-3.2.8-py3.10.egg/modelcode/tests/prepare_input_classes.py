import os
import pickle
import glob
from nexoclom import Input, __file__ as basefile

basepath = os.path.dirname(basefile)

inputfiles = glob.glob(os.path.join(os.path.dirname(__file__), 'test_data',
                                    'inputfiles', '*.input'))
inputs = []
for inputfile in inputfiles:
    input_ = Input(inputfile)

    # Correct the surfaceinteraction.mapfile path
    if ((input_.surfaceinteraction.sticktype == 'surface map') and
        (input_.surfaceinteraction.mapfile != 'default')):
        # put correct surfaceinteraction.mapfile path
        input_.surfaceinteraction.mapfile = os.path.join(basepath, 'modelcode',
            'tests', 'test_data', 'sticking_maps',
            os.path.basename(input_.surfaceinteraction.mapfile))
    else:
        pass
    
    # Correct the spatialdist.mapfile path
    if ((input_.spatialdist.type == 'surface map') and
        (input_.spatialdist.mapfile != 'default')):
        # put correct spatialdist.mapfile path
        input_.spatialdist.mapfile = os.path.join(basepath, 'modelcode', 'tests',
                                                  'test_data', 'surface_maps',
                                                  os.path.basename(input_.spatialdist.mapfile))
    else:
        pass
    
    inputs.append(input_)

with open('test_data/input_classes_data.pkl', 'wb') as f:
    pickle.dump((inputfiles, inputs), f)