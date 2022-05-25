import os
import os.path
import sys
from pathlib import Path
import time
import json
import yaml
from ipywidgets import Button, HBox, VBox, Layout, ToggleButton
from IPython.display import HTML, display, clear_output, Markdown as md, JSON, Javascript, FileLink, Image, display_javascript, display_html, display_json
import ipywidgets as widgets
from ipywidgets import Layout
from ipyfilechooser import FileChooser
from json2html import *
from fabric2 import Connection
import subprocess
from wfgenes.core.BUILTIN import transfer_files
import site
from wfgenes import wfgenes_gui


wfgenes_path = os.path.join(site.getsitepackages()[0], 'wfgenes')
if wfgenes_gui.default_path.selected_path is not None:  
    default_path = wfgenes_gui.default_path.selected_path
else:
    default_path = wfgenes_path    


wfgenes_path = os.path.join(site.getsitepackages()[0], 'wfgenes')
fig_path = os.path.join(wfgenes_path, 'fig')
info_path = os.path.join(wfgenes_path, 'info')


text_input_layout = Layout(width='90%')

style = {'description_width': 'initial'}

# Choose python model's path
model_path = FileChooser('')
model_path.default_path = default_path
model_path.default_filename = ''
model_path.use_dir_icons = True
model_path.filter_pattern = ['*.py']
model_path.title = '<b>Path to the python model:</b>'


plus_lib = widgets.Button(
    tooltip='Transfer additional module(s) to remote machines',
    icon='plus',
    style=style,
    layout=Layout(
        width='100px'),
    description='Modules',
    title='add modules')
plus_lib_output = widgets.Output()

refresh_lib_button = widgets.Button(
    tooltip='Clear module list',
    icon='refresh',
    style=style,
    layout=Layout(
        width='40px'),
    description='')
refresh_lib_button_output = widgets.Output()


input_button = widgets.Button(
    tooltip='Locate inputs(s)',
    icon='plus',
    style=style,
    layout=Layout(
        width='100px'),
    description='Inputs')
input_button_output = widgets.Output()

refresh_input_button = widgets.Button(
    tooltip='Clear input list',
    icon='refresh',
    style=style,
    layout=Layout(
        width='40px'),
    description='')
refresh_input_button_output = widgets.Output()


info_button = widgets.ToggleButton(
    tooltip='Show/Hide Hint',
    icon='info',
    style=style,
    layout=Layout(
        width='60px'),
    description='Hint')
info_button_output = widgets.Output()


user = widgets.Textarea(
    value='th7356',
    placeholder='xy1234',
    description='Username',
    tooltip='Username on the remote cluster',
    layout=text_input_layout,
    disabled=False)

host = widgets.Textarea(
    value='horeka.scc.kit.edu',
    placeholder='hostname.domainname',
    description='Hostname',
    tooltip='Hostname of the remote cluster',
    layout=text_input_layout,
    disabled=False)

pre_launch_command = widgets.Textarea(
    value='',
    placeholder='module load xyz or Conda activate myenv',
    description='Command : Setup the environment before submitting job',
    tooltip='Remote configuration command',
    layout=text_input_layout,
    disabled=False)

launchdir = widgets.Textarea(
    value='/home/hk-project-test-sdlmat/th7356/test_wfgenes',
    placeholder='/absolute/path/to/launchdir',
    description='Launchdir',
    tooltip='Directory in that nodes will be executed',
    layout=text_input_layout
)


syspath_textarea = widgets.Textarea(
    placeholder='Type something',
    description='<b>Path file:</b>',
    description_tooltip='Edit to modify the graph',
    disabled=False,
    style=style,
    layout=Layout(width='100%', height='1000px')
)

pool_type = widgets.Dropdown(
    options=['local_threads', 'local_processes', 'slurm'],
    value='local_threads',
    description='<b>Pool type:<b>',
    disabled=False,
    style=style
)

pool_type_output = widgets.Output()

walltime = widgets.Text(
    value='00:30:00',
    description='<b>Wall time(queue)<b>',
    disabled=False,
    style=style
)

partition = widgets.Text(
    value='dev_cpuonly',
    placeholder='',
    description='<b>Partition(queue)<b>',
    disabled=False,
    style=style
)


memory = widgets.BoundedIntText(
    value=100,
    min=30,
    max=20000,
    step=1,
    description='<b> Total memory per job (GB): <b>',
    disabled=False,
    style=style
)


scale_nodes = widgets.BoundedIntText(
    value=1,
    min=1,
    step=1,
    description='<b>Number of nodes:<b>',
    disabled=False,
    style=style
)

workers_nodes = widgets.BoundedIntText(
    value=1,
    min=1,
    max=10000,
    step=1,
    description='<b>Workers(Processes) per node:<b>',
    disabled=False,
    style=style
)

cpu_per_node = widgets.BoundedIntText(
    value=1,
    min=1,
    max=1000,
    step=1,
    description='<b>CPUs per node:<b>',
    disabled=False,
    style=style
)


threads_number = widgets.BoundedIntText(
    value=1,
    min=1,
    step=1,
    description='<b>Maximum local threads:<b>',
    disabled=False,
    style=style
)
threads_number_output = widgets.Output()

processes_number = widgets.BoundedIntText(
    value=1,
    min=1,
    step=1,
    description='<b>Maximum number of parallel process:<b>',
    disabled=False,
    style=style
)
processes_number_output = widgets.Output()

cpu_per_process = widgets.BoundedIntText(
    value=1,
    min=1,
    step=1,
    description='<b>Number of CPU for each process :<b>',
    disabled=False,
    style=style
)
cpu_per_process_output = widgets.Output()


# Button RUN MODEL
run_model = widgets.Button(
    tooltip='Run model',
    icon='play',
    description='Run model',
    style=style)
output1 = widgets.Output()


# A python program to create user-defined exception

# class MyError is derived from super class Exception
class InputError(Exception):

    # Constructor or Initializer
    def __init__(self):
        self.message = 'Please Select one inputpath. To use local executor you need to have only one input path which will be used as a working directory.'

    # __str__ is to print() the value
    def __str__(self):
        return(repr(self.message))




def set_local_env(libpath, launch_comm):
    # export necessary PYTHONPATH
    if len(libpath) != 0:
        for path in libpath:
            if path.selected_path is not None:
                export_path = 'export PYTHONPATH=$PYTHONPATH:' + path.selected_path
                launch_comm.extend([export_path])


def set_cwd(input_path, launch_comm, pre_launch_command):
    # Set current working directory of local executor
    try:
        if len(input_path) != 1:
            raise(InputError())
        elif input_path[0].selected_path is not None:
            cd_to_cwd = 'cd ' + input_path[0].selected_path
            launch_comm.extend([cd_to_cwd])
        else:
            raise(MyError())
        if pre_launch_command:
            launch_comm.extend([pre_launch_command])
        else:
            pass
    except InputError as error:
        print(error.message)
        sys.exit()


libpath = []
def plus_lib_clicked(b3):
    libpath.append(FileChooser(''))
    libpath[len(libpath) - 1].default_path = default_path
    libpath[len(libpath) - 1].use_dir_icons = True
    with plus_lib_output:
        if len(libpath) == 1:
            display(refresh_lib_button)
        display(libpath[len(libpath) - 1])


input_path = []
def input_button_clicked(b3):
    input_path.append(FileChooser(''))
    input_path[len(input_path) - 1].default_path = default_path
    input_path[len(input_path) - 1].use_dir_icons = True
    with input_button_output:
        if len(input_path) == 1:
            display(refresh_input_button)
        display(input_path[len(input_path) - 1])


def refresh_input_button_clicked(b):
    with input_button_output:
        clear_output()
        input_path.clear()


def refresh_lib_button_clicked(b):
    with plus_lib_output:
        clear_output()
        libpath.clear()


def info_button_clicked(obj):
    with info_button_output:
        if obj['new']:
            slurm_single = os.path.join(fig_path, 'slurm_single.png')
            slurm_multi = os.path.join(fig_path, 'slurm_multi.png')
            blank = os.path.join(fig_path, 'blank.png')
            img1 = open(slurm_single, 'rb').read()
            wi1 = widgets.Image(
                value=img1,
                format='jpg',
                width=300,
                height=400)
            img0 = open(blank, 'rb').read()
            wi0 = widgets.Image(
                value=img0,
                format='jpg',
                width=300,
                height=405)
            img2 = open(slurm_multi, 'rb').read()
            wi2 = widgets.Image(
                value=img2,
                format='jpg',
                width=300,
                height=405)
            a = [wi1, wi0, wi2]
            wid = widgets.HBox(a)
            display(wid)
        else:
            with info_button_output:
                clear_output()


def run_model_clicked(b):
    with output1:
        # Clear cell output
        for i in range(10):
            clear_output(wait=True)
        launch_comm = []    # launch command
        argument_threads = ["--pool", "--threads_number"]
        value_threads = [pool_type.value, threads_number.value]

        argument_processes = [
            "--pool",
            "--processes_number",
            "--cpu_per_process"]
        value_processes = [
            pool_type.value,
            processes_number.value,
            cpu_per_process.value]

        argument_slurm = [
            "--pool",
            "--partition",
            "--walltime",
            "--memory",
            "--scale",
            "--worker_per_node",
            "--cpu_per_node"]
        value_slurm = [
            pool_type.value,
            partition.value,
            walltime.value,
            memory.value,
            scale_nodes.value,
            workers_nodes.value,
            cpu_per_node.value]

        if pool_type.value == 'local_threads':
            argument_list = argument_threads
            value_list = value_threads
            launch_model = "python " + str(model_path.selected)
        elif pool_type.value == 'local_processes':
            argument_list = argument_processes
            value_list = value_processes
            launch_model = "python " + str(model_path.selected)
        elif pool_type.value == 'slurm':
            argument_list = argument_slurm
            value_list = value_slurm
            launch_model = "python " + str(model_path.selected_filename)

        for argument, value in zip(argument_list, value_list):
            launch_model += " " + argument + " " + str(value)

        if pool_type.value == 'local_processes' or pool_type.value == 'local_threads':
            set_local_env(libpath, launch_comm)
            set_cwd(input_path, launch_comm, pre_launch_command.value)
            launch_comm.extend([launch_model])
            cmd = '&&'.join(launch_comm)
            print(cmd)
            proc = subprocess.call(cmd, shell=True)

        elif pool_type.value == 'slurm':
            with Connection(host=host.value, user=user.value) as conn:
                conn.run('mkdir -p ' + launchdir.value)
                transfer_files(user.value, host.value, input_path, launchdir.value)
                conn.put(model_path.selected, launchdir.value)
                launch_comm.extend(
                    [transfer_files(user.value, host.value, libpath, launchdir.value, 'lib')])
                with conn.cd(launchdir.value):
                    if model_path.selected_filename is not None:
                        if pre_launch_command.value:
                            launch_comm.extend(
                                [pre_launch_command.value, launch_model])
                        else:
                            launch_comm.extend([launch_model])
                        cmd = '&&'.join(launch_comm)
                        print(cmd)
                        conn.run(cmd)
                    else:
                        print('Select your python model')


def pool_type_changed(bvar):
    """ Observe Pool type"""
    with pool_type_output:
        clear_output()
        if pool_type.value == 'local_threads':
            display(threads_number)
        elif pool_type.value == 'local_processes':
            display(HBox([processes_number, cpu_per_process]))
        elif pool_type.value == 'slurm':
            display(user, host)
            display(HBox([partition, walltime, memory]))
            display(HBox([cpu_per_node, workers_nodes, scale_nodes]))
            display(info_button, info_button_output)
            display(launchdir)


# edit_environment.on_click(edit_environment_clicked)
pool_type.observe(pool_type_changed)
plus_lib.on_click(plus_lib_clicked)
input_button.on_click(input_button_clicked)
run_model.on_click(run_model_clicked)
refresh_input_button.on_click(refresh_input_button_clicked)
refresh_lib_button.on_click(refresh_lib_button_clicked)
info_button.observe(info_button_clicked, 'value')


def display_executor():
    """ Dask/Parsl Executor Top View"""
    display(model_path)
    display(input_button, input_button_output)
    display(pre_launch_command)
    display(plus_lib, plus_lib_output)
    display(pool_type, pool_type_output)
    pool_type_changed('NULL')
    display(HBox([run_model]), output1)
