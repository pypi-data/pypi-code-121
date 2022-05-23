import os
import zipfile
from typing import Dict,Protocol
from localstack.utils.common import mkdir,new_tmp_dir
from localstack.utils.generic.singleton_utils import SubtypesInstanceManager
from moto.s3.models import FakeBucket
from moto.sqs.models import Queue
from localstack_ext.bootstrap.pods.models import Serialization
from localstack_ext.bootstrap.pods.service_state import Backends
from localstack_ext.bootstrap.state_merge import(merge_dynamodb,merge_kinesis_state,merge_object_state)
from localstack_ext.bootstrap.state_utils import(API_STATES_DIR,DYNAMODB_DIR,KINESIS_DIR,api_states_traverse,load_persisted_object,persist_object)
ROOT_FOLDERS_BY_SERIALIZATION=[API_STATES_DIR,DYNAMODB_DIR,KINESIS_DIR]
class MergeManager(Protocol):
 def merge(self,a:Backends,b:Backends):
  ...
class DefaultMergeManager(MergeManager):
 def merge(self,a:Backends,b:Backends):
  from localstack_ext.utils.persistence import unmarshal_backend
  for state_key in b:
   if state_key in a:
    b_backend=unmarshal_backend(b[state_key])
    a_backend=unmarshal_backend(a[state_key])
    merged_backend=merge_object_state(a_backend,b_backend)
    a[state_key]=merged_backend
   else:
    a[state_key]=unmarshal_backend(b[state_key])
class DynamoDBMergeManager(MergeManager):
 def merge(self,a:Backends,b:Backends):
  ...
class KinesisMergeManager(MergeManager):
 def merge(self,a:Backends,b:Backends):
  ...
def get_merge_manager(service:str)->MergeManager:
 if service=="dynamodb":
  return DynamoDBMergeManager()
 if service=="kinesis":
  return KinesisMergeManager()
 return DefaultMergeManager()
class CloudPodsMergeManager(SubtypesInstanceManager):
 @staticmethod
 def _is_special_case(obj)->bool:
  return isinstance(obj,(Queue,FakeBucket))
 def two_way_merge(self,from_state_files:str,to_state_files):
  raise NotImplementedError
 def three_way_merge(self,common_ancestor_state_files:str,from_state_files:str,to_state_files:str):
  raise NotImplementedError
class CloudPodsMergeManagerDynamoDB(CloudPodsMergeManager):
 @staticmethod
 def impl_name()->str:
  return Serialization.DDB.value
 def two_way_merge(self,from_state_files:str,to_state_files):
  merge_dynamodb(from_state_files,to_state_files)
 def three_way_merge(self,common_ancestor_state_files:str,from_state_files:str,to_state_files:str):
  merge_dynamodb(from_state_files,to_state_files)
class CloudPodsMergeManagerKinesis(CloudPodsMergeManager):
 @staticmethod
 def impl_name()->str:
  return Serialization.KINESIS.value
 def two_way_merge(self,from_state_files:str,to_state_files):
  merge_kinesis_state(to_state_files,from_state_files)
 def three_way_merge(self,common_ancestor_state_files:str,from_state_files:str,to_state_files:str):
  self.two_way_merge(to_state_files,from_state_files)
class CloudPodsMergeManagerMain(CloudPodsMergeManager):
 @staticmethod
 def impl_name()->str:
  return Serialization.MAIN.value
 @staticmethod
 def _merge_three_way_dir_func(**kwargs):
  dir_name=kwargs.get("dir_name")
  account_id=kwargs.get("account_id")
  fname=kwargs.get("fname")
  region=kwargs.get("region")
  service_name=kwargs.get("service_name")
  mutables=kwargs.get("mutables")
  other=mutables[0]
  ancestor=mutables[1]
  src_state_file_path=os.path.join(dir_name,fname)
  ancestor_state_dir=os.path.join(ancestor,account_id,service_name,region)
  ancestor_state_file_path=os.path.join(ancestor_state_dir,fname)
  dst_state_dir=os.path.join(other,account_id,service_name,region)
  dst_state_file_path=os.path.join(dst_state_dir,fname)
  src_state=load_persisted_object(src_state_file_path)
  ancestor_state=load_persisted_object(ancestor_state_file_path)
  special_case=CloudPodsMergeManager._is_special_case(src_state)
  if os.path.isfile(dst_state_file_path):
   if not special_case:
    dst_state=load_persisted_object(dst_state_file_path)
    merge_object_state(dst_state,src_state,ancestor_state)
    persist_object(dst_state,dst_state_file_path)
  else:
   mkdir(dst_state_dir)
   persist_object(src_state,dst_state_file_path)
 @staticmethod
 def _merge_two_state_dir_func(**kwargs):
  dir_name=kwargs.get("dir_name")
  account_id=kwargs.get("account_id")
  fname=kwargs.get("fname")
  region=kwargs.get("region")
  service_name=kwargs.get("service_name")
  mutables=kwargs.get("mutables")
  other=mutables[0]
  src_state_file_path=os.path.join(dir_name,fname)
  dst_state_dir=os.path.join(other,account_id,service_name,region)
  dst_state_file_path=os.path.join(dst_state_dir,fname)
  src_state=load_persisted_object(src_state_file_path)
  special_case=CloudPodsMergeManager._is_special_case(src_state)
  if os.path.isfile(dst_state_file_path):
   if not special_case:
    dst_state=load_persisted_object(dst_state_file_path)
    merge_object_state(dst_state,src_state)
    persist_object(dst_state,dst_state_file_path)
  else:
   mkdir(dst_state_dir)
   persist_object(src_state,dst_state_file_path)
 def two_way_merge(self,from_state_files:str,to_state_files):
  api_states_traverse(api_states_path=to_state_files,side_effect=CloudPodsMergeManagerMain._merge_two_state_dir_func,mutables=[from_state_files])
 def three_way_merge(self,common_ancestor_state_files:str,from_state_files:str,to_state_files:str):
  api_states_traverse(api_states_path=to_state_files,side_effect=CloudPodsMergeManagerMain._merge_three_way_dir_func,mutables=[from_state_files,common_ancestor_state_files])
def create_tmp_archives_by_serialization_mechanism(archive_dir:str)->Dict[str,str]:
 tmp_root_dir=new_tmp_dir()
 with zipfile.ZipFile(archive_dir)as archive:
  archive.extractall(tmp_root_dir)
 result={"root":tmp_root_dir}
 for serialization_mechanism_root_dir in ROOT_FOLDERS_BY_SERIALIZATION:
  tmp_root_dir_for_serialization_mechanism=os.path.join(tmp_root_dir,serialization_mechanism_root_dir)
  mkdir(tmp_root_dir_for_serialization_mechanism)
  result[serialization_mechanism_root_dir]=tmp_root_dir_for_serialization_mechanism
 return result
# Created by pyminifier (https://github.com/liftoff/pyminifier)
