import inspect
import logging
import os
from typing import Type,Union
import localstack.config as localstack_config
import moto.core
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
SERVICES_WITHOUT_STATE=["apigatewaymanagementapi","azure","azure","cloudsearch","cloudwatch","configservice","docdb","elasticsearch","iot-data","iot-jobs-data","iotanalytics","iotevents","iotevents-data","iotwireless","mediaconvert","mediastore-data","neptune","qldb-session","rds-data","redshift-data","resource-groups","resourcegroupstaggingapi","route53resolver","s3control","sagemaker-runtime","ssm","swf","timestream-query","timestream-write"]
EXTERNAL_SERVICES=["dynamodb","kinesis","stepfunctions"]
NON_SERVICE_APIS=["edge","support","logs"]
LOG=logging.getLogger(__name__)
def _service_state_from_region_backend(service_backend:Type[RegionBackend],api:str)->ServiceState:
 from localstack_ext.constants import REGION_STATE_FILE
 service_state=ServiceState()
 for region,backend in service_backend.regions().items():
  service_key=ServiceKey(account_id=TEST_AWS_ACCOUNT_ID,region=region,service=api)
  backend_state=BackendState(service_key,{REGION_STATE_FILE:marshal_backend(backend)})
  service_state.add(state_to_add=backend_state)
 return service_state
def _service_state_from_backend_state(service_backend:BackendDict,api:str)->ServiceState:
 from localstack.constants import TEST_AWS_ACCOUNT_ID
 from localstack_ext.constants import MOTO_BACKEND_STATE_FILE
 service_state=ServiceState()
 if not isinstance(service_backend,dict):
  service_backend={SINGLE_GLOBAL_REGION_NAME:service_backend}
 for region,backend in service_backend.items():
  service_key=ServiceKey(account_id=TEST_AWS_ACCOUNT_ID,region=region,service=api)
  backend_state=BackendState(service_key,{MOTO_BACKEND_STATE_FILE:marshal_backend(backend)})
  service_state.add(state_to_add=backend_state)
 return service_state
def _service_state_from_backend(backend:Union[Type[RegionBackend],BackendDict],api:str,memory_management:str)->ServiceState:
 if memory_management=="localstack":
  return _service_state_from_region_backend(service_backend=backend,api=api)
 if memory_management=="moto":
  return _service_state_from_backend_state(service_backend=backend,api=api)
class PersistenceLifeCycle(StateLifecycle):
 def assets_root(self)->str:
  raise NotImplementedError()
 def get_assets_location(self)->str:
  base_path=(localstack_config.dirs.data if ext_config.PERSIST_ALL else localstack_config.dirs.tmp)
  return os.path.join(base_path,self.assets_root())
 def retrieve_assets(self)->bytes:
  return create_zip_file(self.get_assets_location(),get_content=True)
 def inject_assets(self,pod_assets_dir:str):
  current_assets=self.get_assets_location()
  pod_assets=os.path.join(pod_assets_dir,self.assets_root())
  cp_r(pod_assets,current_assets)
 def on_after_reset(self):
  pass
 def retrieve_state(self)->ServiceState:
  service_state=ServiceState()
  service_name=self.service
  memory_managements=["moto","localstack"]
  for memory_management in memory_managements:
   state=get_backend_state(api=service_name,memory_manager=memory_management)
   if state:
    service_state.add(_service_state_from_backend(backend=state,api=service_name,memory_management=memory_management))
  return service_state
 def inject_state(self,state:ServiceState)->None:
  pass
 def reset_state(self)->None:
  from localstack.utils.common import mkdir,rm_rf
  from localstack_ext.utils.cloud_pods import restart_kinesis
  if self.service=="kinesis":
   if localstack_config.dirs.data:
    kinesis_state_dir=os.path.join(localstack_config.dirs.data,"kinesis")
    rm_rf(kinesis_state_dir)
    mkdir(kinesis_state_dir)
   restart_kinesis()
   return
  state_moto=get_backend_state(self.service,"moto")
  state_ls=get_backend_state(self.service,"localstack")
  state_containers=[]
  state_moto and state_containers.append(state_moto)
  state_ls and state_containers.append(state_ls)
  if not state_containers:
   if self.service not in SERVICES_WITHOUT_STATE+EXTERNAL_SERVICES+NON_SERVICE_APIS:
    LOG.debug("Unable to determine state container for service '%s'",self.service)
   return
  for state_container in state_containers:
   if inspect.isclass(state_container)and issubclass(state_container,RegionBackend):
    state_container.reset()
    continue
   if isinstance(state_container,dict):
    for region in state_container.keys():
     reset_moto_backend_state(state_container,region)
    if isinstance(state_container,moto.core.utils.BackendDict):
     state_container.clear()
    continue
   if isinstance(state_container,moto.core.BaseBackend):
    region_name=getattr(state_container,"region_name",getattr(state_container,"region",None))
    state_container.__dict__={}
    state_container.__init__(*([region_name]if region_name else[]))
    continue
   LOG.warning("Unable to reset state for service '%s', state container: %s",self.service,state_container)
  self.on_after_reset()
def reset_moto_backend_state(state_container,region_key):
 instance=state_container.get(region_key)
 reset_method=getattr(instance,"reset",None)
 if reset_method and callable(reset_method):
  reset_method()
  return instance
 clazz=type(instance)
 args=[region_key]if len(inspect.signature(clazz.__init__).parameters)>1 else[]
 if isinstance(instance,ApplicationAutoscalingBackend):
  args.append(instance.ecs_backend)
 elif isinstance(instance,RedshiftBackend):
  args.insert(0,instance.ec2_backend)
 elif isinstance(instance,AutoScalingBackend):
  args=[instance.ec2_backend,instance.elb_backend,instance.elbv2_backend]
 state_container[region_key]=clazz(*args)
 return state_container[region_key]
# Created by pyminifier (https://github.com/liftoff/pyminifier)
