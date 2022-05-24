_I='FunctionName'
_H='parameters'
_G='lambda'
_F='LayerName'
_E='FunctionVersion'
_D='function'
_C='create'
_B='LayerVersionArn'
_A=None
from localstack.services.cloudformation.models import awslambda
from localstack.services.cloudformation.service_models import GenericBaseModel
from localstack.utils.aws import aws_stack
from localstack.utils.common import select_attributes,short_uid
class LambdaLayerVersion(GenericBaseModel):
	@staticmethod
	def cloudformation_type():return'AWS::Lambda::LayerVersion'
	def get_physical_resource_id(A,attribute=_A,**B):return A.state.get(_B)
	def fetch_state(A,stack_name,resources):C=A.resolve_refs_recursively(stack_name,A.props.get(_F),resources);D=aws_stack.connect_to_service(_G);B=D.list_layer_versions(LayerName=C).get('LayerVersions',[]);return B[-1]if B else _A
	@staticmethod
	def get_deploy_templates():return{_C:{_D:'publish_layer_version'}}
class LambdaLayerVersionPermission(awslambda.LambdaPermission):
	@staticmethod
	def cloudformation_type():return'AWS::Lambda::LayerVersionPermission'
	def fetch_state(A,stack_name,resources):B=A.props;B[_B]=A.resolve_refs_recursively(stack_name,B[_B],resources);C,D=A.layer_name_and_version(B);E=aws_stack.lambda_layer_arn(C);F='%s:%s'%(E,D);G=A.do_fetch_state(C,F);return G
	@staticmethod
	def layer_name_and_version(params):A=params.get(_B,'');B=A.split(':');C=B[6]if':'in A else A;D=int(B[7]if len(B)>7 else 1);return C,D
	@classmethod
	def get_deploy_templates(C):
		def A(params,**F):B=params;D,E=C.layer_name_and_version(B);A=select_attributes(B,['Action','Principal']);A['StatementId']=short_uid();A[_F]=D;A['VersionNumber']=E;return A
		return{_C:{_D:'add_layer_version_permission',_H:A}}
class LambdaAlias(awslambda.LambdaPermission):
	@staticmethod
	def cloudformation_type():return'AWS::Lambda::Alias'
	def fetch_state(A,stack_name,resources):C=resources;B=stack_name;E=aws_stack.connect_to_service(_G);D=A.props;F=A.resolve_refs_recursively(B,D.get(_I),C);G=A.resolve_refs_recursively(B,D.get(_E),C);H=E.list_aliases(FunctionName=F)['Aliases'];I=[A for A in H if G in(_A,A.get(_E))];return(I or[_A])[0]
	def get_physical_resource_id(A,attribute,**C):B=A.props.get('AliasArn');return B
	@classmethod
	def get_deploy_templates(A):return{_C:{_D:'create_alias',_H:['Description',_I,_E,'Name']}}