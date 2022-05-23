from localstack.aws.api import RequestContext
from localstack.aws.api.ec2 import(CreateImageRequest,CreateImageResult,DescribeImagesRequest,DescribeImagesResult,DescribeInstancesRequest,DescribeInstancesResult,ImportImageRequest,ImportImageResult,InstanceState,Reservation,RunInstancesRequest,StartInstancesRequest,StartInstancesResult,StopInstancesRequest,StopInstancesResult,TerminateInstancesRequest,TerminateInstancesResult)
from localstack.services.moto import call_moto
from localstack.utils.aws import aws_stack
from moto.ec2 import ec2_backends
from localstack_ext.services.ec2.vmmanager.base import InvalidAMIIdError,VmManager
class MockVmManager(VmManager):
 @staticmethod
 def impl_name()->str:
  return "mock"
 def start_instances(self,context:RequestContext,start_instances_request:StartInstancesRequest)->StartInstancesResult:
  return call_moto(context)
 def run_instances(self,context:RequestContext,run_instances_request:RunInstancesRequest)->Reservation:
  image_id=run_instances_request.get("ImageId")
  if image_id:
   backend=ec2_backends[context.region]
   if image_id not in backend.amis:
    raise InvalidAMIIdError(image_id)
  return call_moto(context)
 def stop_instances(self,context:RequestContext,stop_instances_request:StopInstancesRequest)->StopInstancesResult:
  return call_moto(context)
 def terminate_instances(self,context:RequestContext,terminate_instances_request:TerminateInstancesRequest)->TerminateInstancesResult:
  return call_moto(context)
 def describe_instances(self,context:RequestContext,describe_instances_request:DescribeInstancesRequest)->DescribeInstancesResult:
  return call_moto(context)
 def create_image(self,context:RequestContext,create_image_request:CreateImageRequest)->CreateImageResult:
  return call_moto(context)
 def describe_images(self,context:RequestContext,describe_images_request:DescribeImagesRequest)->DescribeImagesResult:
  return call_moto(context)
 def import_image(self,context:RequestContext,import_image_request:ImportImageRequest)->ImportImageResult:
  return call_moto(context)
 def instance_state(self,instance_id:str)->InstanceState:
  instance=ec2_backends[aws_stack.get_region()].get_instance(instance_id)
  result={"Code":instance._state.code,"Name":instance._state.name}
  return result
 def initialise_images(self):
  pass
# Created by pyminifier (https://github.com/liftoff/pyminifier)
