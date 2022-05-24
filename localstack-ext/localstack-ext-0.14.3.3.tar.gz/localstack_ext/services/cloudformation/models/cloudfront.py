_P='DistributionConfig'
_O='OriginRequestPolicy'
_N='delete'
_M='CloudFrontOriginAccessIdentityConfig'
_L='Aliases'
_K='parameters'
_J='CallerReference'
_I='Origins'
_H='create'
_G='Comment'
_F='function'
_E='cloudfront'
_D='Id'
_C=None
_B='Name'
_A='Items'
from localstack.services.cloudformation.service_models import REF_ID_ATTRS,GenericBaseModel
from localstack.utils.aws import aws_stack
from localstack.utils.common import select_attributes,short_uid,to_bytes
from localstack_ext.utils.aws import aws_utils
class CloudFrontOriginAccessIdentity(GenericBaseModel):
	@staticmethod
	def cloudformation_type():return'AWS::CloudFront::CloudFrontOriginAccessIdentity'
	def get_physical_resource_id(A,attribute=_C,**B):return A.props.get(_D)
	def fetch_state(B,stack_name,resources):C=aws_stack.connect_to_service(_E);A=C.list_cloud_front_origin_access_identities();A=A.get('CloudFrontOriginAccessIdentityList',{}).get(_A,[]);D=B.props.get(_M,{});A=[B for B in A if B[_G]==D.get(_G)];return A and A[0]or _C
	@staticmethod
	def get_deploy_templates():
		def A(params,**C):A=params;B=A.get(_M);B[_J]=short_uid();return A
		return{_H:{_F:'create_cloud_front_origin_access_identity',_K:A}}
class CloudFrontFunction(GenericBaseModel):
	@staticmethod
	def cloudformation_type():return'AWS::CloudFront::Function'
	def fetch_state(B,stack_name,resources):C=aws_stack.connect_to_service(_E);A=C.list_functions();A=A.get('FunctionList',{}).get(_A,[]);D=B.props;A=[B for B in A if B[_B]==D.get(_B)];return A and A[0]or _C
	def get_physical_resource_id(A,attribute,**B):return A.props.get(_B)
	def get_cfn_attribute(A,attribute_name):
		B=attribute_name
		if B=='FunctionARN':return aws_utils.get_cloudfront_function_arn(A.props.get(_B))
		return super(CloudFrontFunction,A).get_cfn_attribute(B)
	@classmethod
	def get_deploy_templates(C):
		def A(params,**C):
			B='FunctionCode';A=select_attributes(params,[_B,B,'FunctionConfig'])
			if A.get(B):A[B]=to_bytes(A[B])
			return A
		def B(resource_id,resources,resource_type,func,stack_name,*F):D=C(resources[resource_id]);A=aws_stack.connect_to_service(_E);B=D.props.get(_B);E=A.describe_function(Name=B).get('ETag');return A.delete_function(Name=B,IfMatch=E)
		return{_H:{_F:'create_function',_K:A},_N:{_F:B}}
class CloudFrontOriginRequestPolicy(GenericBaseModel):
	@staticmethod
	def cloudformation_type():return'AWS::CloudFront::OriginRequestPolicy'
	def fetch_state(C,stack_name,resources):D='OriginRequestPolicyConfig';E=aws_stack.connect_to_service(_E);A=E.list_origin_request_policies();A=A.get('OriginRequestPolicyList',{}).get(_A,[]);A=[B.get(_O,{})for B in A];A=[{_D:B[_D],**B.get(D,{})}for B in A];B=C.props.get(D,{}).get(_B);B=C.resolve_refs_recursively(stack_name,B,resources);A=[C for C in A if C.get(_B)==B];return A and A[0]or _C
	def get_physical_resource_id(A,attribute,**B):return A.props.get(_D)
	@classmethod
	def get_deploy_templates(C):
		def A(resource_id,resources,resource_type,func,stack_name,*G):A=aws_stack.connect_to_service(_E);D=C(resources[resource_id]);E=D.props;B=E.get(_O).get(_D);F=A.get_origin_request_policy(Id=B).get('ETag');return A.delete_origin_request_policy(Id=B,IfMatch=F)
		return{_H:{_F:'create_origin_request_policy'},_N:{_F:A}}
class CloudFrontDistribution(GenericBaseModel):
	@staticmethod
	def cloudformation_type():return'AWS::CloudFront::Distribution'
	def get_physical_resource_id(B,attribute,**C):
		A=B.props.get(_D)
		if attribute in REF_ID_ATTRS:return A
		return aws_utils.get_cloudfront_distribution_arn(A)
	def fetch_state(F,stack_name,resources):
		E='DomainName';G=aws_stack.connect_to_service(_E);H=G.list_distributions()['DistributionList'].get(_A,[]);D=F.props[_P];A=D.get(_I,[]);A=A if isinstance(A,list)else A.get(_A);I=set([B[E]for B in A]);B=D.get(_L,[]);B=B if isinstance(B,list)else B.get(_A);J=set(B)
		for C in H:
			A=set([A.get(E)for A in C.get(_I,{})[_A]]);B=set(C.get(_L,{}).get(_A,[]))
			if I==A and J==B:return C
	@staticmethod
	def get_deploy_templates():
		def A(params,**m):
			k='Cookies';j='HTTPSPort';i='HTTPPort';h='OriginSslProtocols';g='CacheBehaviors';f='Tags';e='IamCertificateId';d='SslSupportMethod';c='AcmCertificateArn';b='QueryString';a='MinTTL';Z='TrustedSigners';Y='ResponseCode';X='CustomErrorResponses';W='ViewerCertificate';V='true';U=False;R='DefaultCacheBehavior';Q='Enabled';P='GeoRestriction';M=params;L='ForwardedValues';K='Quantity';H='CachedMethods';E='AllowedMethods';A=M[_P];A[_J]=A.get(_J)or short_uid();A[_G]=A.get(_G)or'';A['IsIPV6Enabled']=A.pop('IPV6Enabled',U);A[Q]=str(A.get(Q)).lower()==V;C=A[W]=A.get(W,{});I=A.get(X,[]);I=I.get(_A,[])if isinstance(I,dict)else I
			for S in I:S[Y]=str(S.get(Y))
			F=A[R];F[Z]=F.get(Z)or{K:0,Q:U};F[a]=F.get(a)or 600;T=F[L]=F.get(L,{});T[b]=str(T.get(b)).lower()==V
			if c in C:C['ACMCertificateArn']=C.pop(c)
			if d in C:C['SSLSupportMethod']=C.pop(d)
			if e in C:C['IAMCertificateId']=C.pop(e)
			M[f]={_A:M.get(f)or[]}
			def B(key,parent=_C):
				B=parent;B=A if B is _C else B;C=B.get(key)or[]
				if isinstance(C,dict)and _A in C and K in C:return
				B[key]={K:len(C),_A:C}
			J=A.get(g,[]);J=J.get(_A,[])if isinstance(J,dict)else J
			for N in J:B(E,N);N[E][H]=N.pop(H,[]);B(H,N[E])
			for l in A[_I]:
				D=(l or{}).get('CustomOriginConfig')
				if not D:continue
				D[h]=D.pop('OriginSSLProtocols',[]);D[i]=D.get(i,80);D[j]=D.get(j,443);B(h,D)
			B(_L);B(_I);B('OriginGroups');B(X);B(g);B(E,F);G=A.get(R,{});G[E]=G.get(E);G[E][H]=A.get(R,{}).pop(H,[]);B(H,G[E])
			if G.get(L)and not G[L].get(k):G[L][k]={'Forward':'All'}
			O=A.get('Restrictions',{})
			if O.get(P)and K not in O[P]:O[P][K]=0;O[P][_A]=[]
			return M
		return{_H:{_F:'create_distribution_with_tags',_K:{'DistributionConfigWithTags':A}}}