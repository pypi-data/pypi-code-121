import logging,re,types
from localstack import config as localstack_config
from localstack.constants import HEADER_LOCALSTACK_EDGE_URL,LOCALHOST
from localstack.services.plugins import PersistenceContext
from localstack.services.sqs.legacy import sqs_listener,sqs_starter
from localstack.services.sqs.legacy.sqs_listener import _queue_url,parse_request_data
from localstack.utils.aws import aws_stack
from localstack.utils.common import to_str
from moto.sqs.models import sqs_backends
from requests.models import Request,Response
from localstack_ext.services.base import get_states_dir_for_service,setup_and_restore_persistence
from localstack_ext.utils.persistence import load_backend_state,persist_state
forward_request_orig=sqs_listener.UPDATE_SQS.forward_request
return_response_orig=sqs_listener.UPDATE_SQS.return_response
_set_queue_attributes_orig=sqs_listener._set_queue_attributes
LOG=logging.getLogger(__name__)
def use_elasticmq():return False
def forward_request(self,method,path,data,headers):
	G=method;F=headers;D=path;A=data;H=to_str(A)or'';I=to_str(D)
	if use_elasticmq():J=aws_stack.extract_region_from_auth_header(F);B,C='(^|[\\?&])QueueName=([^&]+)($|&)','\\1QueueName=%s_\\2&'%J;A=re.sub(B,C,H);D=re.sub(B,C,I);B,C='(^|&)QueueUrl=([^&]+%2[fF])([^&]+)($|&)','\\1QueueUrl=\\2%s_\\3&'%J;A=re.sub(B,C,A);B='arn%3[aA]aws%3[aA]sqs%3[aA]([^%]+)%3[aA]([0-9]+)%3[aA]([^%&]+)';C='arn%3Aaws%3Asqs%3A\\1%3A\\2%3A\\1_\\3';A=re.sub(B,C,A)
	E=forward_request_orig(G,D,A,F)
	if(A!=H or D!=I)and not isinstance(E,Request)and not(isinstance(E,Response)and E.status_code>399):K=Request(data=A,headers=F,method=G);return K
	return E
def return_response(self,method,path,data,headers,response,*G,**H):
	C=headers;B=response;D=return_response_orig(method,path,data,C,B,*(G),**H)
	if isinstance(D,Response):B=D
	E=aws_stack.extract_region_from_auth_header(C);F=to_str(B.content)
	def I(match):
		B=match;F=B.group(1);A=''
		if'/%s_'%E in F:
			A='%s%s'%(B.group(2),B.group(5));D=C.get(HEADER_LOCALSTACK_EDGE_URL)
			if D:A=re.sub('[^:]*://[^/]+',D,A)
			A='<QueueUrl>%s</QueueUrl>'%A
		return A
	A=F
	if use_elasticmq():A=re.sub('<QueueUrl>(([^<]+/)(([^<_]+)_)?([^<]+))</QueueUrl>',I,A);A=re.sub('arn:aws:sqs:elasticmq:000000000000:([^_]+)_([a-zA-Z0-9_-]+)','arn:aws:sqs:\\1:000000000000:\\2',A);A=re.sub('>(\\s*[^<]+:)%s_([^<]+\\s*)</'%E,'>\\1\\2</',A)
	if A!=F:B._content=A
	B.headers['Content-Length']=str(len(B._content or''));return B
def get_forward_url(self,method,path,data,headers):
	A=path
	if not use_elasticmq():return
	B='/queue/([^/]+)'
	if re.match(B,A):C=aws_stack.extract_region_from_auth_header(headers);A=re.sub(B,'/queue/%s_\\1'%C,A);D='http://%s:%s%s'%(LOCALHOST,sqs_starter.PORT_SQS_BACKEND,A);return D
def remove_region_in_queue_url(url):A=aws_stack.get_region();return re.sub('/queue/%s_(.*)'%A,'/queue/\\1',url)
def _set_queue_attributes(queue_url,req_data,*B):
	A=queue_url
	if use_elasticmq():A=remove_region_in_queue_url(A)
	return _set_queue_attributes_orig(A,req_data,*(B))
def update_backend_state(context,request):do_update_backend_state(context,request);return False
def do_update_backend_state(context,request):
	A=request
	if not localstack_config.dirs.data:return
	F=parse_request_data(A.method,A.url,A.data);C=F.get('Action')or''
	if C.startswith('List')or C.startswith('Get'):return
	B=aws_stack.extract_region_from_auth_header(A.headers)
	if B not in sqs_backends:LOG.warning('Unable to find SQS backend for region "%s"'%B);return
	D=None;E=F.get('QueueName')
	if C=='CreateQueue':D=sqs_backends[B].queues.get(E)
	elif C in['SendMessage','SendMessageBatch','SetQueueAttributes','DeleteMessage']:G=_queue_url(A.url,F,A.headers);E=G.split('/')[4];D=sqs_backends[B].queues.get(E)
	if D:persist_state(get_states_dir(),B,E,D,context.lock)
def restore_state(*D):
	if not localstack_config.dirs.data:return
	for (A,B,C) in load_backend_state(get_states_dir()):sqs_backends[B].queues[A]=C
def get_states_dir():return get_states_dir_for_service('sqs')
def patch_sqs():sqs_listener.UPDATE_SQS.forward_request=types.MethodType(forward_request,sqs_listener.UPDATE_SQS);sqs_listener.UPDATE_SQS.return_response=types.MethodType(return_response,sqs_listener.UPDATE_SQS);sqs_listener.UPDATE_SQS.get_forward_url=types.MethodType(get_forward_url,sqs_listener.UPDATE_SQS);sqs_listener._set_queue_attributes=_set_queue_attributes;setup_and_restore_persistence('sqs',moto_backend=sqs_backends,update_listeners=update_backend_state,on_restored=restore_state)