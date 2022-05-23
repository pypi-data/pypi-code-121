import os
from threading import local
import PySimpleGUI as SimGUI
import subprocess
import pathlib
import time
import logging


'''
Installing libraries:
Wiliot
Appdirs
Winshell

Checking if testerStationName and R2R_station_name are in System Variables , 
if it doesn't -> GUI will be opened to set the right names and it will be set.

It will set all the env folders for logs and create desktop shortcut for the logs.
'''


def set_new(tester_name, r2r_name):
    layout = [[SimGUI.Text("Do you want to change your environment?", key='question_txt')],
              [SimGUI.Text("Tester Name: "+str(tester_name), key='tester_name_txt')],
              [SimGUI.Text("R2R Name: "+str(r2r_name), key='r2r_name_txt')],
              [SimGUI.Button('Yes'), SimGUI.Button('No', button_color=('white', '#0e6251'))]]

    window = SimGUI.Window('Rechange environment', layout)
    submit = False

    while True:
        event, values = window.read()
        if event == 'Yes':
            submit = True
            break
        elif event == 'No':
            break
        elif event == SimGUI.WIN_CLOSED or event == 'Cancel': 
            print('User exited the program')
            window.close()
            exit()

    window.close()
    return submit



def def_env_values(tester_name, r2r_name):
    if tester_name is None:
        tester_name = ''
    if r2r_name is None:
        r2r_name = ''
    layout = [[SimGUI.Text("Please enter testers name", key='tester_name_txt'),
               SimGUI.Input(tester_name, key='tester_name_gui')],
               [SimGUI.Text("<company name> + _Station + <station number>", key='tester_name_gui_example')],
              [SimGUI.Text("Please enter r2r name", key='r2r_name_txt'),
               SimGUI.Input(r2r_name, key='r2r_name_gui')],
               [SimGUI.Text("<company name> + _Station + <station number>", key='r2r_name_gui_example')],
              [SimGUI.Text(size=(60, 3), key='-OUTPUT-')],
              [SimGUI.Button('Submit', button_color=('white', '#0e6251'))]]

    window = SimGUI.Window('Set Environments', layout)
    submit = False
    while True:
        event, values = window.read()

        if event == 'Submit':
            if ' ' in values['tester_name_gui'] or '/' in values['tester_name_gui'] or '\\' in values['tester_name_gui'] or ' ' in values['r2r_name_gui'] or '/' in values['r2r_name_gui'] or '\\' in values['r2r_name_gui']:          
                    window['-OUTPUT-'].update('Please dont use white spaces, / or \\')
                    submit = False
            else:
                    submit = True
        
        if submit:
            break

        if event == SimGUI.WIN_CLOSED or event == 'Cancel': 
            print('User exited the program')
            window.close()
            exit()

    window.close()
    return values


def env_init():
    reconfig = False
    tester_name = os.getenv('testerStationName')
    r2r_name = os.getenv('R2R_station_name')
    if tester_name is None or r2r_name is None:
        reconfig = True
    else:
        reconfig = set_new(tester_name, r2r_name)

    if reconfig:
        new_values = def_env_values(tester_name, r2r_name)
        os.environ['testerStationName'] = new_values['tester_name_gui']
        os.environ['R2R_station_name'] = new_values['r2r_name_gui']
        set_tester = 'setx testerStationName '+ str(new_values['tester_name_gui'])
        set_r2r = 'setx R2R_station_name '+ str(new_values['r2r_name_gui'])
        print('Please wait few second for environment set')
        try:
            subprocess.Popen(set_tester, shell=True).wait()
            subprocess.Popen(set_r2r, shell=True).wait()
            print('Done')
        except Exception:
            print('Problem with setting environment, please set in manually')


def dir_init():
    local_app_data = user_data_dir('offline','wiliot')
    logs_dir = os.path.join(local_app_data, 'logs')
    if not os.path.isdir(logs_dir):
        pathlib.Path(logs_dir).mkdir(parents=True, exist_ok=True)

    desktop = winshell.desktop()
    path = os.path.join(desktop,'logs_output.lnk')
    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortCut(path)
    #shortcut.WorkingDirectory = logs_dir
    shortcut.Targetpath = logs_dir
    shortcut.save()



def wiliot_init():
    print('Installing libraries')
    try:
        subprocess.Popen('pip install wiliot[advance]', shell=True).wait()
        subprocess.Popen('pip install appdirs', shell=True).wait()
        subprocess.Popen('pip install winshell', shell=True).wait()
        subprocess.Popen('pip install pypiwin32', shell=True).wait()
        print('Done')

    except Exception:
        print('Problem with installing libraries')


if __name__ == "__main__":
    wiliot_init()
    from appdirs import *
    import winshell
    from win32com.client import Dispatch
    import win32api
    env_init()
    dir_init()
    print('Computer will be reseted in 3 seconds')
    time.sleep(3)
    try:
        win32api.InitiateSystemShutdown()
    except Exception:
        os.system("shutdown /r /t 1")

