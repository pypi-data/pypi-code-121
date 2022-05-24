_V='dataSourceArn'
_U='description'
_T='responseMappingTemplate'
_S='requestMappingTemplate'
_R='fieldName'
_Q='FieldName'
_P='TypeName'
_O='resolverArn'
_N='functionArn'
_M='dataSourceName'
_L='DataSourceName'
_K='create'
_J='Description'
_I='Expires'
_H='parameters'
_G='function'
_F='name'
_E='Name'
_D='appsync'
_C='apiId'
_B=None
_A='ApiId'
import json
from typing import Dict,Optional
from localstack.services.cloudformation.service_models import REF_ARN_ATTRS,REF_ID_ATTRS,GenericBaseModel
from localstack.utils.aws import aws_stack
from localstack.utils.common import clone,keys_to_lower,select_attributes,to_str
from localstack_ext.services.appsync import appsync_api
from localstack_ext.services.cloudformation.service_models import LOG
from localstack_ext.utils.aws import aws_utils
class AppSyncResolver(GenericBaseModel):
	@staticmethod
	def cloudformation_type():return'AWS::AppSync::Resolver'
	def get_physical_resource_id(A,attribute,**B):
		if attribute in REF_ID_ATTRS:return A.props.get(_O)
	def fetch_state(B,stack_name,resources):A=B.props;C=A.get(_A);D=A.get(_P);E=A.get(_Q);F=A.get(_L);return B.fetch_details(C,D,E,F)
	@classmethod
	def fetch_details(D,api_id,type_name,field_name,data_source_name):A=aws_stack.connect_to_service(_D);B=A.list_resolvers(apiId=api_id,typeName=type_name)['resolvers'];C=[A for A in B if A.get(_R)==field_name and A.get(_M)==data_source_name];return(C or[_B])[0]
	def update_resource(D,new_resource,stack_name,resources):
		E=aws_stack.connect_to_service(_D);A=new_resource['Properties'];B=D.fetch_state(stack_name,resources)
		if not B:return
		C=set(B.keys())|set(A.keys());C=[A for A in C if A not in[_C,_O]]
		if all((A.get(D)==B.get(D)for D in C)):return
		F=D._get_resolver_params(A);return E.update_resolver(**F)
	@classmethod
	def get_deploy_templates(A):return{_K:{_G:'create_resolver',_H:A._get_resolver_params},'delete':{_G:'delete_resolver',_H:{_C:_A,'typeName':_P,_R:_Q}}}
	@staticmethod
	def _get_resolver_params(props,**E):
		A=keys_to_lower(clone(props));C=A.pop('requestMappingTemplateS3Location',_B);D=A.pop('responseMappingTemplateS3Location',_B)
		if C:
			B=aws_utils.download_s3_object(C,as_str=True)
			if B:A[_S]=B
		if D:
			B=aws_utils.download_s3_object(D,as_str=True)
			if B:A[_T]=B
		return A
class GraphQLSchema(GenericBaseModel):
	@staticmethod
	def cloudformation_type():return'AWS::AppSync::GraphQLSchema'
	def get_physical_resource_id(A,attribute,**B):return'%s-GraphQLSchema'%A.props.get(_A)
	@classmethod
	def fetch_details(E,api_id,definition=_B,s3_location=_B):
		C='schema';B=definition;D=aws_stack.connect_to_service(_D)
		try:
			A=D.get_introspection_schema(apiId=api_id,format='SDL')[C];A=A.read()if hasattr(A,'read')else A;A=to_str(A)
			if A.startswith('{'):A=json.loads(A)[C]
			if B:
				if to_str(B).strip()==to_str(A).strip():return{C:B}
			elif s3_location:LOG.debug('Getting GraphQL schema definition from S3 not yet implemented');return{C:B}
		except Exception:pass
class AppSyncApiKey(GenericBaseModel):
	@staticmethod
	def cloudformation_type():return'AWS::AppSync::ApiKey'
	def get_cfn_attribute(A,attribute_name):
		B=attribute_name
		if B=='ApiKey':return A._get_key_id()
		if B in REF_ID_ATTRS+REF_ARN_ATTRS:return A.get_physical_resource_id()
		return super(AppSyncApiKey,A).get_cfn_attribute(B)
	def get_physical_resource_id(A,attribute=_B,**D):
		B=A.props;C=A._get_key_id()
		if not C or not B.get(_A):return
		return aws_utils.appsync_api_key_arn(B.get(_A),C)
	def _get_key_id(B):A=B.props;return A.get('ApiKeyId')or A.get('id')
	def fetch_state(C,stack_name,resources):D='expires';E=aws_stack.connect_to_service(_D);A=C.props;B=A.get(_A);B=C.resolve_refs_recursively(stack_name,B,resources);F=E.list_api_keys(apiId=B).get('apiKeys',[]);G=A.get(D)or A.get(_I);H=A.get(_J);I=[A for A in F if A.get(_U)==H and G in[_B,A.get(D)]];return(I or[_B])[0]
	@classmethod
	def get_deploy_templates(D):
		def A(_,resources,resource_id,**E):
			B=resources;C=D(B[resource_id]);A=C.properties
			if not A.get(_J):F=C.resolve_refs_recursively(E.get('stack_name'),A.get(_A),B);A[_J]=f"Generated API key for AppSync API ID {F}"
			if A.get(_I):A[_I]=int(A.get(_I))
			G=keys_to_lower(select_attributes(A,[_A,_J,_I]));return G
		return{_K:{_G:'create_api_key',_H:A}}
class AppSyncDataSource(GenericBaseModel):
	@staticmethod
	def cloudformation_type():return'AWS::AppSync::DataSource'
	@staticmethod
	def get_deploy_templates():
		def A(params,**C):
			B='dynamoDBConfig';A=params;A=keys_to_lower(clone(A))
			if A.get(B):A['dynamodbConfig']=A.pop(B)
			return A
		return{_K:{_G:'create_data_source',_H:A}}
	def get_cfn_attribute(A,attribute_name):
		B=attribute_name
		if B in REF_ARN_ATTRS+['DataSourceArn']:return A.props.get(_V)
		if B==_E:return A.props.get(_F)
		return super(AppSyncDataSource,A).get_cfn_attribute(B)
	def get_physical_resource_id(A,attribute=_B,**B):return A.props.get(_V)
	def fetch_state(A,stack_name,resources):D=resources;C=stack_name;E=A.props;F=aws_stack.connect_to_service(_D);B=E.get(_E)or A.resource_id;B=A.resolve_refs_recursively(C,B,D);G=A.resolve_refs_recursively(C,E.get(_A),D);H=F.list_data_sources(apiId=G)['dataSources'];return([A for A in H if A[_F]==B]or[_B])[0]
class AppSyncFunctionConfig(GenericBaseModel):
	@staticmethod
	def cloudformation_type():return'AWS::AppSync::FunctionConfiguration'
	def fetch_state(A,stack_name,resources):D=resources;C=stack_name;F=aws_stack.connect_to_service(_D);E=A.props;G=A.resolve_refs_recursively(C,E[_A],D);H=A.resolve_refs_recursively(C,E[_E],D);B=F.list_functions(apiId=G).get('functions',[]);B=[A for A in B if A.get(_F)==H];return(B or[_B])[0]
	def get_cfn_attribute(C,attribute_name):
		A=attribute_name;B=C.props
		if A=='FunctionId':return B.get(_N,'').split('functions/')[-1]
		if A=='FunctionArn':return B.get(_N)
		if A==_E:return B.get(_F)
		if A==_L:return B.get(_M)
		return super(AppSyncFunctionConfig,C).get_cfn_attribute(A)
	def get_physical_resource_id(A,attribute,**B):return A.props.get(_N)
	@staticmethod
	def get_deploy_templates():
		def A(params,**D):
			B=params;A=B.get('SyncConfig')
			if A:A=keys_to_lower(clone(A))
			C={_C:_A,_F:_E,_U:_J,_M:_L,_S:'RequestMappingTemplate',_T:'ResponseMappingTemplate','functionVersion':'FunctionVersion','syncConfig':A};C={D:B.get(A)for(D,A)in C.items()if B.get(A)};return C
		return{_K:{_G:'create_function',_H:A}}
class GraphQLAPI(GenericBaseModel):
	@staticmethod
	def cloudformation_type():return'AWS::AppSync::GraphQLApi'
	def get_cfn_attribute(C,attribute_name):
		B=attribute_name;A=C.props
		if not A.get(_C):
			D=C.fetch_details(A.get(_E))
			if not D:raise Exception('Unable to find GraphQL API named "%s"'%A.get(_E))
			A[_C]=D[_C]
		if B==_A:return A.get(_C)
		if B in REF_ARN_ATTRS:return C.get_physical_resource_id(B)
		if B=='GraphQLUrl':return appsync_api.get_graphql_url(A[_C],use_domain_name=True)
		return super(GraphQLAPI,C).get_cfn_attribute(B)
	def get_physical_resource_id(B,attribute,**C):A=B.props;return A.get(_C)and aws_utils.appsync_api_arn(A[_C])
	@classmethod
	def fetch_details(C,api_name):A=aws_stack.connect_to_service(_D);B=A.list_graphql_apis()['graphqlApis'];return([A for A in B if A[_F]==api_name]or[_B])[0]