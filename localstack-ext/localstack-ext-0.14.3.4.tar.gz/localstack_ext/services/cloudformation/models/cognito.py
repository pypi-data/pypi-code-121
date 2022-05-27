_O='_deployed'
_N='cognito-identity'
_M='PoolName'
_L='ClientName'
_K='IdentityPoolId'
_J='delete'
_I='Domain'
_H='GroupName'
_G='cognito-idp'
_F='parameters'
_E='create'
_D='ProviderName'
_C=None
_B='UserPoolId'
_A='function'
from localstack.constants import TEST_AWS_ACCOUNT_ID,TRUE_STRINGS
from localstack.services.cloudformation.deployment_utils import PLACEHOLDER_RESOURCE_NAME
from localstack.services.cloudformation.service_models import REF_ATTRS,REF_ID_ATTRS,GenericBaseModel
from localstack.utils.aws import aws_stack
from localstack_ext.services.cognito.cognito_utils import get_issuer_url
from localstack_ext.utils.aws import aws_utils
class CognitoUserPool(GenericBaseModel):
	@staticmethod
	def cloudformation_type():return'AWS::Cognito::UserPool'
	def get_cfn_attribute(B,attribute_name):
		A=attribute_name
		if A in REF_ATTRS:return B.get_physical_resource_id(A)
		C=B._get_id()
		if A=='Arn':return aws_utils.cognito_userpool_arn(C)
		if A==_D:return 'cognito-idp.{r}.amazonaws.com/{r}_{a}'.format(r=aws_stack.get_region(),a=TEST_AWS_ACCOUNT_ID)
		if A=='ProviderURL':return get_issuer_url(pool_id=C)
		return super(CognitoUserPool,B).get_cfn_attribute(A)
	def get_physical_resource_id(B,attribute,**C):
		A=B._get_id()
		if not A:return A
		if attribute in REF_ATTRS:return A
		return aws_utils.cognito_userpool_arn(A)
	def get_resource_name(A):return A.props.get(_M)
	def _get_id(B):A=B.props;return A.get(_B)or A.get('Id')
	@classmethod
	def fetch_details(C,pool_name):A=aws_stack.connect_to_service(_G);B=A.list_user_pools(MaxResults=100)['UserPools'];return([A for A in B if A['Name']==pool_name]or[_C])[0]
	@staticmethod
	def get_deploy_templates():
		def A(params,**Q):
			K='MaxLength';J='MinLength';I='Schema';H='Policies';F='MinimumLength';D='AutoVerifiedAttributes';L=[H,'LambdaConfig',D,'AliasAttributes','UsernameAttributes','VerificationMessageTemplate','EmailVerificationMessage','EmailVerificationSubject','SmsVerificationMessage','SmsAuthenticationMessage','DeviceConfiguration','EmailConfiguration','SmsConfiguration','UserPoolTags','AdminCreateUserConfig',I,'UserPoolAddOns'];G={A:A for A in L};G[_M]='UserPoolName';A={A:params.get(B)for(A,B)in G.items()};M=A.get(H)or{};B=M.get('PasswordPolicy')or{}
			if B.get(F):B[F]=int(B[F])
			N=['RequireLowercase','RequireNumbers','RequireSymbols','RequireUppercase'];O=list(TRUE_STRINGS)+[True]
			for E in N:
				if E in B:B[E]=B[E]in O
			if isinstance(A.get(D),str):A[D]=[A[D]]
			for P in A.get(I)or[]:
				C=P.get('StringAttributeConstraints')
				if C:C[J]=str(C.get(J,1));C[K]=str(C.get(K,50))
			return A
		return{_E:{_A:'create_user_pool',_F:A}}
class UserPoolGroup(GenericBaseModel):
	@staticmethod
	def cloudformation_type():return'AWS::Cognito::UserPoolGroup'
	def get_physical_resource_id(A,attribute,**B):return A.props.get(_H)
	def fetch_state(A,stack_name,resources):C=resources;B=stack_name;E=aws_stack.connect_to_service(_G);D=A.props;F=A.resolve_refs_recursively(B,D.get(_H),C);G=A.resolve_refs_recursively(B,D.get(_B),C);H=E.list_groups(UserPoolId=G)['Groups'];I=[A for A in H if A[_H]==F];return(I or[_C])[0]
	@staticmethod
	def get_deploy_templates():return{_E:{_A:'create_group'},_J:{_A:'delete_group',_F:[_H,_B]}}
class IdentityPool(GenericBaseModel):
	@staticmethod
	def cloudformation_type():return'AWS::Cognito::IdentityPool'
	def get_cfn_attribute(B,attribute_name):
		A=attribute_name
		try:return super(IdentityPool,B).get_cfn_attribute(A)
		except Exception:
			if A in REF_ID_ATTRS:return B.get_physical_resource_id(A)
			if A==_D:return 'cognito.{r}.amazonaws.com/{r}_{a}'.format(r=aws_stack.get_region(),a=TEST_AWS_ACCOUNT_ID)
			raise
	def get_physical_resource_id(A,attribute,**B):
		if attribute in REF_ID_ATTRS:return A.props.get(_K)
	@classmethod
	def fetch_details(D,pool_name):A=aws_stack.connect_to_service(_N);B=A.list_identity_pools(MaxResults=100)['IdentityPools'];C=[A for A in B if A['IdentityPoolName']==pool_name];return(C or[_C])[0]
	@staticmethod
	def get_deploy_templates():return{_E:{_A:'create_identity_pool'}}
class CognitoUserPoolClient(GenericBaseModel):
	@staticmethod
	def cloudformation_type():return'AWS::Cognito::UserPoolClient'
	def get_cfn_attribute(B,attribute_name):
		A=attribute_name
		if A in REF_ID_ATTRS:return B.get_physical_resource_id(A)
		return super(CognitoUserPoolClient,B).get_cfn_attribute(A)
	def get_physical_resource_id(A,attribute,**B):
		if attribute in REF_ID_ATTRS:return A.props.get('ClientId')
	@classmethod
	def fetch_details(C,pool_id,client_name):A=aws_stack.connect_to_service(_G);B=A.list_user_pool_clients(UserPoolId=pool_id)['UserPoolClients'];return([A for A in B if A[_L]==client_name]or[_C])[0]
	@staticmethod
	def get_deploy_templates():
		def A(params,**C):
			B='RefreshTokenValidity';A=params
			if not A.get(_L):A[_L]=PLACEHOLDER_RESOURCE_NAME
			if A.get(B)is not _C:A[B]=int(A[B])
			return A
		return{_E:{_A:'create_user_pool_client',_F:A}}
class CognitoUserPoolDomain(GenericBaseModel):
	@staticmethod
	def cloudformation_type():return'AWS::Cognito::UserPoolDomain'
	def get_physical_resource_id(A,attribute,**B):
		if attribute in REF_ID_ATTRS:return A.props.get(_I)
	def fetch_state(A,stack_name,resources):B=aws_stack.connect_to_service(_G);C=A.resolve_refs_recursively(stack_name,A.props.get(_I),resources);D=B.describe_user_pool_domain(Domain=C)['DomainDescription'];return D or _C
	@staticmethod
	def get_deploy_templates():return{_E:{_A:'create_user_pool_domain'},_J:{_A:'delete_user_pool_domain',_F:{_B:_B,_I:_I}}}
class CognitoIdentityPoolRoleAttachment(GenericBaseModel):
	@staticmethod
	def cloudformation_type():return'AWS::Cognito::IdentityPoolRoleAttachment'
	def fetch_state(B,stack_name,resources):
		C=aws_stack.connect_to_service(_N);D=B.resolve_refs_recursively(stack_name,B.props.get(_K),resources);A=C.get_identity_pool_roles(IdentityPoolId=D)
		if A:A[_O]=True
		return A or _C
	def get_physical_resource_id(B,attribute,**C):A=B.props;return A.get(_O)and'cognito-pool-roles-%s'%A.get(_K)
	@staticmethod
	def get_deploy_templates():
		def A(params,*H,**I):
			F='IdentityProvider';E='RoleMappings';B=params;D=B.get(E)
			if D:
				C={}
				for (G,A) in D.items():
					if A.get(F):C[A.pop(F)]=A
					else:C[G]=A
				B[E]=C
			return B
		return{_E:{_A:'set_identity_pool_roles',_F:A}}
class CognitoUserPoolIdentityProvider(GenericBaseModel):
	@staticmethod
	def cloudformation_type():return'AWS::Cognito::UserPoolIdentityProvider'
	def get_physical_resource_id(A,attribute,**B):return A.props.get(_D)
	def fetch_state(A,stack_name,resources):C=resources;B=stack_name;E=aws_stack.connect_to_service(_G);D=A.props;F=A.resolve_refs_recursively(B,D.get(_B),C);G=A.resolve_refs_recursively(B,D.get(_D),C);H=E.list_identity_providers(UserPoolId=F)['Providers'];I=[A for A in H if A[_D]==G];return(I or[_C])[0]
	@staticmethod
	def get_deploy_templates():return{_E:{_A:'create_identity_provider'},_J:{_A:'delete_identity_provider',_F:{_B:_B,_D:_D}}}