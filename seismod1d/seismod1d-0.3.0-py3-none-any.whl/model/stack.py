import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression


def get_intercept_gradient(traces, theta, max_angle=25):

    # Returns intercept and gradient stacks of AVA gather

    # initiate output
    nt, nth = traces.shape
    intercept_stack = np.zeros(nt)
    gradient_stack = np.zeros(nt)

    # remove data above max angle
    traces = traces[:, theta <= max_angle]
    theta = theta[theta <= max_angle]

    # return if empty
    if len(traces) == 0:
        return intercept_stack, gradient_stack

    # create scaled angle vector
    theta_scaled = np.sin(theta * (np.pi / 180)) ** 2

    # loop through all time samples and derive intercept/gradient from linear fit
    ii = 0
    for row in traces:
        xx = theta_scaled.reshape((-1, 1))
        yy = row
        model = LinearRegression().fit(xx, yy)
        intercept_stack[ii] = model.intercept_
        gradient_stack[ii] = model.coef_
        ii = ii + 1

    # return intercept/gradient
    return intercept_stack, gradient_stack


def get_eei_stack(intercept_stack, gradient_stack, rotation_angle_deg):

    # get angle in radians
    th_rad = rotation_angle_deg * (np.pi / 180)

    # create rotated stack
    eei_stack = np.cos(th_rad) * intercept_stack + np.sin(th_rad) * gradient_stack

    # return ei stack
    return eei_stack


def get_angle_stack(traces, theta, angle_min=0, angle_max=30):

    # get angle stack
    angle_stack = traces[:, (theta >= angle_min) & (theta <= angle_max)].mean(axis=1)

    # return ei stack
    return angle_stack


def get_avo_stacks(traces, theta, avo_stack_opt):

    # returns a set of stacks in a pandas dataframe

    # initiate output
    avo_stacks = pd.DataFrame()

    # get size of input
    nt, nth = traces.shape

    # create near and far stacks
    avo_stacks["NEAR"] = get_angle_stack(
        traces,
        theta,
        angle_min=avo_stack_opt["near_theta_min"],
        angle_max=avo_stack_opt["near_theta_max"],
    )
    avo_stacks["FAR"] = get_angle_stack(
        traces,
        theta,
        angle_min=avo_stack_opt["far_theta_min"],
        angle_max=avo_stack_opt["far_theta_max"],
    )
    avo_stacks["FULL"] = get_angle_stack(
        traces,
        theta,
        angle_min=avo_stack_opt["full_theta_min"],
        angle_max=avo_stack_opt["full_theta_max"],
    )
    # avo_stacks['NEAR'] = traces[:, (theta >= avo_stack_opt['near_theta_min']) & (theta <= avo_stack_opt['near_theta_max'])].mean(axis = 1)
    # avo_stacks['FAR'] = traces[:, (theta >= avo_stack_opt['far_theta_min']) & (theta <= avo_stack_opt['far_theta_max'])].mean(axis = 1)

    # create intercept/gradient stacks
    intercept_stack, gradient_stack = get_intercept_gradient(
        traces, theta, max_angle=avo_stack_opt["max_angle_int_grad"]
    )
    avo_stacks["INT"] = intercept_stack
    avo_stacks["GRAD"] = gradient_stack

    # get EEI stacks
    avo_stacks["LITHO"] = get_eei_stack(
        intercept_stack, gradient_stack, avo_stack_opt["litho_rot_angle"]
    )
    avo_stacks["FLUID"] = get_eei_stack(
        intercept_stack, gradient_stack, avo_stack_opt["fluid_rot_angle"]
    )
    avo_stacks["VPVS"] = get_eei_stack(
        intercept_stack, gradient_stack, avo_stack_opt["vpvs_rot_angle"]
    )
    avo_stacks["SI"] = get_eei_stack(
        intercept_stack, gradient_stack, avo_stack_opt["si_rot_angle"]
    )

    return avo_stacks
