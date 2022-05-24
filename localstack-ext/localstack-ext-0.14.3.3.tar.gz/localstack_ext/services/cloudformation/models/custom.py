_B='result'
_A='AWS::CDK::Metadata'
import json
from localstack import config
from localstack.services.awslambda import lambda_executors
from localstack.services.cloudformation.service_models import GenericBaseModel
from localstack.utils.aws import aws_stack
from localstack.utils.common import recurse_object,retry,short_uid,to_str
from localstack.utils.testutil import map_all_s3_objects
from localstack_ext.services.cloudformation.service_models import CUSTOM_RESOURCE_STATUSES,CUSTOM_RESOURCES_RESULT_POLL_TIMEOUT,CUSTOM_RESOURCES_RESULTS_BUCKET,LOG
from localstack_ext.utils.aws import aws_utils
class CDKMetadata(GenericBaseModel):
	@staticmethod
	def cloudformation_type():return _A
	def fetch_state(A,stack_name,resources):return{'type':_A}
class CustomResource(GenericBaseModel):
	@staticmethod
	def cloudformation_type():return'AWS::CloudFormation::CustomResource'
	def fetch_state(A,stack_name,resources):B=A.logical_resource_id;C=CUSTOM_RESOURCE_STATUSES.get(aws_stack.get_region(),{}).get(stack_name,{}).get(B);return C
	def get_physical_resource_id(A,attribute,**B):return A.state[_B]['PhysicalResourceId']
	@staticmethod
	def get_deploy_templates():
		def A(resource_id,resources,resource_type,func,stack_name,*W):
			D=stack_name;C=resource_id;E=resources[C];F=E['Properties'];B=F.get('ServiceToken')
			if not B:LOG.warning('Missing ServiceToken attribute in custom resource: %s'%E);return
			def J(obj,**D):
				A=obj
				if isinstance(A,dict):
					for (C,B) in A.items():
						if isinstance(B,bool):A[C]=str(B).lower()
				return A
			recurse_object(F,J);aws_stack.get_or_create_bucket(CUSTOM_RESOURCES_RESULTS_BUCKET);G=short_uid();K=lambda_executors.get_main_endpoint_from_container();L='http://%s:%s'%(K,config.get_edge_port_http());M=aws_stack.generate_presigned_url('put_object',Params={'Bucket':CUSTOM_RESOURCES_RESULTS_BUCKET,'Key':G},endpoint_url=L);N=aws_stack.cloudformation_stack_arn(D);O={'RequestType':'Create','ResponseURL':M,'StackId':N,'RequestId':short_uid(),'ResourceType':E.get('Type'),'LogicalResourceId':C,'ResourceProperties':F}
			if str(B).startswith('arn:aws:lambda'):P=B.split(':')[3];Q=aws_stack.lambda_function_name(B);R=aws_stack.connect_to_service('lambda',region_name=P);R.invoke(FunctionName=Q,Payload=json.dumps(O))
			else:LOG.warning('Unsupported ServiceToken attribute in custom resource: %s'%B);return
			def S():return aws_utils.download_s3_object(CUSTOM_RESOURCES_RESULTS_BUCKET,G)
			A=None
			try:A=retry(S,retries=int(CUSTOM_RESOURCES_RESULT_POLL_TIMEOUT/2),sleep=2);A=json.loads(to_str(A))
			except Exception:T=map_all_s3_objects(buckets=[CUSTOM_RESOURCES_RESULTS_BUCKET]);LOG.info('Unable to fetch CF custom resource result from s3://%s/%s . Existing keys: %s'%(CUSTOM_RESOURCES_RESULTS_BUCKET,G,list(T.keys())));raise
			H=aws_stack.get_region();I=CUSTOM_RESOURCE_STATUSES[H]=CUSTOM_RESOURCE_STATUSES.get(H,{});U=I[D]=I.get(D)or{};V=A.get('Data')or{};U[C]={_B:A,**V};return A
		return{'create':{'function':A}}