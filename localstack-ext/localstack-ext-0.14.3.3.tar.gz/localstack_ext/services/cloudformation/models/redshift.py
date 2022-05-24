_J='create_cluster_security_group'
_I='delete'
_H='create'
_G='redshift'
_F='SubnetIds'
_E='Tags'
_D='ParameterGroupName'
_C='Description'
_B='parameters'
_A='function'
from localstack.services.cloudformation.service_models import GenericBaseModel
from localstack.utils.aws import aws_stack
from localstack.utils.common import short_uid
class RedshiftClusterParameterGroup(GenericBaseModel):
	@staticmethod
	def cloudformation_type():return'AWS::Redshift::ClusterParameterGroup'
	def get_physical_resource_id(A,attribute,**B):return A._get_name()
	def fetch_state(B,stack_name,resources):C=aws_stack.connect_to_service(_G);D=B.resolve_refs_recursively(stack_name,B._get_name(),resources);A=C.describe_cluster_parameter_groups(ParameterGroupName=D);A=A.get('ParameterGroups');return(A or[None])[0]
	def _get_name(B):A=B.properties;C=A[_D]=A.get(_D)or'cf-pg-%s'%short_uid();return C
	@staticmethod
	def get_deploy_templates():
		C='Parameters';B='ParameterGroupFamily'
		def A(resource_props,resources,resource_id,*B,**C):A=RedshiftClusterParameterGroup(resources[resource_id]);return A._get_name()
		return{_H:[{_A:_J,_B:{_D:A,B:B,_C:_C,_E:_E}},{_A:'modify_cluster_parameter_group',_B:{_D:A,C:C}}],_I:{_A:'delete_cluster_parameter_group',_B:{_D:A}}}
class RedshiftClusterSecurityGroup(GenericBaseModel):
	@staticmethod
	def cloudformation_type():return'AWS::Redshift::ClusterSecurityGroup'
	def get_physical_resource_id(A,attribute,**B):return A._get_name()
	def fetch_state(B,stack_name,resources):C=aws_stack.connect_to_service(_G);D=B.resolve_refs_recursively(stack_name,B._get_name(),resources);A=C.describe_cluster_security_groups(ClusterSecurityGroupName=D);A=A.get('ClusterSecurityGroups');return(A or[None])[0]
	def _get_name(C):B='SecurityGroupName';A=C.properties;D=A[B]=A.get(B)or'cf-sg-%s'%short_uid();return D
	@staticmethod
	def get_deploy_templates():
		B='ClusterSecurityGroupName'
		def A(resource_props,resources,resource_id,*B,**C):A=RedshiftClusterSecurityGroup(resources[resource_id]);return A._get_name()
		return{_H:{_A:_J,_B:{B:A,_C:_C}},_I:{_A:'delete_cluster_security_group',_B:{B:A}}}
class RedshiftClusterSubnetGroup(GenericBaseModel):
	@staticmethod
	def cloudformation_type():return'AWS::Redshift::ClusterSubnetGroup'
	def get_physical_resource_id(A,attribute,**B):return A._get_name()
	def fetch_state(A,stack_name,resources):B=aws_stack.connect_to_service(_G);C=A.resolve_refs_recursively(stack_name,A._get_name(),resources);D=B.describe_cluster_subnet_groups(ClusterSubnetGroupName=C)['ClusterSubnetGroups'];return(D or[None])[0]
	def _get_name(A):return '-'.join(A.props[_F])
	@staticmethod
	def get_deploy_templates():
		B='ClusterSubnetGroupName'
		def A(resource_props,*A,**B):return '-'.join(resource_props[_F])
		return{_H:{_A:'create_cluster_subnet_group',_B:{B:A,_C:_C,_F:_F,_E:_E}},_I:{_A:'delete_cluster_subnet_group',_B:{B:A}}}