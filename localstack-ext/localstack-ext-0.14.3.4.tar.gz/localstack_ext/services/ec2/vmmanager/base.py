from typing import Type
from localstack.aws.api import CommonServiceException,RequestContext
from localstack.aws.api.ec2 import CopyImageRequest,CopyImageResult,CreateImageRequest,CreateImageResult,DescribeImagesRequest,DescribeImagesResult,DescribeInstancesRequest,DescribeInstancesResult,ImportImageRequest,ImportImageResult,InstanceState,RegisterImageRequest,RegisterImageResult,Reservation,RunInstancesRequest,StartInstancesRequest,StartInstancesResult,StopInstancesRequest,StopInstancesResult,TerminateInstancesRequest,TerminateInstancesResult
from localstack.utils.objects import SubtypesInstanceManager
from localstack_ext import config as config_ext
class InstanceStateCode(int):pending=0;running=16;shutting_down=32;terminated=48;stopped=80
class InternalError(CommonServiceException):
	def __init__(A,message):super(InternalError,A).__init__(code='InternalError',message=message)
class IncorrectInstanceStateError(CommonServiceException):
	def __init__(A,instance_id):super(IncorrectInstanceStateError,A).__init__(code='IncorrectInstanceState',message=f"The instance '{instance_id}' is not in a state from which it can be started")
class InvalidAMIIdError(CommonServiceException):
	def __init__(A,ami_id):super(InvalidAMIIdError,A).__init__(code='InvalidAMIID.NotFound',message=f"The image id '{ami_id}' does not exist")
class InvalidInstanceIdError(CommonServiceException):
	def __init__(A,instance_id):super(InvalidInstanceIdError,A).__init__(code='InvalidInstanceID.NotFound',message=f"The instance ID '{instance_id}' does not exist")
class MissingParameterError(CommonServiceException):
	def __init__(A,parameter):super(MissingParameterError,A).__init__(code='MissingParameter',message=f"The request must contain the parameter {parameter}")
class VmManager(SubtypesInstanceManager):
	@classmethod
	def get_base_type(A):return VmManager
	@classmethod
	def get_manager(A):return A.get(config_ext.EC2_VM_MANAGER)
	def start_instances(A,context,start_instances_request):raise NotImplementedError
	def run_instances(A,context,run_instances_request):raise NotImplementedError
	def stop_instances(A,context,stop_instances_request):raise NotImplementedError
	def terminate_instances(A,context,terminate_instances_request):raise NotImplementedError
	def describe_instances(A,context,describe_instances_request):raise NotImplementedError
	def create_image(A,context,create_image_request):raise NotImplementedError
	def describe_images(A,context,describe_images_request):raise NotImplementedError
	def import_image(A,context,import_image_request):raise NotImplementedError
	def instance_state(A,instance_id):raise NotImplementedError
	def initialise_images(A):raise NotImplementedError
	def register_image(A,context,register_image_request):raise NotImplementedError
	def copy_image(A,context,copy_image_request):raise NotImplementedError