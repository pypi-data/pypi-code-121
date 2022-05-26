import os
import tarfile

from ..clients.service_foundry_client import ServiceFoundryServiceClient
from ..const import SFY_DIR
from ..packaged_component import PackagedComponent
from ..session_factory import get_session


def make_tarfile(output_filename, source_dir):
    with tarfile.open(output_filename, "w:gz") as tar:
        for fn in os.listdir(source_dir):
            p = os.path.join(source_dir, fn)
            tar.add(p, arcname=fn)


def deploy(packaged_component: PackagedComponent):
    package_zip = f"{SFY_DIR}/build.tar.gz"
    make_tarfile(package_zip, packaged_component.build_dir)

    session = get_session()
    tf_client = ServiceFoundryServiceClient(session)
    resp = tf_client.build_and_deploy(
        packaged_component.service_def.get_component(), package_zip
    )
    return resp
