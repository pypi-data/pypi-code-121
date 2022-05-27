_J='Description'
_I='InstanceId'
_H='tag:ec2_vm_manager'
_G='Name'
_F='InstanceIds'
_E=False
_D='Code'
_C='docker'
_B=None
_A=True
import base64,logging,os,tempfile
from typing import Dict,List,Tuple
import parse
from cryptography.hazmat.primitives import serialization
from localstack import config
from localstack.aws.api import RequestContext
from localstack.aws.api.ec2 import CopyImageRequest,CopyImageResult,CreateImageRequest,CreateImageResult,DescribeImagesRequest,DescribeImagesResult,DescribeInstancesRequest,DescribeInstancesResult,ImageState,InstanceState,InstanceStateChange,InstanceStateName,RegisterImageRequest,RegisterImageResult,Reservation,RunInstancesRequest,StartInstancesRequest,StartInstancesResult,StopInstancesRequest,StopInstancesResult,TerminateInstancesRequest,TerminateInstancesResult
from localstack.services.install import ARTIFACTS_REPO
from localstack.services.moto import call_moto
from localstack.utils.common import get_free_tcp_port
from localstack.utils.container_utils.container_client import ContainerException,NoSuchContainer,NoSuchImage
from localstack.utils.container_utils.docker_sdk_client import PortMappings
from localstack.utils.docker_utils import DOCKER_CLIENT
from localstack.utils.files import chmod_r,file_exists_not_empty
from localstack.utils.strings import short_uid,to_str
from localstack.utils.sync import retry
from localstack.utils.threads import start_thread
from moto.ec2 import ec2_backends
from moto.ec2.models.amis import Ami
from localstack_ext.bootstrap.install import download_github_artifact
from localstack_ext.services.ec2.vmmanager.base import IncorrectInstanceStateError,InstanceStateCode,InvalidAMIIdError,InvalidInstanceIdError,MissingParameterError,VmManager
from localstack_ext.services.ec2.vmmanager.virtualbox import call_local_daemon,is_daemon_running
LOG=logging.getLogger(__name__)
URL_DROPBEAR=f"{ARTIFACTS_REPO}/raw/master/ssh-server/dropbear"
URL_SCP=f"{ARTIFACTS_REPO}/raw/master/ssh-server/scp"
CLOUD_INIT_LOG_DIR='/var/log'
CLOUD_INIT_LOG_PATH=f"{CLOUD_INIT_LOG_DIR}/cloud-init-output.log"
DOCKER_PREFIX='localstack-ec2'
CONTAINER_NAME_TEMPL='{docker_prefix}.{instance_id}'
IMAGE_NAME_TEMPL='{docker_prefix}/{ami_name}'
CONTAINER_EC2_STATE_MAPPING={'created':(InstanceStateCode.pending,InstanceStateName.pending),'running':(InstanceStateCode.running,InstanceStateName.running),'restarting':(InstanceStateCode.shutting_down,InstanceStateName.shutting_down),'exited':(InstanceStateCode.terminated,InstanceStateName.terminated),'paused':(InstanceStateCode.stopped,InstanceStateName.stopped),'dead':(InstanceStateCode.terminated,InstanceStateName.terminated)}
UBUNTU_FOCAL_AMI='ami-ff0fea8310f3','ubuntu-20.04-focal-fossa'
class DockerVmManager(VmManager):
	@staticmethod
	def impl_name():return _C
	@staticmethod
	def image_name_from_ami_name(ami_name):return IMAGE_NAME_TEMPL.format(docker_prefix=DOCKER_PREFIX,ami_name=ami_name)
	@staticmethod
	def container_name_from_instance_id(instance_id,verify=_A):
		A=instance_id;B=CONTAINER_NAME_TEMPL.format(docker_prefix=DOCKER_PREFIX,instance_id=A)
		if verify:
			try:DOCKER_CLIENT.inspect_container(B)
			except NoSuchContainer:raise InvalidInstanceIdError(A)
		return B
	@staticmethod
	def image_from_ami_id(ami_id,verify=_A):
		A=ami_id
		for B in DOCKER_CLIENT.get_docker_image_names():
			C,E,D=B.rpartition(':')
			if C.startswith(DOCKER_PREFIX)and D==A:return B
		if verify:raise InvalidAMIIdError(A)
		return''
	@staticmethod
	def ami_id_from_image(docker_image):return docker_image.split(':')[-1]
	@staticmethod
	def ami_name_from_image(docker_image):A,B=docker_image.split(':');return parse.parse(IMAGE_NAME_TEMPL,A)['ami_name']
	@staticmethod
	def instance_id_from_container_name(container_name):return parse.parse(CONTAINER_NAME_TEMPL,container_name)['instance_id']
	def instance_state(B,instance_id):
		A=instance_id;C=B.container_name_from_instance_id(A,verify=_E)
		try:D=DOCKER_CLIENT.inspect_container(C)
		except NoSuchContainer:raise InvalidInstanceIdError(A)
		E=D['State']['Status'];F,G=CONTAINER_EC2_STATE_MAPPING[E];return InstanceState(Code=F,Name=G)
	def initialise_images(B):
		C=[('ami-a33ac4f1069a','alpine-3.14.4','alpine:3.14.4'),(*(UBUNTU_FOCAL_AMI),'ubuntu:20.04')]
		for D in C:
			E,F,A=D
			try:DOCKER_CLIENT.inspect_image(A)
			except NoSuchImage:DOCKER_CLIENT.pull_image(A)
			DOCKER_CLIENT.tag_image(source_ref=A,target_name='{}:{}'.format(B.image_name_from_ami_name(F),E))
	def start_instances(B,context,start_instances_request):
		E=start_instances_request[_F];F=ec2_backends[context.region];D=[]
		for A in E:
			LOG.debug('Starting EC2 instance %s'%A);G=B.container_name_from_instance_id(A,verify=_A);C=B.instance_state(A)
			if C[_D]==InstanceStateCode.stopped:DOCKER_CLIENT.unpause_container(G)
			elif C[_D]==InstanceStateCode.terminated:raise IncorrectInstanceStateError(A)
			H=B.instance_state(A);D.append(InstanceStateChange(CurrentState=H,PreviousState=C,InstanceId=A));F.get_instance(A).start()
		return StartInstancesResult(StartingInstances=D)
	def stop_instances(B,context,stop_instances_request):
		E=stop_instances_request[_F];F=ec2_backends[context.region];C=[]
		for A in E:
			LOG.debug('Stopping EC2 instance %s'%A);G=B.container_name_from_instance_id(A,verify=_A);D=B.instance_state(A)
			if D[_D]==InstanceStateCode.running:DOCKER_CLIENT.pause_container(G)
			H=B.instance_state(A);C.append(InstanceStateChange(CurrentState=H,PreviousState=D,InstanceId=A));I=F.get_instance(A);I.stop()
		return StopInstancesResult(StoppingInstances=C)
	def terminate_instances(B,context,terminate_instances_request):
		E=terminate_instances_request[_F];F=ec2_backends[context.region];C=[]
		for A in E:
			LOG.debug('Terminating EC2 instance %s'%A);G=B.container_name_from_instance_id(A,verify=_A);D=B.instance_state(A)
			if D[_D]in(InstanceStateCode.running,InstanceStateCode.stopped):DOCKER_CLIENT.stop_container(G)
			H=B.instance_state(A);C.append(InstanceStateChange(CurrentState=H,PreviousState=D,InstanceId=A));I=F.get_instance(A);I.terminate()
		return TerminateInstancesResult(TerminatingInstances=C)
	def run_instances(H,context,run_instances_request):
		S='/var/run/docker.sock';R='ImageId';M=context;I=run_instances_request;A=I.get(R)
		if not A:raise MissingParameterError(R)
		T=I.get('UserData');B=ec2_backends[M.region]
		try:U=H.image_from_ami_id(A,verify=_A)
		except InvalidAMIIdError as J:
			if A in B.amis.keys()and B.amis[A].get_filter_value(_H)==_C:LOG.debug(f"Deregistering AMI '{A}' because it no longer exists in Docker");B.amis.pop(A,_B)
			raise J
		N=I.get('KeyName');E='';O=call_moto(M)
		if N:
			C=B.describe_key_pairs([N])[0]
			if C.material.startswith('ssh-rsa'):E=C.material
			elif C.material.startswith('-----BEGIN RSA PRIVATE KEY-----'):V=serialization.load_pem_private_key(C.material.encode(),password=_B);W=V.public_key().public_bytes(encoding=serialization.Encoding.OpenSSH,format=serialization.PublicFormat.OpenSSH);E=to_str(W)
			else:E=to_str(base64.b64decode(C.material))
		for X in O['Instances']:
			D=X[_I];F=H.container_name_from_instance_id(D,verify=_E);P=PortMappings();K='127.0.0.1';G=get_free_tcp_port();L=[f"{K}:{G}"]
			if is_daemon_running():Q=call_local_daemon({'op':'root:ssh_proxy'});K=Q.get('host');G=Q.get('forward_port');L=[f"{K}:22",f"127.0.0.1:{G}"]
			P.add(G,22)
			try:
				LOG.debug('Launching instance %s',D);DOCKER_CLIENT.run_container(U,remove=_E,env_vars={},name=F,command=['sleep','43200'],detach=_A,ports=P,mount_volumes=[(S,S)]);Y=DOCKER_CLIENT.inspect_container(F)['NetworkSettings']['IPAddress'];L.append(f"{Y}:22");LOG.info('Instance %s will be accessible via SSH at: %s',D,', '.join(L))
				def Z():assert F in DOCKER_CLIENT.get_running_container_names()
				retry(Z,sleep=1,retries=10);start_thread(H._cloud_init,(F,E,T))
			except ContainerException as J:LOG.warning('Error launching instance %s: %s',D,J);B.get_instance(D).start()
		return O
	def describe_instances(D,context,describe_instances_request):
		C=context;E=ec2_backends[C.region]
		for A in E.all_instances():
			try:B=D.instance_state(A.id)[_D]
			except InvalidInstanceIdError:continue
			if B==InstanceStateCode.stopped and A._state.code!=InstanceStateCode.stopped:A.stop()
			elif B==InstanceStateCode.terminated and A._state.code!=InstanceStateCode.terminated:A.terminate()
			elif B==InstanceStateCode.running and A._state.code!=InstanceStateCode.running:A.start()
		return call_moto(C)
	def create_image(B,context,create_image_request):C=create_image_request;D=C[_I];E=C[_G];F=B.image_name_from_ami_name(E);A=f"ami-{short_uid()}";G=B.container_name_from_instance_id(D,verify=_A);LOG.debug('Creating image %s named %s from instance %s',A,E,D);DOCKER_CLIENT.commit(G,F,A);return CreateImageResult(ImageId=A)
	def register_image(I,context,register_image_request):
		E='RootDeviceName';A=register_image_request;C=ec2_backends[context.region];B=f"ami-{short_uid()}";F=A[E];G=next((B for B in A['BlockDeviceMappings']if B['DeviceName']==F))
		if'Ebs'in G:D='ebs'
		else:D='standard'
		H=Ami(C,B,instance=_B,source_ami=_B,name=A[_G],description=A[_J],root_device_name=A[E],root_device_type=D);C.amis[B]=H;return RegisterImageResult(ImageId=B)
	def copy_image(F,context,copy_image_request):A=copy_image_request;B=ec2_backends[context.region];C=B.describe_images(ami_ids=[A['SourceImageId']])[0];D=f"ami-{short_uid()}";E=Ami(B,D,instance=_B,source_ami=C,name=A[_G],description=A[_J],root_device_name=C.root_device_name,root_device_type=C.root_device_type);B.amis[D]=E;return CopyImageResult(ImageId=D)
	def describe_images(E,context,describe_images_request):
		F=context;A=ec2_backends[F.region]
		for B in DOCKER_CLIENT.get_docker_image_names():
			if B.startswith(DOCKER_PREFIX):G=DOCKER_CLIENT.inspect_image(B);C=E.ami_id_from_image(B);A.amis[C]=Ami(A,ami_id=C,name=E.ami_name_from_image(B),architecture=G.get('Architecture'),creation_date=G.get('Created'),public=_A,state=ImageState.available,image_location=_C);A.amis[C].add_tag('ec2_vm_manager',_C)
		H=[A.split(':')[-1]for A in DOCKER_CLIENT.get_docker_image_names()if'ami-'in A];I=A.describe_images(filters={_H:[_C]})
		for D in I:
			if D.id not in H:LOG.debug(f"Deregistering AMI '{D.id}' because it no longer exists in Docker");A.amis.pop(D.id,_B)
		return call_moto(F)
	def _cloud_init(I,params):
		A,E,F=params;DOCKER_CLIENT.exec_in_container(A,f"mkdir -p {CLOUD_INIT_LOG_DIR}")
		try:
			LOG.debug('Starting ssh setup in container: %s',A);B=os.path.join(config.TMP_FOLDER,'dropbear-sshd')
			if not file_exists_not_empty(B):download_github_artifact(URL_DROPBEAR,B);chmod_r(B,511)
			C=os.path.join(config.TMP_FOLDER,'scp')
			if not file_exists_not_empty(C):download_github_artifact(URL_SCP,C);chmod_r(C,511)
			G='/usr/bin/dropbear';DOCKER_CLIENT.copy_into_container(A,C,'/usr/bin/scp');DOCKER_CLIENT.copy_into_container(A,B,G);DOCKER_CLIENT.exec_in_container(A,['mkdir','-p','/etc/dropbear'])
			if E:DOCKER_CLIENT.exec_in_container(A,['sh','-c',f'mkdir -p $HOME/.ssh; echo -n "{E}" >> $HOME/.ssh/authorized_keys'])
			DOCKER_CLIENT.exec_in_container(A,[G,'-R','-p','22']);LOG.debug('Finished ssh setup in container: %s',A)
		except Exception as J:LOG.warning('Failed ssh setup: %s',J)
		if F:LOG.debug('Starting userdata setup in container: %s',A);H=I.instance_id_from_container_name(A);LOG.debug('Copying userdata into container: %s',A);K=f"/var/lib/cloud/instances/{H}";D=f"/var/lib/cloud/instances/{H}/user-data.txt";L,M=tempfile.mkstemp();os.write(L,base64.b64decode(F));DOCKER_CLIENT.exec_in_container(A,f"mkdir -p {K}");DOCKER_CLIENT.copy_into_container(A,M,D);LOG.debug('Executing userdata in container: %s',A);DOCKER_CLIENT.exec_in_container(A,f"chmod +x {D}");DOCKER_CLIENT.exec_in_container(A,f'sh -c "{D} 2>&1 | tee --append {CLOUD_INIT_LOG_PATH}"');LOG.debug('Finished userdata setup in container: %s',A)