_G='appArn'
_F='parameters'
_E='function'
_D='create'
_C='BranchName'
_B='amplify'
_A='tags'
from localstack.services.cloudformation.deployment_utils import lambda_keys_to_lower,params_list_to_dict
from localstack.services.cloudformation.service_models import REF_ID_ATTRS,GenericBaseModel
from localstack.utils.aws import aws_stack
from localstack_ext.utils.aws import aws_utils
class AmplifyBranch(GenericBaseModel):
	@staticmethod
	def cloudformation_type():return'AWS::Amplify::Branch'
	def fetch_state(A,stack_name,resources):C=resources;B=stack_name;E=aws_stack.connect_to_service(_B);D=A.props;F=A.resolve_refs_recursively(B,D['AppId'],C);G=A.resolve_refs_recursively(B,D[_C],C);H=E.list_branches(appId=F)['branches'];I=[A for A in H if A['branchName']==G];return(I or[None])[0]
	def get_physical_resource_id(A,attribute,**B):return A.props.get(_C)
	@staticmethod
	def get_deploy_templates():
		def A(params,**C):
			A=params;A=lambda_keys_to_lower()(A,**C);B=A.pop('basicAuthConfig',{})
			if B:A['enableBasicAuth']=B['EnableBasicAuth'];A['basicAuthCredentials']='%s:%s'%(B['Username'],B['Password'])
			A[_A]=params_list_to_dict(_A,key_attr_name='key',value_attr_name='value')(A,**C);return A
		return{_D:{_E:'create_branch',_F:A}}
class AmplifyApp(GenericBaseModel):
	@staticmethod
	def cloudformation_type():return'AWS::Amplify::App'
	def get_cfn_attribute(B,attribute_name):
		A=attribute_name
		if A=='DefaultDomain':return'default.example.com'
		if A in REF_ID_ATTRS:return B.get_physical_resource_id(A)
		if A in['Arn']:return B.props.get(_G)
		return super(AmplifyApp,B).get_cfn_attribute(A)
	def get_physical_resource_id(C,attribute,**D):
		B=C.props;A=B.get('appId')
		if not A:return
		if attribute in REF_ID_ATTRS:return A
		return B.get(_G)or aws_utils.amplify_app_arn(A)
	@classmethod
	def fetch_details(C,app_name):B=aws_stack.connect_to_service(_B);A=B.list_apps()['apps'];A=[B for B in A if B['name']==app_name];return(A or[None])[0]
	def fetch_state(A,stack_name,resources):B=A.resolve_refs_recursively(stack_name,A.props['Name'],resources);return A.fetch_details(B)
	@staticmethod
	def get_deploy_templates():
		def A(params,**B):
			C='IAMServiceRole';A=params
			if C in A:A['iamServiceRoleArn']=A.pop(C)
			A=lambda_keys_to_lower()(A,**B);A[_A]=params_list_to_dict(_A,key_attr_name='key',value_attr_name='value')(A,**B);return A
		return{_D:{_E:'create_app',_F:A}}