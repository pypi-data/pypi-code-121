import base64
import logging
import os
import tempfile
from typing import Dict,List,Tuple
import parse
from cryptography.hazmat.primitives import serialization
from localstack import config
from localstack.aws.api import RequestContext
from localstack.aws.api.ec2 import(CopyImageRequest,CopyImageResult,CreateImageRequest,CreateImageResult,DescribeImagesRequest,DescribeImagesResult,DescribeInstancesRequest,DescribeInstancesResult,ImageState,InstanceState,InstanceStateChange,InstanceStateName,RegisterImageRequest,RegisterImageResult,Reservation,RunInstancesRequest,StartInstancesRequest,StartInstancesResult,StopInstancesRequest,StopInstancesResult,TerminateInstancesRequest,TerminateInstancesResult)
from localstack.services.install import ARTIFACTS_REPO
from localstack.services.moto import call_moto
from localstack.utils.common import get_free_tcp_port
from localstack.utils.container_utils.container_client import(ContainerException,NoSuchContainer,NoSuchImage)
from localstack.utils.container_utils.docker_sdk_client import PortMappings
from localstack.utils.docker_utils import DOCKER_CLIENT
from localstack.utils.files import chmod_r,file_exists_not_empty
from localstack.utils.strings import short_uid,to_str
from localstack.utils.sync import retry
from localstack.utils.threads import start_thread
from moto.ec2 import ec2_backends
from moto.ec2.models.amis import Ami
from localstack_ext.bootstrap.install import download_github_artifact
from localstack_ext.services.ec2.vmmanager.base import(IncorrectInstanceStateError,InstanceStateCode,InvalidAMIIdError,InvalidInstanceIdError,MissingParameterError,VmManager)
from localstack_ext.services.ec2.vmmanager.virtualbox import call_local_daemon,is_daemon_running
LOG=logging.getLogger(__name__)
URL_DROPBEAR=f"{ARTIFACTS_REPO}/raw/master/ssh-server/dropbear"
URL_SCP=f"{ARTIFACTS_REPO}/raw/master/ssh-server/scp"
CLOUD_INIT_LOG_DIR="/var/log"
CLOUD_INIT_LOG_PATH=f"{CLOUD_INIT_LOG_DIR}/cloud-init-output.log"
DOCKER_PREFIX="localstack-ec2"
CONTAINER_NAME_TEMPL="{docker_prefix}.{instance_id}"
IMAGE_NAME_TEMPL="{docker_prefix}/{ami_name}"
CONTAINER_EC2_STATE_MAPPING:Dict[str,Tuple[int,str]]={"created":(InstanceStateCode.pending,InstanceStateName.pending),"running":(InstanceStateCode.running,InstanceStateName.running),"restarting":(InstanceStateCode.shutting_down,InstanceStateName.shutting_down),"exited":(InstanceStateCode.terminated,InstanceStateName.terminated),"paused":(InstanceStateCode.stopped,InstanceStateName.stopped),"dead":(InstanceStateCode.terminated,InstanceStateName.terminated)}
UBUNTU_FOCAL_AMI=("ami-ff0fea8310f3","ubuntu-20.04-focal-fossa")
class DockerVmManager(VmManager):
 @staticmethod
 def impl_name()->str:
  return "docker"
 @staticmethod
 def image_name_from_ami_name(ami_name:str)->str:
  return IMAGE_NAME_TEMPL.format(docker_prefix=DOCKER_PREFIX,ami_name=ami_name)
 @staticmethod
 def container_name_from_instance_id(instance_id:str,verify:bool=True)->str:
  container_name=CONTAINER_NAME_TEMPL.format(docker_prefix=DOCKER_PREFIX,instance_id=instance_id)
  if verify:
   try:
    DOCKER_CLIENT.inspect_container(container_name)
   except NoSuchContainer:
    raise InvalidInstanceIdError(instance_id)
  return container_name
 @staticmethod
 def image_from_ami_id(ami_id:str,verify:bool=True)->str:
  for image in DOCKER_CLIENT.get_docker_image_names():
   name,_,tag=image.rpartition(":")
   if name.startswith(DOCKER_PREFIX)and tag==ami_id:
    return image
  if verify:
   raise InvalidAMIIdError(ami_id)
  return ""
 @staticmethod
 def ami_id_from_image(docker_image:str)->str:
  return docker_image.split(":")[-1]
 @staticmethod
 def ami_name_from_image(docker_image:str)->str:
  image_name,_=docker_image.split(":")
  return parse.parse(IMAGE_NAME_TEMPL,image_name)["ami_name"]
 @staticmethod
 def instance_id_from_container_name(container_name:str)->str:
  return parse.parse(CONTAINER_NAME_TEMPL,container_name)["instance_id"]
 def instance_state(self,instance_id:str)->InstanceState:
  container_name=self.container_name_from_instance_id(instance_id,verify=False)
  try:
   container_obj=DOCKER_CLIENT.inspect_container(container_name)
  except NoSuchContainer:
   raise InvalidInstanceIdError(instance_id)
  container_status=container_obj["State"]["Status"]
  code,name=CONTAINER_EC2_STATE_MAPPING[container_status]
  return InstanceState(Code=code,Name=name)
 def initialise_images(self):
  IMAGES=[("ami-a33ac4f1069a","alpine-3.14.4","alpine:3.14.4"),(*UBUNTU_FOCAL_AMI,"ubuntu:20.04")]
  for image in IMAGES:
   ami_id,ami_name,docker_image=image
   try:
    DOCKER_CLIENT.inspect_image(docker_image)
   except NoSuchImage:
    DOCKER_CLIENT.pull_image(docker_image)
   DOCKER_CLIENT.tag_image(source_ref=docker_image,target_name="{}:{}".format(self.image_name_from_ami_name(ami_name),ami_id))
 def start_instances(self,context:RequestContext,start_instances_request:StartInstancesRequest)->StartInstancesResult:
  instance_ids=start_instances_request["InstanceIds"]
  backend=ec2_backends[context.region]
  state_change_list:List[InstanceStateChange]=[]
  for instance_id in instance_ids:
   LOG.debug("Starting EC2 instance %s"%instance_id)
   container_name=self.container_name_from_instance_id(instance_id,verify=True)
   previous_state=self.instance_state(instance_id)
   if previous_state["Code"]==InstanceStateCode.stopped:
    DOCKER_CLIENT.unpause_container(container_name)
   elif previous_state["Code"]==InstanceStateCode.terminated:
    raise IncorrectInstanceStateError(instance_id)
   current_state=self.instance_state(instance_id)
   state_change_list.append(InstanceStateChange(CurrentState=current_state,PreviousState=previous_state,InstanceId=instance_id))
   backend.get_instance(instance_id).start()
  return StartInstancesResult(StartingInstances=state_change_list)
 def stop_instances(self,context:RequestContext,stop_instances_request:StopInstancesRequest)->StopInstancesResult:
  instance_ids=stop_instances_request["InstanceIds"]
  backend=ec2_backends[context.region]
  state_change_list:List[InstanceStateChange]=[]
  for instance_id in instance_ids:
   LOG.debug("Stopping EC2 instance %s"%instance_id)
   container_name=self.container_name_from_instance_id(instance_id,verify=True)
   previous_state=self.instance_state(instance_id)
   if previous_state["Code"]==InstanceStateCode.running:
    DOCKER_CLIENT.pause_container(container_name)
   current_state=self.instance_state(instance_id)
   state_change_list.append(InstanceStateChange(CurrentState=current_state,PreviousState=previous_state,InstanceId=instance_id))
   moto_instance=backend.get_instance(instance_id)
   moto_instance.stop()
  return StopInstancesResult(StoppingInstances=state_change_list)
 def terminate_instances(self,context:RequestContext,terminate_instances_request:TerminateInstancesRequest)->TerminateInstancesResult:
  instance_ids=terminate_instances_request["InstanceIds"]
  backend=ec2_backends[context.region]
  state_change_list:List[InstanceStateChange]=[]
  for instance_id in instance_ids:
   LOG.debug("Terminating EC2 instance %s"%instance_id)
   container_name=self.container_name_from_instance_id(instance_id,verify=True)
   previous_state=self.instance_state(instance_id)
   if previous_state["Code"]in(InstanceStateCode.running,InstanceStateCode.stopped):
    DOCKER_CLIENT.stop_container(container_name)
   current_state=self.instance_state(instance_id)
   state_change_list.append(InstanceStateChange(CurrentState=current_state,PreviousState=previous_state,InstanceId=instance_id))
   moto_instance=backend.get_instance(instance_id)
   moto_instance.terminate()
  return TerminateInstancesResult(TerminatingInstances=state_change_list)
 def run_instances(self,context:RequestContext,run_instances_request:RunInstancesRequest)->Reservation:
  ami_id=run_instances_request.get("ImageId")
  if not ami_id:
   raise MissingParameterError("ImageId")
  user_data=run_instances_request.get("UserData")
  backend=ec2_backends[context.region]
  try:
   docker_image=self.image_from_ami_id(ami_id,verify=True)
  except InvalidAMIIdError as exc:
   if(ami_id in backend.amis.keys()and backend.amis[ami_id].get_filter_value("tag:ec2_vm_manager")=="docker"):
    LOG.debug(f"Deregistering AMI '{ami_id}' because it no longer exists in Docker")
    backend.amis.pop(ami_id,None)
   raise exc
  key_name=run_instances_request.get("KeyName")
  ssh_public_key=""
  moto_reservation=call_moto(context)
  if key_name:
   key_pair=backend.describe_key_pairs([key_name])[0]
   if key_pair.material.startswith("ssh-rsa"):
    ssh_public_key=key_pair.material
   elif key_pair.material.startswith("-----BEGIN RSA PRIVATE KEY-----"):
    private_key=serialization.load_pem_private_key(key_pair.material.encode(),password=None)
    public_key=private_key.public_key().public_bytes(encoding=serialization.Encoding.OpenSSH,format=serialization.PublicFormat.OpenSSH)
    ssh_public_key=to_str(public_key)
   else:
    ssh_public_key=to_str(base64.b64decode(key_pair.material))
  for moto_instance in moto_reservation["Instances"]:
   instance_id=moto_instance["InstanceId"]
   container_name=self.container_name_from_instance_id(instance_id,verify=False)
   port_mappings=PortMappings()
   host="127.0.0.1"
   ssh_port=get_free_tcp_port()
   accessible_at=[f"{host}:{ssh_port}"]
   if is_daemon_running():
    daemon_reservation=call_local_daemon({"op":"root:ssh_proxy"})
    host=daemon_reservation.get("host")
    ssh_port=daemon_reservation.get("forward_port")
    accessible_at=[f"{host}:22",f"127.0.0.1:{ssh_port}"]
   port_mappings.add(ssh_port,22)
   try:
    LOG.debug("Launching instance %s",instance_id)
    DOCKER_CLIENT.run_container(docker_image,remove=False,env_vars={},name=container_name,command=["sleep","43200"],detach=True,ports=port_mappings,mount_volumes=[("/var/run/docker.sock","/var/run/docker.sock")])
    ip_address=DOCKER_CLIENT.inspect_container(container_name)["NetworkSettings"]["IPAddress"]
    accessible_at.append(f"{ip_address}:22")
    LOG.info("Instance %s will be accessible via SSH at: %s",instance_id,", ".join(accessible_at))
    def _assert_container_running():
     assert container_name in DOCKER_CLIENT.get_running_container_names()
    retry(_assert_container_running,sleep=1,retries=10)
    start_thread(self._cloud_init,(container_name,ssh_public_key,user_data))
   except ContainerException as exc:
    LOG.warning("Error launching instance %s: %s",instance_id,exc)
    backend.get_instance(instance_id).start()
  return moto_reservation
 def describe_instances(self,context:RequestContext,describe_instances_request:DescribeInstancesRequest)->DescribeInstancesResult:
  backend=ec2_backends[context.region]
  for instance in backend.all_instances():
   try:
    container_state_code=self.instance_state(instance.id)["Code"]
   except InvalidInstanceIdError:
    continue
   if(container_state_code==InstanceStateCode.stopped and instance._state.code!=InstanceStateCode.stopped):
    instance.stop()
   elif(container_state_code==InstanceStateCode.terminated and instance._state.code!=InstanceStateCode.terminated):
    instance.terminate()
   elif(container_state_code==InstanceStateCode.running and instance._state.code!=InstanceStateCode.running):
    instance.start()
  return call_moto(context)
 def create_image(self,context:RequestContext,create_image_request:CreateImageRequest)->CreateImageResult:
  instance_id=create_image_request["InstanceId"]
  ami_name=create_image_request["Name"]
  image_name=self.image_name_from_ami_name(ami_name)
  image_tag=f"ami-{short_uid()}"
  container_name=self.container_name_from_instance_id(instance_id,verify=True)
  LOG.debug("Creating image %s named %s from instance %s",image_tag,ami_name,instance_id)
  DOCKER_CLIENT.commit(container_name,image_name,image_tag)
  return CreateImageResult(ImageId=image_tag)
 def register_image(self,context:RequestContext,register_image_request:RegisterImageRequest)->RegisterImageResult:
  backend=ec2_backends[context.region]
  ami_id=f"ami-{short_uid()}"
  root_device=register_image_request["RootDeviceName"]
  block_device=next(device for device in register_image_request["BlockDeviceMappings"]if device["DeviceName"]==root_device)
  if "Ebs" in block_device:
   root_type="ebs"
  else:
   root_type="standard"
  ami=Ami(backend,ami_id,instance=None,source_ami=None,name=register_image_request["Name"],description=register_image_request["Description"],root_device_name=register_image_request["RootDeviceName"],root_device_type=root_type)
  backend.amis[ami_id]=ami
  return RegisterImageResult(ImageId=ami_id)
 def copy_image(self,context:RequestContext,copy_image_request:CopyImageRequest)->CopyImageResult:
  backend=ec2_backends[context.region]
  source_ami=backend.describe_images(ami_ids=[copy_image_request["SourceImageId"]])[0]
  ami_id=f"ami-{short_uid()}"
  ami=Ami(backend,ami_id,instance=None,source_ami=source_ami,name=copy_image_request["Name"],description=copy_image_request["Description"],root_device_name=source_ami.root_device_name,root_device_type=source_ami.root_device_type)
  backend.amis[ami_id]=ami
  return CopyImageResult(ImageId=ami_id)
 def describe_images(self,context:RequestContext,describe_images_request:DescribeImagesRequest)->DescribeImagesResult:
  backend=ec2_backends[context.region]
  for docker_image in DOCKER_CLIENT.get_docker_image_names():
   if docker_image.startswith(DOCKER_PREFIX):
    image_obj=DOCKER_CLIENT.inspect_image(docker_image)
    ami_id=self.ami_id_from_image(docker_image)
    backend.amis[ami_id]=Ami(backend,ami_id=ami_id,name=self.ami_name_from_image(docker_image),architecture=image_obj.get("Architecture"),creation_date=image_obj.get("Created"),public=True,state=ImageState.available,image_location="docker")
    backend.amis[ami_id].add_tag("ec2_vm_manager","docker")
  amis_in_docker=[image.split(":")[-1]for image in DOCKER_CLIENT.get_docker_image_names()if "ami-" in image]
  amis_in_moto=backend.describe_images(filters={"tag:ec2_vm_manager":["docker"]})
  for moto_ami in amis_in_moto:
   if moto_ami.id not in amis_in_docker:
    LOG.debug(f"Deregistering AMI '{moto_ami.id}' because it no longer exists in Docker")
    backend.amis.pop(moto_ami.id,None)
  return call_moto(context)
 def _cloud_init(self,params):
  container_name,ssh_private_key,user_data=params
  DOCKER_CLIENT.exec_in_container(container_name,f"mkdir -p {CLOUD_INIT_LOG_DIR}")
  try:
   LOG.debug("Starting ssh setup in container: %s",container_name)
   dropbear_path_src=os.path.join(config.TMP_FOLDER,"dropbear-sshd")
   if not file_exists_not_empty(dropbear_path_src):
    download_github_artifact(URL_DROPBEAR,dropbear_path_src)
    chmod_r(dropbear_path_src,0o777)
   scp_path_src=os.path.join(config.TMP_FOLDER,"scp")
   if not file_exists_not_empty(scp_path_src):
    download_github_artifact(URL_SCP,scp_path_src)
    chmod_r(scp_path_src,0o777)
   dropbear_path_dest="/usr/bin/dropbear"
   DOCKER_CLIENT.copy_into_container(container_name,scp_path_src,"/usr/bin/scp")
   DOCKER_CLIENT.copy_into_container(container_name,dropbear_path_src,dropbear_path_dest)
   DOCKER_CLIENT.exec_in_container(container_name,["mkdir","-p","/etc/dropbear"])
   if ssh_private_key:
    DOCKER_CLIENT.exec_in_container(container_name,["sh","-c",f'mkdir -p $HOME/.ssh; echo -n "{ssh_private_key}" >> $HOME/.ssh/authorized_keys'])
   DOCKER_CLIENT.exec_in_container(container_name,[dropbear_path_dest,"-R","-p","22"])
   LOG.debug("Finished ssh setup in container: %s",container_name)
  except Exception as exc:
   LOG.warning("Failed ssh setup: %s",exc)
  if user_data:
   LOG.debug("Starting userdata setup in container: %s",container_name)
   instance_id=self.instance_id_from_container_name(container_name)
   LOG.debug("Copying userdata into container: %s",container_name)
   user_data_dir=f"/var/lib/cloud/instances/{instance_id}"
   user_data_path=f"/var/lib/cloud/instances/{instance_id}/user-data.txt"
   data_fd,data_path=tempfile.mkstemp()
   os.write(data_fd,base64.b64decode(user_data))
   DOCKER_CLIENT.exec_in_container(container_name,f"mkdir -p {user_data_dir}")
   DOCKER_CLIENT.copy_into_container(container_name,data_path,user_data_path)
   LOG.debug("Executing userdata in container: %s",container_name)
   DOCKER_CLIENT.exec_in_container(container_name,f"chmod +x {user_data_path}")
   DOCKER_CLIENT.exec_in_container(container_name,f'sh -c "{user_data_path} 2>&1 | tee --append {CLOUD_INIT_LOG_PATH}"')
   LOG.debug("Finished userdata setup in container: %s",container_name)
# Created by pyminifier (https://github.com/liftoff/pyminifier)
