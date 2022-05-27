_A='ClusterArn'
from localstack.services.cloudformation.service_models import GenericBaseModel
from localstack.utils.aws import aws_stack
from localstack.utils.common import clone
class KafkaCluster(GenericBaseModel):
	@staticmethod
	def cloudformation_type():return'AWS::MSK::Cluster'
	def get_physical_resource_id(A,attribute=None,**B):return A.props.get(_A)
	def fetch_state(B,stack_name,resources):C='ClusterName';D=aws_stack.connect_to_service('kafka');E=B.resolve_refs_recursively(stack_name,B.props[C],resources);A=D.list_clusters()['ClusterInfoList'];A=[B for B in A if B[C]==E];return(A or[None])[0]
	@classmethod
	def get_deploy_templates(B):
		C='parameters';A='function'
		def D(params,resource_id,resources,**F):
			D='EBSStorageInfo';E=B(resources[resource_id]);C=clone(E.props);A=C.get('BrokerNodeGroupInfo',{}).get('StorageInfo',{})
			if D in A:A['EbsStorageInfo']=A.pop(D)
			return C
		def E(params,resource_id,resources,**C):A=B(resources[resource_id]);return{_A:A.props.get(_A)}
		return{'create':{A:'create_cluster',C:D},'delete':{A:'delete_cluster',C:E}}