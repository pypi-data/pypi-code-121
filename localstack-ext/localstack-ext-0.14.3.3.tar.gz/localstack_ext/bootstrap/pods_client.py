_M='state_archive'
_L='presigned_url_metadata'
_K='presigned_url_state'
_J='max_ver'
_I='cpvcs'
_H='ci_pod'
_G='qualifying_name'
_F='presigned_urls'
_E='pod_name'
_D='storage_uuid'
_C=True
_B=None
_A=False
import json,logging,os,re
from abc import ABCMeta,abstractmethod
from typing import Dict,List,Optional,Set
from zipfile import ZipFile
import requests
from localstack import config,constants
from localstack.utils.common import clone,cp_r,disk_usage,download,load_file,new_tmp_dir,new_tmp_file,retry,rm_rf,safe_requests,save_file,to_str
from localstack.utils.docker_utils import DOCKER_CLIENT
from localstack.utils.testutil import create_zip_file
from localstack_ext.bootstrap.licensing import get_auth_headers
from localstack_ext.bootstrap.pods import pods_api
from localstack_ext.bootstrap.pods.models import Serialization
from localstack_ext.bootstrap.pods.pods_api import PodsApi
from localstack_ext.bootstrap.state_utils import API_STATES_DIR,DYNAMODB_DIR,KINESIS_DIR,api_states_traverse
from localstack_ext.constants import API_PATH_PODS
LOG=logging.getLogger(__name__)
PERSISTED_FOLDERS=[API_STATES_DIR,DYNAMODB_DIR,KINESIS_DIR]
MERGE_STRATEGY_TWO_WAY='two way'
MERGE_STRATEGY_THREE_WAY='three way'
MERGE_STRATEGY_DISABLED='disabled'
class PodInfo:
	def __init__(A,name=_B,pod_size=0):A.name=name;A.pod_size=pod_size;A.pod_size_compressed=0;A.persisted_resource_names=[]
class CloudPodsManager(metaclass=ABCMeta):
	@abstractmethod
	def __init__(self,pod_name,pre_config):A=self;A.pod_name=pod_name;A.pod_config=clone(pre_config);A.pods_api=PodsApi()
	@abstractmethod
	def init(self):...
	@abstractmethod
	def delete(self,remote):...
	@abstractmethod
	def push(self,comment=_B,three_way=_A):...
	@abstractmethod
	def push_overwrite(self,version,comment=_B):...
	@abstractmethod
	def pull(self,inject_version_state=_A,reset_state_before=_A,lazy=_A):...
	@abstractmethod
	def commit(self,message):...
	@abstractmethod
	def inject(self,version,reset_state):...
	@abstractmethod
	def list_versions(self):...
	@abstractmethod
	def version_info(self,version):...
	@abstractmethod
	def version_metamodel(self,version):...
	@abstractmethod
	def set_version(self,version,inject_version_state,reset_state,commit_before):...
	@abstractmethod
	def list_version_commits(self,version):...
	@abstractmethod
	def get_commit_diff(self,version,commit):...
	@abstractmethod
	def register_remote(self,pod_name,ci_pod):...
	@abstractmethod
	def rename_pod(self,current_pod_name,new_pod_name):...
	@abstractmethod
	def list_pods(self,fetch_remote):...
	@staticmethod
	def restart_container():
		LOG.info('Restarting LocalStack instance with updated persistence state - this may take some time ...');B={'action':'restart'};A='%s/health'%config.get_edge_url()
		try:requests.post(A,data=json.dumps(B))
		except requests.exceptions.ConnectionError:pass
		def C():LOG.info('Waiting for LocalStack instance to be fully initialized ...');B=requests.get(A);C=json.loads(to_str(B.content));D=[A for(B,A)in C['services'].items()];assert set(D)=={'running'}
		retry(C,sleep=3,retries=10)
	@staticmethod
	def get_state_zip_from_instance(get_content=_A):
		B=f"{get_pods_endpoint()}/state";A=requests.get(B)
		if A.status_code>=400:raise Exception('Unable to get local pod state via management API %s (code %s): %s'%(B,A.status_code,A.content))
		if get_content:return A.content
		C=f"{new_tmp_file()}.zip";save_file(C,A.content);return C
	def get_pod_info(C,pod_data_dir=_B):
		A=pod_data_dir;B=PodInfo(C.pod_name)
		if A:B.pod_size=disk_usage(A);B.persisted_resource_names=get_persisted_resource_names(A)
		return B
class CloudPodsVersionManager(CloudPodsManager):
	def __init__(A,pod_name,pre_config):super().__init__(pod_name,pre_config)
	@staticmethod
	def parse_pod_name_from_qualifying_name(qualifying_name):return qualifying_name.split(PODS_NAMESPACE_DELIM,1)[1]
	@staticmethod
	def _prepare_archives_from_pre_signed_urls(content):
		A=new_tmp_file();B=content.get(_F);I=B.get('presigned_version_space_url');download(url=I,path=A);C={};D={};J=B.get('presigned_meta_state_urls')
		for (E,F) in J.items():G=new_tmp_file();H=new_tmp_file();K=F['meta'];L=F['state'];download(K,G);download(L,H);D[E]=G;C[E]=H
		return A,D,C
	@staticmethod
	def _get_max_version_for_pod_from_platform(pod_name,auth_headers):
		B=CloudPodsVersionManager.create_platform_url(f"{pod_name}/info/max-version");A=safe_requests.get(url=B,headers=auth_headers)
		if A.status_code!=200:LOG.warning('Failed to get version information from platform... aborting');return
		C=json.loads(A.content);D=int(C[_J]);return D
	def _add_state_files_func(B,**A):C=A.get('dir_name');D=A.get('account_id');E=A.get('fname');F=A.get('region');G=A.get('service_name');B.pods_api.create_state_file_from_fs(path=C,file_name=E,service=G,region=F,account_id=D,root=API_STATES_DIR,serialization=Serialization.MAIN)
	def _add_state_files_from_directory(B,service,path,root_dir,serialization):
		A=path
		if not os.path.isdir(A):return
		for C in os.listdir(A):B.pods_api.create_state_file_from_fs(path=A,file_name=C,service=service,region='NA',root=root_dir,serialization=serialization)
	def _add_state_to_cloud_pods_store(B,extract_assets=_A):
		if not B.pods_api.config_context.is_initialized():LOG.debug('No Cloud Pod instance detected in the local context - unable to push');return
		C=B.get_state_zip_from_instance();A=new_tmp_dir()
		with ZipFile(C,'r')as G:
			G.extractall(A);H=os.path.join(A,API_STATES_DIR);api_states_traverse(api_states_path=H,side_effect=B._add_state_files_func,mutables=_B);I=os.path.join(A,KINESIS_DIR);J=os.path.join(A,DYNAMODB_DIR);B._add_state_files_from_directory(service='kinesis',path=I,root_dir=KINESIS_DIR,serialization=Serialization.KINESIS);B._add_state_files_from_directory(service='dynamodb',path=J,root_dir=DYNAMODB_DIR,serialization=Serialization.DDB)
			if extract_assets:
				D=[]
				for E in os.listdir(A):
					F=os.path.join(A,E)
					if os.path.isdir(F)and E not in PERSISTED_FOLDERS:D.append(F)
				B.pods_api.add_assets_to_pod(assets_root_paths=D)
		rm_rf(C);rm_rf(A)
	def _pull_versions(A,auth_headers,required_versions):
		D=A.create_platform_url(f"{A.pod_name}?versions={required_versions}");C=safe_requests.get(url=D,headers=auth_headers)
		if C.status_code!=200:LOG.warning('Failed to pull requested versions from platform');return
		E=json.loads(C.content);B=CloudPodsVersionManager._prepare_archives_from_pre_signed_urls(E);F=B[0];G=B[1];H=B[2];A.pods_api.merge_from_remote(version_space_archive=F,meta_archives=G,state_archives=H)
	def _clone_pod(A,auth_headers,lazy=_A):
		E=A.create_platform_url(f"{A.pod_name}/clone")
		if lazy:E+='?lazy=True'
		B=safe_requests.get(E,headers=auth_headers)
		if B.status_code!=200:LOG.warning(f"Failed to clone requested pod {A.pod_name}: {B.content}");return
		C=json.loads(B.content);D=CloudPodsVersionManager._prepare_archives_from_pre_signed_urls(C);G=D[0];H=D[1];I=D[2];F={_D:C.get(_D),_G:C.get(_E)};J=CloudPodsVersionManager.parse_pod_name_from_qualifying_name(F[_G]);A.pods_api.init_remote(pod_name=J,version_space_archive=G,meta_archives=H,state_archives=I,remote_info=F)
	def init(A):A.pods_api.init(pod_name=A.pod_name)
	def delete(A,remote):
		C=A.pods_api.config_context.cloud_pods_root_dir;B=os.path.join(C,A.pod_name)
		if os.path.isdir(B):rm_rf(B);return _C
		if remote:0
		return _A
	def _push_to_remote(B,url):
		C=get_auth_headers();A=safe_requests.put(url=url,headers=C)
		if A.status_code!=200:LOG.warning('Failed to get presigned URLs to upload new version.. aborting');return
		D=json.loads(A.content);E=D.get(_F);B.pods_api.upload_version_and_product_space(presigned_urls=E)
	def push(A,comment=_B,three_way=_A):
		B=comment;A.pods_api.set_pod_context(A.pod_name);A._add_state_to_cloud_pods_store(extract_assets=_C)
		if A.pods_api.is_remotely_managed():
			D=get_auth_headers();C=A.pods_api.get_max_version_no();E=A._get_max_version_for_pod_from_platform(pod_name=A.pod_name,auth_headers=D)
			if C<E:A.pull()
			A.pods_api.push(comment=B);F=A.create_platform_url(f"push/{A.pod_name}?version={C+1}");A._push_to_remote(url=F)
		else:G=A.pods_api.push(comment=B);LOG.debug(f"Created new version: {G}")
		return PodInfo()
	def push_overwrite(A,version,comment=_B):
		B=version;A.pods_api.set_pod_context(pod_name=A.pod_name)
		if B>A.pods_api.get_max_version_no():LOG.warning(f"Version {B} does not exist");return _A
		A._add_state_to_cloud_pods_store();A.pods_api.push_overwrite(version=B,comment=comment)
		if A.pods_api.is_remotely_managed():C=CloudPodsVersionManager.create_platform_url(f"push-overwrite/{A.pod_name}?version={B}");A._push_to_remote(url=C)
		return _C
	def pull(A,inject_version_state=_A,reset_state_before=_A,lazy=_A):
		B=get_auth_headers()
		if A.pod_name in A.pods_api.list_locally_available_pods(show_remote_or_local=_A):
			A.pods_api.set_pod_context(A.pod_name);C=CloudPodsVersionManager._get_max_version_for_pod_from_platform(A.pod_name,B)
			if not C:return
			D=A.pods_api.get_max_version_no()
			if C==D:LOG.info('No new version available remotely. Nothing to pull');return
			if not lazy:E=','.join(map(lambda ver:str(ver),range(D+1,C+1)))
			else:E=D
			A._pull_versions(auth_headers=B,required_versions=E)
		else:A._clone_pod(auth_headers=B,lazy=lazy)
	def commit(A,message=_B):A.pods_api.set_pod_context(A.pod_name);A._add_state_to_cloud_pods_store();B=A.pods_api.commit(message=message);LOG.debug(f"Completed revision: {B}")
	def _download_version_product(D,version,retain=_A):
		A=version;E=D._get_presigned_url_for_version_product(version=A);F=E.get(_K);G=E.get(_L);B=new_tmp_file();C=new_tmp_file();download(F,B);download(G,C)
		if retain:from localstack_ext.bootstrap.pods.utils.remote_utils import extract_meta_and_state_archives as H;H(meta_archives={A:C},state_archives={A:B},config_context=D.pods_api.config_context)
		return{'metadata_archive':C,_M:B}
	def _get_presigned_url_for_version_product(A,version):
		B=version;C=A.create_platform_url(f"{A.pod_name}/version/product")
		if B!=-1:C+=f"?version={B}"
		E=get_auth_headers();D=safe_requests.get(C,headers=E)
		if D.status_code>=300:LOG.warning(f"Failed to retrieve presigned url from remote for version {B} of pod {A.pod_name}");return
		return json.loads(D.content)
	def _inject_from_remote(B,version,retain=_A):
		C=version;from localstack_ext.bootstrap.pods.utils.remote_utils import extract_meta_and_state_archives as F;D=B._get_presigned_url_for_version_product(version=C);G=D.get(_K);A=new_tmp_file();download(G,A);B.deploy_pod_into_instance(pod_path=A)
		if not retain:rm_rf(A);return _C
		H=D.get(_L);E=new_tmp_file();download(H,E);F(meta_archives={C:E},state_archives={C:A},config_context=B.pods_api.config_context);return _C
	@staticmethod
	def deploy_pod_into_instance(pod_path):
		A=pod_path;D=_A
		if os.path.isdir(A):
			B=new_tmp_dir()
			for E in PERSISTED_FOLDERS:
				F=os.path.join(A,E)
				if not os.path.exists(F):continue
				H=os.path.join(B,E);cp_r(F,H,rm_dest_on_conflict=_C)
			A=create_zip_file(B);rm_rf(B);D=_C
		I=load_file(A,mode='rb');G=get_pods_endpoint();C=requests.post(G,data=I)
		if C.status_code>=400:raise Exception('Unable to restore pod state via local pods management API %s (code %s): %s'%(G,C.status_code,C.content))
		if D:rm_rf(A)
		else:return A
	def inject(A,version,reset_state):
		B=version
		if not A.pods_api.config_context.pod_exists_locally(A.pod_name):LOG.debug(f"Pod {A.pod_name} does not exist locally. Requesting state from remote..");C=A._download_version_product(version=B).get(_M)
		else:
			A.pods_api.set_pod_context(A.pod_name)
			if B==-1:B=A.pods_api.get_max_version_no()
			C=A.pods_api.config_context.get_version_state_archive(B)
			if not C and A.pods_api.is_remotely_managed():
				LOG.debug('Fetching requested archive from remote..');D=A._download_version_product(version=B,retain=_C)
				if not D:return _A
				C=A.pods_api.commit_metamodel_utils.get_version_state_archive(B)
		if reset_state:reset_local_state(reset_data_dir=_C)
		A.deploy_pod_into_instance(C);return _C
	def list_versions(A):A.pods_api.set_pod_context(A.pod_name);B=A.pods_api.list_versions();return B
	def version_info(A,version):
		B=version;A.pods_api.set_pod_context(A.pod_name)
		if B==-1:B=A.pods_api.get_max_version_no()
		C=A.pods_api.get_version_info(B);return C
	def version_metamodel(A,version):
		B=version;from localstack_ext.bootstrap.pods.object_storage import get_object_storage_provider as D;A.pods_api.set_pod_context(A.pod_name)
		if B==-1:B=A.pods_api.get_max_version_no()
		E=A.pods_api.get_version_by_number(B);F=D(A.pods_api.config_context);G=F.get_revision_by_key(E.incoming_revision_ptr);C=A.pods_api.commit_metamodel_utils.reconstruct_metamodel(version=B,revision=G.revision_number+1)
		if not C and A.pods_api.is_remotely_managed():A._download_version_product(version=B,retain=_C);C=A.pods_api.commit_metamodel_utils.create_metamodel_from_state_files(version=B)
		return C
	def set_version(A,version,inject_version_state,reset_state,commit_before):
		B=version;A.pods_api.set_pod_context(A.pod_name);C=A.pods_api.set_active_version(version_no=B,commit_before=commit_before)
		if not C:LOG.warning(f"Could not find version {B}")
		if inject_version_state:A.inject(version=B,reset_state=reset_state)
		return C
	def list_version_commits(A,version):A.pods_api.set_pod_context(A.pod_name);B=A.pods_api.list_version_commits(version_no=version);return B
	def get_commit_diff(A,version,commit):A.pods_api.set_pod_context(A.pod_name);B=A.pods_api.commit_metamodel_utils.get_commit_diff(version_no=version,commit_no=commit);return B
	def register_remote(A,pod_name,ci_pod=_A):
		A.pods_api.set_pod_context(A.pod_name);B=A.pods_api.get_max_version_no()
		if B==0:A.pods_api.push('Init Version');B=1
		F=get_auth_headers();G=A.create_platform_url('register');C={_E:A.pod_name,_J:B,_H:ci_pod};C=json.dumps(C);D=safe_requests.post(G,C,headers=F)
		if D.status_code!=200:LOG.warning(f"Failed to register pod {A.pod_name}: {D.content}");return _A
		E=json.loads(D.content);H={_D:E.get(_D),_G:E.get(_E)};I=E.get(_F);A.pods_api.upload_version_and_product_space(presigned_urls=I);pods_api.register_remote(remote_info=H,config_context=A.pods_api.config_context);return _C
	def rename_pod(A,current_pod_name,new_pod_name):
		C=current_pod_name;B=new_pod_name;A.pods_api.set_pod_context(C)
		if B in A.pods_api.list_locally_available_pods():LOG.warning(f"{B} already exists locally");return _A
		if A.pods_api.is_remotely_managed():
			F=get_auth_headers();G=A.create_platform_url(f"{C}/rename");D={'new_pod_name':B};D=json.dumps(D);E=safe_requests.put(G,D,headers=F)
			if E.status_code!=200:LOG.warning(f"Failed to rename {C} to {B}: {E.content}");return _A
		A.pods_api.rename_pod(B);return _C
	def list_pods(A,fetch_remote):
		B=A.pods_api.list_locally_available_pods()
		if fetch_remote:
			C=get_auth_headers();D=A.create_platform_url('pods');E=safe_requests.get(D,headers=C);F=json.loads(E.content)
			for G in F.get('registered_pods')or[]:B.add(f"remote/{G}")
		return B
	@staticmethod
	def create_platform_url(request):A='%s/cpvcs'%constants.API_ENDPOINT;return os.path.join(A,request)
class PodConfigManagerMeta(type):
	def __getattr__(C,attr):
		def A(*D,**E):
			A=_B
			for F in C.CHAIN:
				try:
					B=getattr(F,attr)(*(D),**E)
					if B:
						if not A:A=B
						elif isinstance(B,list)and isinstance(A,list):A.extend(B)
				except Exception:
					if LOG.isEnabledFor(logging.DEBUG):LOG.exception('error during PodConfigManager call chain')
			if A is not _B:return A
			raise Exception('Unable to run operation "%s" for local or remote configuration'%attr)
		return A
class PodConfigManager(metaclass=PodConfigManagerMeta):
	CHAIN=[]
	@classmethod
	def pod_config(D,pod_name):
		A=pod_name;C=PodConfigManager.list_pods();B=[B for B in C if B[_E]==A]
		if not B:raise Exception('Unable to find config for pod named "%s"'%A)
		return B[0]
ALL_MANAGERS={_I:CloudPodsVersionManager}
def get_pods_manager(pods_name,pre_config=_B):
	B='backend';A=pre_config
	if A is _B:A={B:_I}
	C=A.get(B,_I)
	try:D=ALL_MANAGERS[C](pod_name=pods_name,pre_config=A)
	except KeyError as E:raise NotImplementedError from E
	return D
def init_cloudpods(pod_name,pre_config,**B):A=get_pods_manager(pods_name=pod_name);A.init()
def delete_pod(pod_name,remote,pre_config):A=get_pods_manager(pods_name=pod_name);B=A.delete(remote=remote);return B
def register_remote(pod_name,pre_config,**D):A=pod_name;B=get_pods_manager(pods_name=A);C=B.register_remote(pod_name=A,ci_pod=pre_config.get(_H,_A));return C
def rename_pod(current_pod_name,new_pod_name,pre_config,**D):A=new_pod_name;B=get_pods_manager(pods_name=A);C=B.rename_pod(current_pod_name=current_pod_name,new_pod_name=A);return C
def list_pods(remote,pre_config,**C):A=get_pods_manager(pods_name='');B=A.list_pods(fetch_remote=remote);return B
def commit_state(pod_name,pre_config,message=_B,**C):
	B=pod_name;A=get_pods_manager(pods_name=B);A.pods_api.set_pod_context(pod_name=B)
	if not A.pods_api.config_context.is_initialized():A.init()
	A.commit(message=message)
def inject_state(pod_name,version,reset_state,pre_config,**C):A=get_pods_manager(pods_name=pod_name);B=A.inject(version=version,reset_state=reset_state);return B
def list_versions(pod_name,pre_config,**C):A=get_pods_manager(pods_name=pod_name);B=A.list_versions();return B
def get_version_info(version,pod_name,pre_config,**C):A=get_pods_manager(pods_name=pod_name);B=A.version_info(version=version);return B
def get_version_metamodel(version,pod_name,pre_config,**C):A=get_pods_manager(pods_name=pod_name);B=A.version_metamodel(version=version);return B
def set_version(version,inject_version_state,reset_state,commit_before,pod_name,pre_config,**C):A=get_pods_manager(pods_name=pod_name);B=A.set_version(version=version,inject_version_state=inject_version_state,reset_state=reset_state,commit_before=commit_before);return B
def list_version_commits(version,pod_name,pre_config):A=get_pods_manager(pods_name=pod_name);B=A.list_version_commits(version=version);return B
def get_commit_diff(version,commit,pod_name,pre_config):A=get_pods_manager(pods_name=pod_name);B=A.get_commit_diff(version=version,commit=commit);return B
def push_overwrite(version,pod_name,comment,pre_config):A=get_pods_manager(pods_name=pod_name);A.push_overwrite(version=version,comment=comment)
def push_state(pod_name,pre_config=_B,squash_commits=_A,comment=_B,three_way=_A,register=_A,**F):
	B=pod_name;A=get_pods_manager(pods_name=B);A.pods_api.set_pod_context(pod_name=B)
	if not A.pods_api.config_context.is_initialized():A.init()
	D=clone(A.pod_config);C=A.push(comment=comment,three_way=three_way);D['size']=C.pod_size or C.pod_size_compressed;D['available_resources']=C.persisted_resource_names;E=_C
	if register:E&=A.register_remote(pod_name=B,ci_pod=pre_config.get(_H,_A))
	return E
def get_pods_endpoint():A=config.get_edge_url();return f"{A}{API_PATH_PODS}"
def pull_state(pod_name,inject_version_state=_A,reset_state_before=_A,lazy=_A,**C):
	A=pod_name
	if not A:raise Exception('Need to specify a pod name')
	B=get_pods_manager(pods_name=A);B.pull(inject_version_state=inject_version_state,reset_state_before=reset_state_before,lazy=lazy);print('Done.')
def reset_local_state(reset_data_dir=_A,exclude_from_reset=_B):
	C=exclude_from_reset;A=f"{get_pods_endpoint()}/state"
	if reset_data_dir:A+='/datadir'
	if C:A+=f"?exclude={','.join(C)}"
	print('Sending request to reset the service states in local instance ...');B=requests.delete(A)
	if B.status_code>=400:raise Exception('Unable to reset service state via local management API %s (code %s): %s'%(A,B.status_code,B.content))
	print('Done.')
def save_pods_config(options):A=get_pods_manager('');A.pods_api.config_context.save_pods_config(options=options)
def get_pods_config():A=get_pods_manager('');return A.pods_api.config_context.get_pods_config_cache()
def is_initialized(pod_name):A=get_pods_manager(pods_name=pod_name);return A.pods_api.config_context.is_initialized()
def get_data_dir_from_container():
	try:
		C=DOCKER_CLIENT.inspect_container(config.MAIN_CONTAINER_NAME);D=C.get('Mounts');E=C.get('Config',{}).get('Env',[]);A=[A for A in E if A.startswith('DATA_DIR=')][0].partition('=')[2]
		try:B=[B for B in D if B['Destination']==A][0]['Source'];B=re.sub('^(/host_mnt)?','',B);A=B
		except Exception:LOG.debug(f"No docker volume for data dir '{A}' detected")
		return A
	except Exception:LOG.warning('Unable to determine DATA_DIR from LocalStack Docker container - please make sure $MAIN_CONTAINER_NAME is configured properly')
def get_persisted_resource_names(data_dir):
	E='api_states';D=data_dir;B=[]
	with os.scandir(D)as C:
		for A in C:
			if A.is_dir()and A.name!=E:B.append(A.name)
	with os.scandir(os.path.join(D,E))as C:
		for A in C:
			if A.is_dir()and len(os.listdir(A.path))>0:B.append(A.name)
	LOG.debug(f"Detected state files for the following APIs: {B}");return B
PODS_NAMESPACE_DELIM='-'