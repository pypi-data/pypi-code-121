_C='moto'
_B='localstack'
_A='kinesis'
import inspect,logging,os
from typing import Type,Union
import localstack.config as localstack_config,moto.core
from localstack.constants import TEST_AWS_ACCOUNT_ID
from localstack.services.generic_proxy import RegionBackend
from localstack.services.plugins import StateLifecycle
from localstack.utils.files import cp_r
from localstack.utils.testutil import create_zip_file
from moto.applicationautoscaling.models import ApplicationAutoscalingBackend
from moto.autoscaling.models import AutoScalingBackend
from moto.core.utils import BackendDict
from moto.redshift.models import RedshiftBackend
import localstack_ext.config as ext_config
from localstack_ext.bootstrap.pods.service_state import BackendState,ServiceKey,ServiceState
from localstack_ext.utils.cloud_pods import SINGLE_GLOBAL_REGION_NAME
from localstack_ext.utils.lookup_utils import get_backend_state
from localstack_ext.utils.persistence import marshal_backend
SERVICES_WITHOUT_STATE=['apigatewaymanagementapi','azure','azure','cloudsearch','cloudwatch','configservice','docdb','elasticsearch','iot-data','iot-jobs-data','iotanalytics','iotevents','iotevents-data','iotwireless','mediaconvert','mediastore-data','neptune','qldb-session','rds-data','redshift-data','resource-groups','resourcegroupstaggingapi','route53resolver','s3control','sagemaker-runtime','ssm','swf','timestream-query','timestream-write']
EXTERNAL_SERVICES=['dynamodb',_A,'stepfunctions']
NON_SERVICE_APIS=['edge','support','logs']
LOG=logging.getLogger(__name__)
def _service_state_from_region_backend(service_backend,api):
	from localstack_ext.constants import REGION_STATE_FILE as B;A=ServiceState()
	for (C,D) in service_backend.regions().items():E=ServiceKey(account_id=TEST_AWS_ACCOUNT_ID,region=C,service=api);F=BackendState(E,{B:marshal_backend(D)});A.add(state_to_add=F)
	return A
def _service_state_from_backend_state(service_backend,api):
	A=service_backend;from localstack.constants import TEST_AWS_ACCOUNT_ID as C;from localstack_ext.constants import MOTO_BACKEND_STATE_FILE as D;B=ServiceState()
	if not isinstance(A,dict):A={SINGLE_GLOBAL_REGION_NAME:A}
	for (E,F) in A.items():G=ServiceKey(account_id=C,region=E,service=api);H=BackendState(G,{D:marshal_backend(F)});B.add(state_to_add=H)
	return B
def _service_state_from_backend(backend,api,memory_management):
	B=memory_management;A=backend
	if B==_B:return _service_state_from_region_backend(service_backend=A,api=api)
	if B==_C:return _service_state_from_backend_state(service_backend=A,api=api)
class PersistenceLifeCycle(StateLifecycle):
	def assets_root(A):raise NotImplementedError()
	def get_assets_location(A):B=localstack_config.dirs.data if ext_config.PERSIST_ALL else localstack_config.dirs.tmp;return os.path.join(B,A.assets_root())
	def retrieve_assets(A):return create_zip_file(A.get_assets_location(),get_content=True)
	def inject_assets(A,pod_assets_dir):B=A.get_assets_location();C=os.path.join(pod_assets_dir,A.assets_root());cp_r(C,B)
	def on_after_reset(A):0
	def retrieve_state(E):
		A=ServiceState();B=E.service;F=[_C,_B]
		for C in F:
			D=get_backend_state(api=B,memory_manager=C)
			if D:A.add(_service_state_from_backend(backend=D,api=B,memory_management=C))
		return A
	def inject_state(A,state):0
	def reset_state(B):
		from localstack.utils.common import mkdir,rm_rf;from localstack_ext.utils.cloud_pods import restart_kinesis as H
		if B.service==_A:
			if localstack_config.dirs.data:D=os.path.join(localstack_config.dirs.data,_A);rm_rf(D);mkdir(D)
			H();return
		E=get_backend_state(B.service,_C);F=get_backend_state(B.service,_B);C=[];E and C.append(E);F and C.append(F)
		if not C:
			if B.service not in SERVICES_WITHOUT_STATE+EXTERNAL_SERVICES+NON_SERVICE_APIS:LOG.debug("Unable to determine state container for service '%s'",B.service)
			return
		for A in C:
			if inspect.isclass(A)and issubclass(A,RegionBackend):A.reset();continue
			if isinstance(A,dict):
				for I in A.keys():reset_moto_backend_state(A,I)
				if isinstance(A,moto.core.utils.BackendDict):A.clear()
				continue
			if isinstance(A,moto.core.BaseBackend):G=getattr(A,'region_name',getattr(A,'region',None));A.__dict__={};A.__init__(*([G]if G else[]));continue
			LOG.warning("Unable to reset state for service '%s', state container: %s",B.service,A)
		B.on_after_reset()
def reset_moto_backend_state(state_container,region_key):
	D=state_container;B=region_key;A=D.get(B);E=getattr(A,'reset',None)
	if E and callable(E):E();return A
	F=type(A);C=[B]if len(inspect.signature(F.__init__).parameters)>1 else[]
	if isinstance(A,ApplicationAutoscalingBackend):C.append(A.ecs_backend)
	elif isinstance(A,RedshiftBackend):C.insert(0,A.ec2_backend)
	elif isinstance(A,AutoScalingBackend):C=[A.ec2_backend,A.elb_backend,A.elbv2_backend]
	D[B]=F(*(C));return D[B]
class DummyProvider(PersistenceLifeCycle):
	def __init__(A,service):A.service=service