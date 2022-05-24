from localstack.aws.api import RequestContext
from localstack.aws.api.ec2 import CreateImageRequest,CreateImageResult,DescribeImagesRequest,DescribeImagesResult,DescribeInstancesRequest,DescribeInstancesResult,ImportImageRequest,ImportImageResult,InstanceState,Reservation,RunInstancesRequest,StartInstancesRequest,StartInstancesResult,StopInstancesRequest,StopInstancesResult,TerminateInstancesRequest,TerminateInstancesResult
from localstack.services.moto import call_moto
from localstack.utils.aws import aws_stack
from moto.ec2 import ec2_backends
from localstack_ext.services.ec2.vmmanager.base import InvalidAMIIdError,VmManager
class MockVmManager(VmManager):
	@staticmethod
	def impl_name():return'mock'
	def start_instances(A,context,start_instances_request):return call_moto(context)
	def run_instances(D,context,run_instances_request):
		B=context;A=run_instances_request.get('ImageId')
		if A:
			C=ec2_backends[B.region]
			if A not in C.amis:raise InvalidAMIIdError(A)
		return call_moto(B)
	def stop_instances(A,context,stop_instances_request):return call_moto(context)
	def terminate_instances(A,context,terminate_instances_request):return call_moto(context)
	def describe_instances(A,context,describe_instances_request):return call_moto(context)
	def create_image(A,context,create_image_request):return call_moto(context)
	def describe_images(A,context,describe_images_request):return call_moto(context)
	def import_image(A,context,import_image_request):return call_moto(context)
	def instance_state(C,instance_id):A=ec2_backends[aws_stack.get_region()].get_instance(instance_id);B={'Code':A._state.code,'Name':A._state.name};return B
	def initialise_images(A):0