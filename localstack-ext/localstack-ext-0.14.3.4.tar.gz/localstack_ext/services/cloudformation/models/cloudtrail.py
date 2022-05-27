_C='Name'
_B='cloudtrail'
_A='TrailName'
from localstack.services.cloudformation.service_models import REF_ID_ATTRS,GenericBaseModel
from localstack.utils.aws import aws_stack
class CloudTrail(GenericBaseModel):
	@staticmethod
	def cloudformation_type():return'AWS::CloudTrail::Trail'
	def fetch_state(B,stack_name,resources):C=aws_stack.connect_to_service(_B);A=[A for A in C.list_trails()['Trails']if A[_C]==B.props[_A]];return(A or[None])[0]
	def get_physical_resource_id(A,attribute,**B):
		if attribute in REF_ID_ATTRS:return A.props[_A]
	@staticmethod
	def get_deploy_templates():
		K='SnsTopicName';J='S3KeyPrefix';I='S3BucketName';H='IsMultiRegionTrail';G='IncludeGlobalServiceEvents';F='EnableLogFileValidation';E='CloudWatchLogsRoleArn';D='CloudWatchLogsLogGroupArn';C='parameters';B='Properties';A='function'
		def L(resource_id,resources,*F,**G):
			D=resources[resource_id];A=D.get(B,{});C=A.get('EventSelectors',[])
			if C:E=aws_stack.connect_to_service(_B);E.put_event_selectors(TrailName=A[_A],EventSelectors=C)
			return{}
		def M(resource_id,resources,*E,**F):
			C=resources[resource_id];A=C.get(B,{})
			if A.get('IsLogging'):D=aws_stack.connect_to_service(_B);D.start_logging(Name=A[_A])
			return{}
		return{'create':[{A:'create_trail',C:{D:D,E:E,F:F,G:G,H:H,'KmsKeyId':'KMSKeyId',_C:_A,I:I,J:J,K:K,'TagsList':'Tags'}},{A:L},{A:M}],'delete':{A:'delete_trail',C:{_C:_A}}}