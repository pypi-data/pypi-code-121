_S='RouteResponseId'
_R='VpcLinkId'
_Q='DeploymentId'
_P='IntegrationId'
_O='RouteKey'
_N='Body'
_M='RouteId'
_L='Description'
_K='DomainName'
_J='StageName'
_I='delete'
_H='Name'
_G='parameters'
_F='Items'
_E='create'
_D='apigatewayv2'
_C='ApiId'
_B=None
_A='function'
import json
from localstack.services.cloudformation.service_models import REF_ID_ATTRS,GenericBaseModel
from localstack.utils.aws import aws_stack
from localstack.utils.common import select_attributes,short_uid
class ApiGatewayV2VpcLink(GenericBaseModel):
	@staticmethod
	def cloudformation_type():return'AWS::ApiGatewayV2::VpcLink'
	def fetch_state(A,stack_name,resources):B=aws_stack.connect_to_service(_D);C=B.get_vpc_links()[_F];D=A.resolve_refs_recursively(stack_name,A.props[_H],resources);E=[A for A in C if A[_H]==D];return(E or[_B])[0]
	def get_physical_resource_id(A,attribute,**B):return A.props.get(_R)
	@staticmethod
	def get_deploy_templates():return{_E:{_A:'create_vpc_link'},_I:{_A:'delete_vpc_link',_G:[_R]}}
class ApiGatewayV2DomainName(GenericBaseModel):
	@staticmethod
	def cloudformation_type():return'AWS::ApiGatewayV2::DomainName'
	def fetch_state(A,stack_name,resources):B=aws_stack.connect_to_service(_D);C=B.get_domain_names()[_F];D=A.resolve_refs_recursively(stack_name,A.props[_K],resources);E=([A for A in C if A[_K]==D]or[_B])[0];return E
	def get_physical_resource_id(A,attribute,**B):return A.props.get(_K)
	@staticmethod
	def get_deploy_templates():return{_E:{_A:'create_domain_name'},_I:{_A:'delete_domain_name',_G:[_K]}}
class ApiGatewayV2Authorizer(GenericBaseModel):
	@staticmethod
	def cloudformation_type():return'AWS::ApiGatewayV2::Authorizer'
	def fetch_state(A,stack_name,resources):C=resources;B=stack_name;E=aws_stack.connect_to_service(_D);D=A.props;F=A.resolve_refs_recursively(B,D[_C],C);G=A.resolve_refs_recursively(B,D[_H],C);H=E.get_authorizers(ApiId=F)[_F];I=([A for A in H if A[_H]==G]or[_B])[0];return I
	def get_physical_resource_id(A,attribute,**B):return A.props.get('AuthorizerId')
	@staticmethod
	def get_deploy_templates():return{_E:{_A:'create_authorizer'}}
class ApiGatewayV2Api(GenericBaseModel):
	@staticmethod
	def cloudformation_type():return'AWS::ApiGatewayV2::Api'
	def fetch_state(B,stack_name,resources):A=B.props;C=A[_N].get('info',{}).get('title')if A.get(_N)else A[_H];D=aws_stack.connect_to_service(_D);E=D.get_apis()[_F];F=([A for A in E if A[_H]==C]or[_B])[0];return F
	def get_physical_resource_id(A,attribute=_B,**B):
		if attribute in REF_ID_ATTRS:return A.props.get(_C)
	@staticmethod
	def get_deploy_templates():
		def A(resource_id,resources,*I):
			E='Basepath';F=resources[resource_id];B=F['Properties'];C=aws_stack.connect_to_service(_D);A=B.get(_N)
			if A:D=B.get(E);A.setdefault('info',{}).setdefault('title','api-%s'%short_uid());A=json.dumps(A);G={E:D}if D else{};return C.import_api(Body=A,**G)
			H=select_attributes(B,['ApiKeySelectionExpression','CorsConfiguration','CredentialsArn',_L,'DisableSchemaValidation',_H,'ProtocolType',_O,'RouteSelectionExpression','Tags','Target','Version']);return C.create_api(**H)
		return{_E:{_A:A}}
class ApiGatewayV2IntegrationResponse(GenericBaseModel):
	@staticmethod
	def cloudformation_type():return'AWS::ApiGatewayV2::IntegrationResponse'
	def fetch_state(A,stack_name,resources):E='IntegrationResponseKey';C=resources;B=stack_name;F=aws_stack.connect_to_service(_D);D=A.props;G=A.resolve_refs_recursively(B,D[_C],C);H=A.resolve_refs_recursively(B,D[_P],C);I=A.resolve_refs_recursively(B,D[E],C);J=F.get_integration_responses(ApiId=G,IntegrationId=H).get(_F,[]);K=[A for A in J if A[E]==I];return(K or[_B])[0]
	def get_physical_resource_id(A,attribute=_B,**B):return A.props.get('IntegrationResponseId')
	def get_cfn_attribute(B,attribute_name):
		A=attribute_name
		if A in REF_ID_ATTRS:return B.get_physical_resource_id(A)
		return super(ApiGatewayV2IntegrationResponse,B).get_cfn_attribute(A)
	@staticmethod
	def get_deploy_templates():return{_E:{_A:'create_integration_response'}}
class ApiGatewayV2Integration(GenericBaseModel):
	@staticmethod
	def cloudformation_type():return'AWS::ApiGatewayV2::Integration'
	def get_physical_resource_id(A,attribute,**B):
		if attribute in REF_ID_ATTRS:return A.props.get(_P)
	def fetch_state(A,stack_name,resources):G='IntegrationMethod';F='IntegrationUri';E='IntegrationType';C=resources;B=stack_name;H=aws_stack.connect_to_service(_D);D=A.props;I=A.resolve_refs_recursively(B,D.get(_C),C);J=A.resolve_refs_recursively(B,D.get(E),C);K=A.resolve_refs_recursively(B,D.get(F),C);L=A.resolve_refs_recursively(B,D.get(G),C);M=H.get_integrations(ApiId=I);N=[A for A in M.get(_F,[])if J==A.get(E)and K in[_B,A.get(F)]and L in[_B,A.get(G)]];return(N or[_B])[0]
	@staticmethod
	def get_deploy_templates():return{_E:{_A:'create_integration'},_I:{_A:'delete_integration',_G:[_C,_P]}}
class ApiGatewayV2Deployment(GenericBaseModel):
	@staticmethod
	def cloudformation_type():return'AWS::ApiGatewayV2::Deployment'
	def get_physical_resource_id(A,attribute,**B):
		if attribute in REF_ID_ATTRS:return A.props.get(_Q)
	def fetch_state(A,stack_name,resources):C=resources;B=stack_name;D=A.props;F=A.resolve_refs_recursively(B,D.get(_C),C);G=A.resolve_refs_recursively(B,D.get(_J),C);H=A.resolve_refs_recursively(B,D.get(_L),C);I=aws_stack.connect_to_service(_D);E=I.get_deployments(ApiId=F)[_F];E=[A for A in E if A.get(_J)==G or A.get(_L)==H];return(E or[_B])[0]
	@staticmethod
	def get_deploy_templates():return{_E:{_A:'create_deployment'},_I:{_A:'delete_deployment',_G:[_C,_Q]}}
class ApiGatewayV2Stage(GenericBaseModel):
	@staticmethod
	def cloudformation_type():return'AWS::ApiGatewayV2::Stage'
	def fetch_state(A,stack_name,resources):C=resources;B=stack_name;D=A.props;E=A.resolve_refs_recursively(B,D.get(_C),C);F=A.resolve_refs_recursively(B,D.get(_J),C);G=aws_stack.connect_to_service(_D);return G.get_stage(ApiId=E,StageName=F)or _B
	def get_physical_resource_id(A,attribute=_B,**B):
		if attribute in REF_ID_ATTRS:return A.props.get(_J)
	@staticmethod
	def get_deploy_templates():return{_E:{_A:'create_stage',_G:[_C,_Q,_J,_L]},_I:{_A:'delete_stage',_G:[_C,_J]}}
class ApiGatewayV2RouteResponse(GenericBaseModel):
	@staticmethod
	def cloudformation_type():return'AWS::ApiGatewayV2::RouteResponse'
	def fetch_state(A,stack_name,resources):E='RouteResponseKey';C=resources;B=stack_name;F=aws_stack.connect_to_service(_D);D=A.props;G=A.resolve_refs_recursively(B,D[_C],C);H=A.resolve_refs_recursively(B,D[_M],C);I=A.resolve_refs_recursively(B,D[E],C);J=F.get_route_responses(ApiId=G,RouteId=H).get(_F,[]);K=[A for A in J if A[E]==I];return(K or[_B])[0]
	def get_physical_resource_id(A,attribute,**B):return A.props.get(_S)
	@staticmethod
	def get_deploy_templates():return{_E:{_A:'create_route_response'},_I:{_A:'delete_route_response',_G:[_C,_M,_S]}}
class ApiGatewayV2Route(GenericBaseModel):
	@staticmethod
	def cloudformation_type():return'AWS::ApiGatewayV2::Route'
	def fetch_state(A,stack_name,resources):C=resources;B=stack_name;E=aws_stack.connect_to_service(_D);D=A.props;F=A.resolve_refs_recursively(B,D.get(_C),C);G=A.resolve_refs_recursively(B,D.get(_O),C);H=E.get_routes(ApiId=F).get(_F,[]);I=[A for A in H if A[_O]==G];return(I or[_B])[0]
	def get_physical_resource_id(A,attribute=_B,**B):return A.props.get(_M)
	@staticmethod
	def get_deploy_templates():return{_E:{_A:'create_route'},_I:{_A:'delete_route',_G:[_C,_M]}}