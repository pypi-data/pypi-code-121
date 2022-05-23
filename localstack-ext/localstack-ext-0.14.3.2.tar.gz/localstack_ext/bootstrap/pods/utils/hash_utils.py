import hashlib
import logging
import os
import random
import zipfile
from typing import Optional
from localstack.utils.common import new_tmp_dir,rm_rf
from localstack_ext.bootstrap.pods.models import Revision,Version
from localstack_ext.bootstrap.state_utils import API_STATES_DIR,api_states_traverse
LOG=logging.getLogger(__name__)
def random_hash()->str:
 return hex(random.getrandbits(160))
def compute_file_hash(file_path:str,accum=None)->Optional[str]:
 try:
  with open(file_path,"rb")as fp:
   if accum:
    accum.update(fp.read())
   else:
    return hashlib.sha1(fp.read()).hexdigest()
 except Exception as e:
  LOG.warning(f"Failed to open file and compute hash for file at {file_path}: {e}")
def compute_version_archive_hash(version_no:int,state_archive:str)->str:
 def _compute_file_hash_func(**kwargs):
  dir_name=kwargs.get("dir_name")
  file_name=kwargs.get("fname")
  accum=kwargs.get("mutables")[0]
  file_path=os.path.join(dir_name,file_name)
  compute_file_hash(file_path,accum)
 tmp_state_dir=new_tmp_dir()
 with zipfile.ZipFile(state_archive)as archive:
  archive.extractall(tmp_state_dir)
 tmp_state_archive_api_states=os.path.join(tmp_state_dir,API_STATES_DIR)
 m=hashlib.sha1()
 api_states_traverse(tmp_state_archive_api_states,_compute_file_hash_func,[m])
 m.update(str(version_no).encode("utf-8"))
 rm_rf(tmp_state_dir)
 return m.hexdigest()
def compute_revision_hash(pods_node:Revision,obj_store_path:str)->str:
 if not pods_node.state_files:
  return random_hash()
 state_file_keys=map(lambda state_file:state_file.hash_ref,pods_node.state_files)
 m=hashlib.sha1()
 for key in state_file_keys:
  try:
   with open(os.path.join(obj_store_path,key),"rb")as fp:
    m.update(fp.read())
  except Exception as e:
   LOG.warning(f"Failed to open file and compute hash for {key}: {e}")
 if isinstance(pods_node,Revision):
  m.update(pods_node.rid.encode("utf-8"))
  m.update(str(pods_node.revision_number).encode("utf-8"))
 elif isinstance(pods_node,Version):
  m.update(str(pods_node.version_number).encode("utf-8"))
 return m.hexdigest()
# Created by pyminifier (https://github.com/liftoff/pyminifier)
