import os
import sys
import threading
import subprocess
import PySimpleGUI as sg
import time
import psutil
import signal

"""
                             dP                       dP   
                             88                       88   
88d888b. .d8888b. .d8888b. d8888P .d8888b. .d8888b. d8888P 
88'  `88 Y8ooooo. 88'  `88   88   88ooood8 Y8ooooo.   88   
88.  .88       88 88.  .88   88   88.  ...       88   88   
88Y888P' `88888P' `8888P88   dP   `88888P' `88888P'   dP   
88                     .88                                 
dP                 d8888P

    Copyright 2021, 2022 PySimpleGUI.org
"""


DEFAULT_OUTPUT_SIZE = (80,5)


'''
M""MMMMM""MM          dP                               MM""""""""`M                                     
M  MMMMM  MM          88                               MM  mmmmmmmM                                     
M         `M .d8888b. 88 88d888b. .d8888b. 88d888b.    M'      MMMM dP    dP 88d888b. .d8888b. .d8888b. 
M  MMMMM  MM 88ooood8 88 88'  `88 88ooood8 88'  `88    MM  MMMMMMMM 88    88 88'  `88 88'  `"" Y8ooooo. 
M  MMMMM  MM 88.  ... 88 88.  .88 88.  ... 88          MM  MMMMMMMM 88.  .88 88    88 88.  ...       88 
M  MMMMM  MM `88888P' dP 88Y888P' `88888P' dP          MM  MMMMMMMM `88888P' dP    dP `88888P' `88888P' 
MMMMMMMMMMMM             88                            MMMMMMMMMMMM                                     
                         dP
'''


def get_file_list_dict():
    """
    Returns dictionary of files
    Key is short filename
    Value is the full filename and path

    :return: Dictionary of demo files
    :rtype: Dict[str:str]
    """

    demo_path = get_demo_path()
    demo_files_dict = {}
    for dirname, dirnames, filenames in os.walk(demo_path):
        for filename in filenames:
            if filename.endswith('.py') or filename.endswith('.pyw'):
                fname_full = os.path.join(dirname, filename)
                if filename not in demo_files_dict.keys():
                    demo_files_dict[filename] = fname_full
                else:
                    # Allow up to 100 dupicated names. After that, give up
                    for i in range(1, 100):
                        new_filename = f'{filename}_{i}'
                        if new_filename not in demo_files_dict:
                            demo_files_dict[new_filename] = fname_full
                            break

    return demo_files_dict


def get_file_list():
    """
    Returns list of filenames of files to display
    No path is shown, only the short filename

    :return: List of filenames
    :rtype: List[str]
    """
    return sorted(list(get_file_list_dict().keys()))


def get_demo_path():
    """
    Get the top-level folder path
    :return: Path to list of files using the user settings for this file.  Returns folder of this file if not found
    :rtype: str
    """
    demo_path = sg.user_settings_get_entry('-test script folder-', os.path.dirname(__file__))

    return demo_path


def get_theme():
    """
    Get the theme to use for the program
    Value is in this program's user settings. If none set, then use PySimpleGUI's global default theme
    :return: The theme
    :rtype: str
    """
    # First get the current global theme for PySimpleGUI to use if none has been set for this program
    try:
        global_theme = sg.theme_global()
    except:
        global_theme = sg.theme()
    # Get theme from user settings for this program.  Use global theme if no entry found
    user_theme = sg.user_settings_get_entry('-theme-', '')
    if user_theme == '':
        user_theme = global_theme
    return user_theme


"""
MP""""""`MM            dP     dP   oo                            
M  mmmmm..M            88     88                                 
M.      `YM .d8888b. d8888P d8888P dP 88d888b. .d8888b. .d8888b. 
MMMMMMM.  M 88ooood8   88     88   88 88'  `88 88'  `88 Y8ooooo. 
M. .MMM'  M 88.  ...   88     88   88 88    88 88.  .88       88 
Mb.     .dM `88888P'   dP     dP   dP dP    dP `8888P88 `88888P' 
MMMMMMMMMMM                                         .88          
                                                d8888P
"""

interpreter_dict = {'3.4': '-P34-', '3.5': '-P35-', '3.6': '-P36-', '3.7': '-P37-',
                    '3.8': '-P38-', '3.9': '-P39-', '3.10': '-P310-', '3.11': '-P311-'}


def settings_window():
    """
    Show the settings window.
    This is where the folder paths and program paths are set.
    Returns True if settings were changed

    :return: True if settings were changed
    :rtype: (bool)
    """

    try:  # in case running with old version of PySimpleGUI that doesn't have a global PSG settings path
        global_theme = sg.theme_global()
    except:
        global_theme = ''


    layout = [[sg.T('Program Settings', font='_ 25'), sg.Image(data=sg.EMOJI_BASE64_PONDER)],
              [sg.Frame('Path to Tree of Test Programs', [[sg.Combo(sorted(sg.user_settings_get_entry('-folder names-', [])),
                                                                    default_value=sg.user_settings_get_entry('-test script folder-', get_demo_path()),
                                                                    size=(50, 1), key='-FOLDERNAME-'),
                                                           sg.FolderBrowse('Folder Browse', target='-FOLDERNAME-'), sg.B('Clear History')]], font='_ 14')],
              [sg.Frame('Python Interpreters (path to each python executible)', [[sg.Radio('', 1, k=interpreter_dict[k] + '-RADIO-'), sg.T(k, s=(5, 1)),
                                                                                  sg.In(sg.user_settings_get_entry(interpreter_dict[k], ''),
                                                                                        k=interpreter_dict[k]), sg.FileBrowse()] for k in interpreter_dict],
                        font='_ 14')],

              [sg.Frame('Theme', [[sg.T('Leave blank to use global default'), sg.T(global_theme)],
                                  [sg.Combo([''] + sg.theme_list(), sg.user_settings_get_entry('-theme-', ''), readonly=True, k='-THEME-')]], font='_ 14')],

              [sg.Frame('Text Output Settings', [[sg.T('Font and size (e.g. Courier 10) for the output:'),
                                                  sg.In(sg.user_settings_get_entry('-output font-', 'Courier 10'), k='-MLINE FONT-', s=(15, 1))],
                                                 [sg.T('Output size Width x Height in chars'),
                                                  sg.In(sg.user_settings_get_entry('-output width-', DEFAULT_OUTPUT_SIZE[0]), k='-MLINE WIDTH-', s=(4, 1)),
                                                  sg.T(' x '),
                                                  sg.In(sg.user_settings_get_entry('-output height-', DEFAULT_OUTPUT_SIZE[1]), k='-MLINE HEIGHT-', s=(4, 1))]],
                        font='_ 14')],

              [sg.Frame('Double-click Will...', [[sg.R('Run', 2, sg.user_settings_get_entry('-dclick runs-', False), k='-DCLICK RUNS-'),
                                                  sg.R('Edit', 2, sg.user_settings_get_entry('-dclick edits-', False), k='-DCLICK EDITS-'),
                                                  sg.R('Nothing', 2, sg.user_settings_get_entry('-dclick none-', False), k='-DCLICK NONE-')]], font='_ 14')],

              [sg.B('Ok', bind_return_key=True), sg.B('Cancel')],
              ]

    window = sg.Window('Settings', layout, finalize=True)

    current_interpreter = sg.user_settings_get_entry('-current interpreter-', list(interpreter_dict.keys())[0])
    window[interpreter_dict[current_interpreter] + '-RADIO-'].update(True)
    settings_changed = False

    while True:
        event, values = window.read()
        if event in ('Cancel', sg.WIN_CLOSED):
            break
        if event == 'Ok':
            sg.user_settings_set_entry('-test script folder-', values['-FOLDERNAME-'])
            sg.user_settings_set_entry('-theme-', values['-THEME-'])
            sg.user_settings_set_entry('-folder names-', list(set(sg.user_settings_get_entry('-folder names-', []) + [values['-FOLDERNAME-'], ])))
            sg.user_settings_set_entry('-dclick runs-', values['-DCLICK RUNS-'])
            sg.user_settings_set_entry('-dclick edits-', values['-DCLICK EDITS-'])
            sg.user_settings_set_entry('-dclick nothing-', values['-DCLICK NONE-'])
            sg.user_settings_set_entry('-P34-', values['-P34-'])
            sg.user_settings_set_entry('-P35-', values['-P35-'])
            sg.user_settings_set_entry('-P36-', values['-P36-'])
            sg.user_settings_set_entry('-P37-', values['-P37-'])
            sg.user_settings_set_entry('-P38-', values['-P38-'])
            sg.user_settings_set_entry('-P39-', values['-P39-'])
            sg.user_settings_set_entry('-P310-', values['-P310-'])
            sg.user_settings_set_entry('-P311-', values['-P311-'])
            sg.user_settings_set_entry('-output font-', values['-MLINE FONT-'])
            sg.user_settings_set_entry('-output width-', values['-MLINE WIDTH-'])
            sg.user_settings_set_entry('-output height-', values['-MLINE HEIGHT-'])
            sg.user_settings_set_entry('-current interpreter-', *[k for k in interpreter_dict if values[interpreter_dict[k] + '-RADIO-']])
            sg.user_settings_set_entry('-interpreter path-', values[interpreter_dict[sg.user_settings_get_entry('-current interpreter-')]])
            settings_changed = True
            break
        elif event == 'Clear History':
            sg.user_settings_set_entry('-folder names-', [])
            window['-FOLDERNAME-'].update(values=[], value='')

    window.close()
    return settings_changed


'''
M"""""`'"""`YM          dP                   M""""""""M          dP       
M  mm.  mm.  M          88                   Mmmm  mmmM          88       
M  MMM  MMM  M .d8888b. 88  .dP  .d8888b.    MMMM  MMMM .d8888b. 88d888b. 
M  MMM  MMM  M 88'  `88 88888"   88ooood8    MMMM  MMMM 88'  `88 88'  `88 
M  MMM  MMM  M 88.  .88 88  `8b. 88.  ...    MMMM  MMMM 88.  .88 88.  .88 
M  MMM  MMM  M `88888P8 dP   `YP `88888P'    MMMM  MMMM `88888P8 88Y8888' 
MMMMMMMMMMMMMM                               MMMMMMMMMM
'''


def make_output_tab(tab_text, key, tab_key):
    tab = sg.Tab(tab_text, [[sg.Multiline(
        size=(sg.user_settings_get_entry('-output width-', DEFAULT_OUTPUT_SIZE[0]), sg.user_settings_get_entry('-output height-', DEFAULT_OUTPUT_SIZE[1])),
        expand_x=True, expand_y=True, write_only=True, key=key, auto_refresh=True, font=sg.user_settings_get_entry('-output font-', 'Courier 10')), ],
                            [sg.B('Copy To Clipboard', k=('-COPY-', key)), sg.B('Clear', k=('-CLEAR-', key)), sg.B('Close Tab', k=('-CLOSE-', tab_key))]],
                 right_click_menu=['', [f'Close::{tab_key}', 'Exit']], k=tab_key, )

    return tab

'''
M"""""`'"""`YM          dP                
M  mm.  mm.  M          88                
M  MMM  MMM  M .d8888b. 88  .dP  .d8888b. 
M  MMM  MMM  M 88'  `88 88888"   88ooood8 
M  MMM  MMM  M 88.  .88 88  `8b. 88.  ... 
M  MMM  MMM  M `88888P8 dP   `YP `88888P' 
MMMMMMMMMMMMMM                            
                                          
M""MMM""MMM""M oo                dP                     
M  MMM  MMM  M                   88                     
M  MMP  MMP  M dP 88d888b. .d888b88 .d8888b. dP  dP  dP 
M  MM'  MM' .M 88 88'  `88 88'  `88 88'  `88 88  88  88 
M  `' . '' .MM 88 88    88 88.  .88 88.  .88 88.88b.88' 
M    .d  .dMMM dP dP    dP `88888P8 `88888P' 8888P Y8P  
MMMMMMMMMMMMMM
'''

def make_window(sp_to_mline_dict=None, sp_to_filename=None):
    """
    Creates the main window
    :return: The main window object
    :rtype: (sg.Window)
    """
    icon = b'iVBORw0KGgoAAAANSUhEUgAAADIAAAAyCAYAAAAeP4ixAAAABmJLR0QA/wD/AP+gvaeTAAADv0lEQVRogd2Zy0tVQRzHP1bkDa1NtCgtolQIKwlcCJYtFRRsX0S7+gPS9tqDFlmLHhi1lhSF8LHQDKQnLYOgiMRF5SbBV6SW3Ra/3+mcbuece+aeOcfsC8O5zuM739/M/GZ+M0I6KAf6gHlN/UBlSn1bQzkwA2Rz0gxQtoa6jNGHCB9EhJcBQ5r3YA11GWMeEe0d/d2aN2urkw22iELwXb9FPmU/UujfGnqQ0R9C/KUcGNa8njXU9RdG+duRTdOTuCL8ptsUWQscEFPLJksioHAhVgYiDWdPBTZnxNYSKwg2ZuSpBY7Yzm4Tzg6UVP1Q/Dc+kqQh6zbi9S6VKBGv1aVlE15hUSLedWFIlIh3XTi7I9BGCJQ6vCPcT3DE2+dT/59BIyJqSv+uAr7g7+wVWmdK8xpTVRqCDPAWEdXuyS9DHHtOUx+uEWjdrLbNpKI0Dy4igt4BxQbtNgNvtG1nArqMcARYAX4CDQW0b9C2K8q1JigGXiMj2h2Dp1s5XmM2o9ZwRQVMAltj8JQA75XrsgVdRqhDXkBWgeMW+Oo9fEct8EVCBtdJr1nk7cLdxbZY5A3EDeK/muRL15M2ogGZ/qQNWaWwXTASMshZkQWuJtWJcjvnUiIH5eWkO1AU4/rgRdvkNcihFbSrHAJGgGVNw0B1jP6OaV8rwOEYPH9gA/AKGaGbPuWHcO8f3jRHPGNuKc9LLF0HzijhR/wPvhEtH0WCwgpgDDeMLxTbgE/KczoGDwClwGclO+lTXgQsafl+T36F5n0j3mieUp5PqqVgXFKiZwGCvIZ4Q/RKgg1pAcaBRWBBfzcH9F8EPFeuSwVZAOwAviJOVxtSz7n5jSEGVAKPcB8fvHBCfr8UFMrXqoavqskYHdrBQJ561Yhj5wqbBQ546rVo/hJwHtipqQ13VoNmZkDLO0yNKMV9l6qPUL8acewlZDkN5hgB8Fj5zvu0d26L4wH89bhX5ZIIen7jnDZ8YdIoD5wteqdP2S4tmw9p/0LrnPUrDHoOatXvvWgaU8F9/baG1srBNGL9HotCxpWzzafsAuFLC2Cv1pk26dRxvlh7dw6acZ29HVlOuxAjlgl3dpAYzGkfGZPaKGzbLQSdmG+/Dg5qvQ8mHd7RRr2mSiOgGVlCC+Q/EL3oVU23TTrbj5y8zguJzSVmilLgrmpZBPaZErQgI5ZFnj+7gCbkBdHmP1FzsUn7aNI+nafXBaLNnC9qgAmSv9rmSxPkuZdEjUzrgBPICVsFbAc2RmxrilXkBH+HBKsPkTtJKH4B042N7RpiCBAAAAAASUVORK5CYII='
    sg.set_options(icon=icon)
    theme = get_theme()
    if not theme:
        theme = sg.OFFICIAL_PYSIMPLEGUI_THEME
    sg.theme(theme)
    # First the window layout...2 columns

    filter_tooltip = "Filter files\nEnter a string in box to narrow down the list of files.\nFile list will update with list of files with string in filename."

    regression_frame_layout = [[sg.CBox('Kill test after', default=False, k='-REGRESSION TEST-'), sg.Input(15, s=4, k='-REGRESSION SECONDS-'), sg.Text('seconds (regression tests)')],
                               [sg.T('Run'), sg.I(5, s=4, k='-REGRESSION BLOCK SIZE-'), sg.T('programs at a time'), sg.B('Run Regression')]]

    left_col = sg.Column([
        [sg.T('Test Cases (choose 1 or more)', font='_ 15')],
        [sg.Listbox(values=get_file_list(), select_mode=sg.SELECT_MODE_EXTENDED, size=(50, 20), bind_return_key=True, key='-DEMO LIST-', expand_x=True,
                    expand_y=True)],
        # [sg.Listbox(values=get_file_list(), select_mode=sg.SELECT_MODE_EXTENDED, size=(50,20), bind_return_key=True, key='-DEMO LIST-')],
        [sg.Text('Filter (F1):', tooltip=filter_tooltip), sg.Input(size=(25, 1), focus=True, enable_events=True, key='-FILTER-', tooltip=filter_tooltip),
         sg.T(size=(15, 1), k='-FILTER NUMBER-')],
        [sg.Button('Run'), sg.B('Edit'), sg.B('Clear'), ],
        [sg.CBox('Show test program\'s output in this window', default=True, k='-SHOW OUTPUT-')],
        [sg.Frame('Regression Testing', regression_frame_layout)],
    ], element_justification='l', expand_x=True, expand_y=True)

    output_tab_layout = [
        [sg.Multiline(
            size=(sg.user_settings_get_entry('-output width-', DEFAULT_OUTPUT_SIZE[0]), sg.user_settings_get_entry('-output height-', DEFAULT_OUTPUT_SIZE[1])),
            write_only=True, key='-ML-', reroute_stdout=False, reroute_stderr=False, echo_stdout_stderr=True, reroute_cprint=True, auto_refresh=True,
            expand_x=True, expand_y=True, font=sg.user_settings_get_entry('-output font-', 'Courier 10'))],
        [sg.B('Copy To Clipboard', key=('-COPY-', '-ML-')), sg.B('Clear', k=('-CLEAR-', '-ML-'))]]

    bottom_right = [
        [sg.Button('Edit Me (this program)'), sg.B('Settings'), sg.Button('Exit')],
        [sg.T('PySimpleGUI ver ' + sg.version.split(' ')[0] + '  tkinter ver ' + sg.tclversion_detailed, font='Default 8', pad=(0, 0))],
        [sg.T('Python ver ' + sys.version, font='Default 8', pad=(0, 0))]]


    # tab1 = sg.Tab('Output',old_right_col, k='-TAB1-',  expand_x=True, expand_y=True)
    tab1 = sg.Tab('Output', output_tab_layout, k='-TAB1-', )

    tab_group = sg.TabGroup([[tab1, ]], k='-TABGROUP-', expand_x=True, expand_y=True, font='_ 8', tab_location='topleft')
    # tab_group = sg.TabGroup([[tab1,]], k='-TABGROUP-')

    right_col = [[tab_group]] + bottom_right
    choose_folder_at_top = sg.pin(sg.Column([[sg.T('Click settings to set top of your tree or choose a previously chosen folder'),
                                              sg.Combo(sorted(sg.user_settings_get_entry('-folder names-', [])),
                                                       default_value=sg.user_settings_get_entry('-test script folder-', ''), size=(50, 30), key='-FOLDERNAME-',
                                                       enable_events=True, readonly=True)]], pad=(0, 0), k='-FOLDER CHOOSE-', expand_x=True, expand_y=True))

    # interpreter_list = sorted(list(interpreter_dict.keys()))
    # interpreter_keys = sorted(list(interpreter_dict.values()))
    interpreter_list = []
    for key, value in interpreter_dict.items():
        if sg.user_settings_get_entry(value, ''):
            interpreter_list.append(key)

    interpreter_list = sorted(interpreter_list)
    if len(interpreter_list) == 0:      # no interpreters found in settings file, so set one using the currently running version of Python
        default_interpreter = f'{sys.version_info[0]}.{sys.version_info[1]}'
        sg.user_settings_set_entry('-current interpreter-', default_interpreter)
        sg.user_settings_set_entry('-interpreter path-', sys.executable)
        key = interpreter_dict[default_interpreter]
        sg.user_settings_set_entry(key, sys.executable)
    else:
        default_interpreter = interpreter_list[0]
    choose_interpreter_at_top = sg.pin(sg.Column([[sg.T('Launch using'),
                                                   sg.Combo(sorted(interpreter_list),
                                                            default_value=sg.user_settings_get_entry('-current interpreter-', default_interpreter),
                                                            size=(4, 10), key='-INTERPRETER TOP-', enable_events=True, readonly=True)]],
                                                 pad=(0, 0), k='-INTEPRETER CHOOSE-', expand_x=True, expand_y=True))

    # ----- Full layout -----

    layout = [[sg.Image(data=icon, background_color='white'), sg.Text('psgtest - Simple Python Testing', font='Any 20')],
              [sg.T('Testing Using Interpreter: ' + sg.user_settings_get_entry('-current interpreter-', ''), font='Default 12', k='-CURRENT INTERPRETER-'),
               sg.T('Interpreter path: ' + sg.user_settings_get_entry('-interpreter path-', ''), font='Default 12', k='-INTERPRETER PATH-')],
              [choose_folder_at_top, choose_interpreter_at_top],
              # [sg.Column([[left_col],[ lef_col_find_re]], element_justification='l',  expand_x=True, expand_y=True), sg.Column(right_col, element_justification='c', expand_x=True, expand_y=True)],
              [sg.Pane([sg.Column([[left_col]], element_justification='l', expand_x=True, expand_y=True),
                        sg.Column(right_col, element_justification='c', expand_x=True, expand_y=True)], orientation='h', relief=sg.RELIEF_SUNKEN, k='-PANE-',
                       expand_x=True, expand_y=True), sg.Sizegrip()],
              # [sg.Pane([sg.Column([[left_col]], element_justification='l',  expand_x=True, expand_y=True), sg.Column(right_col, element_justification='c', expand_x=True, expand_y=True) ], orientation='h', relief=sg.RELIEF_SUNKEN, k='-PANE-'), sg.Sizegrip()],
              ]

    # --------------------------------- Create Window ---------------------------------
    window = sg.Window('psgtest', layout, finalize=True, resizable=True, use_default_focus=False, right_click_menu=sg.MENU_RIGHT_CLICK_EDITME_VER_LOC_EXIT)
    # window.set_min_size(window.size)

    # Rebild the dynamically created tabs
    if sp_to_mline_dict is not None:
        for sp in sp_to_mline_dict.keys():
            mline_key = sp_to_mline_dict[sp]
            file = sp_to_filename[sp]
            tab = make_output_tab(file, mline_key, file)
            window['-TABGROUP-'].add_tab(tab)

    window.bind('<F1>', '-FOCUS FILTER-')
    window.set_min_size(window.size)
    return window

'''
M""""""""M dP                                        dP 
Mmmm  mmmM 88                                        88 
MMMM  MMMM 88d888b. 88d888b. .d8888b. .d8888b. .d888b88 
MMMM  MMMM 88'  `88 88'  `88 88ooood8 88'  `88 88'  `88 
MMMM  MMMM 88    88 88       88.  ... 88.  .88 88.  .88 
MMMM  MMMM dP    dP dP       `88888P' `88888P8 `88888P8 
MMMMMMMMMM
'''

def the_thread(window: sg.Window, sp: subprocess.Popen):
    """
    The thread that's used to run the subprocess so that the GUI can continue and the stdout/stderror is collected

    :param window:
    :param sp:
    :return:
    """

    window.write_event_value('-THREAD-', (sp, '===THEAD STARTING==='))
    window.write_event_value('-THREAD-', (sp, '----- STDOUT & STDERR Follows ----'))
    for line in sp.stdout:
        oline = line.decode().rstrip()
        window.write_event_value('-THREAD-', (sp, oline))
    window.write_event_value('-THREAD-', (sp, '===THEAD DONE==='))

def timer_thread(window: sg.Window, sp: subprocess.Popen, seconds):
    """
    The thread that's used to run the subprocess so that the GUI can continue and the stdout/stderror is collected

    :param window:
    :param sp:
    :param seconds:
    :return:
    """

    time.sleep(seconds)
    window.write_event_value('-TIMER THREAD-', (sp, '===KILL THREAD==='))


def kill_proc(pid, sig=signal.SIGTERM, include_parent=True,
                   timeout=None, on_terminate=None):
    """Kill a process tree (including grandchildren) with signal
    "sig" and return a (gone, still_alive) tuple.
    "on_terminate", if specified, is a callabck function which is
    called as soon as a child terminates.
    """
    if pid == os.getpid():
        raise RuntimeError("I refuse to kill myself")
    parent = psutil.Process(pid)
    parent.send_signal(sig)
    sg.Print(f'tried killing {pid} with parent {parent}')

def kill_proc_tree(pid, sig=signal.SIGTERM, include_parent=True,
                   timeout=None, on_terminate=None):
    """Kill a process tree (including grandchildren) with signal
    "sig" and return a (gone, still_alive) tuple.
    "on_terminate", if specified, is a callabck function which is
    called as soon as a child terminates.
    """
    try:
        if pid == os.getpid():
            raise RuntimeError("I refuse to kill myself")
        parent = psutil.Process(pid)
        children = parent.children(recursive=True)
        if include_parent:
            children.append(parent)
        for p in children:
            p.send_signal(sig)
        gone, alive = psutil.wait_procs(children, timeout=timeout,
                                        callback=on_terminate)
    except:
        return (None, None)
    return (gone, alive)



'''
M"""""`'"""`YM          oo          
M  mm.  mm.  M                      
M  MMM  MMM  M .d8888b. dP 88d888b. 
M  MMM  MMM  M 88'  `88 88 88'  `88 
M  MMM  MMM  M 88.  .88 88 88    88 
M  MMM  MMM  M `88888P8 dP dP    dP 
MMMMMMMMMMMMMM
'''

def main():
    """
    The main program that contains the event loop.
    It will call the make_window function to create the window.
    """

    def start_batch(list_of_programs):
        current_interpreter = sg.user_settings_get_entry('-current interpreter-')
        if current_interpreter != values['-INTERPRETER TOP-']:
            current_interpreter = values['-INTERPRETER TOP-']
        interpreter_path = sg.user_settings_get_entry(interpreter_dict[current_interpreter])
        # interpreter_path = sg.user_settings_get_entry('-interpreter path-', '')
        if interpreter_path:
            sg.cprint(f"Running using {current_interpreter}....", c='white on green', end='')
            sg.cprint('')
        else:
            sg.cprint('*** No valid interpreter has been chosen ***', c='white on red')
            return
        for file in list_of_programs:
            file_to_run = str(file_list_dict[file])
            sg.cprint(file_to_run, text_color='white', background_color='purple')
            pipe_output = values['-SHOW OUTPUT-']
            sp = sg.execute_command_subprocess(interpreter_path, f'"{file_to_run}"', pipe_output=pipe_output)
            # sg.Print(sg.obj_to_string_single_obj(sp))
            sp_to_filename[sp] = file
            mline_key = f'{file}-MLINE-'
            if mline_key not in sp_to_mline_dict.values():
                tab = make_output_tab(file, mline_key, file)
                window['-TABGROUP-'].add_tab(tab)
            else:
                if not window[file].visible:
                    window[file].update(visible=True)
            sp_to_mline_dict[sp] = mline_key
            window[file].select()
            # Let a thread handle getting all the output so that the rest of the GUI keep running
            if pipe_output:
                threading.Thread(target=the_thread, args=(window, sp), daemon=True).start()
                if values['-REGRESSION TEST-']:
                    try:
                        seconds = float(values['-REGRESSION SECONDS-'])
                    except:
                        seconds = 15
                    threading.Thread(target=timer_thread, args=(window, sp, seconds), daemon=True).start()

    sg.user_settings_filename(filename='psgtest.json')
    os.environ['PYTHONUNBUFFERED'] = '1'
    file_list_dict = get_file_list_dict()
    file_list = get_file_list()
    try:
        window = make_window()
    except Exception as e:
        if sg.popup_yes_no('Exception making the Window... likely means a corrupt settings file.', f'Exception: {e}', 'Do you want to clear your settings?', title='Exception making window') == 'Yes':
            sg.user_settings_delete_filename(filename='psgtest.json')
            sg.popup_auto_close('Settings file deleted... please restart the program')
            exit()
        else:
            sg.popup_auto_close('Cancelling operation... See what you can do about the problem...')
            exit()
    window['-FILTER NUMBER-'].update(f'{len(file_list)} files')
    sp_to_mline_dict = {}
    sp_to_filename = {}
    counter = 0
    dont_close_tab = {}
    regression_programs = []
    while True:
        event, values = window.read()
        # print(event, values)

        counter += 1
        if event in (sg.WINDOW_CLOSED, 'Exit'):
            break
        if event == '-DEMO LIST-':  # if double clicked (used the bind return key parm)
            if sg.user_settings_get_entry('-dclick runs-'):
                event = 'Run'
            elif sg.user_settings_get_entry('-dclick edits-'):
                event = 'Edit'
        # if event is a tuple, then it's from a tab and will have the button and the mline in the tab
        if isinstance(event, tuple):
            button = event[0]
            mline_key = event[1]
            if button == '-CLEAR-':
                window[mline_key].update('')
            elif button == '-COPY-':
                sg.clipboard_set(window[mline_key].get().rstrip())
                sg.cprint('Copied to clipboard', key=mline_key)
            elif button == '-CLOSE-':
                window[event[1]].update(visible=False)
        elif event == '-TIMER THREAD-':
            thread_sp = values['-TIMER THREAD-'][0]
            sg.cprint(f'killing pid {thread_sp.pid}')
            kill_proc_tree(thread_sp.pid)
            file = sp_to_filename[thread_sp]
            if not dont_close_tab.get(file, False):
                window[file].update(visible=False)
        elif event == '-THREAD-':                   # received message from thread to display
            thread_sp = values['-THREAD-'][0]
            line = values['-THREAD-'][1]
            sg.cprint(line, key=sp_to_mline_dict[thread_sp])
            if 'Traceback' in line:
                sg.popup_error(f'Error during running {sp_to_filename[thread_sp]}', non_blocking=True)
                dont_close_tab[sp_to_filename[thread_sp]] = True
            if line == '===THEAD DONE===':
                sg.cprint(f'{sp_to_filename[thread_sp]}', c='white on purple')
                sg.cprint(f'Completed', c='white on green')
                if regression_programs:
                    next_program = regression_programs[0]
                    start_batch((next_program,))
                    del regression_programs[0]
        elif event == 'Run':
            start_batch(values['-DEMO LIST-'])
            #
            # current_interpreter = sg.user_settings_get_entry('-current interpreter-')
            # if current_interpreter != values['-INTERPRETER TOP-']:
            #     current_interpreter = values['-INTERPRETER TOP-']
            # interpreter_path = sg.user_settings_get_entry(interpreter_dict[current_interpreter])
            # # interpreter_path = sg.user_settings_get_entry('-interpreter path-', '')
            # if interpreter_path:
            #     sg.cprint(f"Running using {current_interpreter}....", c='white on green', end='')
            #     sg.cprint('')
            #     start_batch(values['-DEMO LIST-'])
            # else:
            #     sg.cprint('*** No valid interpreter has been chosen ***', c='white on red')
        elif event.startswith('Edit Me'):
            sg.execute_editor(__file__)
        elif event == 'Version':
            sg.cprint(sg.get_versions(), c='white on green')
        elif event == '-FILTER-':
            new_list = [i for i in file_list if values['-FILTER-'].lower() in i.lower()]
            window['-DEMO LIST-'].update(new_list)
        elif event == '-FOCUS FILTER-':
            window['-FILTER-'].set_focus()
        elif event == 'Settings':
            if settings_window() is True:
                pipe_output = values['-SHOW OUTPUT-']
                window.close()
                window = make_window(sp_to_mline_dict, sp_to_filename)
                file_list_dict = get_file_list_dict()
                file_list = get_file_list()
                window['-FILTER NUMBER-'].update(f'{len(file_list)} files')
                window['-SHOW OUTPUT-'].update(pipe_output)
        elif event == 'Clear':
            file_list = get_file_list()
            window['-FILTER-'].update('')
            window['-FILTER NUMBER-'].update(f'{len(file_list)} files')
            window['-DEMO LIST-'].update(file_list)
            window['-ML-'].update('')
        elif event == '-FOLDERNAME-':
            sg.user_settings_set_entry('-test script folder-', values['-FOLDERNAME-'])
            file_list_dict = get_file_list_dict()
            file_list = get_file_list()
            window['-DEMO LIST-'].update(values=file_list)
            window['-FILTER NUMBER-'].update(f'{len(file_list)} files')
            window['-ML-'].update('')
            window['-FILTER-'].update('')
        elif event == '-INTERPRETER TOP-':
            interpreter_path = sg.user_settings_get_entry(interpreter_dict[values['-INTERPRETER TOP-']], '')
            sg.user_settings_set_entry('-current interpreter-', values['-INTERPRETER TOP-'])
            sg.user_settings_set_entry('-interpreter path-', interpreter_path)
            window['-CURRENT INTERPRETER-'].update('Testing Using Interpreter: ' + sg.user_settings_get_entry('-current interpreter-', ''))
            window['-INTERPRETER PATH-'].update('Interpreter path: ' + sg.user_settings_get_entry('-interpreter path-', ''))
        elif event == 'Edit':
            for file in values['-DEMO LIST-']:
                sg.cprint('EDITING: ', c='white on green')
                sg.cprint(f'{file_list_dict[file]}', c='white on purple')
                sg.execute_editor(file_list_dict[file])
        elif event.startswith('Close'):
            tab_key = event[event.index("::") + 2:]
            window[tab_key].update(visible=False)
            # tab_to_close_key = values['-TABGROUP-']
            # window[tab_to_close_key].update(visible=False)
        elif event == 'Version':
            sg.cprint(sg.get_versions(), c='white on green')
            sg.popup_scrolled(sg.get_versions(), non_blocking=True)
        elif event == 'Edit Me':
            sg.execute_editor(__file__)
        elif event == 'File Location':
            sg.cprint('This Python file is:', __file__, c='white on green')
        elif event == 'Run Regression':
            window['-REGRESSION TEST-'].update(True)
            values['-REGRESSION TEST-'] = True
            regression_programs = values['-DEMO LIST-']
            # start the first batch
            num_to_run = int(values['-REGRESSION BLOCK SIZE-'])
            start_batch(regression_programs[:num_to_run])
            del regression_programs[:num_to_run]
    window.close()




if __name__ == '__main__':
    main()