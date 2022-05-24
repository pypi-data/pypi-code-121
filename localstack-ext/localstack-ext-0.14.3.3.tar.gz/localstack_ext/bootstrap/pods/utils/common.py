_A=None
import json,logging,os,zipfile
from typing import Dict,List,Union
from localstack.utils.json import FileMappedDocument
from localstack_ext.bootstrap.auth import get_auth_cache
from localstack_ext.bootstrap.pods.constants import ASSETS_ROOT,COMMIT_FILE,COMPRESSION_FORMAT,DELTA_LOG_DIR,HEAD_FILE,KNOWN_VER_FILE,MAX_VER_FILE,META_ZIP,METAMODELS_FILE,OBJ_STORE_DIR,PODS_CONFIG,REFS_DIR,REMOTE_FILE,REV_SUB_DIR,STATE_ZIP,VER_LOG_FILE,VER_LOG_STRUCTURE,VER_SUB_DIR,VERSION_SPACE_DIRS,VERSION_SPACE_FILES
LOG=logging.getLogger(__name__)
class PodsConfigContext:
	def __init__(A,pod_root_dir):B=pod_root_dir;A.cloud_pods_root_dir=B;A.pod_root_dir=B;A.user=_A
	def get_pod_context(A):return os.path.basename(A.pod_root_dir)
	def get_context_user(A):return A.user
	def get_pod_root_dir(A):return A.pod_root_dir
	def get_cloud_pods_root_dir(A):return A.cloud_pods_root_dir
	def get_head_path(A):return os.path.join(A.pod_root_dir,HEAD_FILE)
	def get_max_ver_path(A):return os.path.join(A.pod_root_dir,MAX_VER_FILE)
	def get_known_ver_path(A):return os.path.join(A.pod_root_dir,KNOWN_VER_FILE)
	def get_ver_log_path(A):return os.path.join(A.pod_root_dir,VER_LOG_FILE)
	def get_obj_store_path(A):return os.path.join(A.pod_root_dir,OBJ_STORE_DIR)
	def get_rev_obj_store_path(A):return os.path.join(A.get_obj_store_path(),REV_SUB_DIR)
	def get_ver_obj_store_path(A):return os.path.join(A.get_obj_store_path(),VER_SUB_DIR)
	def get_ver_refs_path(A):return os.path.join(A.pod_root_dir,REFS_DIR,VER_SUB_DIR)
	def get_rev_refs_path(A):return os.path.join(A.pod_root_dir,REFS_DIR,REV_SUB_DIR)
	def get_version_ref_file_path(A,version_ref):return os.path.join(A.get_ver_refs_path(),version_ref)
	def get_delta_log_path(A):return os.path.join(A.pod_root_dir,A.get_obj_store_path(),DELTA_LOG_DIR)
	def get_assets_root_path(A):return os.path.join(A.pod_root_dir,ASSETS_ROOT)
	def get_version_meta_archive_path(B,version,with_format=True):
		A=os.path.join(B.get_pod_root_dir(),META_ZIP.format(version_no=version))
		if not with_format:return A
		return f"{A}.{COMPRESSION_FORMAT}"
	def get_version_state_archive_path(B,version,with_format=True):
		A=os.path.join(B.get_pod_root_dir(),STATE_ZIP.format(version_no=version))
		if not with_format:return A
		return f"{A}.{COMPRESSION_FORMAT}"
	def update_ver_log(A,author,ver_no,rev_id,rev_no):
		with open(A.get_ver_log_path(),'a')as B:B.write(f"{VER_LOG_STRUCTURE.format(author=author,ver_no=ver_no,rev_rid_no=f'{rev_id}_{rev_no}')}\n")
	def create_version_symlink(A,name,key=_A):return A._create_symlink(name,key,A.get_ver_refs_path())
	def create_revision_symlink(A,name,key=_A):return A._create_symlink(name,key,A.get_rev_refs_path())
	def is_initialized(A):return A.pod_root_dir and os.path.isdir(A.pod_root_dir)
	def _create_symlink(A,name,key,path):
		B=os.path.relpath(path,start=A.get_pod_root_dir());C=os.path.join(B,name)
		if key:
			D=os.path.join(path,name)
			with open(D,'w')as E:E.write(key)
		return C
	def get_head_key(A):return A._get_key(A.get_head_path())
	def get_max_ver_key(A):return A._get_key(A.get_max_ver_path())
	def _get_key(B,path):
		with open(path,'r')as A:C=A.readline().strip()
		D=B.get_pod_absolute_path(C)
		with open(D,'r')as A:E=A.readline();return E
	def get_pod_absolute_path(A,rel_path):return os.path.join(A.get_pod_root_dir(),rel_path)
	def get_obj_file_path(A,key):return os.path.join(A.get_obj_store_path(),key)
	def get_remote_info_path(A):return os.path.join(A.pod_root_dir,REMOTE_FILE)
	def is_remotely_managed(A,pod_name=_A):
		B=pod_name
		if B:return os.path.isfile(os.path.join(A.cloud_pods_root_dir,B,REMOTE_FILE))
		else:return os.path.isfile(A.get_remote_info_path())
	def set_pod_context(A,pod_name):B=get_auth_cache();C=B.get('username','unknown');A.pod_root_dir=os.path.join(A.cloud_pods_root_dir,pod_name);A.user=C
	def pod_exists_locally(A,pod_name):return os.path.isdir(os.path.join(A.cloud_pods_root_dir,pod_name))
	def rename_pod(A,new_pod_name):C=A.get_pod_root_dir();B=os.path.join(A.cloud_pods_root_dir,new_pod_name);os.rename(C,B);A.set_pod_context(B)
	def get_pod_name(A):return os.path.basename(A.get_pod_root_dir())
	def get_version_space_dir_paths(A):return[os.path.join(A.get_pod_root_dir(),B)for B in VERSION_SPACE_DIRS]
	def get_version_space_file_paths(A):return[os.path.join(A.get_pod_root_dir(),B)for B in VERSION_SPACE_FILES]
	def get_pods_config_cache(A,conf_cache_file=PODS_CONFIG):return FileMappedDocument(os.path.join(A.cloud_pods_root_dir,conf_cache_file),mode=384)
	def save_pods_config(B,options):A=B.get_pods_config_cache();A.update(options);A.save()
	def metamodel_file(D,revision,version=_A,absolute=False):
		B=version;A=revision
		if not A:return METAMODELS_FILE
		C=f"metamodel_commit_{A}.json"
		if absolute:
			if B is _A:raise Exception('Missing pod version when constructing revision metamodel file path')
			C=os.path.join(D.metadata_dir(B))
		return C
	@staticmethod
	def commit_metamodel_file(commit_no):return COMMIT_FILE.format(commit_no=commit_no)
	def metadata_dir(A,version):return os.path.join(A.get_pod_root_dir(),META_ZIP.format(version_no=version))
	def get_version_meta_archive(B,version):
		A=B.get_version_meta_archive_path(version)
		if os.path.isfile(A):return A
	def get_version_state_archive(B,version):
		A=B.get_version_state_archive_path(version)
		if os.path.isfile(A):return A
def zip_directories(zip_dest,directories):
	B=zip_dest;from localstack.utils.testutil import create_zip_file_python as C
	for A in directories:C(source_path=A,content_root=os.path.basename(A),base_dir=A,zip_file=B,mode='a')
	return B
def add_file_to_archive(archive,entry_name,content):
	with zipfile.ZipFile(archive,'a')as A:A.writestr(entry_name,content)
def read_file_from_archive(archive_path,file_name):
	B=file_name;A=archive_path
	try:
		with zipfile.ZipFile(A)as C:D=json.loads(C.read(B));return json.dumps(D)
	except Exception as E:LOG.debug(f"Could not find {B} in archive {A}: {E}")