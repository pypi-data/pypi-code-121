# pylint: disable=unused-argument
""" A graphical user interface for WFEngine based on ipywidgets """
import ast
import os
import os.path
import time
from pathlib import Path
import ipywidgets as widgets
from ipywidgets import HBox, VBox, Layout
from ipyfilechooser import FileChooser
from IPython.display import display, clear_output, JSON
from fireworks import LaunchPad
from fireworks.user_objects.queue_adapters.common_adapter import CommonAdapter
from fireworks.fw_config import LAUNCHPAD_LOC, QUEUEADAPTER_LOC
from fireworks import Workflow
from wfengine import WFEngine
from wfengine_remote import WFEngineRemote
from BUILTIN import transfer_files


# Getting the arguments with FileChooser and SelectMultiple
lp_file = FileChooser('')
qa_file = FileChooser('')
wf_file = FileChooser('')

style = {'description_width': 'initial'}

# Set default paths for file chooser
HOME = str(Path.home())
lp_file.show_hidden = True
lp_file.default_path = os.path.join(HOME, '.fireworks')
lp_file.default_filename = 'launchpad.yaml'
qa_file.show_hidden = True
qa_file.default_path = os.path.join(HOME, '.fireworks')
qa_file.default_filename = 'qadapter.yaml'
wf_file.default_path = os.path.join(HOME)
wf_file.default_filename = 'workflow.yaml'

# Show folder icons for file chooser
lp_file.use_dir_icons = True
qa_file.use_dir_icons = True

# Set multiple file filter patterns for config file
lp_file.filter_pattern = ['*.yaml', '*.json']
qa_file.filter_pattern = ['*.yaml', '*.json']
wf_file.filter_pattern = ['*.yaml', '*.json']

# Set titles for choosers
lp_file.title = 'Select your launchpad file'
qa_file.title = 'Select your qadapter file'
wf_file.title = 'Select your workflow file'


text_input_layout = Layout(width='100%')

configure_button = widgets.Button(
    tooltip='Create a new and manage running engine',
    description='Manage engine',
    style=style,
    icon='')
output_configure_button = widgets.Output()

rsync_button = widgets.Button(
    tooltip='Create a new and manage running engine',
    description='Transfer files',
    style=style,
    icon='')
output_rsync_button = widgets.Output()

send_files_button = widgets.Button(
    tooltip='Create a new and manage running engine',
    description='Transfer files',
    style=style,
    icon='')

output_send_files_button = widgets.Output()


plus_lib = widgets.Button(tooltip='Transfer additional module(s) to remote machines', icon='plus', style=style, layout=Layout(width='100px'), description='Modules', title= 'add modules')
plus_lib_output = widgets.Output()


plus_input = widgets.Button(tooltip='Transfer additional files(s) to remote machines', icon='plus', style=style, layout=Layout(width='100px'), description='Files', title= 'add files')
plus_input_output = widgets.Output()


clear_lib_button = widgets.Button(tooltip='Clear module list', icon='refresh', style=style, layout=Layout(width='40px'), description='')
clear_lib_button_output = widgets.Output()

clear_input_button = widgets.Button(tooltip='Clear input list', icon='refresh', style=style, layout=Layout(width='40px'), description='')
clear_input_button_output = widgets.Output()



lpad_button = widgets.Button(
    description='Load launchpad',
    style=style,
    icon='upload')
output_lpad_button = widgets.Output()

qadapter_button = widgets.Button(
    description='Load qadapter',
    style=style,
    icon='upload')
output_qadapter_button = widgets.Output()

new_engine_button = widgets.Button(
    tooltip='New engine will be created',
    description='Create new engine',
    style=style,
    icon='cogs')
output_new_engine_button = widgets.Output()

dump_engine_button = widgets.Button(
    tooltip='Save the current engine into a file',
    description='Save engine',
    style=style,
    icon='download')

resume_engine_button = widgets.Button(
    tooltip='Load an engine from a file',
    description='Load engine',
    style=style,
    icon='upload')

output_saveload_engine_button = widgets.Output()

manage_launcher_button = widgets.Button(
    tooltip='Manage launcher threads',
    description='Manage launcher',
    style=style,
    icon='')
output_manage_launcher_button = widgets.Output()

start_button = widgets.Button(
    description='Start launcher',
    style=style,
    icon='play')
output_start_button = widgets.Output()

stop_button = widgets.Button(
    description='Stop launcher',
    style=style,
    icon='power-off')
output_stop_button = widgets.Output()

manage_workflows_button = widgets.Button(
    tooltip='Manage workflows',
    description='Manage workflows',
    style=style,
    icon='')
output_manage_workflows_button = widgets.Output()

new_workflow_button = widgets.Button(
    tooltip='Add a new workflow to the engine',
    description='Add new workflow',
    style=style,
    icon='plus')
output_new_workflow_button = widgets.Output()

add_workflow_button = widgets.Button(
    description='Add workflow',
    style=style,
    icon='upload')
output_add_workflow_button = widgets.Output()

remove_workflow_button = widgets.Button(
    description='Remove a workflow',
    style=style,
    icon='trash')
output_remove_workflow_button = widgets.Output()

manage_nodes_button = widgets.Button(
    tooltip='Manage individual workflow nodes',
    description='Manage nodes',
    style=style,
    icon='')
output_manage_nodes_button = widgets.Output()

status_button = widgets.Button(
    tooltip='Show the status of all workflows',
    description='Status',
    style=style,
    icon='eye')
output_status_button = widgets.Output()

status_button_detail = widgets.Button(
    tooltip='Show the status of specified nodes',
    description='Status',
    style=style,
    icon='search-plus')
status_button_detail_output = widgets.Output()

rerun_node_button = widgets.Button(
    description='Rerun a node',
    style=style,
    icon='redo')
output_rerun_node_button = widgets.Output()

query = widgets.Textarea(
    value='None',
    placeholder='{}',
    description='Query',
    tooltip='Query to select the workflows to include to engine',
    layout=text_input_layout,
    disabled=False)

engine_file = FileChooser('')
engine_file.default_path = '.'
engine_file.use_dir_icons = True
engine_file.filter_pattern = ['*.yaml', '*.json']
engine_file.title = 'WFEngine file'

firework_id = widgets.IntText(
    value=1,
    description='fw id',
    placeholder='firework id',
    disabled=False
)

configure_engine_method = widgets.RadioButtons(
    options=['Save or load an existing engine',
             'Create a new engine from scratch'],
    value='Save or load an existing engine',
    layout={'width': 'max-content'},
    description='Method',
    disabled=False
)
configure_engine_method_output = widgets.Output()

remote_cluster = widgets.Checkbox(
    value=False,
    description='Use a remote cluster',
    tooltip='Use a remote cluster to launch jobs',
    disabled=False,
    indent=False
)
remote_cluster_output = widgets.Output()

user_name = widgets.Textarea(
    value='',
    placeholder='xy1234',
    description='Username',
    tooltip='Username on the remote cluster',
    layout=text_input_layout,
    disabled=False)

host_name = widgets.Textarea(
    value='',
    placeholder='hostname.domainname',
    description='Hostname',
    tooltip='Hostname of the remote cluster',
    layout=text_input_layout,
    disabled=False)

remote_conf = widgets.Textarea(
    value='',
    placeholder='module load xyz',
    description='Command',
    tooltip='Remote configuration command',
    layout=text_input_layout,
    disabled=False)

launch_dir = widgets.Textarea(
    value='.',
    placeholder='/absolute/path/to/launchdir',
    description='Launchdir',
    tooltip='Directory in that nodes will be executed',
    layout=text_input_layout,
    disabled=False)

dest_dir = widgets.Textarea(
    value='.',
    placeholder='/absolute/path/to/destdir',
    description='Destination of transfer, default is launchdir if it is set',
    tooltip='Directory in that nodes will be executed',
    layout=text_input_layout,
    disabled=False)

eng_name = widgets.Textarea(
    value=None,
    placeholder='None',
    description='Engine name',
    tooltip='A name for the engine (one will be generated if not specified)',
    layout=text_input_layout,
    disabled=False)



libpath = []
def plus_lib_clicked(b3):
    libpath.append(FileChooser(''))
    libpath[len(libpath)-1].default_path = '../'
    libpath[len(libpath)-1].use_dir_icons = True
    with plus_lib_output:
        display(libpath[len(libpath)-1])
        
inputpath = []
def plus_input_clicked(b3):
    inputpath.append(FileChooser(''))
    inputpath[len(inputpath)-1].default_path = '../'
    inputpath[len(inputpath)-1].use_dir_icons = True
    with plus_input_output:
        display(inputpath[len(inputpath)-1])
        
        

def clear_lib_button_clicked(b):
    with plus_lib_output:
        clear_output()
        libpath.clear() 
        
def clear_input_button_clicked(b):
    with plus_input_output:
        clear_output()
        inputpath.clear() 
    with output_send_files_button:
        clear_output()
        
        
         
def clear_engineoutput():
    """ Clear outputs """
    with output_manage_nodes_button:
        clear_output()
    with output_new_workflow_button:
        clear_output()
    with output_new_workflow_button:
        clear_output()
    with output_stop_button:
        clear_output()
    with output_start_button:
        clear_output()
    with output_saveload_engine_button:
        clear_output()


def clear_consoleoutput():
    """ clear outputs """
    with output_status_button:
        clear_output()
    with output_remove_workflow_button:
        clear_output()
    with output_rerun_node_button:
        clear_output()


def clear_button_outputs():
    """ Clear top buttons output """
    with output_new_workflow_button:
        clear_output()
    with output_configure_button:
        clear_output()
    with output_rsync_button:
        clear_output()
    with output_manage_launcher_button:
        clear_output()
    with output_manage_workflows_button:
        clear_output()
    with output_stop_button:
        clear_output()
    with output_manage_nodes_button:
        clear_output()
    with output_new_engine_button:
        clear_output()
    with output_saveload_engine_button:
        clear_output()
    clear_consoleoutput()


def manage_nodes_button_clicked(bvar):
    """ Manage nodes button is clicked """
    with output_manage_nodes_button:
        clear_button_outputs()
        clear_output()
        display(firework_id)
        display(HBox([status_button, status_button_detail,
                      rerun_node_button]), output_status_button,
                status_button_detail_output, output_rerun_node_button)


def configure_button_clicked(bvar):
    """ Configure button is clicked """
    with output_configure_button:
        clear_button_outputs()
        clear_output()
        display(VBox([configure_engine_method,
                      configure_engine_method_output]))
        configure_engine_method_changed(bvar)


def manage_launcher_button_clicked(bvar):
    """ manage launcher button is clicked """
    with output_manage_workflows_button:
        clear_button_outputs()
        clear_output()
        display(HBox([start_button, stop_button]), output_start_button,
                output_stop_button)

        
def rsync_button_clicked(bvar):
    """ Prepare to send files"""
    with output_rsync_button:
        clear_button_outputs()
        clear_output()
        display(user_name,host_name, dest_dir)
        display(HBox([plus_input, clear_input_button]), plus_input_output)
        display(send_files_button, output_send_files_button)
        
def send_files_button_clicked(bvar):
    """ Transfer files clicked"""
    with output_send_files_button:
        clear_output()
        transfer_files(user_name.value, host_name.value, inputpath, dest_dir.value)
        
    
        
def manage_workflows_button_clicked(bvar):
    """ manage workflows button is clicked """
    with output_manage_workflows_button:
        clear_button_outputs()
        clear_output()
        display(firework_id)
        display(HBox([status_button, new_workflow_button,
                      remove_workflow_button]), output_status_button,
                output_new_workflow_button, output_remove_workflow_button)


def new_workflow_button_clicked(bvar):
    """ new workflow button is clicked """
    with output_new_workflow_button:
        clear_output()
        display(wf_file)
        display(add_workflow_button, output_add_workflow_button)


def remote_cluster_changed(bvar):
    """ toggle the remote cluster checkbox """
    with remote_cluster_output:
        clear_output()
        if remote_cluster.value and configure_engine_method.value == 'Create a new engine from scratch':
            display(user_name, host_name, remote_conf)
            display(HBox([plus_lib, clear_lib_button]),
                    plus_lib_output)

            


def configure_engine_method_changed(bvar):
    """ select engine configuration method from radio buttons """
    with configure_engine_method_output:
        clear_output()
        if configure_engine_method.value == 'Save or load an existing engine':
            print('Save or load an existing engine')
            display(VBox([remote_cluster, remote_cluster_output]))
            display(engine_file)
            display(HBox([dump_engine_button, resume_engine_button]),
                    output_saveload_engine_button)
            if remote_cluster.value:
                remote_cluster_changed(bvar)
        if configure_engine_method.value == 'Create a new engine from scratch':
            print('Create a new engine from scratch')
            display(lp_file)
            display(lpad_button, output_lpad_button)
            display(qa_file)
            display(qadapter_button, output_qadapter_button)
            display(query, launch_dir, eng_name)
            display(VBox([remote_cluster, remote_cluster_output]))
            remote_cluster_changed(bvar)
            display(new_engine_button, output_new_engine_button)


class WFEnginejupyter():
    """ A class for construcing a GUI for FireWorks """
    wfe = None

    def __init__(self):
        """ Load default launchpad and qadapter """
        if LAUNCHPAD_LOC:
            try:
                self.jlaunchpad = LaunchPad.from_file(LAUNCHPAD_LOC)
                print('Default lpad in ' + LAUNCHPAD_LOC + ' is loaded')
            except FileNotFoundError as error:
                print('The default launchpad file is missing.')
                print('Error message is:' + str(error.args))
            except KeyError as error:
                print('The default lpad file is not correct.')
                print('Error message is:' + str(error.args))

        if QUEUEADAPTER_LOC:
            try:
                self.jqadapter = CommonAdapter.from_file(QUEUEADAPTER_LOC)
                print('Default qadapter in ' + QUEUEADAPTER_LOC + ' is loaded')
            except FileNotFoundError as error:
                print('The default qadapter file is missing.')
                print(error.args)
            except KeyError as error:
                print('The default qadapter file is not correct.')
                print(error.args)
    
    def new_engine_button_clicked(self, bvar):
        """ create new engine button is clicked """
        with output_new_engine_button:
            clear_output()
            if self.wfe and self.wfe.thread and self.wfe.thread.is_alive():
                self.wfe.stop()
                print('Stopping the running launcher thread, please wait ...')
                self.wfe.thread.join()
            else:
                query_dict = ast.literal_eval(query.value)
                if remote_cluster.value:
                    assert host_name.value != '' and user_name.value != ''
                    self.wfe = WFEngineRemote(launchpad=self.jlaunchpad,
                                              qadapter=self.jqadapter,
                                              wf_query=query_dict,
                                              host=host_name.value,
                                              user=user_name.value,
                                              conf=remote_conf.value,
                                              libpath = libpath,
                                              launchdir=launch_dir.value,
                                              name=eng_name.value,
                                             )
                    print('Engine is created for remote launcher')
                else:
                    self.wfe = WFEngine(launchpad=self.jlaunchpad,
                                        qadapter=self.jqadapter,
                                        wf_query=query_dict,
                                        launchdir=launch_dir.value,
                                        name=eng_name.value)
                    print('Engine is created for local launcher')

    def resume_engine_button_clicked(self, bvar):
        """ resume engine button is clicked """
        with output_saveload_engine_button:
            clear_output()
            if self.wfe and self.wfe.thread and self.wfe.thread.is_alive():
                self.wfe.stop()
                print('Stopping the running launcher thread, please wait ...')
                self.wfe.thread.join()
            eng_class = WFEngineRemote if remote_cluster.value else WFEngine
            try:
                self.wfe = eng_class.from_file(filename=engine_file.value)
            except (FileNotFoundError, IsADirectoryError) as error:
                print('Specify a valid engine filename or path.')
                print(error.args)
            except ValueError as error:
                if 'Unsupported format' in error.args[0]:
                    print('Specify a valid engine filename ending with .json or .yaml')
                    print(error.args)
                else:
                    raise
            except PermissionError as error:
                print(error.args)
            else:
                print('An engine has been loaded from file', engine_file.value)

    def dump_engine_button_clicked(self, bvar):
        """ dump the engine to file """
        with output_saveload_engine_button:
            clear_output()
            if self.wfe:
                try:
                    self.wfe.to_file(filename=engine_file.value)
                except (FileNotFoundError, IsADirectoryError) as error:
                    print('Specify a valid engine filename or path.')
                    print(error.args)
                except ValueError as error:
                    if 'Unsupported format' in error.args[0]:
                        print('Specify a valid engine filename ending with .json or .yaml')
                        print(error.args)
                    else:
                        raise
                except PermissionError as error:
                    print(error.args)
                else:
                    print('The engine has been saved in file', engine_file.value)
            else:
                print('Create an engine first.')

    def lpad_button_clicked(self, bvar):
        """ load user defined launchpad """
        with output_lpad_button:
            clear_output()
            if lp_file.selected is None:
                print('Select a launchpad file.')
                time.sleep(1)
                return
            try:
                self.jlaunchpad = LaunchPad.from_file(lp_file.selected)
            except FileNotFoundError as error:
                print('Select a valid launchpad file')
                print(error.args)
            else:
                print('Launchpad has been loaded from file', lp_file.selected)

    def qadapter_button_clicked(self, bvar):
        """ load user defined qadapter """
        with output_qadapter_button:
            clear_output()
            if qa_file.selected is None:
                print('Select a qadapter file.')
                time.sleep(1)
                return
            try:
                self.jqadapter = CommonAdapter.from_file(qa_file.selected)
            except FileNotFoundError as error:
                print('Select a valid qadapter file')
                print(error.args)
            else:
                print('Qadapter has been loaded from file', qa_file.selected)

    def add_wf_clicked(self, bvar):
        """ add a workflow from the file """
        with output_add_workflow_button:
            clear_output()
            if wf_file.selected is None:
                print('Select a workflow file.')
                time.sleep(1)
                return
            try:
                workflow = Workflow.from_file(wf_file.selected)
                self.wfe.add_workflow(workflow=workflow)
            except FileNotFoundError as error:
                print('Select a valid workflow file')
                print(error.args)
            else:
                print('Workflow has been loaded from file', wf_file.selected)

    def start_launcher_clicked(self, bvar):
        """ start launcher button clicked """
        clear_engineoutput()
        with output_start_button:
            clear_output()
            self.wfe.start()
            print('The launcher thread is created.')


    def stop_launcher_clicked(self, bvar):
        """ stop launcher button clicked """
        clear_engineoutput()
        with output_stop_button:
            try:
                self.wfe.stop()
                print('please wait ...')
                self.wfe.thread.join()
                clear_output()
            except AttributeError:
                clear_output()
                print('There is no running thread')

    def status_button_clicked(self, bvar):
        """ status summary """
        clear_consoleoutput()
        with output_status_button:
            clear_output()
            self.wfe.status_summary()

    def status_detailed_button_clicked(self, bvar):
        """ status details about specified nodes """
        clear_consoleoutput()
        with output_status_button:
            status_dict = self.wfe.status_detail(firework_id.value)
            del status_dict['_id']
            for element in status_dict['archived_launches']:
                del element['_id']
            status_dict['previous_launches']=status_dict['archived_launches']    
            del status_dict['archived_launches']
            del status_dict['launches'][0]['_id']
            display(JSON(status_dict))
            

    def remove_workflow_button_clicked(self, bvar):
        """ remove a workflow from engine """
        clear_consoleoutput()
        with output_remove_workflow_button:
            self.wfe.remove_workflow(firework_id.value)
            self.wfe.status_summary()

    def rerun_node_button_clicked(self, bvar):
        """ rerun a node and print a new status summary """
        clear_consoleoutput()
        with output_rerun_node_button:
            self.wfe.rerun_node(firework_id.value)
            self.wfe.status_summary()


wfengine = WFEnginejupyter()

new_engine_button.on_click(wfengine.new_engine_button_clicked)
manage_workflows_button.on_click(manage_workflows_button_clicked)
rsync_button.on_click(rsync_button_clicked)
send_files_button.on_click(send_files_button_clicked)
resume_engine_button.on_click(wfengine.resume_engine_button_clicked)
configure_button.on_click(configure_button_clicked)
new_workflow_button.on_click(new_workflow_button_clicked)
lpad_button.on_click(wfengine.lpad_button_clicked)
qadapter_button.on_click(wfengine.qadapter_button_clicked)
start_button.on_click(wfengine.start_launcher_clicked)
stop_button.on_click(wfengine.stop_launcher_clicked)
status_button.on_click(wfengine.status_button_clicked)
status_button_detail.on_click(wfengine.status_detailed_button_clicked)
dump_engine_button.on_click(wfengine.dump_engine_button_clicked)
manage_launcher_button.on_click(manage_launcher_button_clicked)
manage_workflows_button.on_click(manage_workflows_button_clicked)
add_workflow_button.on_click(wfengine.add_wf_clicked)
remove_workflow_button.on_click(wfengine.remove_workflow_button_clicked)
manage_nodes_button.on_click(manage_nodes_button_clicked)
rerun_node_button.on_click(wfengine.rerun_node_button_clicked)
remote_cluster.observe(remote_cluster_changed)
configure_engine_method.observe(configure_engine_method_changed)
plus_lib.on_click(plus_lib_clicked)
plus_input.on_click(plus_input_clicked)
clear_lib_button.on_click(clear_lib_button_clicked)
clear_input_button.on_click(clear_input_button_clicked)



def display_wfengine():
    display(HBox([configure_button, manage_launcher_button,
                  manage_workflows_button, manage_nodes_button, rsync_button]),
            output_configure_button, output_manage_launcher_button,
            output_manage_workflows_button, output_manage_nodes_button, output_rsync_button)
