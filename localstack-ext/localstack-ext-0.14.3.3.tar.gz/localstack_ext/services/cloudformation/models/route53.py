_A='Name'
from localstack.services.cloudformation.service_models import REF_ID_ATTRS,GenericBaseModel
from localstack.utils.aws import aws_stack
from localstack.utils.common import select_attributes,short_uid
def canonicalize_name(name):
	A=name
	if A[-1]!='.':return f"{A}."
	return A
class Route53HostedZone(GenericBaseModel):
	@staticmethod
	def cloudformation_type():return'AWS::Route53::HostedZone'
	def fetch_state(B,stack_name,resources):C=aws_stack.connect_to_service('route53');A=C.list_hosted_zones()['HostedZones'];D=canonicalize_name(B.props.get(_A));A=[B for B in A if B[_A]==D];return(A or[None])[0]
	def get_physical_resource_id(A,attribute=None,**B):return A.props.get('Id')
	def get_cfn_attribute(A,attribute_name):
		B=attribute_name
		if B=='NameServers':return[A.props.get(_A)]
		if B in REF_ID_ATTRS:return A.get_physical_resource_id()
		return super(Route53HostedZone,A).get_cfn_attribute(B)
	@staticmethod
	def get_deploy_templates():
		B='parameters';A='function'
		def C(resource_props,resources,resource_id,*E,**F):D=Route53HostedZone(resources[resource_id]);B=D.props;A=select_attributes(B,['HostedZoneConfig',_A]);C=B.get('VPCs',[]);A['VPC']=C and C[0]or{};A['CallerReference']=short_uid();return A
		def D(resource_props,resources,resource_id,*B,**C):A=Route53HostedZone(resources[resource_id]);return A.props.get('Id')
		return{'create':{A:'create_hosted_zone',B:C},'delete':{A:'delete_hosted_zone',B:{'Id':D}}}