import logging
import re
import types
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
def use_elasticmq():
 return False
def forward_request(self,method,path,data,headers):
 data_orig=to_str(data)or ""
 path_orig=to_str(path)
 if use_elasticmq():
  region=aws_stack.extract_region_from_auth_header(headers)
  regex,replace=r"(^|[\?&])QueueName=([^&]+)($|&)",r"\1QueueName=%s_\2&"%region
  data=re.sub(regex,replace,data_orig)
  path=re.sub(regex,replace,path_orig)
  regex,replace=r"(^|&)QueueUrl=([^&]+%2[fF])([^&]+)($|&)",r"\1QueueUrl=\2%s_\3&"%region
  data=re.sub(regex,replace,data)
  regex=r"arn%3[aA]aws%3[aA]sqs%3[aA]([^%]+)%3[aA]([0-9]+)%3[aA]([^%&]+)"
  replace=r"arn%3Aaws%3Asqs%3A\1%3A\2%3A\1_\3"
  data=re.sub(regex,replace,data)
 result=forward_request_orig(method,path,data,headers)
 if((data!=data_orig or path!=path_orig)and not isinstance(result,Request)and not(isinstance(result,Response)and result.status_code>399)):
  request=Request(data=data,headers=headers,method=method)
  return request
 return result
def return_response(self,method,path,data,headers,response,*args,**kwargs):
 result=return_response_orig(method,path,data,headers,response,*args,**kwargs)
 if isinstance(result,Response):
  response=result
 region=aws_stack.extract_region_from_auth_header(headers)
 content_orig=to_str(response.content)
 def sub(match):
  content=match.group(1)
  result=""
  if("/%s_"%region)in content:
   result="%s%s"%(match.group(2),match.group(5))
   edge_url=headers.get(HEADER_LOCALSTACK_EDGE_URL)
   if edge_url:
    result=re.sub(r"[^:]*://[^/]+",edge_url,result)
   result="<QueueUrl>%s</QueueUrl>"%result
  return result
 content=content_orig
 if use_elasticmq():
  content=re.sub(r"<QueueUrl>(([^<]+/)(([^<_]+)_)?([^<]+))</QueueUrl>",sub,content)
  content=re.sub(r"arn:aws:sqs:elasticmq:000000000000:([^_]+)_([a-zA-Z0-9_-]+)",r"arn:aws:sqs:\1:000000000000:\2",content)
  content=re.sub(r">(\s*[^<]+:)%s_([^<]+\s*)</"%region,r">\1\2</",content)
 if content!=content_orig:
  response._content=content
 response.headers["Content-Length"]=str(len(response._content or ""))
 return response
def get_forward_url(self,method,path,data,headers):
 if not use_elasticmq():
  return
 queue_url_path=r"/queue/([^/]+)"
 if re.match(queue_url_path,path):
  region=aws_stack.extract_region_from_auth_header(headers)
  path=re.sub(queue_url_path,r"/queue/%s_\1"%region,path)
  url="http://%s:%s%s"%(LOCALHOST,sqs_starter.PORT_SQS_BACKEND,path)
  return url
def remove_region_in_queue_url(url):
 region=aws_stack.get_region()
 return re.sub(r"/queue/%s_(.*)"%region,r"/queue/\1",url)
def _set_queue_attributes(queue_url,req_data,*args):
 if use_elasticmq():
  queue_url=remove_region_in_queue_url(queue_url)
 return _set_queue_attributes_orig(queue_url,req_data,*args)
def update_backend_state(context:PersistenceContext,request:Request):
 do_update_backend_state(context,request)
 return False
def do_update_backend_state(context:PersistenceContext,request:Request):
 if not localstack_config.dirs.data:
  return
 req_data=parse_request_data(request.method,request.url,request.data)
 action=req_data.get("Action")or ""
 if action.startswith("List")or action.startswith("Get"):
  return
 region=aws_stack.extract_region_from_auth_header(request.headers)
 if region not in sqs_backends:
  LOG.warning('Unable to find SQS backend for region "%s"'%region)
  return
 state=None
 queue_name=req_data.get("QueueName")
 if action=="CreateQueue":
  state=sqs_backends[region].queues.get(queue_name)
 elif action in["SendMessage","SendMessageBatch","SetQueueAttributes","DeleteMessage"]:
  queue_url=_queue_url(request.url,req_data,request.headers)
  queue_name=queue_url.split("/")[4]
  state=sqs_backends[region].queues.get(queue_name)
 if state:
  persist_state(get_states_dir(),region,queue_name,state,context.lock)
def restore_state(*args):
 if not localstack_config.dirs.data:
  return
 for key,region,queue in load_backend_state(get_states_dir()):
  sqs_backends[region].queues[key]=queue
def get_states_dir():
 return get_states_dir_for_service("sqs")
def patch_sqs():
 sqs_listener.UPDATE_SQS.forward_request=types.MethodType(forward_request,sqs_listener.UPDATE_SQS)
 sqs_listener.UPDATE_SQS.return_response=types.MethodType(return_response,sqs_listener.UPDATE_SQS)
 sqs_listener.UPDATE_SQS.get_forward_url=types.MethodType(get_forward_url,sqs_listener.UPDATE_SQS)
 sqs_listener._set_queue_attributes=_set_queue_attributes
 setup_and_restore_persistence("sqs",moto_backend=sqs_backends,update_listeners=update_backend_state,on_restored=restore_state)
# Created by pyminifier (https://github.com/liftoff/pyminifier)
