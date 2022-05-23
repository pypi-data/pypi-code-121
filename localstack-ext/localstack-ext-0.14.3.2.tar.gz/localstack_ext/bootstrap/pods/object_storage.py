import abc
import logging
import os
from typing import Dict,List,Union
from localstack_ext.bootstrap.pods.models import PodObject,Revision,Version
from localstack_ext.bootstrap.pods.utils.common import PodsConfigContext
from localstack_ext.bootstrap.pods.utils.serializers import PodsSerializer,txt_serializers
LOG=logging.getLogger(__name__)
class StateFileLocator(abc.ABC):
 location="_none_"
 active_instance=None
 @abc.abstractmethod
 def get_state_file_location_by_key(self,key:str,obj_store_path:str)->str:
  pass
 @classmethod
 def get(cls,requested_file_locator:str):
  if not cls.active_instance or cls.active_instance.location!=requested_file_locator:
   for clazz in cls.__subclasses__():
    if clazz.location==requested_file_locator:
     cls.active_instance=clazz()
  return cls.active_instance
class StateFileLocatorLocal(StateFileLocator):
 location="local"
 def get_state_file_location_by_key(self,key:str,obj_store_path:str)->str:
  return os.path.join(obj_store_path,key)
class ObjectStorageProvider(abc.ABC):
 location="_none_"
 active_instance=None
 @classmethod
 def get(cls,state_file_locator:str,requested_storage:str,serializers:Dict[str,PodsSerializer],config_context:PodsConfigContext):
  if not cls.active_instance or cls.active_instance.location!=requested_storage:
   state_file_locator=StateFileLocator.get(requested_file_locator=state_file_locator)
   for clazz in cls.__subclasses__():
    if clazz.location==requested_storage:
     cls.active_instance=clazz(state_file_locator=state_file_locator,serializers=serializers,config_context=config_context)
  cls.active_instance.config_context=config_context
  return cls.active_instance
 def __init__(self,state_file_locator:StateFileLocator,serializers:Dict[str,PodsSerializer],config_context:PodsConfigContext):
  self.state_file_locator=state_file_locator
  self.serializers=serializers
  self.config_context=config_context
 @abc.abstractmethod
 def get_terminal_revision(self,revision_path_root:Revision):
  pass
 @abc.abstractmethod
 def get_state_file_location_by_key(self,key:str)->str:
  pass
 @abc.abstractmethod
 def get_version_by_key(self,key:str)->Version:
  pass
 @abc.abstractmethod
 def get_revision_by_key(self,key:str)->Revision:
  pass
 @abc.abstractmethod
 def get_revision_or_version_by_key(self,key:str)->Union[Revision,Version]:
  pass
 @abc.abstractmethod
 def get_delta_file_by_key(self,key:str,get_delta_file_by_key:str)->str:
  pass
 @abc.abstractmethod
 def upsert_objects(self,*args:PodObject)->List[str]:
  pass
 @abc.abstractmethod
 def update_revision_key(self,old_key:str,new_key:str,referenced_by_version:str=None):
  pass
 @abc.abstractmethod
 def version_exists(self,key:str)->bool:
  pass
 @abc.abstractmethod
 def merge_remote_into_local_version(self,remote_location:str,key:str):
  pass
 @abc.abstractmethod
 def _update_key(self,old_key:str,new_key:str,base_path:str)->bool:
  pass
 @abc.abstractmethod
 def _serialize(self,*args:PodObject)->List[str]:
  pass
 @abc.abstractmethod
 def _deserialize(self,key_serializer:Dict[str,str],remote_location:str=None,local_location:str=None)->List[PodObject]:
  pass
 @property
 def version_store_path(self):
  return self.config_context.get_ver_obj_store_path()
 @property
 def revision_store_path(self):
  return self.config_context.get_rev_obj_store_path()
 @property
 def object_store_path(self):
  return self.config_context.get_obj_store_path()
class ObjectStorageLocal(ObjectStorageProvider):
 location="local"
 def get_terminal_revision(self,revision_path_root:Revision)->Revision:
  result=revision_path_root
  while result.assoc_commit:
   result=self.get_revision_by_key(result.assoc_commit.head_ptr)
  return result
 def get_state_file_location_by_key(self,key:str)->str:
  return self.state_file_locator.get_state_file_location_by_key(obj_store_path=self.object_store_path,key=key)
 def get_version_by_key(self,key:str)->Version:
  return self._deserialize(key_serializer={key:"version"},local_location=self.version_store_path)[0]
 def get_revision_by_key(self,key:str)->Revision:
  return self._deserialize(key_serializer={key:"revision"},local_location=self.revision_store_path)[0]
 def get_revision_or_version_by_key(self,key:str)->Union[Revision,Version]:
  for func in[self.get_revision_by_key,self.get_version_by_key]:
   result=func(key)
   if result:
    return result
  LOG.warning("No revision or version found with key %s",key)
 def get_delta_file_by_key(self,key:str,delta_log_path:str)->str:
  path=os.path.join(delta_log_path,key)
  if os.path.isfile(path):
   return path
  LOG.warning("No state file found for key: %s",key)
 def upsert_objects(self,*args:PodObject)->List[str]:
  return self._serialize(*args)
 def update_revision_key(self,old_key:str,new_key:str,referenced_by_version:str=None):
  updated=self._update_key(old_key,new_key,self.revision_store_path)
  if not updated:
   LOG.warning(f"No revision found with key {old_key} to update")
   return
  if referenced_by_version:
   version=self.get_version_by_key(referenced_by_version)
   version.active_revision_ptr=new_key
   version.outgoing_revision_ptrs.remove(old_key)
   version.outgoing_revision_ptrs.add(new_key)
   self.upsert_objects(version)
 def version_exists(self,key:str)->bool:
  return os.path.isfile(os.path.join(self.version_store_path,key))
 def merge_remote_into_local_version(self,remote_location:str,key:str):
  local_version=self.get_version_by_key(key)
  remote_version=self._deserialize({key:"version"},remote_location,self.version_store_path)[0]
  local_version.outgoing_revision_ptrs.update(remote_version.outgoing_revision_ptrs)
  self.upsert_objects(local_version)
 def _update_key(self,old_key:str,new_key:str,base_path:str)->bool:
  path_old_key=os.path.join(base_path,old_key)
  if not os.path.isfile(path_old_key):
   return False
  path_new_key=os.path.join(base_path,new_key)
  os.rename(path_old_key,path_new_key)
  return True
 def _serialize(self,*args:PodObject)->List[str]:
  hash_refs=[]
  for pods_object in args:
   if isinstance(pods_object,Version):
    hash_refs.append(self.serializers["version"].store_obj(pods_object,self.version_store_path))
   elif isinstance(pods_object,Revision):
    hash_refs.append(self.serializers["revision"].store_obj(pods_object,self.revision_store_path))
  return hash_refs
 def _deserialize(self,key_serializer:Dict[str,str],remote_location:str=None,local_location:str=None)->List[Union[Revision,Version]]:
  return[self.serializers[serializer].retrieve_obj(key,remote_location,local_location)for key,serializer in key_serializer.items()]
def get_object_storage_provider(config_context:PodsConfigContext,requested_storage:str="local")->ObjectStorageProvider:
 return ObjectStorageProvider.get(state_file_locator=requested_storage,requested_storage=requested_storage,serializers=txt_serializers,config_context=config_context)
# Created by pyminifier (https://github.com/liftoff/pyminifier)
