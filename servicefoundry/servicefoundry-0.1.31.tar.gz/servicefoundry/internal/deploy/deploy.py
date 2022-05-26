from servicefoundry.internal.deploy.local_deploy import deploy as local_deploy
from servicefoundry.internal.deploy.remote_deploy import deploy as remote_deploy


def deploy(packaged_component):
    return remote_deploy(packaged_component)


def deploy_local(packaged_component, callback):
    return local_deploy(packaged_component, callback)
