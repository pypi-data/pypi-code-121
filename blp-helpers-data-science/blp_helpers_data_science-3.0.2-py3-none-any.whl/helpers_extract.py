from azure.storage.blob import ContainerClient
from io import StringIO
import yaml
import pandas as pd


def get_data_using_catalog(dataset_name, config_version, azure_storage_connection_string):
    """Returns a pandas dataframe for a dataset_name stored in a catalog.yml file

    It either gets the data from azure or local

    Filepaths are stored in the catalog.yml according to kedro
    See: https://kedro.readthedocs.io/en/stable/02_get_started/05_example_project.html

    Parameters
    ----------
    dataset_name : str
        The name of the dataset to be loaded according to the catalog.yml-file
    config_version : str
        Which conf-folder to use, according to kedro it can be local or base
    azure_storage_connection_string : str
        Connection string for Azure Data Lake (see Azure Doc. for more info)
    Returns
    -------
    A pandas dataframe
    """

    with open("../conf/{}/catalog.yml".format(config_version), 'r') as stream:
        try:
            yaml_file_content = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    # the storage_provider determines if the file is on azure or local
    storage_provider = yaml_file_content.get(dataset_name).get('storage_provider')

    # depending whether it is on azure or local change loading way
    if storage_provider == 'local':
        # get the relative path
        data_file_path = '../' + yaml_file_content.get(dataset_name).get('filepath')
        df = pd.read_csv(data_file_path)
    else:  # it is azure
        data_container_name = yaml_file_content.get(dataset_name).get('container_name')
        data_blob_name = yaml_file_content.get(dataset_name).get('filepath')
        container_client = ContainerClient.from_connection_string(
            conn_str=azure_storage_connection_string
            , container_name=data_container_name
        )
        # Download blob as StorageStreamDownloader object (stored in memory)
        downloaded_blob = container_client.download_blob(data_blob_name)

        df = pd.read_csv(StringIO(downloaded_blob.content_as_text()))

    return df