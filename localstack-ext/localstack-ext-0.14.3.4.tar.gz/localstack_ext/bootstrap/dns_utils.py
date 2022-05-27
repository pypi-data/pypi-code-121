import logging
LOG=logging.getLogger(__name__)
def configure_systemd(revert):
	I='resolvectl';H='sudo';A=False;from subprocess import CalledProcessError as K;from localstack import config as D;from localstack.utils.container_utils.container_client import ContainerException as L;from localstack.utils.docker_utils import DOCKER_CLIENT as E;from localstack.utils.run import is_linux as M,run as F,to_str as N
	if not M():LOG.warning('Command only supported on GNU/Linux')
	try:
		O=E.get_container_ip(D.MAIN_CONTAINER_NAME);G=E.get_networks(D.MAIN_CONTAINER_NAME);G=G[0];J=E.inspect_network(G);B=J['Options'].get('com.docker.network.bridge.name');B=B or f"br-{J['Id'][:12]}"
		if revert:C=[H,I,'revert',B];F(C,shell=A,print_error=A);LOG.info('Reverting DNS config completed!')
		else:C=[H,I,'dns',B,O];F(C,shell=A,print_error=A);C=[H,I,'domain',B,'~amazonaws.com','~aws.amazon.com','~cloudfront.net','~localhost.localstack.cloud'];F(C,shell=A,print_error=A);LOG.info('Setting DNS config completed!')
	except L:
		if D.DEBUG:LOG.exception('Error while getting container information')
		LOG.warning('LocalStack container might not be running. Is container %s running?',D.MAIN_CONTAINER_NAME);LOG.warning('Is $MAIN_CONTAINER_NAME set correctly?')
	except K as P:LOG.warning('Error while configuring systemd-resolved: %s',N(P.output).strip())