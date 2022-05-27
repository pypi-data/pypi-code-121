_A='utf-8'
import hashlib,logging,os,random,zipfile
from typing import Optional
from localstack.utils.common import new_tmp_dir,rm_rf
from localstack_ext.bootstrap.pods.models import Revision,Version
from localstack_ext.bootstrap.state_utils import API_STATES_DIR,api_states_traverse
LOG=logging.getLogger(__name__)
def random_hash():return hex(random.getrandbits(160))
def compute_file_hash(file_path,accum=None):
	B=accum;A=file_path
	try:
		with open(A,'rb')as C:
			if B:B.update(C.read())
			else:return hashlib.sha1(C.read()).hexdigest()
	except Exception as D:LOG.warning(f"Failed to open file and compute hash for file at {A}: {D}")
def compute_version_archive_hash(version_no,state_archive):
	def C(**A):B=A.get('dir_name');C=A.get('fname');D=A.get('mutables')[0];E=os.path.join(B,C);compute_file_hash(E,D)
	A=new_tmp_dir()
	with zipfile.ZipFile(state_archive)as D:D.extractall(A)
	E=os.path.join(A,API_STATES_DIR);B=hashlib.sha1();api_states_traverse(E,C,[B]);B.update(str(version_no).encode(_A));rm_rf(A);return B.hexdigest()
def compute_revision_hash(pods_node,obj_store_path):
	A=pods_node
	if not A.state_files:return random_hash()
	D=map(lambda state_file:state_file.hash_ref,A.state_files);B=hashlib.sha1()
	for C in D:
		try:
			with open(os.path.join(obj_store_path,C),'rb')as E:B.update(E.read())
		except Exception as F:LOG.warning(f"Failed to open file and compute hash for {C}: {F}")
	if isinstance(A,Revision):B.update(A.rid.encode(_A));B.update(str(A.revision_number).encode(_A))
	elif isinstance(A,Version):B.update(str(A.version_number).encode(_A))
	return B.hexdigest()