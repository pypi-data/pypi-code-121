#  -*- coding: utf-8 -*-

"""
Convenience functions to make ArUco marker patterns
"""

import numpy

def makemarkerpattern_wholeboard(board):
    """
    draw a pattern of markers using cv2.aruco drawPlanarBoard
    """

    raise NotImplementedError
    #outsize = (32,32)
    #marginSize = 3
    #borderBits = 1

    #this is struggling, lets try doing it ourselves one marker at a time
    #image = aruco.drawPlanarBoard(board, outsize, marginSize, borderBits)

def makemarkerpattern_bymarker(board):
    """
    draw a pattern one marker at a time
    """
    print (board.dictionary)
    print (board.ids)
    print (board.objPoints)
    return 1


def float_to_int(array_in, min_scale = 1, max_scale = 100, increment = 1):
    """
    converts array_in to integers, with scaling to
    prevent loss of information
    :return: an integer array, and the scaling factor used.
    """
    good_scale = None
    array_out = numpy.copy(array_in)
    for scale in range (min_scale, max_scale, increment):
        scale_ok = True
        for element in numpy.nditer(array_in):
            if round(element * scale) != element * scale:
                scale_ok = False
                break
        if scale_ok:
            array_out *= scale
            good_scale = scale
            break

    return array_out, good_scale
