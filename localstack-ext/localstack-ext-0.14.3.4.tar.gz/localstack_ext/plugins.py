_J='neptune'
_I='transfer'
_H='mediastore'
_G='elasticache'
_F='apigatewayv2'
_E='apigateway'
_D='azure'
_C='athena'
_B='s3'
_A='rds'
import logging,os
from localstack import config as localstack_config
from localstack.runtime import hooks
from localstack.runtime.hooks import on_infra_ready
from localstack.services.edge import ROUTER
from localstack.utils import common
from localstack.utils.bootstrap import API_DEPENDENCIES,LocalstackContainer,get_enabled_apis,is_api_enabled
from localstack.utils.container_utils.container_client import VolumeBind
from localstack_ext import config as config_ext
from localstack_ext.aws.protocol import service_router
from localstack_ext.bootstrap import install,licensing,local_daemon
LOG=logging.getLogger(__name__)
EXTERNAL_PORT_APIS=_E,_F,_C,'cloudfront','codecommit','ecs','ecr',_G,_H,_A,_I,'kafka',_J,_D
API_DEPENDENCIES.update({'amplify':[_B,'appsync','cognito'],_E:[_F],_C:['emr'],'docdb':[_A],'ecs':['ecr'],_G:['ec2'],'elb':['elbv2'],'emr':[_C,_B],'glacier':[_B],'glue':[_A],'iot':['iotanalytics','iot-data','iotwireless'],'kinesisanalytics':['kinesis','dynamodb'],_J:[_A],_A:['rds-data'],_H:['mediastore-data'],'redshift':['redshift-data'],'timestream':['timestream-write','timestream-query'],_I:[_B]})
get_enabled_apis.cache_clear()
def api_key_configured():A='LOCALSTACK_API_KEY';return True if os.environ.get(A)and os.environ.get(A).strip()else False
def modify_edge_port_config():
	if os.environ.get('EDGE_PORT')and not localstack_config.EDGE_PORT_HTTP:LOG.warning(('!! Configuring EDGE_PORT={p} without setting EDGE_PORT_HTTP may lead '+'to issues; better leave the defaults, or set EDGE_PORT=443 and EDGE_PORT_HTTP={p}').format(p=localstack_config.EDGE_PORT))
	else:A=localstack_config.EDGE_PORT;localstack_config.EDGE_PORT=443;localstack_config.EDGE_PORT_HTTP=A
@hooks.install(should_load=api_key_configured)
def install_pro_libs():install.install_libs()
@hooks.on_infra_start(should_load=api_key_configured)
def add_custom_edge_routes():from localstack_ext.services.xray.routes import store_xray_records as A;ROUTER.add('/xray_records',A,methods=['POST'])
@hooks.prepare_host(priority=100,should_load=api_key_configured)
def activate_pro_key_on_host():
	with licensing.prepare_environment():LOG.debug('pro activation done')
@hooks.prepare_host(should_load=api_key_configured)
def create_dns_forward():
	try:from localstack_ext.services import dns_server as A;A.setup_network_configuration()
	except Exception as B:LOG.warning('Unable to start DNS: %s'%B)
@hooks.prepare_host(should_load=api_key_configured)
def start_ec2_daemon():
	try:
		if is_api_enabled('ec2')and config_ext.EC2_AUTOSTART_DAEMON:LOG.debug('Starting EC2 daemon...');local_daemon.start_in_background()
	except Exception as A:LOG.warning('Unable to start local daemon process: %s'%A)
@hooks.configure_localstack_container(priority=10,should_load=api_key_configured)
def configure_pro_container(container):
	A=container
	try:
		from localstack_ext.services import dns_server as B;C=[]
		if config_ext.use_custom_dns():
			if not common.is_port_open(B.DNS_PORT,protocols='tcp'):C+=['-p','{a}:{p}:{p}'.format(a=config_ext.DNS_ADDRESS,p=B.DNS_PORT)]
			if not common.is_port_open(B.DNS_PORT,protocols='udp'):C+=['-p','{a}:{p}:{p}/udp'.format(a=config_ext.DNS_ADDRESS,p=B.DNS_PORT)]
		A.additional_flags.extend(C)
	except Exception as E:LOG.warning('failed to configure DNS: %s',E)
	modify_edge_port_config()
	if is_api_enabled('eks'):
		D=os.path.expanduser('~/.kube/config')
		if os.path.exists(D):A.volumes.add(VolumeBind(D,'/root/.kube/config'))
	if is_api_enabled(_D):A.ports.add(5671)
	if os.environ.get('AZURE'):A.ports.add(config_ext.PORT_AZURE)
@hooks.on_infra_start(should_load=api_key_configured,priority=10)
def setup_pro_infra():
	_setup_logging()
	if not localstack_config.SKIP_SSL_CERT_DOWNLOAD:install.setup_ssl_cert()
	modify_edge_port_config()
	with licensing.prepare_environment():
		try:from localstack_ext.services import dns_server as B;B.setup_network_configuration()
		except Exception as A:LOG.warning('error setting up dns server: %s',A)
		try:from localstack_ext.bootstrap.dashboard import dashboard_extended as C;from localstack_ext.services import edge;from localstack_ext.utils import persistence as D;from localstack_ext.utils.aws import aws_utils as E;D.enable_extended_persistence();C.patch_dashboard();service_router.patch_service_router();edge.patch_start_edge();patch_start_infra();E.patch_aws_utils();set_default_providers_to_pro()
		except Exception as A:
			if LOG.isEnabledFor(level=logging.DEBUG):LOG.exception('error enabling pro code')
			else:LOG.error('error enabling pro code: %s',A)
def set_default_providers_to_pro():
	C='pro';from localstack.services.plugins import SERVICE_PLUGINS as B;D=B.apis_with_provider(C);localstack_config.SERVICE_PROVIDER_CONFIG.bulk_set_provider_if_not_exists(D,C);E=[_D]
	for A in E:
		if not is_api_enabled(A):continue
		try:LOG.debug('loading service plugin for %s',A);B.get_service_container(A).start()
		except Exception as F:LOG.error('error while loading service %s: %s',A,F)
def patch_start_infra():
	from localstack.services import infra as B
	try:from localstack_ext.utils.aws.metadata_service import start_metadata_service as A
	except Exception:A=None
	def C(asynchronous,apis,is_in_docker,*B,**C):
		if common.in_docker():
			try:A and A()
			except Exception:pass
		E=config_ext.ENFORCE_IAM
		try:config_ext.ENFORCE_IAM=False;return D(asynchronous,apis,is_in_docker,*(B),**C)
		finally:config_ext.ENFORCE_IAM=E
	D=B.do_start_infra;B.do_start_infra=C
@on_infra_ready(should_load=api_key_configured)
def initialize_health_info():from localstack_ext.utils.persistence import update_persistence_health_info as A;A()
def _setup_logging():A=logging.DEBUG if localstack_config.DEBUG else logging.INFO;logging.getLogger('localstack_ext').setLevel(A);logging.getLogger('botocore').setLevel(logging.INFO);logging.getLogger('kubernetes').setLevel(logging.INFO);logging.getLogger('pyftpdlib').setLevel(logging.INFO);logging.getLogger('pyhive').setLevel(logging.INFO);logging.getLogger('websockets').setLevel(logging.INFO);logging.getLogger('asyncio').setLevel(logging.INFO);logging.getLogger('hpack').setLevel(logging.INFO);logging.getLogger('jnius.reflect').setLevel(logging.INFO);logging.getLogger('dulwich').setLevel(logging.ERROR);logging.getLogger('kazoo').setLevel(logging.ERROR);logging.getLogger('postgresql_proxy').setLevel(logging.WARNING);logging.getLogger('intercept').setLevel(logging.WARNING);logging.getLogger('root').setLevel(logging.WARNING);logging.getLogger('').setLevel(logging.WARNING)