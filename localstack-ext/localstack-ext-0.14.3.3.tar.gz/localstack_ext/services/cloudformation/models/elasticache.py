_N='CacheSecurityGroupName'
_M='ReplicationGroupId'
_L='CacheClusterId'
_K='ClusterName'
_J='Tags'
_I='Description'
_H='delete'
_G='create'
_F='elasticache'
_E=None
_D='CacheSubnetGroupName'
_C='CacheParameterGroupName'
_B='parameters'
_A='function'
from localstack.services.cloudformation.service_models import GenericBaseModel
from localstack.utils.aws import aws_stack
from localstack_ext.services.cloudformation.service_models import lambda_convert_types,lambda_rename_attributes
class ElastiCacheSubnetGroup(GenericBaseModel):
	@staticmethod
	def cloudformation_type():return'AWS::ElastiCache::SubnetGroup'
	def fetch_state(A,stack_name,resources):B=aws_stack.connect_to_service(_F);C=B.describe_cache_subnet_groups().get('CacheSubnetGroups',[]);D=A.resolve_refs_recursively(stack_name,A.props[_D],resources);E=[A for A in C if A[_D]==D];return(E or[_E])[0]
	def get_physical_resource_id(A,attribute,**B):return A.props.get(_D)
	@staticmethod
	def get_deploy_templates():A='SubnetIds';return{_G:{_A:'create_cache_subnet_group',_B:{_D:_D,'CacheSubnetGroupDescription':_I,A:A,_J:_J}},_H:{_A:'delete_cache_subnet_group',_B:[_D]}}
class ElastiCacheReplicationGroup(GenericBaseModel):
	@staticmethod
	def cloudformation_type():return'AWS::ElastiCache::ReplicationGroup'
	def fetch_state(A,stack_name,resources):B=aws_stack.connect_to_service(_F);C=B.describe_replication_groups().get('ReplicationGroups',[]);D=A.resolve_refs_recursively(stack_name,A.props['ReplicationGroupDescription'],resources);E=[A for A in C if A.get(_I)==D];return(E or[_E])[0]
	def get_physical_resource_id(A,attribute,**B):return A.props.get(_M)
	@staticmethod
	def get_deploy_templates():return{_G:{_A:'create_replication_group'},_H:{_A:'delete_replication_group',_B:[_M]}}
class ElastiCacheSecurityGroup(GenericBaseModel):
	@staticmethod
	def cloudformation_type():return'AWS::ElastiCache::SecurityGroup'
	def fetch_state(A,stack_name,resources):B=aws_stack.connect_to_service(_F);C=B.describe_cache_security_groups().get('CacheSecurityGroups',[]);D=A.resolve_refs_recursively(stack_name,A.props[_I],resources);E=[A for A in C if A[_I]==D];return(E or[_E])[0]
	def get_physical_resource_id(A,attribute,**B):return A.props.get(_N)
	@staticmethod
	def get_deploy_templates():return{_G:{_A:'create_cache_security_group'},_H:{_A:'delete_cache_security_group',_B:[_N]}}
class ElastiCacheParameterGroup(GenericBaseModel):
	@staticmethod
	def cloudformation_type():return'AWS::ElastiCache::ParameterGroup'
	def fetch_state(A,stack_name,resources):B=aws_stack.connect_to_service(_F);C=B.describe_cache_parameter_groups().get('CacheParameterGroups',[]);D=A.resolve_refs_recursively(stack_name,A.props[_C],resources);E=[A for A in C if A[_C]==D];return(E or[_E])[0]
	def get_physical_resource_id(A,attribute,**B):return A.props.get(_C)
	@staticmethod
	def get_deploy_templates():
		def A(params,**B):A=params.get('Properties')or{};return[{'ParameterName':B,'ParameterValue':C}for(B,C)in A.items()]
		return{_G:[{_A:'create_cache_parameter_group',_B:[_C,'CacheParameterGroupFamily',_I,_J]},{_A:'modify_cache_parameter_group',_B:{_C:_C,'ParameterNameValues':A}}],_H:{_A:'delete_cache_parameter_group',_B:[_C]}}
class ElastiCacheCluster(GenericBaseModel):
	@staticmethod
	def cloudformation_type():return'AWS::ElastiCache::CacheCluster'
	def get_cfn_attribute(A,attribute_name):
		G='ConfigurationEndpoint';B=attribute_name
		try:D=super(ElastiCacheCluster,A).get_cfn_attribute(B);assert D is not _E;return D
		except Exception:
			E=A.props
			if B in['Port','Address']:B='RedisEndpoint.%s'%B
			C=B.split('.');H=[G,'RedisEndpoint','Endpoint']
			if C[0]in H and len(C)>1:
				F=G
				if not E.get(F):A.state=A.fetch_details(E.get(_K))
				I=A.state.get(C[0])or A.state.get(F)or{};D=I.get(C[1])or E.get(C[1]);return str(D)
			return E.get(B)
	@classmethod
	def fetch_details(D,cluster_name):A=aws_stack.connect_to_service(_F);B=A.describe_cache_clusters(MaxRecords=500).get('CacheClusters',[]);C=[A for A in B if A.get(_L)==cluster_name];return(C or[_E])[0]
	@staticmethod
	def get_deploy_templates():return{_G:{_A:'create_cache_cluster',_B:lambda_convert_types(lambda_rename_attributes({_K:_L,'VpcSecurityGroupIds':'SecurityGroupIds'}),{'NumCacheNodes':int})},_H:{_A:'delete_cache_cluster',_B:{_L:_K}}}