_C=None
_B=False
_A=True
import json,logging,os,shutil,zipfile
from typing import Dict,List,Optional,Set,Tuple,Union
from localstack import config as localstack_config
from localstack.constants import TEST_AWS_ACCOUNT_ID
from localstack.utils.common import cp_r,mkdir,rm_rf,save_file,short_uid,to_str
from localstack.utils.http import safe_requests
from localstack_ext.bootstrap.pods.constants import CLOUD_PODS_DIR,COMPRESSION_FORMAT,DEFAULT_POD_DIR,NIL_PTR,STATE_ZIP,VER_SYMLINK,VERSION_SERVICE_INFO_FILE,VERSION_SPACE_ARCHIVE
from localstack_ext.bootstrap.pods.models import Commit,Revision,Serialization,StateFileRef,Version
from localstack_ext.bootstrap.pods.object_storage import get_object_storage_provider
from localstack_ext.bootstrap.pods.utils.common import PodsConfigContext,read_file_from_archive,zip_directories
from localstack_ext.bootstrap.pods.utils.hash_utils import compute_file_hash,compute_revision_hash,compute_version_archive_hash,random_hash
from localstack_ext.bootstrap.pods.utils.merge_utils import CloudPodsMergeManager,create_tmp_archives_by_serialization_mechanism
from localstack_ext.bootstrap.pods.utils.metamodel_utils import CommitMetamodelUtils,MetamodelDelta,MetamodelDeltaMethod
from localstack_ext.bootstrap.pods.utils.remote_utils import extract_meta_and_state_archives,merge_version_space,register_remote
from localstack_ext.bootstrap.state_utils import API_STATES_DIR,DYNAMODB_DIR,KINESIS_DIR,persist_object
LOG=logging.getLogger(__name__)
ROOT_DIR_LOOKUP={str(Serialization.KINESIS):KINESIS_DIR,str(Serialization.DDB):DYNAMODB_DIR,str(Serialization.MAIN):API_STATES_DIR}
class PodsApi:
	def __init__(A):
		B=os.environ.get('POD_DIR')
		if not B:B=os.path.join(localstack_config.dirs.tmp,DEFAULT_POD_DIR)
		B=os.path.join(B,CLOUD_PODS_DIR);A.config_context=PodsConfigContext(B);A.object_storage=get_object_storage_provider(A.config_context);A.commit_metamodel_utils=CommitMetamodelUtils(A.config_context)
	def init(A,pod_name='My-Pod'):
		C=pod_name
		if A.config_context.pod_exists_locally(pod_name=C):LOG.warning(f"Pod with name {C} already exists locally");return
		A.config_context.set_pod_context(C)
		def H():mkdir(A.config_context.get_pod_root_dir());mkdir(A.config_context.get_ver_refs_path());mkdir(A.config_context.get_rev_refs_path());mkdir(A.config_context.get_ver_obj_store_path());mkdir(A.config_context.get_rev_obj_store_path());mkdir(A.config_context.get_delta_log_path())
		H();D=random_hash();I=random_hash();E=Revision(hash_ref=D,parent_ptr=NIL_PTR,creator=A.config_context.get_context_user(),rid=short_uid(),revision_number=0,state_files=set());F=Version(hash_ref=I,parent_ptr=NIL_PTR,creator=A.config_context.get_context_user(),comment='Init version',active_revision_ptr=D,outgoing_revision_ptrs={D},incoming_revision_ptr=_C,state_files=set(),version_number=0);K,J=A.object_storage.upsert_objects(E,F);G=A.config_context.create_version_symlink(VER_SYMLINK.format(ver_no=F.version_number),J)
		with open(A.config_context.get_head_path(),'w')as B:B.write(G)
		with open(A.config_context.get_max_ver_path(),'w')as B:B.write(G)
		with open(A.config_context.get_known_ver_path(),'w')as B:B.write(G)
		A.config_context.update_ver_log(author=A.config_context.get_context_user(),ver_no=F.version_number,rev_id=E.rid,rev_no=E.revision_number);LOG.debug(f"Successfully initiated CloudPods for pod at {A.config_context.get_pod_root_dir()}")
	def init_remote(A,version_space_archive,meta_archives,state_archives,remote_info,pod_name):
		B=version_space_archive;A.config_context.set_pod_context(pod_name=pod_name);mkdir(A.config_context.get_pod_root_dir())
		with zipfile.ZipFile(B)as C:C.extractall(A.config_context.get_pod_root_dir());LOG.debug('Successfully extracted version space zip')
		rm_rf(B);extract_meta_and_state_archives(meta_archives=meta_archives,state_archives=state_archives,config_context=A.config_context);D=A._get_max_version();E=A.config_context.create_version_symlink(name=VER_SYMLINK.format(ver_no=D.version_number))
		with open(A.config_context.get_head_path(),'w')as F:F.write(E)
		register_remote(remote_info=remote_info,config_context=A.config_context)
	def commit(B,message=_C):
		A,F=B._get_expansion_point_with_head();D=compute_revision_hash(A,B.config_context.get_obj_store_path());G=set()
		if A.parent_ptr!=NIL_PTR:H=_C;E=B.object_storage.get_revision_by_key(A.parent_ptr);G=E.state_files;E.assoc_commit.head_ptr=D;B.object_storage.upsert_objects(E)
		else:H=F.hash_ref
		B.object_storage.update_revision_key(old_key=A.hash_ref,new_key=D,referenced_by_version=H);A.hash_ref=D;C=Revision(hash_ref=random_hash(),state_files=set(),parent_ptr=D,creator=A.creator,rid=short_uid(),revision_number=A.revision_number+1);I=B.create_delta_log(G,A.state_files);J=Commit(tail_ptr=A.hash_ref,head_ptr=C.hash_ref,message=message,delta_log_ptr=I);A.assoc_commit=J;B.object_storage.upsert_objects(C,A);B.config_context.update_ver_log(author=C.creator,ver_no=F.version_number,rev_id=C.rid,rev_no=C.revision_number);return A
	def merge_from_remote(A,version_space_archive,meta_archives,state_archives):merge_version_space(version_space_archive,config_context=A.config_context);extract_meta_and_state_archives(meta_archives=meta_archives,state_archives=state_archives,config_context=A.config_context)
	def is_remotely_managed(A):return A.config_context.is_remotely_managed()
	def rename_pod(B,new_pod_name):
		A=new_pod_name
		if B.config_context.pod_exists_locally(A):LOG.warning(f"{A} already exists locally");return _B
		B.config_context.rename_pod(A);return _A
	def list_locally_available_pods(A,show_remote_or_local=_A):
		mkdir(A.config_context.cloud_pods_root_dir);C=[B for B in os.listdir(A.config_context.cloud_pods_root_dir)if not B.endswith('.json')]
		if not show_remote_or_local:return set(C)
		D=set()
		for B in C:E=f"remote/{B}"if A.config_context.is_remotely_managed(B)else f"local/{B}";D.add(E)
		return D
	def push(A,comment=_C,three_way=_B,include_assets=_A):
		C,F=A._get_expansion_point_with_head();G=A._get_max_version();D=Revision(hash_ref=random_hash(),state_files=set(),parent_ptr=NIL_PTR,creator=C.creator,rid=short_uid(),revision_number=0);E=G.version_number+1
		if F.version_number!=G.version_number:A.merge_expansion_point_with_max(three_way=three_way)
		else:A._create_state_directory(E,state_file_refs=C.state_files)
		B=Version(hash_ref=compute_version_archive_hash(E,A.config_context.get_version_state_archive(E)),state_files=set(),parent_ptr=G.hash_ref,creator=C.creator,comment=comment,active_revision_ptr=D.hash_ref,outgoing_revision_ptrs={D.hash_ref},incoming_revision_ptr=C.hash_ref,version_number=E)
		if C.parent_ptr!=NIL_PTR:I=A.object_storage.get_revision_by_key(C.parent_ptr);J=I.state_files;H=A.create_delta_log(J,B.state_files)
		else:H=A.create_delta_log(C.state_files,set())
		K=Commit(tail_ptr=C.hash_ref,head_ptr=B.hash_ref,message='Finalizing commit',delta_log_ptr=H);C.state_files=B.state_files;C.assoc_commit=K;F.active_revision_ptr=NIL_PTR;A.object_storage.upsert_objects(F,C,D,B);A._update_head(B.version_number,B.hash_ref);A._update_max_ver(B.version_number,B.hash_ref);A._add_known_ver(B.version_number,B.hash_ref)
		if include_assets:A._add_assets_to_version_state_archive(B.version_number)
		A.commit_metamodel_utils.create_metadata_archive(B);A.config_context.update_ver_log(author=C.creator,ver_no=B.version_number,rev_id=D.rid,rev_no=D.revision_number);return B
	def set_pod_context(A,pod_name):A.config_context.set_pod_context(pod_name)
	def create_state_file_from_fs(D,path,file_name,service,region,root,serialization,account_id=TEST_AWS_ACCOUNT_ID):
		E=file_name;B=os.path.join(path,E);C=compute_file_hash(B);A=path.split(f"{root}/")
		if len(A)>1:A=A[1]
		else:A=''
		shutil.copy(B,os.path.join(D.config_context.get_obj_store_path(),C));F=StateFileRef(hash_ref=C,rel_path=A,file_name=E,size=os.path.getsize(B),service=service,region=region,account_id=account_id,serialization=serialization);D._add_state_file_to_expansion_point(F);return C
	def _create_state_file_from_in_memory_blob(B,blob):D=random_hash();A=os.path.join(B.config_context.get_obj_store_path(),D);persist_object(blob,A);C=compute_file_hash(A);E=os.path.join(B.config_context.get_obj_store_path(),C);os.rename(A,E);return C
	def _get_state_file_path(B,key):
		A=os.path.join(B.config_context.get_obj_store_path(),key)
		if os.path.isfile(A):return A
		LOG.warning(f"No state file with found with key: {key}")
	def _add_state_file_to_expansion_point(B,state_file):C=state_file;A,E=B._get_expansion_point_with_head();D=set(filter(lambda sf:not sf.congruent(C),A.state_files));D.add(C);A.state_files=D;B.object_storage.upsert_objects(A)
	def list_state_files(B,key):
		A=B.object_storage.get_revision_or_version_by_key(key)
		if A:return A.state_files_info()
		LOG.debug(f"No Version or Revision associated to {key}")
	def get_version_info(D,version_no):
		B=version_no;C=D.config_context.get_version_meta_archive(B)
		if not C:LOG.warning(f"No Info found for version {B}");return
		A=read_file_from_archive(C,VERSION_SERVICE_INFO_FILE);A=json.loads(to_str(A or'{}'));return A
	def create_version_space_archive(A):
		B=os.path.join(A.config_context.get_pod_root_dir(),VERSION_SPACE_ARCHIVE);rm_rf(B);C=zip_directories(zip_dest=B,directories=A.config_context.get_version_space_dir_paths())
		with zipfile.ZipFile(C,'a')as E:
			for D in A.config_context.get_version_space_file_paths():E.write(D,arcname=os.path.basename(D))
		return C
	def get_head(A):return A.object_storage.get_version_by_key(A.config_context.get_head_key())
	def _get_max_version(A):return A.object_storage.get_version_by_key(A.config_context.get_max_ver_key())
	def get_max_version_no(A):
		with open(A.config_context.get_max_ver_path())as B:return int(os.path.basename(B.readline()))
	def _get_expansion_point_with_head(A):B=A.get_head();C=A.object_storage.get_revision_by_key(key=B.active_revision_ptr);D=A.object_storage.get_terminal_revision(revision_path_root=C);return D,B
	def push_overwrite(A,version,comment):
		B=version;D,F=A._get_expansion_point_with_head()
		if B>A.get_max_version_no():LOG.debug('Attempted to overwrite a non existing version.. Aborting');return _B
		C=A.get_version_by_number(B);A._create_state_directory(version_number=B,state_file_refs=D.state_files);E=A.config_context.metamodel_file(D.revision_number);A.commit_metamodel_utils.create_metadata_archive(C,overwrite=_A,metamodels_file=E);C.comment=comment;A.object_storage.upsert_objects(C);return _A
	def _add_assets_to_version_state_archive(A,version_number,cleanup=_A):
		D=A.config_context.get_version_state_archive_path(version=version_number);B=A.config_context.get_assets_root_path()
		with zipfile.ZipFile(D,'a')as E:
			for (F,I,G) in os.walk(B):
				for H in G:C=os.path.join(F,H);E.write(filename=C,arcname=os.path.relpath(C,start=A.config_context.get_pod_root_dir()))
		if cleanup:rm_rf(B)
	@staticmethod
	def _get_dst_path_for_state_file(version_state_dir,state_file):
		C=version_state_dir;A=state_file
		if A.serialization in[str(Serialization.KINESIS),str(Serialization.DDB)]:B=os.path.join(C,ROOT_DIR_LOOKUP[A.serialization])
		else:B=os.path.join(C,ROOT_DIR_LOOKUP[A.serialization],A.rel_path)
		mkdir(B);return B
	def _create_state_directory(C,version_number,state_file_refs,delete_files=_B,archive=_A):
		A=os.path.join(C.config_context.get_pod_root_dir(),STATE_ZIP.format(version_no=version_number));mkdir(A)
		for B in state_file_refs:
			try:
				E=C._get_dst_path_for_state_file(A,B);D=C.object_storage.get_state_file_location_by_key(B.hash_ref);F=os.path.join(E,B.file_name);shutil.copy(D,F)
				if delete_files:os.remove(D)
			except Exception as G:LOG.warning(f"Failed to locate state file with rel path: {B.rel_path}: {G}")
		if archive:shutil.make_archive(A,COMPRESSION_FORMAT,root_dir=A);rm_rf(A);return f"{A}.{COMPRESSION_FORMAT}"
		return A
	def set_active_version(A,version_no,commit_before=_B):
		B=version_no;C=A.load_version_references()
		for (D,E) in C:
			if D==B:
				if commit_before:A.commit()
				A._set_active_version(E);return _A
		LOG.info(f"Version with number {B} not found");return _B
	def _set_active_version(A,key):
		C=key;E=A.get_head()
		if E.hash_ref!=C and A.object_storage.version_exists(C):
			B=A.object_storage.get_version_by_key(C);A._update_head(B.version_number,C)
			if B.active_revision_ptr==NIL_PTR:D=Revision(hash_ref=random_hash(),state_files=set(),parent_ptr=NIL_PTR,creator=A.config_context.get_context_user(),rid=short_uid(),revision_number=0);B.active_revision_ptr=D.hash_ref;B.outgoing_revision_ptrs.add(D.hash_ref);A.object_storage.upsert_objects(D,B)
	def get_version_by_number(A,version_no):
		B=version_no;D=A.load_version_references();C=next((A[1]for A in D if A[0]==B),_C)
		if not C:LOG.warning(f"Could not find version number {B}");return
		return A.object_storage.get_version_by_key(C)
	def load_version_references(B):
		C={}
		with open(B.config_context.get_known_ver_path(),'r')as D:
			E=D.readlines()
			for A in E:
				A=B.config_context.get_pod_absolute_path(A.rstrip())
				with open(A,'r')as F:C[int(os.path.basename(A))]=F.readline()
		return sorted(C.items(),key=lambda x:x[0],reverse=_A)
	def list_versions(A):B=A.load_version_references();C=[A.object_storage.get_version_by_key(C).info_str()for(D,C)in B];return C
	def list_version_commits(B,version_no):
		C=version_no
		if C==-1:D=B._get_max_version()
		else:D=B.get_version_by_number(C)
		if not D:return[]
		G=[];A=B.object_storage.get_revision_by_key(D.incoming_revision_ptr)
		while A:
			H=A.assoc_commit;E=A.revision_number
			if E!=0:F=f"Revision-{E-1}"
			elif C!=0:F=f"Version-{C}"
			else:F='Empty state'
			I=f"Revision-{E}";G.append(H.info_str(from_node=F,to_node=I));A=B.object_storage.get_revision_by_key(A.parent_ptr)
		return G
	def _update_head(A,new_head_ver_no,new_head_key):
		with open(A.config_context.get_head_path(),'w')as C:B=A.config_context.create_version_symlink(VER_SYMLINK.format(ver_no=new_head_ver_no),new_head_key);C.write(B);return B
	def _update_max_ver(A,new_max_ver_no,new_max_ver_key):
		with open(A.config_context.get_max_ver_path(),'w')as C:B=A.config_context.create_version_symlink(VER_SYMLINK.format(ver_no=new_max_ver_no),new_max_ver_key);C.write(B);return B
	def _add_known_ver(A,new_ver_no,new_ver_key):
		with open(A.config_context.get_known_ver_path(),'a')as C:B=A.config_context.create_version_symlink(VER_SYMLINK.format(ver_no=new_ver_no),new_ver_key);C.write(f"\n{B}");return B
	def merge_expansion_point_with_max(A,three_way=_B):
		C=three_way;M,E=A._get_expansion_point_with_head();F=A.get_max_version_no();N=F+1;G=A._create_state_directory(version_number=N,state_file_refs=M.state_files);O=A.config_context.get_version_state_archive(F)
		if E.version_number<2:C=_B
		if C:P=A.config_context.get_version_state_archive(E.version_number-1);H=create_tmp_archives_by_serialization_mechanism(P)
		else:H={}
		I=create_tmp_archives_by_serialization_mechanism(G);Q=create_tmp_archives_by_serialization_mechanism(O)
		for (B,J) in I.items():
			try:
				K=CloudPodsMergeManager.get(B,raise_if_missing=_A);L=H.get(B);D=Q.get(B)
				if not D:LOG.warning('No merge performed for %s serialized state files',B);continue
				if L and C:K.three_way_merge(common_ancestor_state_files=L,from_state_files=D,to_state_files=J)
				else:K.two_way_merge(from_state_files=J,to_state_files=D)
			except Exception as R:LOG.warning('Failed to perform merge for %s: %s',B,R)
		shutil.make_archive(base_name=os.path.splitext(G)[0],format=COMPRESSION_FORMAT,root_dir=I['root'])
	def add_assets_to_pod(B,assets_root_paths):
		for A in assets_root_paths:
			C=os.path.join(B.config_context.get_assets_root_path(),os.path.basename(A))
			try:cp_r(src=A,dst=C)
			except Exception as D:LOG.warning('Failed to copy assets for %s: %s',A,D)
	def create_delta_log(A,state_from,state_to,diff_method=MetamodelDeltaMethod.SIMPLE):
		try:C=MetamodelDelta.get(diff_method);return C.create_delta_log(state_from,state_to,A.config_context)
		except Exception as D:LOG.debug('Unable to create delta log for version graph nodes: %s',D);B=short_uid();E=os.path.join(A.config_context.get_delta_log_path(),B);save_file(E,'{}');return B
	def upload_version_and_product_space(A,presigned_urls):
		D=presigned_urls;C='rb'
		def B(pre_signed_url,zip_data_content):
			A=safe_requests.put(pre_signed_url,data=zip_data_content)
			if A.status_code>=400:raise Exception(f"Unable to upload pod state to S3 (code {A.status_code}): {A.content}")
			return A
		H=D.get('presigned_version_space_url');E=A.create_version_space_archive()
		with open(E,C)as I:B(H,I.read())
		J=D.get('presigned_meta_state_urls');rm_rf(E)
		for (F,G) in J.items():
			K=G['meta'];L=A.config_context.get_version_meta_archive(F)
			with open(L,C)as M:B(K,M)
			N=G['state'];O=A.config_context.get_version_state_archive(F)
			with open(O,C)as P:B(N,P)