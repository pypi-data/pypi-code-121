_N='datastoreName'
_M='datasetName'
_L='DatastoreName'
_K='pipelineName'
_J='DatasetName'
_I='channelName'
_H='PipelineName'
_G='delete'
_F='create'
_E=None
_D='iotanalytics'
_C='ChannelName'
_B='parameters'
_A='function'
from localstack.services.cloudformation.deployment_utils import lambda_keys_to_lower
from localstack.services.cloudformation.service_models import GenericBaseModel
from localstack.utils.aws import aws_stack
from localstack_ext.services.cloudformation.service_models import lambda_rename_attributes
class IoTAnalyticsChannel(GenericBaseModel):
	@staticmethod
	def cloudformation_type():return'AWS::IoTAnalytics::Channel'
	def fetch_state(A,stack_name,resources):B=A.resolve_refs_recursively(stack_name,A.props.get(_C),resources);C=aws_stack.connect_to_service(_D);D=C.list_channels(maxResults=500)['channelSummaries'];E=[A for A in D if A.get(_I)==B];return(E or[_E])[0]
	def get_physical_resource_id(A,attribute,**B):return A.props.get(_C)
	@classmethod
	def get_deploy_templates(A):return{_F:{_A:'create_channel',_B:{_I:_C,'channelStorage':'ChannelStorage','retentionPeriod':'RetentionPeriod','tags':lambda_keys_to_lower('Tags')}},_G:{_A:'delete_channel',_B:{_I:_C}}}
class IoTAnalyticsDataset(GenericBaseModel):
	@staticmethod
	def cloudformation_type():return'AWS::IoTAnalytics::Dataset'
	def fetch_state(A,stack_name,resources):B=A.resolve_refs_recursively(stack_name,A.props.get(_J),resources);C=aws_stack.connect_to_service(_D);D=C.list_datasets(maxResults=500)['datasetSummaries'];E=[A for A in D if A.get(_M)==B];return(E or[_E])[0]
	def get_physical_resource_id(A,attribute,**B):return A.props.get(_J)
	@classmethod
	def get_deploy_templates(A):return{_F:{_A:'create_dataset',_B:lambda_rename_attributes({'scheduleExpression':'expression'},func=lambda_keys_to_lower())},_G:{_A:'delete_dataset',_B:{_M:_J}}}
class IoTAnalyticsPipeline(GenericBaseModel):
	@staticmethod
	def cloudformation_type():return'AWS::IoTAnalytics::Pipeline'
	def fetch_state(A,stack_name,resources):B=A.resolve_refs_recursively(stack_name,A.props.get(_H),resources);C=aws_stack.connect_to_service(_D);D=C.list_pipelines(maxResults=500)['pipelineSummaries'];E=[A for A in D if A.get(_K)==B];return(E or[_E])[0]
	def get_physical_resource_id(A,attribute,**B):return A.props.get(_H)
	@classmethod
	def get_deploy_templates(A):return{_F:{_A:'create_pipeline',_B:{_K:_H,'pipelineActivities':lambda_keys_to_lower('PipelineActivities'),'tags':lambda_keys_to_lower('Tags')}},_G:{_A:'delete_pipeline',_B:{_K:_H}}}
class IoTAnalyticsDatastore(GenericBaseModel):
	@staticmethod
	def cloudformation_type():return'AWS::IoTAnalytics::Datastore'
	def fetch_state(A,stack_name,resources):B=A.resolve_refs_recursively(stack_name,A.props.get(_L),resources);C=aws_stack.connect_to_service(_D);D=C.list_datastores(maxResults=500)['datastoreSummaries'];E=[A for A in D if A.get(_N)==B];return(E or[_E])[0]
	def get_physical_resource_id(A,attribute,**B):return A.props.get(_L)
	@classmethod
	def get_deploy_templates(A):return{_F:{_A:'create_datastore',_B:lambda_keys_to_lower()},_G:{_A:'delete_datastore',_B:{_N:_L}}}