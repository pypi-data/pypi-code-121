from servicefoundry.core import is_notebook
from servicefoundry.core.notebook.notebook_util import get_default_callback
from servicefoundry.internal.clients.service_foundry_client import (
    ServiceFoundryServiceClient,
)
from servicefoundry.internal.deploy.deploy import deploy as __deploy_remote
from servicefoundry.internal.deploy.deploy import deploy_local as __deploy_local
from servicefoundry.internal.package.package import package

process = None


def _deploy_local(packaged_output, callback):
    global process
    if not is_notebook():
        process = __deploy_local(packaged_output, callback)
        process.join()
    else:
        callback.start_panel()
        if process is not None and process.is_alive():
            callback.print_line("Stopping the old process.")
            process.stop()
            process.join()
            callback.print_line("Old process stopped.")
        process = __deploy_local(packaged_output, callback)
        callback.close_panel()


def deploy_local():
    callback = get_default_callback()
    packaged_output = package(callback=callback)
    return _deploy_local(packaged_output, callback)


def _deploy(packaged_output, callback):
    deployment = __deploy_remote(packaged_output)
    tfs_client = ServiceFoundryServiceClient.get_client()
    tfs_client.tail_logs(deployment["runId"], wait=True, callback=callback)
    return deployment


def deploy():
    callback = get_default_callback()
    packaged_output = package(callback=callback)
    _deploy(packaged_output, callback)
