#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np


def generate_decay_model(t, lam_true):
    def model(lam=np.array([[lam_true]])):
        if isinstance(lam, float) or isinstance(lam, int):
            lam = np.array([[lam]])
        initial_cond = 0.75
        rate = lam[:, 0].reshape(-1, 1)
        response = initial_cond * np.exp(np.outer(rate, -t))
        # this allows support for simpler 1D plotting.
        if response.shape[0] == 1:
            return response.ravel()
        return response

    return model


def generate_temporal_measurements(measurement_hertz=100, start_time=1, end_time=3):
    num_measure = measurement_hertz * (end_time - start_time)
    return np.linspace(start_time, end_time, num_measure)


def generate_spatial_measurements(
    num_measure, xmin=0.05, xmax=0.95, ymin=0.05, ymax=0.95
):
    sensors = np.random.rand(num_measure, 2)  # noqa: E221
    sensors[:, 0] = xmin + (xmax - xmin) * sensors[:, 0]  # x_0 location
    sensors[:, 1] = ymin + (ymax - ymin) * sensors[:, 1]  # x_1 location
    return sensors


def generate_rotation_map(qnum=10, orth=True):
    if orth:
        vec = np.linspace(0, np.pi, qnum + 1)[0:-1]
    else:
        vec = np.linspace(0, np.pi, qnum)
    matrix_entries = [[np.sin(theta), np.cos(theta)] for theta in vec]
    return np.array(matrix_entries).reshape(qnum, 2)
