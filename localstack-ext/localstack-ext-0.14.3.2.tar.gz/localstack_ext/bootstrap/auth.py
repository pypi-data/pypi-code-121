import getpass
import json
import logging
import os
import sys
from abc import ABC
from typing import Any,Dict,Optional
from localstack.config import dirs
from localstack.constants import API_ENDPOINT
from localstack.utils.common import FileMappedDocument,call_safe,safe_requests,to_str
from localstack.utils.objects import SubtypesInstanceManager
LOG=logging.getLogger(__name__)
AUTH_CACHE_FILE="auth.json"
class AuthToken:
 def __init__(self,token:str,metadata:Optional[Dict]=None):
  self.token=token
  self.metadata=metadata
class AuthProvider(SubtypesInstanceManager,ABC):
 def get_or_create_token(self,username:str,password:str,headers=None)->Optional[AuthToken]:
  pass
 def refresh_token(self,token:Optional[AuthToken])->Optional[AuthToken]:
  pass
 def get_user_for_token(self,token)->Any:
  pass
 @classmethod
 def providers(cls)->Dict[str,"AuthProvider"]:
  return cls.instances()
class AuthProviderInternal(AuthProvider):
 @staticmethod
 def impl_name()->str:
  return "internal"
 def get_or_create_token(self,username,password,headers=None):
  data={"username":username,"password":password}
  response=safe_requests.post(f"{API_ENDPOINT}/user/signin",json.dumps(data),headers=headers)
  if response.status_code>=400:
   return
  try:
   result=json.loads(to_str(response.content or "{}"))
   return AuthToken(token=result["token"],metadata=result)
  except Exception:
   pass
 def refresh_token(self,token:Optional[AuthToken])->Optional[AuthToken]:
  return token
 def read_credentials(self,username):
  print("Please provide your login credentials below")
  if not username:
   sys.stdout.write("Username: ")
   sys.stdout.flush()
   username=input()
  password=getpass.getpass()
  return username,password,{}
 def get_user_for_token(self,token):
  raise Exception("Not implemented")
def get_auth_cache()->FileMappedDocument:
 return FileMappedDocument(os.path.join(dirs.cache,AUTH_CACHE_FILE),mode=0o600)
def login(provider,username=None):
 auth_provider=AuthProvider.get(provider)
 if not auth_provider:
  providers=list(AuthProvider.providers().keys())
  raise Exception('Unknown provider "%s", should be one of %s'%(provider,providers))
 username,password,headers=auth_provider.read_credentials(username)
 print("Verifying credentials ... (this may take a few moments)")
 token=auth_provider.get_or_create_token(username,password,headers)
 if not token:
  raise Exception("Unable to verify login credentials - please try again")
 cache=get_auth_cache()
 cache.update({"provider":provider,"username":username,"token":token.token})
 call_safe(cache.save,exception_message="error saving authentication information")
def logout():
 cache=get_auth_cache()
 cache.clear()
 cache.save()
def json_loads(s):
 return json.loads(to_str(s))
# Created by pyminifier (https://github.com/liftoff/pyminifier)
