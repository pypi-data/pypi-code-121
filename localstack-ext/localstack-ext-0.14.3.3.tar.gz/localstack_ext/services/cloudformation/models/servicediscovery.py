_G='parameters'
_F='delete'
_E='create'
_D='servicediscovery'
_C='function'
_B='Name'
_A='Id'
from localstack.services.cloudformation.service_models import GenericBaseModel
from localstack.utils.aws import aws_stack
class ServiceDiscoveryNamespace(GenericBaseModel):
	def fetch_state(A,stack_name,resources):B=aws_stack.connect_to_service(_D);C=A.resolve_refs_recursively(stack_name,A.props[_B],resources);D=B.list_namespaces()['Namespaces'];E=[B for B in D if B['Type']==A._type()and B[_B]==C];return(E or[None])[0]
	def get_physical_resource_id(A,attribute,**B):return A.props.get(_A)
	@classmethod
	def get_deploy_templates(A):
		def B(resource_props,resources,resource_id,**C):B=A(resources[resource_id]);return{_A:B.props.get(_A)}
		C=A._create_function();return{_E:{_C:C},_F:{_C:'delete_namespace',_G:B}}
	def _type(A):raise
class ServiceDiscoveryService(ServiceDiscoveryNamespace):
	@staticmethod
	def cloudformation_type():return'AWS::ServiceDiscovery::Service'
	def fetch_state(A,stack_name,resources):B=aws_stack.connect_to_service(_D);C=A.resolve_refs_recursively(stack_name,A.props[_B],resources);D=B.list_services()['Services'];E=[A for A in D if A[_B]==C];return(E or[None])[0]
	def get_physical_resource_id(A,attribute,**C):
		B='Arn'
		if attribute==B:return A.props.get(B)
		return A.props.get(_A)
	@classmethod
	def get_deploy_templates(A):
		def B(resource_props,resources,resource_id,**C):B=A(resources[resource_id]);return{_A:B.props.get(_A)}
		return{_E:{_C:'create_service'},_F:{_C:'delete_service',_G:B}}
class ServiceDiscoveryHttpNamespace(ServiceDiscoveryNamespace):
	@staticmethod
	def cloudformation_type():return'AWS::ServiceDiscovery::HttpNamespace'
	@classmethod
	def _type(A):return'HTTP'
	@classmethod
	def _create_function(A):return'create_http_namespace'
class ServiceDiscoveryPublicDnsNamespace(ServiceDiscoveryNamespace):
	@staticmethod
	def cloudformation_type():return'AWS::ServiceDiscovery::PublicDnsNamespace'
	@classmethod
	def _type(A):return'DNS_PUBLIC'
	@classmethod
	def _create_function(A):return'create_public_dns_namespace'
class ServiceDiscoveryPrivateDnsNamespace(ServiceDiscoveryNamespace):
	@staticmethod
	def cloudformation_type():return'AWS::ServiceDiscovery::PrivateDnsNamespace'
	@classmethod
	def _type(A):return'DNS_PRIVATE'
	@classmethod
	def _create_function(A):return'create_private_dns_namespace'