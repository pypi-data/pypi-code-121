from localstack.aws.protocol import service_router as localstack_service_router
from localstack.utils.patch import patch
def patch_service_router():
	C='appsync';import re;from typing import Callable,Optional;from localstack.http import Request;from localstack.services.apigateway.context import ApiInvocationContext as F;from localstack_ext.services.apigateway.apigateway_extended import is_custom_domain_api_invocation as G
	@patch(localstack_service_router.custom_signing_name_rules)
	def A(fn,signing_name,path,**C):
		B='rds';A=signing_name
		if A in[B,'docdb','neptune']:return B
		return fn(A,path,**C)
	@patch(localstack_service_router.custom_host_addressing_rules)
	def B(fn,host,**B):
		A=host
		if'.cloudfront.'in A:return'cloudfront'
		if'mediastore-'in A:return'mediastore-data'
		if'.elb.'in A:return'elbv2'
		if'.appsync-api.'in A:return C
		return fn(A,**B)
	@patch(localstack_service_router.legacy_rules)
	def D(fn,request,**H):
		E='apigateway';A=request;B=A.path;I=A.method;J=A.data;D=A.headers;K=F(I,B,data=J,headers=D)
		if G(K):return E
		if re.match('/graphql/[a-zA-Z0-9-]+',B):return C
		L=D.get('authorization','')
		if L.startswith('Bearer '):return E
		if B.startswith('/_messages_'):return'ses'
		if'/2018-06-01/runtime'in B:return'lambda'
		return fn(request=A,**H)