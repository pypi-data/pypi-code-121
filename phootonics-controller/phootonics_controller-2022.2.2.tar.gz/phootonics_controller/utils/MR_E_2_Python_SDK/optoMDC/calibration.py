# -*- coding: utf-8 -*-
"""
Created by gregory on 17.03.16

Copyright 2016 Alpes Lasers SA, Neuchatel, Switzerland
"""

import logging
import numbers
import math

logger = logging.getLogger(__name__)

__author__ = 'gregory'
__copyright__ = "Copyright 2016, Alpes Lasers SA"


def validate_calibration(calibration):
    error = False
    if not isinstance(calibration, list):
        error = True
    else:
        for tuple in calibration:
            if len(tuple) != 2 or not isinstance(tuple[0], numbers.Number) or tuple[0] < 0 \
                    or not isinstance(tuple[1], numbers.Number) or tuple[1] < 0:
                error = True
                break
    if error:
        raise ValueError('The calibration must be given as a list of pairs angle, wavelength,'
                         'e.g. [(350, 1500), (351, 1512), ...])')


def _angle_delta(angle1, angle2):
    delta = math.fmod(angle1 - angle2, 360.0)
    if delta > 180.0:
        return delta - 360.0
    elif delta < -180.0:
        return delta + 360.0
    return delta


def _reduced_angle(angle):
    reduced = math.fmod(angle, 360.0)
    if reduced < 0:
        return reduced + 360.0
    return reduced


def angle_for_wavelength(calibration, wavelength):
    prev_angle, prev_wl = None, None
    for angle, wl in calibration:
        if prev_wl is not None:
            cpd = float(wavelength - prev_wl)
            wcd = float(wl - wavelength)
            if cpd * wcd >= 0:
                s = cpd / float(wl - prev_wl)
                return _reduced_angle(prev_angle + s * _angle_delta(angle, prev_angle))
        prev_angle, prev_wl = angle, wl
    raise ValueError('The desired wavelength is outside of the calibration range.')


def wavelength_for_angle(calibration, current_angle):
    prev_angle, prev_wl = None, None
    for angle, wl in calibration:
        if prev_angle is not None:
            cpd = _angle_delta(current_angle, prev_angle)
            acd = _angle_delta(angle, current_angle)
            if cpd * acd >= 0:
                s = cpd / _angle_delta(angle, prev_angle)
                return prev_wl + s * (wl - prev_wl)
        prev_angle, prev_wl = angle, wl
    raise ValueError('The given angle is outside of the calibration range.')

if __name__ == '__main__':
    test_calibration = [
        (309.5, 5089.73),
        (309.0, 5126.55),
        (308.5, 5163.52),
        (308.0, 5199.6),
        (307.5, 5234.88),
        (307.0, 5269.71),
        (306.5, 5305.75),
        (306.0, 5341.4),
        (305.5, 5376.71),
        (305.0, 5410.91),
        (304.5, 5444.79),
        (304.0, 5479.02),
        (303.5, 5513.56),
        (303.0, 5547.3),
        (302.5, 5576.99),
        (302.0, 5610.65),
        (301.5, 5641.1),
        (300.5, 5701.11),
        (300.0, 5730.07),
        (299.5, 5759.29),
        (299.0, 5789.03),
        (298.5, 5817.98),
        (298.0, 5847.06),
        (297.5, 5874.83),
        (297.0, 5902.25),
        (301.0, 5671.68),
        (296.5, 5929.32),
        (296.0, 5957.04),
        (295.5, 5983.46),
        (295.0, 6009.48),
        (294.5, 6034.35),
        (294.0, 6058.87),
        (293.5, 6082.37),
        (293.0, 6105.56), ]

    import numpy as np
    lines = ["angle [deg],wavelength [nm]"]
    for angle in np.arange(309.5, 293, -0.001):
         lines.append("{:.4f},{:.2f}".format(angle, wavelength_for_angle(test_calibration, angle)))
    with open("calibration.csv", 'w') as fp:
        fp.write('\n'.join(lines))
    test_calibration = list(reversed(test_calibration))
    angle = angle_for_wavelength(test_calibration, 5701.12)
    print(angle)
    print(wavelength_for_angle(test_calibration, angle))
