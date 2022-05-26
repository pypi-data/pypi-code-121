# Copyright (C) 2018-2021 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
# Author: Karthik Kumaar <karthikx.kumaar@intel.com>

from typing import (
    List,
)
from . import dc_utils
#import dc_utils
import cmd2
import argparse
import os
import sys
from cmd2 import (
    Bg,
    Fg,
    style,
    Cmd,
    Cmd2ArgumentParser,
    CompletionError,
    CompletionItem,
    ansi,
    with_argparser,
)

DC_TOOLS = [ 'system-tools', 'dev-tools', 'app-services','dataset-services','dl-model-services','dl-model-training-services',
                'dl-streamer-pipeline-services','edge-deployment-services','edge-inference-app-services',
                'edge-to-cloud-app-services','k8s-services','intel-dev-tools']
DC_COMMANDS = ['install', 'uninstall', 'enable', 'disable']
APP_COMMANDS = ['start', 'stop', 'restart']

SUB_TOOLS={
  "system-tools":['sftp', 'ssh', 'vnc', 'no-machine','vim'],
  "dev-tools":['docker', 'docker-compose','jupyter', 'n8n', 'openvino-2021.4','vscode'],
  "app-services":['telemetry','log-anlytics','perf-analysis','video-playback','rtsp-streamer','configs','benchmark-report'],  
  "dataset-services":['intel','partner','public','synthetic'],
  "dl-model-services":['dl-model-tools', 'inference-runtimes', 'object-detection-models','object-recognition-models'],
  "dl-model-training-services":['data-engineering-tools', 'datasets', 'model-zoo', 'training-frameworks'],
  "dl-streamer-pipeline-services":['audio-pipelines','dl-streamer-tools','multi-sensory-pipelines','video-pipelines'],
  "edge-deployment-services":['cross-plane','health-check','mass','vpshere-vm'],
  "edge-inference-app-services":['healthcare','industrial','market-places','media','retail','safety-security','transportation'],
  "edge-to-cloud-app-services":['seo-samples','seo-reference-implementations','seo-3rd-party-applications'],
  "k8s-services":['kind','kubespray','microk8s','minikube','openshift','rancher-k3s','rancher-rke2','smart-edge-open','starlingx','tanzu'],
  "intel-dev-tools":['intel-auto-deploy','intel-auto-test','intel-code-scans','mgt-console']
}

TOOLS={
  "dl-model-tools":['dl-model-benchmark', 'nncf', 'omz-tools', 'openvino-dl-workbench','openvino-model-server', 
                    'openvino-training-extension', 'post-training-optimization-toolkit'],
  "inference-runtimes":['intel-optimized-pytorch', 'intel-optimized-tensorflow','onnx', 'openvino-2022.1', 'openvino-addon-tensorflow'],
  "model-zoo":['telemetry','analystics','perf-analysis','web-video-playback','rancher','OKD','tanzu'],
  "data-engineering-tools":['cvat'],
  "datasets":['emotion-recognition','face-detection','object-detection'],
  "object-detection-models":['face-detection-retail-0005','pedestrian-detection-adas-0002','person-detection-retail-0002','vehicle-detection-adas-0002'],
  "object-recognition-models":['age-gender-recognition-retail-0013','head-pose-estimation-adas-0001'],
  "training-frameworks":['cnvrg','intel-optimized-pytorch','intel-optimized-tensorflow','kubeflow','one-api','sonoma-creek'],
  "dl-streamer-tools":['dlstreamer','dlstreamer-pipeline-server','dlstreamer-pipeline-zoo','dlstreamer-pipeline-composer','gst-shark'],
  "audio-pipelines":['audio-event-detection-sample'],
  "video-pipelines":['action-recognition-sample','human-pose-estimation-sample','vehicle-pedestrian-tracking-sample','face-detection-classification-sample','gvapython-sample','metadata-publishing-sample'],
  "multi-sensory-pipelines":['multi-sensor-pipeline'],
  "healthcare":['brain-tumor-segmentation','monai','openfl'],
  "industrial":['edge-controls-for-industrial','edge-insights-for-amr','edge-insights-for-industrial','industrial-surface-detect-detection','industrial-textline-recognition','rotor-bearing-defect-detector','textile-defect-classifier','weld-porosity-detection'],
  "market-places":['artifactory','dev-catalog','kube-apps','mrs','rrk'],
  "media":['ad-insertion','cdn-transcode-sample','immersive-video-sample','open-visual-cloud','smart-city','video-curation-sample'],
  "retail":['automated-checkout','edgex','interactive-kisok-ai-chatbot','real-time-sensor-fusion-for-loss-detection','social-distancing-for-retail-settings'],
  "safety-security":['edge-aibox-for-video-analytics','edge-insights-for-vision','smart-video-and-ai-workload','social-distancing-for-retail','social-distancing-for-retail-settings'],
  "transportation":['address-recognition-and-analytics','automatic-license-plate-recognition','cargo-management','drive-behavior-analytics','edge-insights-for-fleet','intelligent-traffic-management','public-transit-analytics','vehicle-event-recording','workzone-analytics'],
  "seo-samples":['openvino-sample-application-in-openness','sample-eaa-test-application','telemetry-sample','video-analytics-services-sample-application-in-openness'],
  "seo-reference-implementations":['intelligent-connection-management-for-automated-handover','smartvr–livestreaming-of-immersive-media','telehealth-remote-monitoring','wireless-network-ready-intelligent-traffic-management','wireless-network-ready-pcb-defect-detection','network-optimization-and-ai-inferencing-management-for-telepathology'],
  "seo-3rd-party-applications":['a5gnetworks','herta','orbo','qwilt','radisys']

}

class DC(cmd2.Cmd):
    CUSTOM_CATEGORY = 'My Custom Commands'
    def __init__(self):
        super().__init__(
            multiline_commands=['echo'],
            persistent_history_file='cmd2_history.dat',
            startup_script='scripts/startup.txt',
            include_ipy=True,
            allow_cli_args=False,
            silence_startup_script=True
        )
        """"Set up interactive command line interface."""
        # delete unused commands that are baked-into cmd2 and set some options
        del cmd2.Cmd.do_py
        del cmd2.Cmd.do_edit
        del cmd2.Cmd.do_shortcuts
        del cmd2.Cmd.do_run_pyscript
        del cmd2.Cmd.do_run_script
        del cmd2.Cmd.do_ipy
        del cmd2.Cmd.do_history
        #del cmd2.Cmd.do_shell
        #del cmd2.Cmd.do_set
        #del cmd2.Cmd.do_alias
        del cmd2.Cmd.do_macro
        #del cmd2.Cmd.do_quit
        del cmd2.Cmd.do__relative_run_script
        
        cmd2.Cmd.abbrev = True
        self.allow_cli_args = False  # disable parsing of command-line args by cmd2
        self.allow_redirection = False  # disable redirection to enable right shift (>>) in custom_hash to work
        self.redirector = '\xff'  # disable redirection in the parser as well
        #self.shortcuts.update({'sh': 'show'})  # don't want "sh" to trigger the hidden "shell" command

        # init cmd2 and the history file
        #cmd2.Cmd.__init__(self, persistent_history_file=hist_file, persistent_history_length=200)

        # disable help on builtins
        #self.hidden_commands.append('shell')
        self.hidden_commands.append('exit') 
        self.hidden_commands.append('intro')
        self.hidden_commands.append('echo')

        # Prints an intro banner once upon application startup
        self.intro = style('Welcome to Intel Devcloud! \n An Interactive CLI to Install Devcloud tools & Components', fg=Fg.BLUE, bg=Bg.BLACK, bold=True)

        # Show this as the prompt when asking for input
        self.prompt = style('$>',fg=Fg.GREEN, bold=True)

        # Used as prompt for multiline commands after the first line
        self.continuation_prompt = '... '

        # Allow access to your application in py and ipy via self
        self.self_in_py = True

        # Set the default category name
        self.default_category = 'cmd2 Built-in Commands'

        # Color to output text in with echo command
        self.foreground_color = Fg.CYAN.name.lower()

        # Make echo_fg settable at runtime
        fg_colors = [c.name.lower() for c in Fg]
        self.add_settable(
            cmd2.Settable('foreground_color', str, 'Foreground color to use with echo command', self, choices=fg_colors)
        )

        # For Pyinstaller Binary temp folder
        self.bundle_dir = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
    
    @cmd2.with_category(CUSTOM_CATEGORY)
    def do_intro(self, _):
        """Display the intro banner"""
        self.poutput(self.intro)

    @cmd2.with_category(CUSTOM_CATEGORY)
    def do_echo(self, arg):
        """Example of a multiline command"""
        fg_color = Fg[self.foreground_color.upper()]
        self.poutput(style(arg, fg=fg_color))

    '''
    eval_parser=cmd2.Cmd2ArgumentParser(description='Obtain the eval command')
    eval_parser.add_argument("Dev-Tools",help="Help for Dev-Tools")

    @cmd2.with_argparser(eval_parser)
    '''
    def do_dc(self, statement: cmd2.Statement):
        """Tab completes first 3 arguments using index_based_complete"""
        #dc_utils.aptGet_uninstall("vim")
        #dc_utils.aptGet_install("vim")
        self.poutput("Args: {}".format(statement.args))
        argsList=statement.args.split(' ')        
        print("length of args:", len(argsList))

        
        if len(argsList)>6:
            self.poutput("Invalid Args: {}".format(statement.args))        
            
        if len(argsList) >= 4:
            typeName=argsList[0]
            toolName=argsList[1]
            subtoolName=argsList[2]
            commandName=argsList[3]        
            print("{0} : {1} : {2} : {3}".format(typeName,toolName,subtoolName,commandName))
            print("cd:",os.getcwd())
            installation_path = self.bundle_dir + "/scripts/" + typeName + '/' + toolName + '/' + subtoolName + '/' + commandName
            self.poutput(installation_path)
            # checking the argList if any command line args given after install
            if len(argsList)>4 and len(argsList)<6:
                dc_utils.processArgs(installation_path,serviceName=argsList[4])
            else:
                dc_utils.processArgs(installation_path,serviceName="")
        
        if len(argsList) == 3:
            typeName=argsList[0]
            toolName=argsList[1]
            commandName=argsList[2]        
            print("{0} : {1} : {2}".format(typeName,toolName,commandName))
            print("cd:",os.getcwd())
            installation_path = self.bundle_dir + "/scripts/" + typeName + '/' + toolName + '/' + commandName
            self.poutput(installation_path)
            # checking the argList if any command line args given after install
            if len(argsList)>3 and len(argsList)<5:
                dc_utils.processArgs(installation_path,serviceName=argsList[3])
            else:
                dc_utils.processArgs(installation_path,serviceName="")
                
    def complete_dc(self, text, line, begidx, endidx) -> List[str]:
        """Completion function for do_index_based"""
        SUB_TOOLS_1=[]
        CMD_TOOLS=[]
        TM_TOOLS=[]
        index_dict={}      
        
        if begidx>3:
            for t in SUB_TOOLS:    
                # print("t:",t)            
                if line.__contains__(t):                    
                    SUB_TOOLS_1=SUB_TOOLS[t]
                    # print("subtools:", SUB_TOOLS[t])
                    CMD_TOOLS = DC_COMMANDS

                for st in TOOLS:
                    if line.__contains__(st):
                        # print(TOOLS[st])
                        TM_TOOLS = TOOLS[st]                    
                        

        if len(TM_TOOLS) != 0:                
            index_dict = {
                1: DC_TOOLS,  # Tab complete food items at index 1 in command line
                2: SUB_TOOLS_1,  # Tab complete sport items at index 2 in command line
                3: TM_TOOLS,
                4: CMD_TOOLS  # Tab complete using path_complete function at index 3 in command line
                 
            }
        else:
            # print("Inside else")
            index_dict = {
                1: DC_TOOLS,  # Tab complete food items at index 1 in command line
                2: SUB_TOOLS_1,  # Tab complete sport items at index 2 in command line
                3: CMD_TOOLS,  # Tab complete using path_complete function at index 3 in command line
                
            }

        return self.index_based_complete(text, line, begidx, endidx, index_dict=index_dict)
        #return self.path_complete(text, line, begidx, endidx)
 

def main():
    app = DC()
    app.cmdloop()

# if __name__ == "__main__":
#    main()


