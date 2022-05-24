_A='RestApiId'
from localstack.services.cloudformation.deployment_utils import lambda_keys_to_lower
from localstack.services.cloudformation.service_models import GenericBaseModel
from localstack.utils.aws import aws_stack
class ApiGatewayAuthorizer(GenericBaseModel):
	@staticmethod
	def cloudformation_type():return'AWS::ApiGateway::Authorizer'
	def fetch_state(A,stack_name,resources):D=resources;C=stack_name;B=A.props;E=aws_stack.connect_to_service('apigateway');F=A.resolve_refs_recursively(C,B[_A],D);G=A.resolve_refs_recursively(C,B.get('AuthorizerUri'),D);H=E.get_authorizers(restApiId=F,limit=200)['items'];I=[A for A in H if A['type']==B.get('Type')and A.get('authorizerUri')==G];return(I or[None])[0]
	def get_physical_resource_id(A,attribute=None,**B):return A.props.get('id')
	@classmethod
	def get_deploy_templates(C):
		B='parameters';A='function'
		def D(params,resource_id,resources,**B):A=C(resources[resource_id]);return{'restApiId':A.props[_A],'authorizerId':A.props.get('id')}
		return{'create':{A:'create_authorizer',B:lambda_keys_to_lower()},'delete':{A:'delete_authorizer',B:D}}