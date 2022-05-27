"""
See how-to on our confluence page for more details.
Use Azure python sdk to sync the files with Azure Files Share service.
The config file shall have a settings in a format like:
    azure_config = {
            'azure_connection_string' : r'{the azure connection string}'
            'share_name' : "/sharename/",
            'parent_dir_path' : r"volume/data/" : ALAWAYS start with a test file, to make sure you don't mess up the other folders/files
        }
"""

import os
import sys
from azure.storage.fileshare import ShareClient

basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(basedir)
import config


class AzureConnection():
    """
    connection_string: the connection_string which functions as a token for the Azure connection
    share_name: the share name in Azure
    """
    def __init__(self):
        self.connection_string = config.azure_config['azure_connection_string']
        self.share_name = config.azure_config['share_name']
        self.share_client = ShareClient.from_connection_string(self.connection_string, share_name=self.share_name)

    def list_files_and_dirs(self, dir_client):
        """
        List all the files and folders under this directory_path.
        :param dir_client: The connection to a specified directory
        :return: two lists consist of files and subfolders separately
        """
        my_list = list(dir_client.list_directories_and_files())
        subdir_list = [x['name'] for x in my_list if x['is_directory'] is True]
        file_list = [x['name'] for x in my_list if x['is_directory'] is False]
        return file_list, subdir_list

    def create_directory(self, dir_path):
        """
        Create a ShareDirectoryClient from a connection string
        :param dir_path: The directory_path
        :return: a share_client which connects with the specified directory,
                    and a Flag to indicate if this directory exists before
        """
        dir_client = self.share_client.get_directory_client(directory_path=dir_path)
        dir_already_existed = False
        try:
            dir_client.create_directory()
        except:
            dir_already_existed = True
        return dir_client, dir_already_existed


    def empty_folder(self, dir_client, delete_folder = False):
        """
        To empty a folder including all the subfolders and files within.
        :param dir_client: The share to connect with this directory
        :param delete_folder: To delete the folder as well. If yes then the whole folder will be removed, otherwise only remove the files.
        """
        file_list, subdir_list = self.list_files_and_dirs(dir_client)
        if len(subdir_list)>0:
            for subdir in subdir_list:
                self.empty_folder(dir_client.get_subdirectory_client(subdir), delete_folder=True)
        for file in file_list:
            dir_client.delete_file(file)
        if delete_folder:
            dir_client.delete_directory()

    def create_subdirectory_and_upload_file(self, parentdir_path, subdir_path, local_file_path, filename):
        """
        Create a subfolder and upload files to this folder
        :param parentdir_path: The parent directory
        :param subdir_path: the subfolder directory
        :param local_file_path: local file directory from which to upload the files
        :param filename: filename to be uploaded
        :return:
        """
        _, _ = self.create_directory(parentdir_path)
        dir_path = os.path.join(parentdir_path,subdir_path)
        subdir, dir_already_existed = self.create_directory(dir_path)
        if dir_already_existed:
            self.empty_folder(subdir, delete_folder=False)
        # Upload a file to the subdirectory
        with open(os.path.join(local_file_path,filename), "rb") as source:
            subdir.upload_file(file_name=filename, data=source)

    def create_directory_and_upload_file(self, parentdir_path, local_file_path, filename):
        """
        Create a folder and upload files to this folder
        :param parentdir_path: The parent directory
        :param local_file_path: local file directory from which to upload the files
        :param filename: filename to be uploaded
        :return:
        """
        # Get the directory client
        parentdir_dir, _ = self.create_directory(parentdir_path)
        # Upload a file to the subdirectory
        with open(os.path.join(local_file_path, filename), "rb") as source:
            parentdir_dir.upload_file(file_name=filename, data=source)