import abc,logging,os
from typing import Dict,Optional,Set,Union
from localstack_ext.bootstrap.pods.models import Commit,PodNode,PodObject,Revision,StateFileRef,Version
LOG=logging.getLogger(__name__)
class PodsSerializer(abc.ABC):
	def __init__(A):0
	@abc.abstractmethod
	def store_obj(self,pod_object,path):0
	@abc.abstractmethod
	def retrieve_obj(self,key,remote_path,local_path):0
	@staticmethod
	def _deserialize_state_files(state_files_str):
		B=state_files_str
		if not B:return set()
		D=B.split(';');C=set()
		for E in D:A=list(map(lambda x:x.split(':')[1],E.split(',')));C.add(StateFileRef(size=int(A[0]),service=A[1],account_id=A[2],region=A[3],hash_ref=A[4],file_name=A[5],rel_path=A[6],serialization=A[7]))
		return C
class VersionSerializerTxt(PodsSerializer):
	def store_obj(C,pod_object,path):
		A=pod_object
		with open(os.path.join(path,A.hash_ref),'w')as B:B.write(str(A))
		return A.hash_ref
	def retrieve_obj(D,key,remote_path,local_path):
		C=remote_path
		if C:B=os.path.join(C,key)
		else:B=os.path.join(local_path,key)
		if not os.path.isfile(B):LOG.debug(f"No Version Obj file found in path {B}");return
		with open(B,'r')as E:F=list(map(lambda line:line.rstrip(),E.readlines()));A=list(map(lambda line:line.split('=')[1],F));G=D._deserialize_state_files(A[8]);return Version(parent_ptr=A[0],hash_ref=A[1],creator=A[2],comment=A[3],version_number=int(A[4]),active_revision_ptr=A[5],outgoing_revision_ptrs=set(A[6].split(';')),incoming_revision_ptr=A[7],state_files=G)
class RevisionSerializerTxt(PodsSerializer):
	def store_obj(D,pod_obj,path):
		A=pod_obj
		try:
			with open(os.path.join(path,A.hash_ref),'w')as B:B.write(str(A))
		except FileNotFoundError as C:print(C)
		return A.hash_ref
	def retrieve_obj(C,key,remote_path,local_path):
		B=os.path.join(local_path,key)
		if not os.path.isfile(B):LOG.debug(f"No Revision Obj file found in path {B}");return
		def D(commit_str):
			B=commit_str
			if not B or B=='None':return
			A=list(map(lambda commit_attr:commit_attr.split(':')[1],B.split(',')));return Commit(tail_ptr=A[0],head_ptr=A[1],message=A[2],timestamp=A[3],delta_log_ptr=A[4])
		with open(B)as E:F=list(map(lambda line:line.rstrip(),E.readlines()));A=list(map(lambda line:line.split('=')[1],F));G=C._deserialize_state_files(A[5]);return Revision(parent_ptr=A[0],hash_ref=A[1],creator=A[2],rid=A[3],revision_number=int(A[4]),state_files=G,assoc_commit=D(A[6]))
version_serializer=VersionSerializerTxt()
revision_serializer=RevisionSerializerTxt()
txt_serializers={'version':version_serializer,'revision':revision_serializer}