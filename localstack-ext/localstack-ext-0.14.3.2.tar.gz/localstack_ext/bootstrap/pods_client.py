import json
import logging
import os
import re
from abc import ABCMeta,abstractmethod
from typing import Dict,List,Optional,Set
from zipfile import ZipFile
import requests
from localstack import config,constants
from localstack.utils.common import(clone,cp_r,disk_usage,download,load_file,new_tmp_dir,new_tmp_file,retry,rm_rf,safe_requests,save_file,to_str)
from localstack.utils.docker_utils import DOCKER_CLIENT
from localstack.utils.testutil import create_zip_file
from localstack_ext.bootstrap.licensing import get_auth_headers
from localstack_ext.bootstrap.pods import pods_api
from localstack_ext.bootstrap.pods.models import Serialization
from localstack_ext.bootstrap.pods.pods_api import PodsApi
from localstack_ext.bootstrap.state_utils import(API_STATES_DIR,DYNAMODB_DIR,KINESIS_DIR,api_states_traverse)
from localstack_ext.constants import API_PATH_PODS
LOG=logging.getLogger(__name__)
PERSISTED_FOLDERS=[API_STATES_DIR,DYNAMODB_DIR,KINESIS_DIR]
MERGE_STRATEGY_TWO_WAY="two way"
MERGE_STRATEGY_THREE_WAY="three way"
MERGE_STRATEGY_DISABLED="disabled"
class PodInfo:
 def __init__(self,name=None,pod_size=0):
  self.name=name
  self.pod_size=pod_size
  self.pod_size_compressed=0
  self.persisted_resource_names=[]
class CloudPodsManager(object,metaclass=ABCMeta):
 @abstractmethod
 def __init__(self,pod_name:str,pre_config:{}):
  self.pod_name=pod_name
  self.pod_config=clone(pre_config)
  self.pods_api=PodsApi()
 @abstractmethod
 def init(self):
  ...
 @abstractmethod
 def delete(self,remote:bool)->bool:
  ...
 @abstractmethod
 def push(self,comment:str=None,three_way:bool=False)->PodInfo:
  ...
 @abstractmethod
 def push_overwrite(self,version:int,comment:str=None):
  ...
 @abstractmethod
 def pull(self,inject_version_state:bool=False,reset_state_before:bool=False,lazy:bool=False):
  ...
 @abstractmethod
 def commit(self,message:str)->None:
  ...
 @abstractmethod
 def inject(self,version:int,reset_state:bool)->bool:
  ...
 @abstractmethod
 def list_versions(self)->List[str]:
  ...
 @abstractmethod
 def version_info(self,version:int):
  ...
 @abstractmethod
 def version_metamodel(self,version:int)->Dict:
  ...
 @abstractmethod
 def set_version(self,version:int,inject_version_state:bool,reset_state:bool,commit_before:bool)->bool:
  ...
 @abstractmethod
 def list_version_commits(self,version:int)->List[str]:
  ...
 @abstractmethod
 def get_commit_diff(self,version:int,commit:int)->Dict:
  ...
 @abstractmethod
 def register_remote(self,pod_name:str,ci_pod:bool)->bool:
  ...
 @abstractmethod
 def rename_pod(self,current_pod_name,new_pod_name)->bool:
  ...
 @abstractmethod
 def list_pods(self,fetch_remote:bool)->Set[str]:
  ...
 @staticmethod
 def restart_container()->None:
  LOG.info("Restarting LocalStack instance with updated persistence state - this may take some time ...")
  data={"action":"restart"}
  url="%s/health"%config.get_edge_url()
  try:
   requests.post(url,data=json.dumps(data))
  except requests.exceptions.ConnectionError:
   pass
  def check_status():
   LOG.info("Waiting for LocalStack instance to be fully initialized ...")
   response=requests.get(url)
   content=json.loads(to_str(response.content))
   statuses=[v for k,v in content["services"].items()]
   assert set(statuses)=={"running"}
  retry(check_status,sleep=3,retries=10)
 @staticmethod
 def get_state_zip_from_instance(get_content=False)->str:
  url=f"{get_pods_endpoint()}/state"
  result=requests.get(url)
  if result.status_code>=400:
   raise Exception("Unable to get local pod state via management API %s (code %s): %s"%(url,result.status_code,result.content))
  if get_content:
   return result.content
  zip_file=f"{new_tmp_file()}.zip"
  save_file(zip_file,result.content)
  return zip_file
 def get_pod_info(self,pod_data_dir:str=None):
  result=PodInfo(self.pod_name)
  if pod_data_dir:
   result.pod_size=disk_usage(pod_data_dir)
   result.persisted_resource_names=get_persisted_resource_names(pod_data_dir)
  return result
class CloudPodsVersionManager(CloudPodsManager):
 def __init__(self,pod_name:str,pre_config:{}):
  super().__init__(pod_name,pre_config)
 @staticmethod
 def parse_pod_name_from_qualifying_name(qualifying_name:str)->str:
  return qualifying_name.split(PODS_NAMESPACE_DELIM,1)[1]
 @staticmethod
 def _prepare_archives_from_pre_signed_urls(content):
  zip_path_version_space=new_tmp_file()
  presigned_urls=content.get("presigned_urls")
  version_space_url=presigned_urls.get("presigned_version_space_url")
  download(url=version_space_url,path=zip_path_version_space)
  zip_paths_state_archives={}
  zip_paths_meta_archives={}
  meta_and_state_urls=presigned_urls.get("presigned_meta_state_urls")
  for version_no,meta_and_state_url in meta_and_state_urls.items():
   zip_path_meta_archive=new_tmp_file()
   zip_path_state_archive=new_tmp_file()
   meta_url=meta_and_state_url["meta"]
   state_url=meta_and_state_url["state"]
   download(meta_url,zip_path_meta_archive)
   download(state_url,zip_path_state_archive)
   zip_paths_meta_archives[version_no]=zip_path_meta_archive
   zip_paths_state_archives[version_no]=zip_path_state_archive
  return zip_path_version_space,zip_paths_meta_archives,zip_paths_state_archives
 @staticmethod
 def _get_max_version_for_pod_from_platform(pod_name:str,auth_headers):
  url=CloudPodsVersionManager.create_platform_url(f"{pod_name}/info/max-version")
  response=safe_requests.get(url=url,headers=auth_headers)
  if response.status_code!=200:
   LOG.warning("Failed to get version information from platform... aborting")
   return
  content=json.loads(response.content)
  remote_max_ver=int(content["max_ver"])
  return remote_max_ver
 def _add_state_files_func(self,**kwargs):
  dir_name=kwargs.get("dir_name")
  account_id=kwargs.get("account_id")
  file_name=kwargs.get("fname")
  region=kwargs.get("region")
  service_name=kwargs.get("service_name")
  self.pods_api.create_state_file_from_fs(path=dir_name,file_name=file_name,service=service_name,region=region,account_id=account_id,root=API_STATES_DIR,serialization=Serialization.MAIN)
 def _add_state_files_from_directory(self,service:str,path:str,root_dir:str,serialization:Serialization):
  if not os.path.isdir(path):
   return
  for state_file in os.listdir(path):
   self.pods_api.create_state_file_from_fs(path=path,file_name=state_file,service=service,region="NA",root=root_dir,serialization=serialization)
 def _add_state_to_cloud_pods_store(self,extract_assets=False):
  if not self.pods_api.config_context.is_initialized():
   LOG.debug("No Cloud Pod instance detected in the local context - unable to push")
   return
  zip_file=self.get_state_zip_from_instance()
  tmp_dir=new_tmp_dir()
  with ZipFile(zip_file,"r")as state_zip:
   state_zip.extractall(tmp_dir)
   api_states_path=os.path.join(tmp_dir,API_STATES_DIR)
   api_states_traverse(api_states_path=api_states_path,side_effect=self._add_state_files_func,mutables=None)
   kinesis_states_path=os.path.join(tmp_dir,KINESIS_DIR)
   dynamodb_states_path=os.path.join(tmp_dir,DYNAMODB_DIR)
   self._add_state_files_from_directory(service="kinesis",path=kinesis_states_path,root_dir=KINESIS_DIR,serialization=Serialization.KINESIS)
   self._add_state_files_from_directory(service="dynamodb",path=dynamodb_states_path,root_dir=DYNAMODB_DIR,serialization=Serialization.DDB)
   if extract_assets:
    asset_roots=[]
    for file_name in os.listdir(tmp_dir):
     file_path=os.path.join(tmp_dir,file_name)
     if os.path.isdir(file_path)and file_name not in PERSISTED_FOLDERS:
      asset_roots.append(file_path)
    self.pods_api.add_assets_to_pod(assets_root_paths=asset_roots)
  rm_rf(zip_file)
  rm_rf(tmp_dir)
 def _pull_versions(self,auth_headers,required_versions:str):
  url=self.create_platform_url(f"{self.pod_name}?versions={required_versions}")
  response=safe_requests.get(url=url,headers=auth_headers)
  if response.status_code!=200:
   LOG.warning("Failed to pull requested versions from platform")
   return
  content=json.loads(response.content)
  archives=CloudPodsVersionManager._prepare_archives_from_pre_signed_urls(content)
  zip_path_version_space=archives[0]
  zip_paths_meta_archives=archives[1]
  zip_paths_state_archives=archives[2]
  self.pods_api.merge_from_remote(version_space_archive=zip_path_version_space,meta_archives=zip_paths_meta_archives,state_archives=zip_paths_state_archives)
 def _clone_pod(self,auth_headers,lazy:bool=False):
  url=self.create_platform_url(f"{self.pod_name}/clone")
  if lazy:
   url+="?lazy=True"
  response=safe_requests.get(url,headers=auth_headers)
  if response.status_code!=200:
   LOG.warning(f"Failed to clone requested pod {self.pod_name}: {response.content}")
   return
  content=json.loads(response.content)
  archives=CloudPodsVersionManager._prepare_archives_from_pre_signed_urls(content)
  zip_path_version_space=archives[0]
  zip_paths_meta_archives=archives[1]
  zip_paths_state_archives=archives[2]
  remote_info={"storage_uuid":content.get("storage_uuid"),"qualifying_name":content.get("pod_name")}
  pod_name=CloudPodsVersionManager.parse_pod_name_from_qualifying_name(remote_info["qualifying_name"])
  self.pods_api.init_remote(pod_name=pod_name,version_space_archive=zip_path_version_space,meta_archives=zip_paths_meta_archives,state_archives=zip_paths_state_archives,remote_info=remote_info)
 def init(self):
  self.pods_api.init(pod_name=self.pod_name)
 def delete(self,remote:bool)->bool:
  cloud_pods_dir=self.pods_api.config_context.cloud_pods_root_dir
  pod_dir=os.path.join(cloud_pods_dir,self.pod_name)
  if os.path.isdir(pod_dir):
   rm_rf(pod_dir)
   return True
  if remote:
   pass
  return False
 def _push_to_remote(self,url:str):
  auth_headers=get_auth_headers()
  response=safe_requests.put(url=url,headers=auth_headers)
  if response.status_code!=200:
   LOG.warning("Failed to get presigned URLs to upload new version.. aborting")
   return
  content=json.loads(response.content)
  presigned_urls=content.get("presigned_urls")
  self.pods_api.upload_version_and_product_space(presigned_urls=presigned_urls)
 def push(self,comment:str=None,three_way:bool=False)->PodInfo:
  self.pods_api.set_pod_context(self.pod_name)
  self._add_state_to_cloud_pods_store(extract_assets=True)
  if self.pods_api.is_remotely_managed():
   auth_headers=get_auth_headers()
   local_max_ver=self.pods_api.get_max_version_no()
   remote_max_ver=self._get_max_version_for_pod_from_platform(pod_name=self.pod_name,auth_headers=auth_headers)
   if local_max_ver<remote_max_ver:
    self.pull()
   self.pods_api.push(comment=comment)
   url=self.create_platform_url(f"push/{self.pod_name}?version={local_max_ver + 1}")
   self._push_to_remote(url=url)
  else:
   created_version=self.pods_api.push(comment=comment)
   LOG.debug(f"Created new version: {created_version}")
  return PodInfo()
 def push_overwrite(self,version:int,comment:str=None):
  self.pods_api.set_pod_context(pod_name=self.pod_name)
  if version>self.pods_api.get_max_version_no():
   LOG.warning(f"Version {version} does not exist")
   return False
  self._add_state_to_cloud_pods_store()
  self.pods_api.push_overwrite(version=version,comment=comment)
  if self.pods_api.is_remotely_managed():
   url=CloudPodsVersionManager.create_platform_url(f"push-overwrite/{self.pod_name}?version={version}")
   self._push_to_remote(url=url)
  return True
 def pull(self,inject_version_state:bool=False,reset_state_before:bool=False,lazy:bool=False):
  auth_headers=get_auth_headers()
  if self.pod_name in self.pods_api.list_locally_available_pods(show_remote_or_local=False):
   self.pods_api.set_pod_context(self.pod_name)
   remote_max_ver=CloudPodsVersionManager._get_max_version_for_pod_from_platform(self.pod_name,auth_headers)
   if not remote_max_ver:
    return
   current_max_ver=self.pods_api.get_max_version_no()
   if remote_max_ver==current_max_ver:
    LOG.info("No new version available remotely. Nothing to pull")
    return
   if not lazy:
    required_versions=",".join(map(lambda ver:str(ver),range(current_max_ver+1,remote_max_ver+1)))
   else:
    required_versions=current_max_ver
   self._pull_versions(auth_headers=auth_headers,required_versions=required_versions)
  else:
   self._clone_pod(auth_headers=auth_headers,lazy=lazy)
 def commit(self,message:str=None):
  self.pods_api.set_pod_context(self.pod_name)
  self._add_state_to_cloud_pods_store()
  completed_revision=self.pods_api.commit(message=message)
  LOG.debug(f"Completed revision: {completed_revision}")
 def _download_version_product(self,version:int,retain:bool=False)->Dict[str,str]:
  content=self._get_presigned_url_for_version_product(version=version)
  state_url=content.get("presigned_url_state")
  metadata_url=content.get("presigned_url_metadata")
  tmp_state_archive=new_tmp_file()
  tmp_metadata_archive=new_tmp_file()
  download(state_url,tmp_state_archive)
  download(metadata_url,tmp_metadata_archive)
  if retain:
   from localstack_ext.bootstrap.pods.utils.remote_utils import(extract_meta_and_state_archives)
   extract_meta_and_state_archives(meta_archives={version:tmp_metadata_archive},state_archives={version:tmp_state_archive},config_context=self.pods_api.config_context)
  return{"metadata_archive":tmp_metadata_archive,"state_archive":tmp_state_archive}
 def _get_presigned_url_for_version_product(self,version:int)->Optional[Dict]:
  url=self.create_platform_url(f"{self.pod_name}/version/product")
  if version!=-1:
   url+=f"?version={version}"
  auth_headers=get_auth_headers()
  response=safe_requests.get(url,headers=auth_headers)
  if response.status_code>=300:
   LOG.warning(f"Failed to retrieve presigned url from remote for version {version} of pod {self.pod_name}")
   return
  return json.loads(response.content)
 def _inject_from_remote(self,version:int,retain:bool=False)->bool:
  from localstack_ext.bootstrap.pods.utils.remote_utils import extract_meta_and_state_archives
  content=self._get_presigned_url_for_version_product(version=version)
  state_url=content.get("presigned_url_state")
  tmp_state_archive=new_tmp_file()
  download(state_url,tmp_state_archive)
  self.deploy_pod_into_instance(pod_path=tmp_state_archive)
  if not retain:
   rm_rf(tmp_state_archive)
   return True
  metadata_url=content.get("presigned_url_metadata")
  tmp_metadata_archive=new_tmp_file()
  download(metadata_url,tmp_metadata_archive)
  extract_meta_and_state_archives(meta_archives={version:tmp_metadata_archive},state_archives={version:tmp_state_archive},config_context=self.pods_api.config_context)
  return True
 @staticmethod
 def deploy_pod_into_instance(pod_path:str):
  delete_pod_zip=False
  if os.path.isdir(pod_path):
   tmpdir=new_tmp_dir()
   for folder in PERSISTED_FOLDERS:
    src_folder=os.path.join(pod_path,folder)
    if not os.path.exists(src_folder):
     continue
    tgt_folder=os.path.join(tmpdir,folder)
    cp_r(src_folder,tgt_folder,rm_dest_on_conflict=True)
   pod_path=create_zip_file(tmpdir)
   rm_rf(tmpdir)
   delete_pod_zip=True
  zip_content=load_file(pod_path,mode="rb")
  url=get_pods_endpoint()
  result=requests.post(url,data=zip_content)
  if result.status_code>=400:
   raise Exception("Unable to restore pod state via local pods management API %s (code %s): %s"%(url,result.status_code,result.content))
  if delete_pod_zip:
   rm_rf(pod_path)
  else:
   return pod_path
 def inject(self,version:int,reset_state:bool)->bool:
  if not self.pods_api.config_context.pod_exists_locally(self.pod_name):
   LOG.debug(f"Pod {self.pod_name} does not exist locally. Requesting state from remote..")
   state_archive_path=self._download_version_product(version=version).get("state_archive")
  else:
   self.pods_api.set_pod_context(self.pod_name)
   if version==-1:
    version=self.pods_api.get_max_version_no()
   state_archive_path=self.pods_api.config_context.get_version_state_archive(version)
   if not state_archive_path and self.pods_api.is_remotely_managed():
    LOG.debug("Fetching requested archive from remote..")
    product_archive_path=self._download_version_product(version=version,retain=True)
    if not product_archive_path:
     return False
    state_archive_path=self.pods_api.commit_metamodel_utils.get_version_state_archive(version)
  if reset_state:
   reset_local_state(reset_data_dir=True)
  self.deploy_pod_into_instance(state_archive_path)
  return True
 def list_versions(self)->List[str]:
  self.pods_api.set_pod_context(self.pod_name)
  version_list=self.pods_api.list_versions()
  return version_list
 def version_info(self,version:int):
  self.pods_api.set_pod_context(self.pod_name)
  if version==-1:
   version=self.pods_api.get_max_version_no()
  version_info=self.pods_api.get_version_info(version)
  return version_info
 def version_metamodel(self,version:int)->Dict:
  from localstack_ext.bootstrap.pods.object_storage import get_object_storage_provider
  self.pods_api.set_pod_context(self.pod_name)
  if version==-1:
   version=self.pods_api.get_max_version_no()
  version_vertex=self.pods_api.get_version_by_number(version)
  object_storage=get_object_storage_provider(self.pods_api.config_context)
  final_revision=object_storage.get_revision_by_key(version_vertex.incoming_revision_ptr)
  result=self.pods_api.commit_metamodel_utils.reconstruct_metamodel(version=version,revision=final_revision.revision_number+1)
  if not result and self.pods_api.is_remotely_managed():
   self._download_version_product(version=version,retain=True)
   result=self.pods_api.commit_metamodel_utils.create_metamodel_from_state_files(version=version)
  return result
 def set_version(self,version:int,inject_version_state:bool,reset_state:bool,commit_before:bool)->bool:
  self.pods_api.set_pod_context(self.pod_name)
  version_exists=self.pods_api.set_active_version(version_no=version,commit_before=commit_before)
  if not version_exists:
   LOG.warning(f"Could not find version {version}")
  if inject_version_state:
   self.inject(version=version,reset_state=reset_state)
  return version_exists
 def list_version_commits(self,version:int)->List[str]:
  self.pods_api.set_pod_context(self.pod_name)
  commits=self.pods_api.list_version_commits(version_no=version)
  return commits
 def get_commit_diff(self,version:int,commit:int)->Dict:
  self.pods_api.set_pod_context(self.pod_name)
  commit_diff=self.pods_api.commit_metamodel_utils.get_commit_diff(version_no=version,commit_no=commit)
  return commit_diff
 def register_remote(self,pod_name:str,ci_pod:bool=False)->bool:
  self.pods_api.set_pod_context(self.pod_name)
  max_ver=self.pods_api.get_max_version_no()
  if max_ver==0:
   self.pods_api.push("Init Version")
   max_ver=1
  auth_headers=get_auth_headers()
  url=self.create_platform_url("register")
  data={"pod_name":self.pod_name,"max_ver":max_ver,"ci_pod":ci_pod}
  data=json.dumps(data)
  response=safe_requests.post(url,data,headers=auth_headers)
  if response.status_code!=200:
   LOG.warning(f"Failed to register pod {self.pod_name}: {response.content}")
   return False
  content=json.loads(response.content)
  remote_info={"storage_uuid":content.get("storage_uuid"),"qualifying_name":content.get("pod_name")}
  presigned_urls=content.get("presigned_urls")
  self.pods_api.upload_version_and_product_space(presigned_urls=presigned_urls)
  pods_api.register_remote(remote_info=remote_info,config_context=self.pods_api.config_context)
  return True
 def rename_pod(self,current_pod_name,new_pod_name)->bool:
  self.pods_api.set_pod_context(current_pod_name)
  if new_pod_name in self.pods_api.list_locally_available_pods():
   LOG.warning(f"{new_pod_name} already exists locally")
   return False
  if self.pods_api.is_remotely_managed():
   auth_headers=get_auth_headers()
   url=self.create_platform_url(f"{current_pod_name}/rename")
   data={"new_pod_name":new_pod_name}
   data=json.dumps(data)
   response=safe_requests.put(url,data,headers=auth_headers)
   if response.status_code!=200:
    LOG.warning(f"Failed to rename {current_pod_name} to {new_pod_name}: {response.content}")
    return False
  self.pods_api.rename_pod(new_pod_name)
  return True
 def list_pods(self,fetch_remote:bool)->Set[str]:
  result=self.pods_api.list_locally_available_pods()
  if fetch_remote:
   auth_headers=get_auth_headers()
   url=self.create_platform_url("pods")
   response=safe_requests.get(url,headers=auth_headers)
   content=json.loads(response.content)
   for remote_pod in content.get("registered_pods")or[]:
    result.add(f"remote/{remote_pod}")
  return result
 @staticmethod
 def create_platform_url(request:str)->str:
  base_url="%s/cpvcs"%constants.API_ENDPOINT
  return os.path.join(base_url,request)
class PodConfigManagerMeta(type):
 def __getattr__(cls,attr):
  def _call(*args,**kwargs):
   result=None
   for manager in cls.CHAIN:
    try:
     tmp=getattr(manager,attr)(*args,**kwargs)
     if tmp:
      if not result:
       result=tmp
      elif isinstance(tmp,list)and isinstance(result,list):
       result.extend(tmp)
    except Exception:
     if LOG.isEnabledFor(logging.DEBUG):
      LOG.exception("error during PodConfigManager call chain")
   if result is not None:
    return result
   raise Exception('Unable to run operation "%s" for local or remote configuration'%attr)
  return _call
class PodConfigManager(object,metaclass=PodConfigManagerMeta):
 CHAIN=[]
 @classmethod
 def pod_config(cls,pod_name):
  pods=PodConfigManager.list_pods()
  pod_config=[pod for pod in pods if pod["pod_name"]==pod_name]
  if not pod_config:
   raise Exception('Unable to find config for pod named "%s"'%pod_name)
  return pod_config[0]
ALL_MANAGERS={"cpvcs":CloudPodsVersionManager}
def get_pods_manager(pods_name:str,pre_config=None)->CloudPodsManager:
 if pre_config is None:
  pre_config={"backend":"cpvcs"}
 backend=pre_config.get("backend","cpvcs")
 try:
  manager=ALL_MANAGERS[backend](pod_name=pods_name,pre_config=pre_config)
 except KeyError as err:
  raise NotImplementedError from err
 return manager
def init_cloudpods(pod_name:str,pre_config:Dict[str,str],**kwargs):
 backend=get_pods_manager(pods_name=pod_name)
 backend.init()
def delete_pod(pod_name:str,remote:bool,pre_config:Dict[str,str])->bool:
 backend=get_pods_manager(pods_name=pod_name)
 result=backend.delete(remote=remote)
 return result
def register_remote(pod_name:str,pre_config:Dict[str,str],**kwargs)->bool:
 backend=get_pods_manager(pods_name=pod_name)
 result=backend.register_remote(pod_name=pod_name,ci_pod=pre_config.get("ci_pod",False))
 return result
def rename_pod(current_pod_name:str,new_pod_name:str,pre_config:Dict[str,str],**kwargs):
 backend=get_pods_manager(pods_name=new_pod_name)
 result=backend.rename_pod(current_pod_name=current_pod_name,new_pod_name=new_pod_name)
 return result
def list_pods(remote:bool,pre_config:Dict[str,str],**kwargs)->List[str]:
 backend=get_pods_manager(pods_name="")
 result=backend.list_pods(fetch_remote=remote)
 return result
def commit_state(pod_name:str,pre_config:Dict[str,str],message:str=None,**kwargs):
 backend=get_pods_manager(pods_name=pod_name)
 backend.pods_api.set_pod_context(pod_name=pod_name)
 if not backend.pods_api.config_context.is_initialized():
  backend.init()
 backend.commit(message=message)
def inject_state(pod_name:str,version:int,reset_state:bool,pre_config:Dict[str,str],**kwargs):
 backend=get_pods_manager(pods_name=pod_name)
 result=backend.inject(version=version,reset_state=reset_state)
 return result
def list_versions(pod_name:str,pre_config:Dict[str,str],**kwargs)->List[str]:
 backend=get_pods_manager(pods_name=pod_name)
 versions=backend.list_versions()
 return versions
def get_version_info(version:int,pod_name:str,pre_config:Dict[str,str],**kwargs):
 backend=get_pods_manager(pods_name=pod_name)
 info=backend.version_info(version=version)
 return info
def get_version_metamodel(version:int,pod_name:str,pre_config:Dict[str,str],**kwargs)->Dict:
 backend=get_pods_manager(pods_name=pod_name)
 metamodel=backend.version_metamodel(version=version)
 return metamodel
def set_version(version:int,inject_version_state:bool,reset_state:bool,commit_before:bool,pod_name:str,pre_config:Dict[str,str],**kwargs)->bool:
 backend=get_pods_manager(pods_name=pod_name)
 success=backend.set_version(version=version,inject_version_state=inject_version_state,reset_state=reset_state,commit_before=commit_before)
 return success
def list_version_commits(version:int,pod_name:str,pre_config:Dict[str,str])->List[str]:
 backend=get_pods_manager(pods_name=pod_name)
 commits=backend.list_version_commits(version=version)
 return commits
def get_commit_diff(version:int,commit:int,pod_name:str,pre_config:Dict[str,str])->Dict:
 backend=get_pods_manager(pods_name=pod_name)
 commit_diff=backend.get_commit_diff(version=version,commit=commit)
 return commit_diff
def push_overwrite(version:int,pod_name:str,comment:str,pre_config:Dict[str,str]):
 backend=get_pods_manager(pods_name=pod_name)
 backend.push_overwrite(version=version,comment=comment)
def push_state(pod_name,pre_config=None,squash_commits=False,comment=None,three_way=False,register:bool=False,**kwargs)->bool:
 backend=get_pods_manager(pods_name=pod_name)
 backend.pods_api.set_pod_context(pod_name=pod_name)
 if not backend.pods_api.config_context.is_initialized():
  backend.init()
 pod_config=clone(backend.pod_config)
 pod_info=backend.push(comment=comment,three_way=three_way)
 pod_config["size"]=pod_info.pod_size or pod_info.pod_size_compressed
 pod_config["available_resources"]=pod_info.persisted_resource_names
 result=True
 if register:
  result&=backend.register_remote(pod_name=pod_name,ci_pod=pre_config.get("ci_pod",False))
 return result
def get_pods_endpoint():
 edge_url=config.get_edge_url()
 return f"{edge_url}{API_PATH_PODS}"
def pull_state(pod_name,inject_version_state=False,reset_state_before=False,lazy=False,**kwargs):
 if not pod_name:
  raise Exception("Need to specify a pod name")
 backend=get_pods_manager(pods_name=pod_name)
 backend.pull(inject_version_state=inject_version_state,reset_state_before=reset_state_before,lazy=lazy)
 print("Done.")
def reset_local_state(reset_data_dir=False,exclude_from_reset:List[str]=None):
 url=f"{get_pods_endpoint()}/state"
 if reset_data_dir:
  url+="/datadir"
 if exclude_from_reset:
  url+=f"?exclude={','.join(exclude_from_reset)}"
 print("Sending request to reset the service states in local instance ...")
 result=requests.delete(url)
 if result.status_code>=400:
  raise Exception("Unable to reset service state via local management API %s (code %s): %s"%(url,result.status_code,result.content))
 print("Done.")
def save_pods_config(options:Dict):
 backend=get_pods_manager("")
 backend.pods_api.config_context.save_pods_config(options=options)
def get_pods_config():
 backend=get_pods_manager("")
 return backend.pods_api.config_context.get_pods_config_cache()
def is_initialized(pod_name:str)->bool:
 backend=get_pods_manager(pods_name=pod_name)
 return backend.pods_api.config_context.is_initialized()
def get_data_dir_from_container()->str:
 try:
  details=DOCKER_CLIENT.inspect_container(config.MAIN_CONTAINER_NAME)
  mounts=details.get("Mounts")
  env=details.get("Config",{}).get("Env",[])
  data_dir_env=[e for e in env if e.startswith("DATA_DIR=")][0].partition("=")[2]
  try:
   data_dir_host=[m for m in mounts if m["Destination"]==data_dir_env][0]["Source"]
   data_dir_host=re.sub(r"^(/host_mnt)?",r"",data_dir_host)
   data_dir_env=data_dir_host
  except Exception:
   LOG.debug(f"No docker volume for data dir '{data_dir_env}' detected")
  return data_dir_env
 except Exception:
  LOG.warning('''Unable to determine DATA_DIR from LocalStack Docker container - please make sure $MAIN_CONTAINER_NAME is configured properly''')
def get_persisted_resource_names(data_dir)->List[str]:
 names=[]
 with os.scandir(data_dir)as entries:
  for entry in entries:
   if entry.is_dir()and entry.name!="api_states":
    names.append(entry.name)
 with os.scandir(os.path.join(data_dir,"api_states"))as entries:
  for entry in entries:
   if entry.is_dir()and len(os.listdir(entry.path))>0:
    names.append(entry.name)
 LOG.debug(f"Detected state files for the following APIs: {names}")
 return names
PODS_NAMESPACE_DELIM="-"
# Created by pyminifier (https://github.com/liftoff/pyminifier)
