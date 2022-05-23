import argparse
import json
import traceback
import subprocess
from acido.azure_utils.BlobManager import BlobManager
from acido.azure_utils.InstanceManager import *
from acido.azure_utils.ManagedIdentity import ManagedAuthentication
from msrestazure.azure_exceptions import CloudError
from acido.utils.functions import chunks, jpath, expanduser
from azure.cli.command_modules.container import container_exec
from huepy import good, bad, info, bold, green, red, orange
from multiprocessing.pool import ThreadPool
import code
import re
import os
import sys
import time
from os import mkdir, getenv
from acido.utils.decoration import BANNER, __version__

__author__ = "Xavier Alvarez Delgado (xalvarez@merabytes.com)"
__coauthor__ = "Juan Ramón Higueras Pica (juanramon.higueras@wsg127.com)"

parser = argparse.ArgumentParser()
parser.add_argument("-d", "--download",
                    dest="download_input",
                    help="Download file contents remotely from the acido blob.",
                    action='store')
parser.add_argument("-f", "--fleet",
                    dest="fleet",
                    help="Create new fleet.",
                    action='store')
parser.add_argument("-x", "--launch",
                    dest="scan",
                    help="Launch a new scan.",
                    action='store')
parser.add_argument("-n", "--num-instances",
                    dest="num_instances",
                    help="Instances that the operation affect",
                    action='store')
parser.add_argument("-l", "--list",
                    dest="list",
                    help="List all instances.",
                    action='store_true')
parser.add_argument("-e", "--exec",
                    dest="exec_cmd",
                    help="Execute command in all selected instances.",
                    action='store')
parser.add_argument("-sh", "--shell",
                    dest="shell",
                    help="Execute command and upload to blob.",
                    action='store')
parser.add_argument("-s", "--select",
                    dest="select",
                    help="Select instances matching name/regex.",
                    action='store')
parser.add_argument("-r", "--rm",
                    dest="remove",
                    help="Remove instances matching name/regex.",
                    action='store')
parser.add_argument("-c", "--config",
                    dest="config",
                    help="Start configuration of acido.",
                    action='store_true')
parser.add_argument("-ps", "--interactive",
                    dest="interactive",
                    help="Start interactive acido session.",
                    action='store_true')


args = parser.parse_args()

instances_inputs = {}
instances_outputs = {}

def build_output(result):
    global instances_outputs
    instances_outputs[result[0]] = result[1]

def exec_command(rg, cg, cont, command, max_retries):
    env = os.environ.copy()
    env["PATH"] = "/usr/sbin:/sbin:" + env["PATH"]
    # Kill tmux window
    subprocess.Popen(["tmux", "kill-session", "-t", cont], env=env)
    time.sleep(2)
    subprocess.Popen(["tmux", "new-session", "-d", "-s", cont], env=env)
    time.sleep(5)
    subprocess.Popen(["tmux", "send-keys", "-t", cont,
                    f"az container exec -g {rg} -n {cg} --container-name {cont} --exec-command /bin/bash", "Enter",
                    ], env=env)
    time.sleep(5)
    subprocess.Popen(["tmux", "send-keys", "-t", cont, f"nohup python3 -m acido.cli -sh '{command}' > temp &", "Enter"], env=env)
    time.sleep(2)
    subprocess.Popen(["tmux", "send-keys", "-t", cont, "Enter"], env=env)

    output = subprocess.check_output(["tmux", "capture-pane", "-pt", cont], env=env).decode()

    time.sleep(4)

    retries = 0
    failed = False

    while 'Done' not in output or 'Exit' not in output:

        retries += 1

        if retries > max_retries:
            output = ''
            failed = True
            break

        subprocess.Popen(["tmux", "send-keys", "-t", cont, "Enter"], env=env)
        time.sleep(5)
        output = subprocess.check_output(["tmux", "capture-pane", "-pt", cont], env=env).decode()
        print(output)

        if 'Done' in output:
            break

    if not failed:
        subprocess.Popen(["tmux", "send-keys", "-t", cont, "Enter"], env=env)
        time.sleep(2)
        subprocess.Popen(["tmux", "send-keys", "-t", cont, "(cat temp) > output", "Enter", "Enter"], env=env)
        time.sleep(5)
        subprocess.Popen(["tmux", "send-keys", "-t", cont, "cat output", "Enter"], env=env)
        time.sleep(10)
        subprocess.Popen(["tmux", "send-keys", "-t", cont, "Enter"], env=env)
        time.sleep(2)

        try:
            output = subprocess.check_output(["tmux", "capture-pane", "-pt", cont], env=env)
            output = output.decode()
            print(output)
        except Exception as e:
            output = None
            print(bad(f'Error capturing output from: {bold(cont)}'))


    # Kill shell
    subprocess.Popen(["tmux", "send-keys", "-t", cont, "(rm temp && rm output && exit)", "Enter"], env=env)
    time.sleep(1)
    # Kill tmux window
    subprocess.Popen(["tmux", "kill-session", "-t", cont], env=env)

    return cont, output

class Acido(object):

    if args.interactive:
        print(red(BANNER))

    def __init__(self, rg: str = None, login: bool = True):

        self.selected_instances = []
        self.image_registry_server = None
        self.image_registry_username = None
        self.image_registry_password = None
        self.user_assigned = None
        self.rg = None

        if rg:
            self.rg = rg

        self.io_blob = None

        try:
            self.rows, self.cols = os.popen('stty size', 'r').read().split()
        except:
            self.rows, self.cols = 55, 160
        
        try:
            self._load_config()
        except FileNotFoundError:
            self.setup()
        

        try:
            az_identity_list = subprocess.check_output(f'az identity create --resource-group {self.rg} --name acido', shell=True)
            az_identity_list = json.loads(az_identity_list)
            self.user_assigned = az_identity_list
        except Exception as e:
            self.user_assigned = None

        im = InstanceManager(self.rg, login, self.user_assigned)
        im.login_image_registry(
            self.image_registry_server, 
            self.image_registry_username, 
            self.image_registry_password
        )
        self.instance_manager = im
        self.blob_manager = BlobManager(resource_group=self.rg, account_name='acido', login=login)
        self.blob_manager.use_container(container_name='acido', create_if_not_exists=True)
        self.all_instances, self.instances_named = self.ls(interactive=False)

    def _save_config(self):
        home = expanduser("~")
        config = {
            'rg': self.rg,
            'selected_instances' : self.selected_instances,
            'image_registry_username': self.image_registry_username,
            'image_registry_password': self.image_registry_password,
            'image_registry_server': self.image_registry_server,
            'user_assigned_id': self.user_assigned_id
        }

        try:
            mkdir(jpath(f'{home}', '.acido'))
        except:
            pass

        try:
            mkdir(jpath(f'{home}', '.acido', 'logs'))
        except:
            pass

        with open(jpath(f'{home}', '.acido', 'config.json'), 'w') as conf:
            conf.write(json.dumps(config, indent=4))
            conf.close()

        return True
        

    def _load_config(self):
        home = expanduser("~")
        with open(jpath(f'{home}', '.acido', 'config.json'), 'r') as conf:
            config = json.loads(conf.read())
        
        for key, value in config.items():
            if key == 'rg' and self.rg:
                continue
            setattr(self, key, value)

        self._save_config()


    def ls(self, interactive=True):
        all_instances = {}
        all_instances_names = {}
        all_instances_states = {}
        all_names = []
        instances = self.instance_manager.ls()
        while instances:
            try:
                container_group = instances.next()
                all_instances[container_group.name] = [c for c in container_group.containers]
                all_instances_names[container_group.name] = [c.name for c in container_group.containers]
                all_instances_states[container_group.name] = green(container_group.provisioning_state) if container_group.provisioning_state == 'Succeeded' else orange(container_group.provisioning_state)
                all_names += [c.name for c in container_group.containers]
            except StopIteration:
                break
        if interactive:
            print(good(f"Listing all instances: [ {bold(' '.join(all_names))} ]"))
            print(good(f"Container group status: [ {' '.join([f'{bold(cg)}: {status}' for cg, status in all_instances_states.items()])} ]"))
            return
        return all_instances, all_instances_names
    
    def select(self, selection, interactive=True):
        self.all_instances, self.instances_named = self.ls(interactive=False)
        selection = f'^{selection.replace("*", "(.*)")}$'
        self.selected_instances = [scg for scg, i in self.instances_named.items() if bool(re.match(selection, scg))]
        self._save_config()
        if interactive:
            print(good(f"Selected all instances of group/s: [ {bold(' '.join(self.selected_instances))} ]"))
            return 

    def fleet(self, fleet_name, instance_num=3, interactive=True):
        response = {}
        if instance_num > 10:
            instance_num_groups = list(chunks(range(1, instance_num + 1), 10))
            for cg_n, ins_num in enumerate(instance_num_groups):
                group_name = f'{fleet_name}-{cg_n+1:02d}'
                if group_name not in response.keys():
                    response[group_name] = []
                last_instance = len(ins_num)
                response[group_name] = self.instance_manager.deploy(
                                            name=group_name, 
                                            instance_number=last_instance
                                        )
        else:
            response[fleet_name] = self.instance_manager.deploy(name=fleet_name, instance_number=instance_num)
        
        if not interactive:
            return response
        else:
            all_names = []
            all_groups = []

            for group, inst in response.items():
                all_groups.append(group)
                all_names += list(inst.keys())

            print(good(f"Successfully created new group/s: [ {bold(' '.join(all_groups))} ]"))
            print(good(f"Successfully created new instance/s: [ {bold(' '.join(all_names))} ]"))

            return

    def rm(self, selection):
        self.all_instances, self.instances_named = self.ls(interactive=False)
        response = {}
        selection = f'^{selection.replace("*", "(.*)")}$'
        removable_instances = [cg for cg, i in self.instances_named.items() if bool(re.match(selection, cg))]

        for erased_group in removable_instances:
            response[erased_group] = self.instance_manager.rm(erased_group)

        for group, status in response.items():
            if status:
                print(good(f'Successfully erased {group} and all its instances.'))
            else:
                print(bad(f'Error while erasing {group} and its instances. Maybe its already deleted?'))
        return

    def save_output(self, command: list = None):
        output = subprocess.check_output(command, shell=True)
        file, filename = self.blob_manager.upload(
            output
        )
        if file:
            print(good(f'Executed command: {filename}'))
        return output
    
    def load_input(self, command_uuid: str = None, filename: str = 'input.txt'):
        if command_uuid:
            input_file = self.blob_manager.download(command_uuid)
            if input_file:
                print(good(f'Downloaded file: {command_uuid}'))
                open(filename, 'wb').write(input_file)
                print(good(f'Input written to: {filename}'))
        return input_file

    def exec(self, command, max_retries=60, input_cmd: str = None):
        global instances_outputs
        self.all_instances, self.instances_named = self.ls(interactive=False)
        results = []
        executed = False
        if not self.selected_instances:
            print(bad('You didn\'t select any containers to execute the command.'))
            return

        for cg, containers in self.instances_named.items():
            if cg in self.selected_instances:
                for cont in containers:
                    executed = True
                    result = pool.apply_async(exec_command, 
                                             (self.rg, cg, cont, command, max_retries), 
                                              callback=build_output)
                    results.append(result)
        
        if not executed:
            print(bad('An error happened. You probably didn\'t select any containers to execute the command.'))
            return
        
        results = [result.wait() for result in results]

        for c, o in instances_outputs.items():
            if o:
                print(good(f'Executed command on {bold(c)}. Output: [\n{o}\n]'))
            else:
                if max_retries == 0:
                    print(good(f'Executed command on {bold(c)}'))
                else:
                    print(bad(f'Executed command on {bold(c)} Output: FAILED TO PARSE'))

        instances_outputs = {}

        return

    def scan(self, command: list = None, instance_num: int = 3, fleet_name: str = 'acido', interactive=False):
        response = {}
        if instance_num > 10:
            instance_num_groups = list(chunks(range(1, instance_num + 1), 10))
            for cg_n, ins_num in enumerate(instance_num_groups):
                group_name = f'{fleet_name}-{cg_n+1:02d}'
                env_vars = {
                    'RG': self.rg,
                    'IMAGE_REGISTRY_SERVER': self.image_registry_server,
                    'IMAGE_REGISTRY_USERNAME': self.image_registry_username,
                    'IMAGE_REGISTRY_PASSWORD': self.image_registry_password
                }
                if group_name not in response.keys():
                    response[group_name] = []
                last_instance = len(ins_num)
                response[group_name] = self.instance_manager.deploy(
                                            name=group_name, 
                                            instance_number=last_instance,
                                            env_vars=env_vars
                                        )
        else:
            env_vars = {
                    'RG': self.rg,
                    'IMAGE_REGISTRY_SERVER': self.image_registry_server,
                    'IMAGE_REGISTRY_USERNAME': self.image_registry_username,
                    'IMAGE_REGISTRY_PASSWORD': self.image_registry_password
                }
            response[fleet_name] = self.instance_manager.deploy(
                command=command, 
                name=fleet_name, 
                instance_number=instance_num, 
                env_vars=env_vars
            )
        
        if not interactive:
            return response
        else:
            all_names = []
            all_groups = []

            for group, inst in response.items():
                all_groups.append(group)
                all_names += list(inst.keys())

            print(good(f"Successfully created new group/s: [ {bold(' '.join(all_groups))} ]"))
            print(good(f"Successfully created new scan/s: [ {bold(' '.join(all_names))} ]"))

            return

    def setup(self):
        rg = os.getenv('RG') if os.getenv('RG', None) else input(info('Please provide a Resource Group Name to deploy the ACIs: '))
        self.rg = rg
        image_registry_server = os.getenv('IMAGE_REGISTRY_SERVER') if os.getenv('RG', None) else input(info('Image Registry Server: '))
        image_registry_username = os.getenv('IMAGE_REGISTRY_USERNAME') if os.getenv('IMAGE_REGISTRY_USERNAME', None) else input(info('Image Registry Username: '))
        image_registry_password = os.getenv('IMAGE_REGISTRY_PASSWORD') if os.getenv('IMAGE_REGISTRY_PASSWORD', None) else input(info('Image Registry Password: '))
        self.selected_instances = []
        self.image_registry_server = image_registry_server
        self.image_registry_username = image_registry_username
        self.image_registry_password = image_registry_password
        self._save_config()

if __name__ == "__main__":
    acido = Acido()
    if args.config:
        acido.setup()

    if args.shell:
        acido.save_output(args.shell)
    if args.download_input:
        acido.load_input(args.download_input)
    if args.fleet:
        fleet_name = args.fleet if args.fleet else 'kali'
        instance_num = int(args.num_instances) if args.num_instances else 1
        acido.fleet(fleet_name, instance_num, interactive=bool(args.interactive))
    if args.select:
        acido.select(selection=args.select, interactive=bool(args.interactive))
    if args.exec_cmd:
        print(args.exec_cmd)
        pool = ThreadPool(processes=30)
        acido.exec(command=args.exec_cmd)
    if args.remove:
        acido.rm(args.remove)
    if args.interactive:
        code.interact(banner=f'acido {__version__}', local=locals())