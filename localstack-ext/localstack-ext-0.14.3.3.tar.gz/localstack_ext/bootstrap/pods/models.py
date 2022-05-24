_A=False
from datetime import datetime
from enum import Enum
from typing import Set
from localstack_ext.bootstrap.pods.constants import COMMIT_TXT_LAYOUT,REV_TXT_LAYOUT,STATE_TXT_LAYOUT,STATE_TXT_METADATA,VER_TXT_LAYOUT
from localstack_ext.bootstrap.state_utils import API_STATES_DIR,DYNAMODB_DIR,KINESIS_DIR
class PodObject:
	def __init__(A,hash_ref):A.hash_ref=hash_ref
class Serialization(Enum):MAIN=API_STATES_DIR;DDB=DYNAMODB_DIR;KINESIS=KINESIS_DIR;serializer_root_lookup={str(MAIN):API_STATES_DIR,str(DDB):DYNAMODB_DIR,str(KINESIS):KINESIS_DIR}
class StateFileRef(PodObject):
	txt_layout=STATE_TXT_LAYOUT;metadata_layout=STATE_TXT_METADATA
	def __init__(A,hash_ref,rel_path,file_name,size,service,region,account_id,serialization):super(StateFileRef,A).__init__(hash_ref);A.rel_path=rel_path;A.file_name=file_name;A.size=size;A.service=service;A.region=region;A.account_id=account_id;A.serialization=serialization
	def __str__(A):return A.txt_layout.format(size=A.size,account_id=A.account_id,service=A.service,region=A.region,hash_ref=A.hash_ref,file_name=A.file_name,rel_path=A.rel_path,serialization=A.serialization)
	def __eq__(A,other):
		B=other
		if not B:return _A
		if not isinstance(B,StateFileRef):return _A
		return A.hash_ref==B.hash_ref and A.account_id==B.account_id and A.region==B.region and A.service==A.service and A.file_name==B.file_name and A.size==B.size
	def __hash__(A):return hash((A.hash_ref,A.account_id,A.region,A.service,A.file_name,A.size))
	def congruent(A,other):
		B=other
		if not B:return _A
		if not isinstance(B,StateFileRef):return _A
		return A.region==B.region and A.account_id==A.account_id and A.service==B.service and A.file_name==B.file_name and A.rel_path==B.rel_path
	def any_congruence(A,others):
		for B in others:
			if A.congruent(B):return True
		return _A
	def metadata(A):return A.metadata_layout.format(size=A.size,service=A.service,region=A.region)
class PodNode(PodObject):
	def __init__(A,hash_ref,state_files,parent_ptr):super(PodNode,A).__init__(hash_ref);A.state_files=state_files;A.parent_ptr=parent_ptr
	def state_files_info(A):return '\n'.join(list(map(lambda state_file:str(state_file),A.state_files)))
class Commit:
	txt_layout=COMMIT_TXT_LAYOUT
	def __init__(A,tail_ptr,head_ptr,message,timestamp=str(datetime.now().timestamp()),delta_log_ptr=None):A.tail_ptr=tail_ptr;A.head_ptr=head_ptr;A.message=message;A.timestamp=timestamp;A.delta_log_ptr=delta_log_ptr
	def __str__(A):return A.txt_layout.format(tail_ptr=A.tail_ptr,head_ptr=A.head_ptr,message=A.message,timestamp=A.timestamp,log_hash=A.delta_log_ptr)
	def info_str(A,from_node,to_node):return f"from: {from_node}, to: {to_node}, message: {A.message}, time: {datetime.fromtimestamp(float(A.timestamp))}"
class Revision(PodNode):
	txt_layout=REV_TXT_LAYOUT
	def __init__(A,hash_ref,state_files,parent_ptr,creator,rid,revision_number,assoc_commit=None):super(Revision,A).__init__(hash_ref,state_files,parent_ptr);A.creator=creator;A.rid=rid;A.revision_number=revision_number;A.assoc_commit=assoc_commit
	def __str__(A):return A.txt_layout.format(hash_ref=A.hash_ref,parent=A.parent_ptr,creator=A.creator,rid=A.rid,rev_no=A.revision_number,state_files=';'.join(map(lambda state_file:str(state_file),A.state_files))if A.state_files else'',assoc_commit=A.assoc_commit)
class Version(PodNode):
	txt_layout=VER_TXT_LAYOUT
	def __init__(A,hash_ref,state_files,parent_ptr,creator,comment,active_revision_ptr,outgoing_revision_ptrs,incoming_revision_ptr,version_number):super(Version,A).__init__(hash_ref,state_files,parent_ptr);A.creator=creator;A.comment=comment;A.active_revision_ptr=active_revision_ptr;A.outgoing_revision_ptrs=outgoing_revision_ptrs;A.incoming_revision_ptr=incoming_revision_ptr;A.version_number=version_number
	def __str__(A):return VER_TXT_LAYOUT.format(hash_ref=A.hash_ref,parent=A.parent_ptr,creator=A.creator,comment=A.comment,version_number=A.version_number,active_revision=A.active_revision_ptr,outgoing_revisions=';'.join(A.outgoing_revision_ptrs),incoming_revision=A.incoming_revision_ptr,state_files=';'.join(map(lambda stat_file:str(stat_file),A.state_files))if A.state_files else'')
	def info_str(A):return f"{A.version_number}, {A.creator}, {A.comment}"