import json
import logging
import os
import shutil
import zipfile
from typing import Dict,List,Optional,Set,Tuple,Union
from localstack import config as localstack_config
from localstack.constants import TEST_AWS_ACCOUNT_ID
from localstack.utils.common import cp_r,mkdir,rm_rf,save_file,short_uid,to_str
from localstack.utils.http import safe_requests
from localstack_ext.bootstrap.pods.constants import(CLOUD_PODS_DIR,COMPRESSION_FORMAT,DEFAULT_POD_DIR,NIL_PTR,STATE_ZIP,VER_SYMLINK,VERSION_SERVICE_INFO_FILE,VERSION_SPACE_ARCHIVE)
from localstack_ext.bootstrap.pods.models import(Commit,Revision,Serialization,StateFileRef,Version)
from localstack_ext.bootstrap.pods.object_storage import get_object_storage_provider
from localstack_ext.bootstrap.pods.utils.common import(PodsConfigContext,read_file_from_archive,zip_directories)
from localstack_ext.bootstrap.pods.utils.hash_utils import(compute_file_hash,compute_revision_hash,compute_version_archive_hash,random_hash)
from localstack_ext.bootstrap.pods.utils.merge_utils import(CloudPodsMergeManager,create_tmp_archives_by_serialization_mechanism)
from localstack_ext.bootstrap.pods.utils.metamodel_utils import(CommitMetamodelUtils,MetamodelDelta,MetamodelDeltaMethod)
from localstack_ext.bootstrap.pods.utils.remote_utils import(extract_meta_and_state_archives,merge_version_space,register_remote)
from localstack_ext.bootstrap.state_utils import(API_STATES_DIR,DYNAMODB_DIR,KINESIS_DIR,persist_object)
LOG=logging.getLogger(__name__)
ROOT_DIR_LOOKUP={str(Serialization.KINESIS):KINESIS_DIR,str(Serialization.DDB):DYNAMODB_DIR,str(Serialization.MAIN):API_STATES_DIR}
class PodsApi:
 def __init__(self):
  pod_root_dir=os.environ.get("POD_DIR")
  if not pod_root_dir:
   pod_root_dir=os.path.join(localstack_config.dirs.tmp,DEFAULT_POD_DIR)
  pod_root_dir=os.path.join(pod_root_dir,CLOUD_PODS_DIR)
  self.config_context=PodsConfigContext(pod_root_dir)
  self.object_storage=get_object_storage_provider(self.config_context)
  self.commit_metamodel_utils=CommitMetamodelUtils(self.config_context)
 def init(self,pod_name:str="My-Pod"):
  if self.config_context.pod_exists_locally(pod_name=pod_name):
   LOG.warning(f"Pod with name {pod_name} already exists locally")
   return
  self.config_context.set_pod_context(pod_name)
  def _create_internal_fs():
   mkdir(self.config_context.get_pod_root_dir())
   mkdir(self.config_context.get_ver_refs_path())
   mkdir(self.config_context.get_rev_refs_path())
   mkdir(self.config_context.get_ver_obj_store_path())
   mkdir(self.config_context.get_rev_obj_store_path())
   mkdir(self.config_context.get_delta_log_path())
  _create_internal_fs()
  r0_hash=random_hash()
  v0_hash=random_hash()
  r0=Revision(hash_ref=r0_hash,parent_ptr=NIL_PTR,creator=self.config_context.get_context_user(),rid=short_uid(),revision_number=0,state_files=set())
  v0=Version(hash_ref=v0_hash,parent_ptr=NIL_PTR,creator=self.config_context.get_context_user(),comment="Init version",active_revision_ptr=r0_hash,outgoing_revision_ptrs={r0_hash},incoming_revision_ptr=None,state_files=set(),version_number=0)
  rev_key,ver_key=self.object_storage.upsert_objects(r0,v0)
  ver_symlink=self.config_context.create_version_symlink(VER_SYMLINK.format(ver_no=v0.version_number),ver_key)
  with open(self.config_context.get_head_path(),"w")as fp:
   fp.write(ver_symlink)
  with open(self.config_context.get_max_ver_path(),"w")as fp:
   fp.write(ver_symlink)
  with open(self.config_context.get_known_ver_path(),"w")as fp:
   fp.write(ver_symlink)
  self.config_context.update_ver_log(author=self.config_context.get_context_user(),ver_no=v0.version_number,rev_id=r0.rid,rev_no=r0.revision_number)
  LOG.debug(f"Successfully initiated CloudPods for pod at {self.config_context.get_pod_root_dir()}")
 def init_remote(self,version_space_archive:str,meta_archives:Dict[int,str],state_archives:Dict[int,str],remote_info:Dict[str,str],pod_name:str):
  self.config_context.set_pod_context(pod_name=pod_name)
  mkdir(self.config_context.get_pod_root_dir())
  with zipfile.ZipFile(version_space_archive)as version_space_zip:
   version_space_zip.extractall(self.config_context.get_pod_root_dir())
   LOG.debug("Successfully extracted version space zip")
  rm_rf(version_space_archive)
  extract_meta_and_state_archives(meta_archives=meta_archives,state_archives=state_archives,config_context=self.config_context)
  max_ver=self._get_max_version()
  ver_symlink=self.config_context.create_version_symlink(name=VER_SYMLINK.format(ver_no=max_ver.version_number))
  with open(self.config_context.get_head_path(),"w")as fp:
   fp.write(ver_symlink)
  register_remote(remote_info=remote_info,config_context=self.config_context)
 def commit(self,message:str=None)->Revision:
  curr_expansion_point,head_version=self._get_expansion_point_with_head()
  curr_expansion_point_hash=compute_revision_hash(curr_expansion_point,self.config_context.get_obj_store_path())
  curr_expansion_point_parent_state_files=set()
  if curr_expansion_point.parent_ptr!=NIL_PTR:
   referenced_by_version=None
   curr_expansion_point_parent=self.object_storage.get_revision_by_key(curr_expansion_point.parent_ptr)
   curr_expansion_point_parent_state_files=curr_expansion_point_parent.state_files
   curr_expansion_point_parent.assoc_commit.head_ptr=curr_expansion_point_hash
   self.object_storage.upsert_objects(curr_expansion_point_parent)
  else:
   referenced_by_version=head_version.hash_ref
  self.object_storage.update_revision_key(old_key=curr_expansion_point.hash_ref,new_key=curr_expansion_point_hash,referenced_by_version=referenced_by_version)
  curr_expansion_point.hash_ref=curr_expansion_point_hash
  new_expansion_point=Revision(hash_ref=random_hash(),state_files=set(),parent_ptr=curr_expansion_point_hash,creator=curr_expansion_point.creator,rid=short_uid(),revision_number=curr_expansion_point.revision_number+1)
  delta_log_ptr=self.create_delta_log(curr_expansion_point_parent_state_files,curr_expansion_point.state_files)
  assoc_commit=Commit(tail_ptr=curr_expansion_point.hash_ref,head_ptr=new_expansion_point.hash_ref,message=message,delta_log_ptr=delta_log_ptr)
  curr_expansion_point.assoc_commit=assoc_commit
  self.object_storage.upsert_objects(new_expansion_point,curr_expansion_point)
  self.config_context.update_ver_log(author=new_expansion_point.creator,ver_no=head_version.version_number,rev_id=new_expansion_point.rid,rev_no=new_expansion_point.revision_number)
  return curr_expansion_point
 def merge_from_remote(self,version_space_archive:str,meta_archives:Dict[int,str],state_archives:Dict[int,str]):
  merge_version_space(version_space_archive,config_context=self.config_context)
  extract_meta_and_state_archives(meta_archives=meta_archives,state_archives=state_archives,config_context=self.config_context)
 def is_remotely_managed(self)->bool:
  return self.config_context.is_remotely_managed()
 def rename_pod(self,new_pod_name:str)->bool:
  if self.config_context.pod_exists_locally(new_pod_name):
   LOG.warning(f"{new_pod_name} already exists locally")
   return False
  self.config_context.rename_pod(new_pod_name)
  return True
 def list_locally_available_pods(self,show_remote_or_local:bool=True)->Set[str]:
  mkdir(self.config_context.cloud_pods_root_dir)
  available_pods=[p for p in os.listdir(self.config_context.cloud_pods_root_dir)if not p.endswith(".json")]
  if not show_remote_or_local:
   return set(available_pods)
  result=set()
  for available_pod in available_pods:
   pod_name=(f"remote/{available_pod}" if self.config_context.is_remotely_managed(available_pod)else f"local/{available_pod}")
   result.add(pod_name)
  return result
 def push(self,comment:str=None,three_way:bool=False,include_assets:bool=True)->Version:
  expansion_point,head_version=self._get_expansion_point_with_head()
  max_version=self._get_max_version()
  new_active_revision=Revision(hash_ref=random_hash(),state_files=set(),parent_ptr=NIL_PTR,creator=expansion_point.creator,rid=short_uid(),revision_number=0)
  new_max_version_no=max_version.version_number+1
  if head_version.version_number!=max_version.version_number:
   self.merge_expansion_point_with_max(three_way=three_way)
  else:
   self._create_state_directory(new_max_version_no,state_file_refs=expansion_point.state_files)
  new_version=Version(hash_ref=compute_version_archive_hash(new_max_version_no,self.config_context.get_version_state_archive(new_max_version_no)),state_files=set(),parent_ptr=max_version.hash_ref,creator=expansion_point.creator,comment=comment,active_revision_ptr=new_active_revision.hash_ref,outgoing_revision_ptrs={new_active_revision.hash_ref},incoming_revision_ptr=expansion_point.hash_ref,version_number=new_max_version_no)
  if expansion_point.parent_ptr!=NIL_PTR:
   expansion_point_parent=self.object_storage.get_revision_by_key(expansion_point.parent_ptr)
   state_from=expansion_point_parent.state_files
   delta_log_ptr=self.create_delta_log(state_from,new_version.state_files)
  else:
   delta_log_ptr=self.create_delta_log(expansion_point.state_files,set())
  expansion_point_commit=Commit(tail_ptr=expansion_point.hash_ref,head_ptr=new_version.hash_ref,message="Finalizing commit",delta_log_ptr=delta_log_ptr)
  expansion_point.state_files=new_version.state_files
  expansion_point.assoc_commit=expansion_point_commit
  head_version.active_revision_ptr=NIL_PTR
  self.object_storage.upsert_objects(head_version,expansion_point,new_active_revision,new_version)
  self._update_head(new_version.version_number,new_version.hash_ref)
  self._update_max_ver(new_version.version_number,new_version.hash_ref)
  self._add_known_ver(new_version.version_number,new_version.hash_ref)
  if include_assets:
   self._add_assets_to_version_state_archive(new_version.version_number)
  self.commit_metamodel_utils.create_metadata_archive(new_version)
  self.config_context.update_ver_log(author=expansion_point.creator,ver_no=new_version.version_number,rev_id=new_active_revision.rid,rev_no=new_active_revision.revision_number)
  return new_version
 def set_pod_context(self,pod_name:str):
  self.config_context.set_pod_context(pod_name)
 def create_state_file_from_fs(self,path:str,file_name:str,service:str,region:str,root:str,serialization:Serialization,account_id=TEST_AWS_ACCOUNT_ID)->str:
  file_path=os.path.join(path,file_name)
  key=compute_file_hash(file_path)
  rel_path=path.split(f"{root}/")
  if len(rel_path)>1:
   rel_path=rel_path[1]
  else:
   rel_path=""
  shutil.copy(file_path,os.path.join(self.config_context.get_obj_store_path(),key))
  state_file=StateFileRef(hash_ref=key,rel_path=rel_path,file_name=file_name,size=os.path.getsize(file_path),service=service,region=region,account_id=account_id,serialization=serialization)
  self._add_state_file_to_expansion_point(state_file)
  return key
 def _create_state_file_from_in_memory_blob(self,blob)->str:
  tmp_file_name=random_hash()
  tmp_dest=os.path.join(self.config_context.get_obj_store_path(),tmp_file_name)
  persist_object(blob,tmp_dest)
  key=compute_file_hash(tmp_dest)
  dest=os.path.join(self.config_context.get_obj_store_path(),key)
  os.rename(tmp_dest,dest)
  return key
 def _get_state_file_path(self,key:str)->str:
  file_path=os.path.join(self.config_context.get_obj_store_path(),key)
  if os.path.isfile(file_path):
   return file_path
  LOG.warning(f"No state file with found with key: {key}")
 def _add_state_file_to_expansion_point(self,state_file:StateFileRef):
  revision,_=self._get_expansion_point_with_head()
  updated_state_files=set(filter(lambda sf:not sf.congruent(state_file),revision.state_files))
  updated_state_files.add(state_file)
  revision.state_files=updated_state_files
  self.object_storage.upsert_objects(revision)
 def list_state_files(self,key:str)->Optional[str]:
  pods_object=self.object_storage.get_revision_or_version_by_key(key)
  if pods_object:
   return pods_object.state_files_info()
  LOG.debug(f"No Version or Revision associated to {key}")
 def get_version_info(self,version_no:int)->Union[Dict[str,str],None]:
  archive_path=self.config_context.get_version_meta_archive(version_no)
  if not archive_path:
   LOG.warning(f"No Info found for version {version_no}")
   return
  result=read_file_from_archive(archive_path,VERSION_SERVICE_INFO_FILE)
  result=json.loads(to_str(result or "{}"))
  return result
 def create_version_space_archive(self)->str:
  zip_dest=os.path.join(self.config_context.get_pod_root_dir(),VERSION_SPACE_ARCHIVE)
  rm_rf(zip_dest)
  result=zip_directories(zip_dest=zip_dest,directories=self.config_context.get_version_space_dir_paths())
  with zipfile.ZipFile(result,"a")as archive:
   for version_space_file in self.config_context.get_version_space_file_paths():
    archive.write(version_space_file,arcname=os.path.basename(version_space_file))
  return result
 def get_head(self)->Version:
  return self.object_storage.get_version_by_key(self.config_context.get_head_key())
 def _get_max_version(self)->Version:
  return self.object_storage.get_version_by_key(self.config_context.get_max_ver_key())
 def get_max_version_no(self)->int:
  with open(self.config_context.get_max_ver_path())as fp:
   return int(os.path.basename(fp.readline()))
 def _get_expansion_point_with_head(self)->Tuple[Revision,Version]:
  head_version=self.get_head()
  active_revision_root=self.object_storage.get_revision_by_key(key=head_version.active_revision_ptr)
  expansion_point=self.object_storage.get_terminal_revision(revision_path_root=active_revision_root)
  return expansion_point,head_version
 def push_overwrite(self,version:int,comment:str)->bool:
  expansion_point,_=self._get_expansion_point_with_head()
  if version>self.get_max_version_no():
   LOG.debug("Attempted to overwrite a non existing version.. Aborting")
   return False
  version_node=self.get_version_by_number(version)
  self._create_state_directory(version_number=version,state_file_refs=expansion_point.state_files)
  metamodels_file=self.config_context.metamodel_file(expansion_point.revision_number)
  self.commit_metamodel_utils.create_metadata_archive(version_node,overwrite=True,metamodels_file=metamodels_file)
  version_node.comment=comment
  self.object_storage.upsert_objects(version_node)
  return True
 def _add_assets_to_version_state_archive(self,version_number:int,cleanup:bool=True):
  archive_path=self.config_context.get_version_state_archive_path(version=version_number)
  assets_path=self.config_context.get_assets_root_path()
  with zipfile.ZipFile(archive_path,"a")as archive:
   for folder_name,subfolders,file_names in os.walk(assets_path):
    for file in file_names:
     path=os.path.join(folder_name,file)
     archive.write(filename=path,arcname=os.path.relpath(path,start=self.config_context.get_pod_root_dir()))
  if cleanup:
   rm_rf(assets_path)
 @staticmethod
 def _get_dst_path_for_state_file(version_state_dir:str,state_file:StateFileRef):
  if state_file.serialization in[str(Serialization.KINESIS),str(Serialization.DDB)]:
   dst_path=os.path.join(version_state_dir,ROOT_DIR_LOOKUP[state_file.serialization])
  else:
   dst_path=os.path.join(version_state_dir,ROOT_DIR_LOOKUP[state_file.serialization],state_file.rel_path)
  mkdir(dst_path)
  return dst_path
 def _create_state_directory(self,version_number:int,state_file_refs:Set[StateFileRef],delete_files=False,archive=True):
  version_state_dir=os.path.join(self.config_context.get_pod_root_dir(),STATE_ZIP.format(version_no=version_number))
  mkdir(version_state_dir)
  for state_file in state_file_refs:
   try:
    dst_path=self._get_dst_path_for_state_file(version_state_dir,state_file)
    src=self.object_storage.get_state_file_location_by_key(state_file.hash_ref)
    dst=os.path.join(dst_path,state_file.file_name)
    shutil.copy(src,dst)
    if delete_files:
     os.remove(src)
   except Exception as e:
    LOG.warning(f"Failed to locate state file with rel path: {state_file.rel_path}: {e}")
  if archive:
   shutil.make_archive(version_state_dir,COMPRESSION_FORMAT,root_dir=version_state_dir)
   rm_rf(version_state_dir)
   return f"{version_state_dir}.{COMPRESSION_FORMAT}"
  return version_state_dir
 def set_active_version(self,version_no:int,commit_before=False)->bool:
  known_versions=self.load_version_references()
  for known_version_no,known_version_key in known_versions:
   if known_version_no==version_no:
    if commit_before:
     self.commit()
    self._set_active_version(known_version_key)
    return True
  LOG.info(f"Version with number {version_no} not found")
  return False
 def _set_active_version(self,key:str):
  current_head=self.get_head()
  if current_head.hash_ref!=key and self.object_storage.version_exists(key):
   requested_version=self.object_storage.get_version_by_key(key)
   self._update_head(requested_version.version_number,key)
   if requested_version.active_revision_ptr==NIL_PTR:
    new_path_root=Revision(hash_ref=random_hash(),state_files=set(),parent_ptr=NIL_PTR,creator=self.config_context.get_context_user(),rid=short_uid(),revision_number=0)
    requested_version.active_revision_ptr=new_path_root.hash_ref
    requested_version.outgoing_revision_ptrs.add(new_path_root.hash_ref)
    self.object_storage.upsert_objects(new_path_root,requested_version)
 def get_version_by_number(self,version_no:int)->Union[Version,None]:
  versions=self.load_version_references()
  version_ref=next((version[1]for version in versions if version[0]==version_no),None)
  if not version_ref:
   LOG.warning(f"Could not find version number {version_no}")
   return
  return self.object_storage.get_version_by_key(version_ref)
 def load_version_references(self)->List[Tuple[int,str]]:
  result={}
  with open(self.config_context.get_known_ver_path(),"r")as vp:
   symlinks=vp.readlines()
   for symlink in symlinks:
    symlink=self.config_context.get_pod_absolute_path(symlink.rstrip())
    with open(symlink,"r")as sp:
     result[int(os.path.basename(symlink))]=sp.readline()
  return sorted(result.items(),key=lambda x:x[0],reverse=True)
 def list_versions(self)->List[str]:
  version_references=self.load_version_references()
  result=[self.object_storage.get_version_by_key(version_key).info_str()for _,version_key in version_references]
  return result
 def list_version_commits(self,version_no:int)->List[str]:
  if version_no==-1:
   version=self._get_max_version()
  else:
   version=self.get_version_by_number(version_no)
  if not version:
   return[]
  result=[]
  revision=self.object_storage.get_revision_by_key(version.incoming_revision_ptr)
  while revision:
   assoc_commit=revision.assoc_commit
   revision_no=revision.revision_number
   if revision_no!=0:
    from_node=f"Revision-{revision_no - 1}"
   elif version_no!=0:
    from_node=f"Version-{version_no}"
   else:
    from_node="Empty state"
   to_node=f"Revision-{revision_no}"
   result.append(assoc_commit.info_str(from_node=from_node,to_node=to_node))
   revision=self.object_storage.get_revision_by_key(revision.parent_ptr)
  return result
 def _update_head(self,new_head_ver_no,new_head_key)->str:
  with open(self.config_context.get_head_path(),"w")as fp:
   ver_symlink=self.config_context.create_version_symlink(VER_SYMLINK.format(ver_no=new_head_ver_no),new_head_key)
   fp.write(ver_symlink)
   return ver_symlink
 def _update_max_ver(self,new_max_ver_no,new_max_ver_key)->str:
  with open(self.config_context.get_max_ver_path(),"w")as fp:
   max_ver_symlink=self.config_context.create_version_symlink(VER_SYMLINK.format(ver_no=new_max_ver_no),new_max_ver_key)
   fp.write(max_ver_symlink)
   return max_ver_symlink
 def _add_known_ver(self,new_ver_no,new_ver_key)->str:
  with open(self.config_context.get_known_ver_path(),"a")as fp:
   new_ver_symlink=self.config_context.create_version_symlink(VER_SYMLINK.format(ver_no=new_ver_no),new_ver_key)
   fp.write(f"\n{new_ver_symlink}")
   return new_ver_symlink
 def merge_expansion_point_with_max(self,three_way=False):
  expansion_point,head=self._get_expansion_point_with_head()
  curr_max_version_no=self.get_max_version_no()
  new_version_no=curr_max_version_no+1
  new_version_state_archive=self._create_state_directory(version_number=new_version_no,state_file_refs=expansion_point.state_files)
  max_version_state_archive=self.config_context.get_version_state_archive(curr_max_version_no)
  if head.version_number<2:
   three_way=False
  if three_way:
   lca_state_archive=self.config_context.get_version_state_archive(head.version_number-1)
   lca_tmp_dirs=create_tmp_archives_by_serialization_mechanism(lca_state_archive)
  else:
   lca_tmp_dirs={}
  new_version_tmp_dirs=create_tmp_archives_by_serialization_mechanism(new_version_state_archive)
  max_version_tmp_dirs=create_tmp_archives_by_serialization_mechanism(max_version_state_archive)
  for serialization_mechanism,new_version_state_files_path in new_version_tmp_dirs.items():
   try:
    merge_manager=CloudPodsMergeManager.get(serialization_mechanism,raise_if_missing=True)
    lca_state_files_path=lca_tmp_dirs.get(serialization_mechanism)
    max_version_files_path=max_version_tmp_dirs.get(serialization_mechanism)
    if not max_version_files_path:
     LOG.warning("No merge performed for %s serialized state files",serialization_mechanism)
     continue
    if lca_state_files_path and three_way:
     merge_manager.three_way_merge(common_ancestor_state_files=lca_state_files_path,from_state_files=max_version_files_path,to_state_files=new_version_state_files_path)
    else:
     merge_manager.two_way_merge(from_state_files=new_version_state_files_path,to_state_files=max_version_files_path)
   except Exception as e:
    LOG.warning("Failed to perform merge for %s: %s",serialization_mechanism,e)
  shutil.make_archive(base_name=os.path.splitext(new_version_state_archive)[0],format=COMPRESSION_FORMAT,root_dir=new_version_tmp_dirs["root"])
 def add_assets_to_pod(self,assets_root_paths:List[str]):
  for assets_root_path in assets_root_paths:
   pod_asset_root=os.path.join(self.config_context.get_assets_root_path(),os.path.basename(assets_root_path))
   try:
    cp_r(src=assets_root_path,dst=pod_asset_root)
   except Exception as e:
    LOG.warning("Failed to copy assets for %s: %s",assets_root_path,e)
 def create_delta_log(self,state_from:Set[StateFileRef],state_to:Set[StateFileRef],diff_method:MetamodelDeltaMethod=MetamodelDeltaMethod.SIMPLE)->str:
  try:
   delta_manager=MetamodelDelta.get(diff_method)
   return delta_manager.create_delta_log(state_from,state_to,self.config_context)
  except Exception as e:
   LOG.debug("Unable to create delta log for version graph nodes: %s",e)
   key=short_uid()
   dest=os.path.join(self.config_context.get_delta_log_path(),key)
   save_file(dest,"{}")
   return key
 def upload_version_and_product_space(self,presigned_urls):
  def upload_content(pre_signed_url:str,zip_data_content):
   res=safe_requests.put(pre_signed_url,data=zip_data_content)
   if res.status_code>=400:
    raise Exception(f"Unable to upload pod state to S3 (code {res.status_code}): {res.content}")
   return res
  presigned_version_space_url=presigned_urls.get("presigned_version_space_url")
  version_space_archive=self.create_version_space_archive()
  with open(version_space_archive,"rb")as version_space_content:
   upload_content(presigned_version_space_url,version_space_content.read())
  presigned_meta_state_urls=presigned_urls.get("presigned_meta_state_urls")
  rm_rf(version_space_archive)
  for version_no,urls in presigned_meta_state_urls.items():
   meta_presigned_url=urls["meta"]
   meta_archive=self.config_context.get_version_meta_archive(version_no)
   with open(meta_archive,"rb")as meta_archive_content:
    upload_content(meta_presigned_url,meta_archive_content)
   state_presigned_url=urls["state"]
   state_archive=self.config_context.get_version_state_archive(version_no)
   with open(state_archive,"rb")as state_archive_content:
    upload_content(state_presigned_url,state_archive_content)
# Created by pyminifier (https://github.com/liftoff/pyminifier)
