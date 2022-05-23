# -*- coding: utf-8 -*-
from external_cavity.controllers.driver_utils.MR_E_2_Python_SDK.optoMDC.mre2 import MRE2Board
mre2 = MRE2Board(port='/dev/ttyACM0', verbose=True)  # this will connect and synchronize all channel with the firmware
mirror = mre2.Mirror
from time import sleep
from external_cavity.controllers.driver_utils.MR_E_2_Python_SDK.optoKummenberg.tools.systems_registers_tools import get_registers
import math

# TODO: write initialisation function trying to reconnect and reinitializing, busy while performing commands

def set_xy_control_mode_both_axes():
    current_control_mode_x = mirror.Channel_0.GetControlMode()
    if current_control_mode_x != 2:
        mirror.Channel_0.SetControlMode(2)
    current_control_mode_y = mirror.Channel_1.GetControlMode()
    if current_control_mode_y != 2:
        mirror.Channel_1.SetControlMode(2)


def get_current_xy_position():
    current_position_x = mirror.Channel_0.StaticInput.GetXY()
    current_position_y = mirror.Channel_1.StaticInput.GetXY()
    return current_position_x[0], current_position_y[0]


def move_to_xy_position(posx, posy):
        if posx**2+posy**2 <= 1.0:
            mirror.Channel_0.StaticInput.SetXY(posx)
            mirror.Channel_1.StaticInput.SetXY(posy)
        else:
            Exception ('XY position out of range, x² + y² should be <= 1.0')


def move_along_x_stepwise_to_position(target_x, step, delay):
        x, y = get_current_xy_position()
        if target_x < x:
            step_x = -step
        else:
            step_x = step
        distance_x = abs(target_x - x)
        x_0 = 0
        while x_0 + abs(step_x) <= distance_x:
            x, y = get_current_xy_position()
            move_to_xy_position(x + step_x, y)
            sleep(delay)
            xcurr, ycurr = get_current_xy_position()
            x_0 = x_0 + abs(step_x)
            print(xcurr, ycurr)


def move_along_x_stepwise_from_a_to_b(posx_a, posx_b, step, delay):
    mirror.Channel_0.StaticInput.SetAsInput()
    x, y = get_current_xy_position()
    move_to_xy_position(posx_a,y)
    if posx_b < posx_a:
        step_x = -step
    else:
        step_x = step
    distance_x = abs(posx_b-posx_a)
    x_0 = 0
    while x_0 + abs(step_x) <= distance_x:
        x, y = get_current_xy_position()
        move_to_xy_position(x + step_x, y)
        sleep(delay)
        xcurr, ycurr = get_current_xy_position()
        x_0 = x_0 + abs(step_x)
        print(xcurr, ycurr)


def move_along_y_stepwise_to_position(target_y, step, delay):
        x, y = get_current_xy_position()
        if target_y < y:
            step_y = -step
        else:
            step_y = step
        distance_y = abs(target_y - y)
        y_0 = 0
        while y_0 + abs(step_y) <= distance_y:
            x, y = get_current_xy_position()
            move_to_xy_position(x, y + step_y)
            sleep(delay)
            xcurr, ycurr = get_current_xy_position()
            y_0 = y_0 + abs(step_y)
            print(xcurr, ycurr)


def sweep_along_x_from_a_to_b(start_angle, stop_angle, speed, n_repetitions):
    start_position = convert_angles_deg_to_position_x(start_angle)
    print(start_position)
    stop_position= convert_angles_deg_to_position_x(stop_angle)
    print(stop_position)
    speed_conv=convert_angles_deg_to_position_x(speed)
    mirror.Channel_0.StaticInput.SetXY(start_position)
    sleep(5)
    sig_gen = mre2.Mirror.Channel_0.SignalGenerator
    sig_gen.SetAsInput()
    frequency =float(1/(abs(stop_position-start_position)/speed_conv))
    sig_gen.SetUnit(2)
    sig_gen.SetShape(0)
    sig_gen.SetFrequency(frequency)
    amplitude = float(abs(stop_position-start_position))
    sig_gen.SetAmplitude(amplitude)
    sig_gen.SetCycles(n_repetitions)
    sig_gen.Run()


def convert_position_to_angles_xy_deg(posx, posy):
    tan_50=math.tan(math.radians(50))
    angle_x= math.degrees(math.atan(posx * tan_50))
    angle_y = math.degrees(math.atan(posy * tan_50))
    return angle_x, angle_y


def convert_angles_deg_to_position_xy(degx, degy):
    tan_50=math.tan(math.radians(50))
    posx = math.tan(math.radians(degx))/tan_50
    posy = math.tan(math.radians(degy))/tan_50
    return posx, posy

def convert_x_position_to_angles_deg(pos):
    tan_50 = math.tan(math.radians(50))
    angle = math.degrees(math.atan(pos * tan_50))
    return angle

def convert_angles_deg_to_position_x(angle):
    tan_50 = math.tan(math.radians(50))
    pos = math.tan(math.radians(angle)) / tan_50
    return pos


def is_not_out_of_bounds(position_x):
    y= mre2.Mirror.OpticalFeedback.get_register('y')[0]
    if (position_x**2 + y**2)<= 1.0:
        return True
    else:
        return False


def move_rel(increment):
    current_position_x = float(mre2.Mirror.OpticalFeedback.get_register('x')[0])
    current_angle = convert_x_position_to_angles_deg(current_position_x)
    target_angle = current_angle + increment
    target_position= convert_angles_deg_to_position_x(target_angle)
    if is_not_out_of_bounds(target_position):
        mre2.Mirror.Channel_0.StaticInput.SetXY(target_position)
    else:
        print('out of bounds')


if __name__ == '__main__':
    start_position = convert_angles_deg_to_position_x(0)
    print(start_position)
    end_position = convert_angles_deg_to_position_x(6)
    print(end_position)
    conv_velocity = convert_angles_deg_to_position_x(0.5)
    frequency = float(1 / ((abs(end_position - start_position) / conv_velocity)))
    print(frequency)
    amplitude = float(abs(end_position - start_position)) /2
    print(amplitude)
    offset = (1/frequency)/4
    print(offset)




