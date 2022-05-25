""" helper functions for manipulating surfaces """

__author__ = 'Ivan Kondov'
__email__ = 'ivan.kondov@kit.edu'
__copyright__ = 'Copyright 2018, Karlsruhe Institute of Technology'

import numpy as np

def modify_surface_atom(slab, symbol, offset=None):
    """ modify surface atom by specified offset """

    info = slab.info.get('adsorbate_info', {})
    spos = np.array([0.0, 0.0])
    if offset is not None:
        spos += np.asarray(offset, float)

    if 'cell' in info:
        cell = info['cell']
    else:
        cell = slab.get_cell()[:2, :2]

    pos = np.dot(spos, cell)

    # get the z-coordinate:
    if 'top layer atom index' in info:
        atom = info['top layer atom index']
    else:
        atom = slab.positions[:, 2].argmax()
        if 'adsorbate_info' not in slab.info:
            slab.info['adsorbate_info'] = {}
        slab.info['adsorbate_info']['top layer atom index'] = atom

    zcoord = slab.positions[atom, 2]
    distances = slab.positions - np.array([pos[0], pos[1], zcoord])
    indices = np.argwhere(np.isclose(np.linalg.norm(distances, axis=1), 0))
    for index in list(indices.flatten()):
        slab[index].set('symbol', symbol)
