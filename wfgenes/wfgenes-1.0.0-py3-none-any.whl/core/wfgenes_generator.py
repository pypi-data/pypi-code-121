import sys
import os
import os.path
from pathlib import Path
from IPython.display import Image
import ipywidgets as widgets
import json, yaml
from ipywidgets import Button, HBox, VBox, Layout
from IPython.display import HTML, display, clear_output, Markdown as md, JSON, Javascript, FileLink, Image, display_javascript, display_html, display_json
from ipyfilechooser import FileChooser
import time
from json2html import *
import wfgenes
import yaml
from wfgenes import wfgenes_gui
import site

wfgenes_path = os.path.join(site.getsitepackages()[0], 'wfgenes')



if wfgenes_gui.default_path.selected_path is not None:  
    default_path = wfgenes_gui.default_path.selected_path
else:
    default_path = wfgenes_path    

                                        
# Getting the arguments with FileChooser and SelectMultiple
config = FileChooser('')
inputp = FileChooser('')

style = {'description_width': 'initial'}

model = widgets.Dropdown(
    options=['FireWorks', 'SimStack', 'Dask', 'Parsl'],
    value='FireWorks',
    description='<b>Choose a model:<b>',
    disabled=False,
    style=style
)

model_output = widgets.Output()

embedded_wms= widgets.Checkbox(
    value=False,
    description='Embedded in FireWorks',
    disabled=False,
    indent=False
)

# Set default paths for file chooser


config.default_path= default_path
inputp.default_path = default_path


# Show folder icons for file chooser
config.use_dir_icons = True
inputp.use_dir_icons = True

# Set multiple file filter patterns for config file
config.filter_pattern = ['*.txt','*.yaml','*.json', '*.yml']

# Set titles for choosers
config.title = '<b>Select a configuration file</b>'
inputp.title = '<b>Select the input path</b>'

#Button for runing wgenerator
button = widgets.Button(description='Run wfGenes', style=style, icon='play')
output = widgets.Output()

#Button for displaying Wconfig file 
dis_wconfig = widgets.Button(description='Preview WConfig', tooltip='display wconfig', icon='eye')
output2 = widgets.Output()

#Button for editing Wconfig file 
edit_wconfig = widgets.Button(description='Edit Wconfig', tooltip='Edit configuration file for modifying the graph', icon='pen')
output2 = widgets.Output()

#Button for adding another input path
plus_input = widgets.Button(tooltip='Aadding additional input paths', icon='plus', style=style, layout=Layout(width='56px'))
output3 = widgets.Output()

#Button for saving wconfig file after modifications
save_wconfig = widgets.Button(description='save', tooltip='Save wconfig after modifications', icon='save')
updated = widgets.Output()

#Text area for displaying config file
config_textarea = widgets.Textarea(
                    placeholder='Type something',
                    description='<b>Configuration file:</b>',
                    description_tooltip = 'Edit to modify the graph',
                    disabled=False,
                    style = style,
                    layout=Layout( width='100%', height='1000px')
                 )

#Dash board for displaying the graph
graph_dash = widgets.Output()

#Prepare args to wgenerator
def prepare_args(config, input):
    args = {'workflowconfig' : config.selected, 'inputpath':  inputp.selected_path , 'wms':model.value, 'embedded': embedded_wms.value}
    return args

#Run wgenerator
def run_wgenerator(args):
    png = wfgenes.core.wgenerator.run_wfgenes(args)
    return png
    
#Display graph
def display_graph(graph):
    file = open(graph, "rb") 
    image = file.read()
    graph = widgets.Image(
            value=image,
            format='png',
            height=100,
            )
    with graph_dash:
        clear_output()
        display(graph)   
    
#Define event when run wconfig button is clicked
def run_wfgenes_clicked(b):
    with output:
        clear_output()
        if config.selected == None or inputp.selected == None:
            print('Please select a configuration file and an input path.')
            time.sleep(2)
            clear_output()
            return
        args = prepare_args(config, inputp)
        png = run_wgenerator(args)
        time.sleep(1)
        display_graph(png)

#Define event when edit config button is clicked
config_output = widgets.Output()
def on_button_clicked_2(b_2):
    with config_output:
        clear_output()
        if config.selected == None:
            print('Please select a configuration file.')
            time.sleep(1.7)
            clear_output()
            return
        config_file = open(config.selected, "r")
        config_content = config_file.read()
        config_textarea.value = config_content
        display(HBox([save_wconfig, close_wconfig]))
        display(save_msg)
        display(config_textarea)
            
#Define event when WConfig preview button is clicked
config_preview = widgets.Output()
def on_wconfig_preview_clicked(b_2):
    with config_output:
        clear_output()
        if config.selected == None:
            print('Please select a configuration file.')
            time.sleep(1.7)
            clear_output()
            return
        config_file = open(config.selected, "r")
        config_content = config_file.read()
        config_split = config.selected.split('.')
        suffix_dot = len(config_split) - 1
        if config_split[suffix_dot] == 'json': 
            config_dic = json.loads(config_content)
        elif config_split[suffix_dot] == 'yaml':
            config_dic = yaml.load(config_content, Loader=yaml.Loader)
        config_to_html = json2html.convert(json = config_dic)
        config_html = HTML(config_to_html)
        display(close_wconfig)
        display_html(config_html)
            
#Define event when save wconfig button is clicked
save_msg = widgets.Output()
def on_save_wconfig_clicked(b):
    new_content = config_textarea.value
    config_file = open(config.selected, "w")
    config_file.write(new_content)
    config_file.close()
    with save_msg:
        clear_output()
        print('Configuration file was saved.')
        time.sleep(1.5)
        clear_output()

#Button to close wconfig
close_wconfig = widgets.Button(description='close', tooltip='Close wconfig', icon='close')
def on_close_wconfig_clicked(b):
    with config_output:
        clear_output()
close_wconfig.on_click(on_close_wconfig_clicked)

#Button to clear all outputs
clear_all = widgets.Button(description='Clear', tooltip='Close graph and wconfig', icon='eraser')
def on_clear_all_clicked(b):
    with graph_dash:
        clear_output()
    with config_output:
        clear_output()
    with output:
        clear_output()
    with output2:
        clear_output()
clear_all.on_click(on_clear_all_clicked)
        
#Define event when plus input button in clicked
inputpath = []
def on_button_clicked_3(b3):
    inputpath.append(FileChooser(''))
    inputpath[len(inputpath)-1].default_path = default_path
    inputpath[len(inputpath)-1].use_dir_icons = True
    with output3:
        display(inputpath[len(inputpath)-1])
        
def model_changed(bvar):
    with model_output:
        clear_output()
        if model.value == 'Dask' or model.value == 'Parsl':  
            display(embedded_wms)
        
button.on_click(run_wfgenes_clicked)
edit_wconfig.on_click(on_button_clicked_2)
plus_input.on_click(on_button_clicked_3)
dis_wconfig.on_click(on_wconfig_preview_clicked)
save_wconfig.on_click(on_save_wconfig_clicked)
model.observe(model_changed)

#Display buttons
def display_generator():
    """"""
    display(config)
    display(inputp)
    display(plus_input, output3)
    display(model, model_output)
    display(HBox([button, clear_all]), output)
    display(HBox([ dis_wconfig, edit_wconfig]), output2, output2, graph_dash, output3, config_output)
