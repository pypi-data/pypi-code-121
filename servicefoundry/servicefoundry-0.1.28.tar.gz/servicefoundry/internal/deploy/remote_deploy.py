import os
import tarfile

from ..clients.service_foundry_client import ServiceFoundryServiceClient
from ..session_factory import get_session


def make_tarfile(output_filename, source_dir):
    with tarfile.open(output_filename, "w:gz") as tar:
        for fn in os.listdir(source_dir):
            p = os.path.join(source_dir, fn)
            tar.add(p, arcname=fn)


def deploy(service_def, package_dir, build_dir, stdout):
    package_zip = f"{build_dir}/build.tar.gz"
    make_tarfile(package_zip, package_dir)

    session = get_session()
    tf_client = ServiceFoundryServiceClient(session)
    resp = tf_client.build_and_deploy(service_def, package_zip)
    return resp
