#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: José Sánchez-Gallego (gallegoj@uw.edu)
# @Date: 2019-11-11
# @Filename: adaptors.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)


def rh_dwyer(raw_value):
    """Returns Dwyer sensor relative humidity (RH) from a raw register value.

    Range is 0-100%.

    """

    # Humidity linear calibration = 100 / (2^15 - 1)
    RH0 = 0.0
    RHs = 100.0 / (2**15 - 1)

    return (RH0 + RHs * float(raw_value), "percent")


def t_dwyer(raw_value):
    """Returns Dwyer sensor temperature from a raw register value.

    Range is -30C to +70C.

    """

    # Temperature linear calibration = 100 / (2^15 - 1)
    T0 = -30.0
    Ts = 100.0 / (2**15 - 1)

    return (T0 + Ts * float(raw_value), "degC")


def rtd(raw_value):
    """Converts platinum RTD (resistance thermometer) output to degrees C.

    The temperature resolution is 0.1C per ADU, and the temperature range
    is -273C to +850C. The 16-bit digital number wraps below 0C to
    2^16-1 ADU. This handles that conversion.

    """

    tempRes = 0.1  # Module resolution is 0.1C per ADU
    tempMax = 850.0  # Maximum temperature for a Pt RTD in deg C
    wrapT = tempRes * (2**16 - 1)  # ADU wrap at 0C to 2^16-1

    temp = tempRes * raw_value
    if temp > tempMax:
        temp -= wrapT

    return (temp, "degC")


def rtd10(raw_value):
    """Convert platinum RTD output to degrees C.

    The conversion is simply ``0.1 * raw_value``.

    """

    return (float(raw_value) / 10.0, "degC")


def voltage(raw_value, v_min=0, v_max=10, res=32760, gain=1):
    """Converts a raw value to a voltage measurement.

    ``V = raw_value / res * (v_max - v_min) * gain``

    """

    return (float(raw_value) / res * (v_max - v_min) * gain, "V")


def linear(raw_value, min, max, range_min, range_max, unit=None):
    """A general adaptor for a linear sensor.

    ``M = min + raw_value / (range_max - range_min) * (max - min)``

    """

    return (
        min + float(raw_value - range_min) / (range_max - range_min) * (max - min),
        unit,
    )


def proportional(raw_value, factor, unit=None):
    """Applies a proportional factor."""

    return (float(raw_value) * factor, unit)


def pwd(raw_value, unit=None):
    """Pulse Width Modulator (PWM) output.

    The register is a 16-bit word as usual, but the module does not use the 5 LSBs.
    So, 10-bit resolution on the PWM value (MSB is for sign and is fixed).
    0-100% duty cycle maps to 0 to 32736 decimal value in the register.

    ``PWD = 100 * raw_value / (2**15 - 1)``


    """

    return (100 * float(raw_value) / (2**15 - 1), unit)


def flow(raw_value, meter_gain=1):
    """Flow meter conversion.

    ``flow_rate = meter_gain * (raw_value - 3276) / 3276``

    """

    return (meter_gain * (float(raw_value) - 3276) / 3276, "l/min")
