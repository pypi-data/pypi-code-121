from typing import Type
from localstack.aws.api import CommonServiceException,RequestContext
from localstack.aws.api.ec2 import(CopyImageRequest,CopyImageResult,CreateImageRequest,CreateImageResult,DescribeImagesRequest,DescribeImagesResult,DescribeInstancesRequest,DescribeInstancesResult,ImportImageRequest,ImportImageResult,InstanceState,RegisterImageRequest,RegisterImageResult,Reservation,RunInstancesRequest,StartInstancesRequest,StartInstancesResult,StopInstancesRequest,StopInstancesResult,TerminateInstancesRequest,TerminateInstancesResult)
from localstack.utils.objects import SubtypesInstanceManager
from localstack_ext import config as config_ext
class InstanceStateCode(int):
 pending=0
 running=16
 shutting_down=32
 terminated=48
 stopped=80
class InternalError(CommonServiceException):
 def __init__(self,message):
  super(InternalError,self).__init__(code="InternalError",message=message)
class IncorrectInstanceStateError(CommonServiceException):
 def __init__(self,instance_id):
  super(IncorrectInstanceStateError,self).__init__(code="IncorrectInstanceState",message=f"The instance '{instance_id}' is not in a state from which it can be started")
class InvalidAMIIdError(CommonServiceException):
 def __init__(self,ami_id):
  super(InvalidAMIIdError,self).__init__(code="InvalidAMIID.NotFound",message=f"The image id '{ami_id}' does not exist")
class InvalidInstanceIdError(CommonServiceException):
 def __init__(self,instance_id):
  super(InvalidInstanceIdError,self).__init__(code="InvalidInstanceID.NotFound",message=f"The instance ID '{instance_id}' does not exist")
class MissingParameterError(CommonServiceException):
 def __init__(self,parameter):
  super(MissingParameterError,self).__init__(code="MissingParameter",message=f"The request must contain the parameter {parameter}")
class VmManager(SubtypesInstanceManager):
 @classmethod
 def get_base_type(cls)->Type:
  return VmManager
 @classmethod
 def get_manager(cls)->"VmManager":
  return cls.get(config_ext.EC2_VM_MANAGER)
 def start_instances(self,context:RequestContext,start_instances_request:StartInstancesRequest)->StartInstancesResult:
  raise NotImplementedError
 def run_instances(self,context:RequestContext,run_instances_request:RunInstancesRequest)->Reservation:
  raise NotImplementedError
 def stop_instances(self,context:RequestContext,stop_instances_request:StopInstancesRequest)->StopInstancesResult:
  raise NotImplementedError
 def terminate_instances(self,context:RequestContext,terminate_instances_request:TerminateInstancesRequest)->TerminateInstancesResult:
  raise NotImplementedError
 def describe_instances(self,context:RequestContext,describe_instances_request:DescribeInstancesRequest)->DescribeInstancesResult:
  raise NotImplementedError
 def create_image(self,context:RequestContext,create_image_request:CreateImageRequest)->CreateImageResult:
  raise NotImplementedError
 def describe_images(self,context:RequestContext,describe_images_request:DescribeImagesRequest)->DescribeImagesResult:
  raise NotImplementedError
 def import_image(self,context:RequestContext,import_image_request:ImportImageRequest)->ImportImageResult:
  raise NotImplementedError
 def instance_state(self,instance_id:str)->InstanceState:
  raise NotImplementedError
 def initialise_images(self):
  raise NotImplementedError
 def register_image(self,context:RequestContext,register_image_request:RegisterImageRequest)->RegisterImageResult:
  raise NotImplementedError
 def copy_image(self,context:RequestContext,copy_image_request:CopyImageRequest)->CopyImageResult:
  raise NotImplementedError
# Created by pyminifier (https://github.com/liftoff/pyminifier)
