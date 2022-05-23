from datetime import datetime
from enum import Enum
from typing import Set
from localstack_ext.bootstrap.pods.constants import(COMMIT_TXT_LAYOUT,REV_TXT_LAYOUT,STATE_TXT_LAYOUT,STATE_TXT_METADATA,VER_TXT_LAYOUT)
from localstack_ext.bootstrap.state_utils import API_STATES_DIR,DYNAMODB_DIR,KINESIS_DIR
class PodObject:
 def __init__(self,hash_ref:str):
  self.hash_ref:str=hash_ref
class Serialization(Enum):
 MAIN=API_STATES_DIR
 DDB=DYNAMODB_DIR
 KINESIS=KINESIS_DIR
 serializer_root_lookup={str(MAIN):API_STATES_DIR,str(DDB):DYNAMODB_DIR,str(KINESIS):KINESIS_DIR}
class StateFileRef(PodObject):
 txt_layout=STATE_TXT_LAYOUT
 metadata_layout=STATE_TXT_METADATA
 def __init__(self,hash_ref:str,rel_path:str,file_name:str,size:int,service:str,region:str,account_id:str,serialization:Serialization):
  super(StateFileRef,self).__init__(hash_ref)
  self.rel_path:str=rel_path
  self.file_name:str=file_name
  self.size:int=size
  self.service:str=service
  self.region:str=region
  self.account_id:str=account_id
  self.serialization:Serialization=serialization
 def __str__(self):
  return self.txt_layout.format(size=self.size,account_id=self.account_id,service=self.service,region=self.region,hash_ref=self.hash_ref,file_name=self.file_name,rel_path=self.rel_path,serialization=self.serialization)
 def __eq__(self,other):
  if not other:
   return False
  if not isinstance(other,StateFileRef):
   return False
  return(self.hash_ref==other.hash_ref and self.account_id==other.account_id and self.region==other.region and self.service==self.service and self.file_name==other.file_name and self.size==other.size)
 def __hash__(self):
  return hash((self.hash_ref,self.account_id,self.region,self.service,self.file_name,self.size))
 def congruent(self,other)->bool:
  if not other:
   return False
  if not isinstance(other,StateFileRef):
   return False
  return(self.region==other.region and self.account_id==self.account_id and self.service==other.service and self.file_name==other.file_name and self.rel_path==other.rel_path)
 def any_congruence(self,others)->bool:
  for other in others:
   if self.congruent(other):
    return True
  return False
 def metadata(self)->str:
  return self.metadata_layout.format(size=self.size,service=self.service,region=self.region)
class PodNode(PodObject):
 def __init__(self,hash_ref:str,state_files:Set[StateFileRef],parent_ptr:str):
  super(PodNode,self).__init__(hash_ref)
  self.state_files:Set[StateFileRef]=state_files
  self.parent_ptr:str=parent_ptr
 def state_files_info(self)->str:
  return "\n".join(list(map(lambda state_file:str(state_file),self.state_files)))
class Commit:
 txt_layout=COMMIT_TXT_LAYOUT
 def __init__(self,tail_ptr:str,head_ptr:str,message:str,timestamp:str=str(datetime.now().timestamp()),delta_log_ptr:str=None):
  self.tail_ptr:str=tail_ptr
  self.head_ptr:str=head_ptr
  self.message:str=message
  self.timestamp:str=timestamp
  self.delta_log_ptr:str=delta_log_ptr
 def __str__(self):
  return self.txt_layout.format(tail_ptr=self.tail_ptr,head_ptr=self.head_ptr,message=self.message,timestamp=self.timestamp,log_hash=self.delta_log_ptr)
 def info_str(self,from_node:str,to_node:str)->str:
  return f"from: {from_node}, to: {to_node}, message: {self.message}, time: {datetime.fromtimestamp(float(self.timestamp))}"
class Revision(PodNode):
 txt_layout=REV_TXT_LAYOUT
 def __init__(self,hash_ref:str,state_files:Set[StateFileRef],parent_ptr:str,creator:str,rid:str,revision_number:int,assoc_commit:Commit=None):
  super(Revision,self).__init__(hash_ref,state_files,parent_ptr)
  self.creator:str=creator
  self.rid:str=rid
  self.revision_number:int=revision_number
  self.assoc_commit=assoc_commit
 def __str__(self):
  return self.txt_layout.format(hash_ref=self.hash_ref,parent=self.parent_ptr,creator=self.creator,rid=self.rid,rev_no=self.revision_number,state_files=";".join(map(lambda state_file:str(state_file),self.state_files))if self.state_files else "",assoc_commit=self.assoc_commit)
class Version(PodNode):
 txt_layout=VER_TXT_LAYOUT
 def __init__(self,hash_ref:str,state_files:Set[StateFileRef],parent_ptr:str,creator:str,comment:str,active_revision_ptr:str,outgoing_revision_ptrs:Set[str],incoming_revision_ptr:str,version_number:int):
  super(Version,self).__init__(hash_ref,state_files,parent_ptr)
  self.creator=creator
  self.comment=comment
  self.active_revision_ptr=active_revision_ptr
  self.outgoing_revision_ptrs=outgoing_revision_ptrs
  self.incoming_revision_ptr=incoming_revision_ptr
  self.version_number=version_number
 def __str__(self):
  return VER_TXT_LAYOUT.format(hash_ref=self.hash_ref,parent=self.parent_ptr,creator=self.creator,comment=self.comment,version_number=self.version_number,active_revision=self.active_revision_ptr,outgoing_revisions=";".join(self.outgoing_revision_ptrs),incoming_revision=self.incoming_revision_ptr,state_files=";".join(map(lambda stat_file:str(stat_file),self.state_files))if self.state_files else "")
 def info_str(self):
  return f"{self.version_number}, {self.creator}, {self.comment}"
# Created by pyminifier (https://github.com/liftoff/pyminifier)
