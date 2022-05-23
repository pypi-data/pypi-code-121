import json
import logging
import os
import time
from typing import Dict,List
import requests
from localstack import config
from localstack.aws.api import RequestContext
from localstack.aws.api.ec2 import(ImportImageRequest,ImportImageResult,Reservation,RunInstancesRequest)
from localstack.config import in_docker
from localstack.constants import LOCALHOST
from localstack.services.generic_proxy import RegionBackend
from localstack.utils.common import get_free_tcp_port,to_str
from localstack_ext.config import DEFAULT_PORT_LOCAL_DAEMON
from localstack_ext.services.ec2.vmmanager.base import InternalError,VmManager
LOG=logging.getLogger(__name__)
VBOX_COMMAND="VBoxManage"
VBOX_PREFIX="localstack-ec2"
VM_SEED_ISO_URL="https://github.com/localstack/localstack-artifacts/raw/master/ec2-iso/seed.iso"
HOST_OS=None
class UnixVirtualBox:
 def create_vm(self,image,instance,disk):
  self.check_vm_env()
  LOG.info('Start VM instance "%s" from image "%s"',instance,image)
  vbmg=VBOX_COMMAND
  cmd_attach=f"{vbmg} storageattach"
  request={"op":"s3:download","file_name":"s3file.%s"%image,"bucket":disk["s3Bucket"],"key":disk["s3Key"],"overwrite":False}
  result=call_local_daemon(request)
  image_file=result["local_file"]
  cmd=f"{vbmg} internalcommands sethduuid {image_file}"
  run_local_daemon_cmd(cmd)
  vm_name=f"{VBOX_PREFIX}{instance}"
  cmd=f"{vbmg} createvm --name {vm_name} --register"
  run_local_daemon_cmd(cmd)
  cmd=f'{vbmg} storagectl {vm_name} --name "SATA" --add sata --bootable on --portcount 1'
  run_local_daemon_cmd(cmd)
  cmd=f"{cmd_attach} {vm_name} --storagectl SATA --port 0 --type hdd --medium {image_file}"
  run_local_daemon_cmd(cmd)
  host_iso=os.path.join(config.dirs.functions,"vm_seed.iso")
  cmd="test -e %s || wget -O %s %s"%(host_iso,host_iso,VM_SEED_ISO_URL)
  run_local_daemon_cmd(cmd)
  cmd=(f"{cmd_attach} {vm_name} --storagectl SATA --port 1 --type dvddrive --medium {host_iso}")
  run_local_daemon_cmd(cmd)
  request={"op":"root:ssh_proxy"}
  result=call_local_daemon(request)
  ssh_port=result.get("forward_port")or get_free_tcp_port()
  vm_host=result.get("host")
  cmd=(f'{vbmg} modifyvm {vm_name} --memory 1024 --nic1 nat --natpf1 "ssh,tcp,,{ssh_port},,22"')
  run_local_daemon_cmd(cmd)
  self.pre_startup(vm_name)
  cmd=f"{vbmg} startvm {vm_name} --type headless"
  result=run_local_daemon_cmd(cmd)
  time.sleep(3)
  return{"result":result,"host":vm_host,"ssh_port":ssh_port}
 def pre_startup(self,vm_name):
  pass
 def remove_vm(self,instance_id):
  cmd=f"{VBOX_COMMAND} controlvm MyVM poweroff"
  print(cmd)
 def check_vm_env(self):
  request={"op":"shell","command":"which %s"%VBOX_COMMAND}
  result=call_local_daemon(request)
  if not result.get("result"):
   raise InternalError("Please install VirtualBox and VBoxManage utility on the host system")
 def cleanup(self):
  try:
   lines=run_local_daemon_cmd("%s list vms"%VBOX_COMMAND)
   lines=lines.split("\n")
   for line in lines:
    vm_name=line.split(" ")[0].strip('"')
    if vm_name.startswith(VBOX_PREFIX):
     run_local_daemon_cmd(f"{VBOX_COMMAND} unregistervm {vm_name} --delete")
  except Exception:
   pass
class MacOsVirtualBox(UnixVirtualBox):
 pass
class LinuxVirtualBox(UnixVirtualBox):
 def pre_startup(self,vm_name):
  cmd=f"{VBOX_COMMAND} modifyvm {vm_name} --nictype1 virtio"
  run_local_daemon_cmd(cmd)
def get_virtualbox():
 global HOST_OS
 if not HOST_OS:
  result=call_local_daemon({"op":"getos"})
  HOST_OS=result["result"]
  LOG.debug("Determined host operating system type: %s",HOST_OS)
 if HOST_OS=="macos":
  return MacOsVirtualBox()
 if HOST_OS=="linux":
  return LinuxVirtualBox()
 raise InternalError("Host operating system not supported: %s"%HOST_OS)
def run_local_daemon_cmd(cmd):
 request={"op":"shell","command":cmd}
 response=call_local_daemon(request)
 if "result" in response:
  return response["result"]
 raise InternalError("Error running command: %s"%response.get("error"))
def call_local_daemon(data):
 host=config.DOCKER_HOST_FROM_CONTAINER if in_docker()else LOCALHOST
 endpoint=f"http://{host}:{DEFAULT_PORT_LOCAL_DAEMON}"
 result=requests.post(endpoint,json.dumps(data))
 if result.status_code>=400:
  raise InternalError("Error calling : %s"%result.content)
 return json.loads(to_str(result.content))
def is_daemon_running()->bool:
 request={"op":"root:ssh_proxy"}
 try:
  call_local_daemon(request)
  return True
 except Exception:
  return False
class Ec2Backend(RegionBackend):
 disk_containers:Dict[str,List[Dict]]
 instance_hosts:Dict[str,str]
 def __init__(self):
  super().__init__()
  self.disk_containers={}
  self.instance_hosts={}
class VirtualBoxVmManager(VmManager):
 @staticmethod
 def impl_name()->str:
  return "virtualbox"
 def import_image(self,context:RequestContext,import_image_request:ImportImageRequest)->ImportImageResult:
  raise NotImplementedError
 def run_instances(self,context:RequestContext,run_instances_request:RunInstancesRequest)->Reservation:
  raise NotImplementedError
# Created by pyminifier (https://github.com/liftoff/pyminifier)
