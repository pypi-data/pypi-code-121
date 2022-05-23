from shutil import copy2
from .thread import get_bin_dir
import zipfile
from os import remove, mkdir
from os.path import exists
import shutil
from typing import Optional

sdkversion = '1.5.94'


def _create_or_clean_bin_dir():
    path = get_bin_dir()
    if not exists(path):
        # Create the bin folder if it's not there
        mkdir(path)
    else:
        # Otherwise delete it and start afresh
        shutil.rmtree(path)
        mkdir(path)


def _get_python_provider_factory_package(zip_location=None):

    zipfile_lib_path = get_bin_dir() + f'Finbourne.Honeycomb.PythonProviders.{sdkversion}.zip'

    if zip_location is None:
        print("  Connecting to S3 and downloading zip file...")
        import boto3
        sess = boto3.Session(profile_name='fbn-prod-developers')
        s3 = sess.client('s3')
        s3.download_file(
            Bucket='fbn-build-artifacts',
            Key=f'honeycomb/py-providers/Finbourne.Honeycomb.PythonProviders.{sdkversion}.zip',
            Filename=zipfile_lib_path
        )
    else:
        # copy it from local folder rather than download from S3...
        shutil.copy(zip_location, zipfile_lib_path)

    # Unzip it
    print("  Unzipping it...", end='')
    with zipfile.ZipFile(zipfile_lib_path, "r") as zf:
        zf.extractall(get_bin_dir())
    print(' done.')


def _copy_certs_to_factory_dir(certs_path):
    print("  Copying certs...", end='')
    copy2(certs_path + '/client_cert.pem', get_bin_dir() + '/content/')
    copy2(certs_path + '/client_key.pem', get_bin_dir() + '/content/')
    print(' done.')


def _clean_up_and_validate():
    print("  Cleaning up...", end='')
    zipfile_path = get_bin_dir() + f'Finbourne.Honeycomb.PythonProviders.{sdkversion}.zip'
    remove(zipfile_path)
    print(" done.")

    print("  Checking everything's in place...", end='')

    factory_path = get_bin_dir() + '/content/Finbourne.Honeycomb.Host.dll'
    if not exists(factory_path):
        raise ValueError(
            f"Luminesce python provider factory dll was not found at {factory_path}. "
            "You may need to run the setup with lumipy.provider.setup(<path to certs>).\n"
        )

    client_cert = get_bin_dir() + '/content/client_cert.pem'
    if not exists(client_cert):
        raise ValueError(f'Client Cert not found at {client_cert}')

    client_key = get_bin_dir() + '/content/client_key.pem'
    if not exists(client_key):
        raise ValueError(f'Client Cert not found at {client_key}')
    print(" done.")


def setup_python_providers(certs_path: str, zip_location: Optional[str] = None) -> None:

    """Set up the local python provider infrastructure.

    This will do the following:\
        * download the python-based provider binaries zip from S3
        * extract it to lumipy/provider/bin in the lumipy library
        * copy the certs at a given path to the Host.dll location
        * Clean up the zip file

    Args:
        zip_location (Optional[str]): location of python provider factory zip file. If not supplied the setup helper
        will attempt to access the zip file hosted in S3 (Finbourne-internal use only)
        certs_path (str): path to a folder containing both your client_key.pem and client_cert.pem files.

    """
    print("Setting up the reqired parts for python providers 🛠")
    _create_or_clean_bin_dir()
    _get_python_provider_factory_package(zip_location)
    _copy_certs_to_factory_dir(certs_path)
    _clean_up_and_validate()
    print("All set! You can now build and run python providers.")
