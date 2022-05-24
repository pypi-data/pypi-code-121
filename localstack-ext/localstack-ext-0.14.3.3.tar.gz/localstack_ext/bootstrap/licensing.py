_G='key_hash'
_F='enterprise'
_E='token'
_D='timestamp'
_C='key'
_B=True
_A=False
import base64,json,logging,os,sys,traceback
from typing import Dict,Union
from localstack import config as localstack_config
from localstack.constants import ENV_PRO_ACTIVATED
from localstack.utils.common import FileMappedDocument,get_proxies,load_file,md5,now_utc
from localstack.utils.common import safe_requests as requests
from localstack.utils.common import str_insert,str_remove,to_bytes,to_str
from localstack_ext import __version__,config
from localstack_ext.bootstrap.auth import get_auth_cache
from localstack_ext.bootstrap.decryption import DecryptionHandler,init_source_decryption
from localstack_ext.config import ROOT_FOLDER
ENV_PREPARED={}
MAX_KEY_CACHE_DURATION_SECS=60*60*24
LOG=logging.getLogger(__name__)
ENV_LOCALSTACK_API_KEY='LOCALSTACK_API_KEY'
class KeyActivationError(Exception):0
class CachedKeyError(KeyActivationError):0
class InvalidKeyError(KeyActivationError):0
class InvalidDecryptionKeyError(KeyActivationError):0
def is_enterprise():return read_api_key(raise_if_missing=_A)==_F
def read_api_key(raise_if_missing=_B):
	A=(os.environ.get(ENV_LOCALSTACK_API_KEY)or'').strip()
	if not A and raise_if_missing:raise Exception('Unable to retrieve API key. Please configure $%s in your environment'%ENV_LOCALSTACK_API_KEY)
	return A
def truncate_api_key(api_key):A=api_key;return'"%s..."(%s)'%(A[:3],len(A))
def fetch_key():
	F='py.warnings';A=read_api_key()
	if A=='test':return b'test'
	elif A==_F:LOG.debug('Looking for a cached enterprise key, skipping online activation.');C=load_cached_key(api_key=A,check_timeout=_A);D=base64.b64decode(C);return D
	G=get_proxies()or None;H={'api_key':A,'version':__version__}
	try:
		logging.getLogger(F).setLevel(logging.ERROR);B=requests.post('%s/activate'%config.API_URL,json.dumps(H),verify=_A,proxies=G)
		if B.status_code>=400:
			E=B.content;I=B.headers.get('Content-Type')
			if B.status_code==403:J=json.loads(to_str(E))['message'];raise InvalidKeyError('Activation key %s is invalid or expired! Reason: %s'%(truncate_api_key(A),J))
			raise KeyActivationError('Received error activating key (code %s): ctype "%s" - %s'%(B.status_code,I,E))
		C=json.loads(to_str(B.content))[_C];cache_key_locally(A,C)
	except InvalidKeyError:raise
	except Exception as K:
		if log_license_issues():A=str(api_key_configured()or'');LOG.warning('Error activating API key %s: %s %s'%(truncate_api_key(A),K,traceback.format_exc()));LOG.warning('Looking for cached key as fallback...')
		C=load_cached_key(A)
	finally:logging.getLogger(F).setLevel(logging.WARNING)
	D=base64.b64decode(C);return D
def get_key_cache():return FileMappedDocument(os.path.join(localstack_config.dirs.cache,'key.json'),mode=384)
def cache_key_locally(api_key,key_b64):
	A=key_b64;B=str(int(now_utc()));C=to_str(base64.b64decode(A))
	for D in range(len(B)):C=str_insert(C,D*2,B[D])
	A=to_str(base64.b64encode(to_bytes(C)));E=get_key_cache();E.update({_D:int(B),_G:md5(api_key),_C:A});E.save()
def load_cached_key(api_key,check_timeout=_B):
	A=get_key_cache()
	if not A.get(_C):raise CachedKeyError('Could not find cached key')
	if A.get(_G)!=md5(api_key):raise CachedKeyError('Cached key was created for a different API key')
	E=now_utc()
	if check_timeout and E-A[_D]>MAX_KEY_CACHE_DURATION_SECS:raise CachedKeyError('Cached key expired')
	D=str(A[_D]);B=to_str(base64.b64decode(A[_C]))
	for C in range(len(D)):assert B[C]==D[C];B=str_remove(B,C)
	F=to_str(base64.b64encode(to_bytes(B)));return F
def enable_file_decryption(key):
	A=DecryptionHandler(key)
	try:
		B=f"{ROOT_FOLDER}/localstack_ext/utils/common.py.enc";C=load_file(B,mode='rb');D=A.decrypt(C)
		if'import'not in to_str(D):raise ValueError('Decryption resulted in invalid python file!')
	except Exception:raise InvalidDecryptionKeyError('Error while trying to validate decryption key!')
	init_source_decryption(A)
def check_require_pro():
	if config.REQUIRE_PRO:LOG.error('Unable to activate API key, but $REQUIRE_PRO is configured - quitting.');sys.exit(1)
def prepare_environment():
	C='finalized'
	class D:
		def __exit__(A,*B,**D):ENV_PREPARED[C]=_B
		def __enter__(A,*B,**C):0
	if not ENV_PREPARED.get(C):
		try:
			A=fetch_key()
			if not A:raise Exception('Unable to fetch and validate API key from environment')
			if to_str(A)!='test':enable_file_decryption(A);LOG.info('Successfully activated API key')
			else:LOG.info('Using test API key')
			os.environ[ENV_PRO_ACTIVATED]='1'
		except KeyActivationError as B:
			if log_license_issues():
				if LOG.isEnabledFor(level=logging.DEBUG):LOG.exception('exception while activating key')
				else:LOG.warning('error while activating key: %s',B)
			check_require_pro()
		except Exception as B:
			if log_license_issues():LOG.warning('Unable to activate API key: %s %s'%(B,traceback.format_exc()))
			check_require_pro()
	return D()
def log_license_issues():return api_key_configured()and localstack_config.is_env_not_false('LOG_LICENSE_ISSUES')
def api_key_configured():return read_api_key(raise_if_missing=_A)
def is_logged_in():return _B if get_auth_cache().get(_E)else _A
def get_auth_headers(auth_cache=None):
	B=auth_cache;B=B or get_auth_cache();A=B.get(_E)
	if isinstance(A,dict):A=A.get(_E)
	if A:
		C=B.get('provider')
		if C:
			D=f"{C} "
			if not A.startswith(D)and' 'not in A:A=f"{D}{A}"
		return{'authorization':A}
	E=read_api_key(raise_if_missing=_A)
	if E:return{'ls-api-key':E,'ls-version':__version__}
	raise Exception('Please log in first')