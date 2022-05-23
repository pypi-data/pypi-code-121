import json
from localstack import config
from localstack.services.awslambda import lambda_executors
from localstack.services.cloudformation.service_models import GenericBaseModel
from localstack.utils.aws import aws_stack
from localstack.utils.common import recurse_object,retry,short_uid,to_str
from localstack.utils.testutil import map_all_s3_objects
from localstack_ext.services.cloudformation.service_models import(CUSTOM_RESOURCE_STATUSES,CUSTOM_RESOURCES_RESULT_POLL_TIMEOUT,CUSTOM_RESOURCES_RESULTS_BUCKET,LOG)
from localstack_ext.utils.aws import aws_utils
class CDKMetadata(GenericBaseModel):
 @staticmethod
 def cloudformation_type():
  return "AWS::CDK::Metadata"
 def fetch_state(self,stack_name,resources):
  return{"type":"AWS::CDK::Metadata"}
class CustomResource(GenericBaseModel):
 @staticmethod
 def cloudformation_type():
  return "AWS::CloudFormation::CustomResource"
 def fetch_state(self,stack_name,resources):
  resource_id=self.logical_resource_id
  result=(CUSTOM_RESOURCE_STATUSES.get(aws_stack.get_region(),{}).get(stack_name,{}).get(resource_id))
  return result
 def get_physical_resource_id(self,attribute,**kwargs):
  return self.state["result"]["PhysicalResourceId"]
 @staticmethod
 def get_deploy_templates():
  def create_custom_resource(resource_id,resources,resource_type,func,stack_name,*args):
   resource=resources[resource_id]
   resource_props=resource["Properties"]
   service_token=resource_props.get("ServiceToken")
   if not service_token:
    LOG.warning("Missing ServiceToken attribute in custom resource: %s"%resource)
    return
   def _convert(obj,**kwargs):
    if isinstance(obj,dict):
     for key,value in obj.items():
      if isinstance(value,bool):
       obj[key]=str(value).lower()
    return obj
   recurse_object(resource_props,_convert)
   aws_stack.get_or_create_bucket(CUSTOM_RESOURCES_RESULTS_BUCKET)
   result_key=short_uid()
   main_endpoint=lambda_executors.get_main_endpoint_from_container()
   endpoint_url="http://%s:%s"%(main_endpoint,config.get_edge_port_http())
   response_url=aws_stack.generate_presigned_url("put_object",Params={"Bucket":CUSTOM_RESOURCES_RESULTS_BUCKET,"Key":result_key},endpoint_url=endpoint_url)
   stack_arn=aws_stack.cloudformation_stack_arn(stack_name)
   request={"RequestType":"Create","ResponseURL":response_url,"StackId":stack_arn,"RequestId":short_uid(),"ResourceType":resource.get("Type"),"LogicalResourceId":resource_id,"ResourceProperties":resource_props}
   if str(service_token).startswith("arn:aws:lambda"):
    region_name=service_token.split(":")[3]
    function_name=aws_stack.lambda_function_name(service_token)
    lambda_client=aws_stack.connect_to_service("lambda",region_name=region_name)
    lambda_client.invoke(FunctionName=function_name,Payload=json.dumps(request))
   else:
    LOG.warning("Unsupported ServiceToken attribute in custom resource: %s"%service_token)
    return
   def fetch_result():
    return aws_utils.download_s3_object(CUSTOM_RESOURCES_RESULTS_BUCKET,result_key)
   result=None
   try:
    result=retry(fetch_result,retries=int(CUSTOM_RESOURCES_RESULT_POLL_TIMEOUT/2),sleep=2)
    result=json.loads(to_str(result))
   except Exception:
    bucket_objects=map_all_s3_objects(buckets=[CUSTOM_RESOURCES_RESULTS_BUCKET])
    LOG.info("Unable to fetch CF custom resource result from s3://%s/%s . Existing keys: %s"%(CUSTOM_RESOURCES_RESULTS_BUCKET,result_key,list(bucket_objects.keys())))
    raise
   region=aws_stack.get_region()
   status=CUSTOM_RESOURCE_STATUSES[region]=CUSTOM_RESOURCE_STATUSES.get(region,{})
   status_stack=status[stack_name]=status.get(stack_name)or{}
   result_data=result.get("Data")or{}
   status_stack[resource_id]={"result":result,**result_data}
   return result
  return{"create":{"function":create_custom_resource}}
# Created by pyminifier (https://github.com/liftoff/pyminifier)
