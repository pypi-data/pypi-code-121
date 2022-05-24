import os
import os.path
from pathlib import Path
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "engine"))
import ipywidgets as widgets
import wfgenes.core.wgenerator
import json, yaml
from ipywidgets import Button, HBox, VBox, Layout
from IPython.display import HTML, display, clear_output, Markdown as md, JSON, Javascript, FileLink, Image, display_javascript, display_html, display_json
from ipyfilechooser import FileChooser
import time
from json2html import *
from fabric2 import Connection
import imp
import site

style = {'description_width': 'initial'}

HOME = str(Path.home())
wfgenes_path = os.path.join(site.getsitepackages()[0], 'wfgenes')
fig_path=os.path.join(wfgenes_path, 'fig','wfgenes_logo.png')



default_path = FileChooser('')
default_path.default_path = HOME
default_path.use_dir_icons = True
default_path.filter_pattern = []
default_path.title = 'Work Space'



update_default_path_button = widgets.Button(
    tooltip='Update Workspace',
    description='Update Workspace',
    style=style, 
    icon='folder')
update_default_path_button_output = widgets.Output()

generation_button = widgets.Button(description='WF Generation', icon='gears', tooltip='Workflow Generation')
generation_output_button = widgets.Output()

execution_button = widgets.Button(description='WF Execution', icon='play', tooltip= 'Workflow Execution')
execution_output_button = widgets.Output()

fireworks_button = widgets.Button(description='FireWorks', icon='fast-forward')
fireworks_output_button = widgets.Output()

dask_parsl_button = widgets.Button(description='Dask or Parsl', icon='fast-forward')
dask_parsl_output_button = widgets.Output()

simstack_button = widgets.Button(description='SimStack', icon='fast-forward')
simstack_output_button = widgets.Output()


#Define event when run wconfig button is clicked
def generation_button_clicked(b):
    clear_output()
    clear_wfgenes_output()
    with generation_output_button:
        import wfgenes.core.wfgenes_generator
        #imp.reload(wfgenes.core.wfgenes_generator)
        wfgenes.core.wfgenes_generator.display_generator()
        

def execution_button_clicked(b):
    clear_output()
    clear_wfgenes_output()
    with execution_output_button:
        display(HBox([fireworks_button, dask_parsl_button,simstack_button]), 
                fireworks_output_button, dask_parsl_output_button, simstack_output_button) 

def fireworks_execution_button_clicked(b):
    clear_output()
    #clear_wfgenes_output()
    clear_executor_output()
    import wfgenes.engine.wfengine_jupyter
    with fireworks_output_button:
        wfgenes.engine.wfengine_jupyter.display_wfengine()

def dask_parsl_execution_button_clicked(b):
    clear_output()
    clear_executor_output()
    with dask_parsl_output_button:
        import wfgenes.core.wfgenes_executor
        wfgenes.core.wfgenes_executor.display_executor()        
             
def clear_wfgenes_output():
    """ Clear top outputs """
    with generation_output_button:
        clear_output()
    with execution_output_button:
        clear_output()
        

def clear_executor_output():
    """ Clear top outputs """
    with fireworks_output_button:
        clear_output()
    with dask_parsl_output_button:
        clear_output()

def update_default_path_button_clicked(b):
    with update_default_path_button_output:
        clear_output()
        def_path=os.path.join(wfgenes_path, 'WS.yml')
        try:
            print(default_path.selected_path+' is set as your workspace')
        except TypeError as error:                 
            print('Choose a valid path')
    
        
generation_button.on_click(generation_button_clicked)
execution_button.on_click(execution_button_clicked)
fireworks_button.on_click(fireworks_execution_button_clicked)
dask_parsl_button.on_click(dask_parsl_execution_button_clicked)
update_default_path_button.on_click(update_default_path_button_clicked)



#Display buttons
display(Image(filename=fig_path, width = 150, height =150))
display(default_path)
display(update_default_path_button, update_default_path_button_output)
display(HBox([generation_button, execution_button]), generation_output_button, execution_output_button) 