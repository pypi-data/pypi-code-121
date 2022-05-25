from servicefoundry.internal.build import LOCAL, REMOTE, build_and_deploy
from servicefoundry.internal.clients.service_foundry_client import (
    ServiceFoundryServiceClient,
)
from servicefoundry.internal.output_callback import OutputCallBack

thread = None


def _deploy_local(project_folder, output_callback):
    return build_and_deploy(
        base_dir=project_folder,
        build=LOCAL,
        callback=output_callback,
    )


def deploy_local(project_folder=""):
    thread = _deploy_local(project_folder, OutputCallBack())
    thread.join()


def deploy(project_folder=""):
    deployment = build_and_deploy(base_dir=project_folder, build=REMOTE)
    print(deployment)
    # tail logs
    tfs_client = ServiceFoundryServiceClient.get_client()
    tfs_client.tail_logs(deployment["runId"], wait=True)
