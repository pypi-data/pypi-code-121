_B='username'
_A=None
import getpass,json,logging,os,sys
from abc import ABC
from typing import Any,Dict,Optional
from localstack.config import dirs
from localstack.constants import API_ENDPOINT
from localstack.utils.common import FileMappedDocument,call_safe,safe_requests,to_str
from localstack.utils.objects import SubtypesInstanceManager
LOG=logging.getLogger(__name__)
AUTH_CACHE_FILE='auth.json'
class AuthToken:
	def __init__(A,token,metadata=_A):A.token=token;A.metadata=metadata
class AuthProvider(SubtypesInstanceManager,ABC):
	def get_or_create_token(A,username,password,headers=_A):0
	def refresh_token(A,token):0
	def get_user_for_token(A,token):0
	@classmethod
	def providers(A):return A.instances()
class AuthProviderInternal(AuthProvider):
	@staticmethod
	def impl_name():return'internal'
	def get_or_create_token(D,username,password,headers=_A):
		C={_B:username,'password':password};A=safe_requests.post(f"{API_ENDPOINT}/user/signin",json.dumps(C),headers=headers)
		if A.status_code>=400:return
		try:B=json.loads(to_str(A.content or'{}'));return AuthToken(token=B['token'],metadata=B)
		except Exception:pass
	def refresh_token(A,token):return token
	def read_credentials(C,username):
		A=username;print('Please provide your login credentials below')
		if not A:sys.stdout.write('Username: ');sys.stdout.flush();A=input()
		B=getpass.getpass();return A,B,{}
	def get_user_for_token(A,token):raise Exception('Not implemented')
def get_auth_cache():return FileMappedDocument(os.path.join(dirs.cache,AUTH_CACHE_FILE),mode=384)
def login(provider,username=_A):
	B=provider;A=username;C=AuthProvider.get(B)
	if not C:F=list(AuthProvider.providers().keys());raise Exception('Unknown provider "%s", should be one of %s'%(B,F))
	A,G,H=C.read_credentials(A);print('Verifying credentials ... (this may take a few moments)');D=C.get_or_create_token(A,G,H)
	if not D:raise Exception('Unable to verify login credentials - please try again')
	E=get_auth_cache();E.update({'provider':B,_B:A,'token':D.token});call_safe(E.save,exception_message='error saving authentication information')
def logout():A=get_auth_cache();A.clear();A.save()
def json_loads(s):return json.loads(to_str(s))