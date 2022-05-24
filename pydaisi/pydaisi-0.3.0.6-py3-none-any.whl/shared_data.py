import requests
import os
from pathlib import Path
from pydaisi.pydaisi import daisi_base_url
from tqdm import tqdm
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor

shared_data_base_route = "/ui-api/shared-data"


def post_with_progress(session, url: str, fields: dict) -> requests.models.Response:
    """
    fields: example {"field": ('filename', open('file.py', 'rb'))}
    """
    e = MultipartEncoder(fields=fields)
    with tqdm(total=e.len) as bar:
        m = MultipartEncoderMonitor(
            e, lambda monitor: bar.update(monitor.bytes_read - bar.n)
        )
        return session.post(url, data=m, headers={"Content-Type": m.content_type})


class SharedDataObject():
    """
    General Shared Data object, i.e. folder, file
    """

    def __init__(self, session, base_url: str, name: str, id_: int):
        """
        :param session: requests session from client
        :param name: absolute path for the object
        :param id_: object id
        :param base_url: The default URL to use for connecting to the daisi
        """
        self.base_url = base_url
        self.folders_base_url = self.base_url + "/folders"
        self.files_base_url = self.base_url + "/files"
        
        self.session = session
        self.name = name
        self.id = id_ if id_ != -1 else self.get_id(list(Path(name).parts))
        print(f"Load {self.name}: {self.id}")

    def __repr__(self):
        return f"{type(self).__name__}(id={self.id}, name={self.name})"

    def __str__(self):
        return self.__repr__()

    def get_id(self, path: list, id_: int=-1, add_if_not_exist: bool=False):
        """
        get the object id
        
        :param path: path parts relative to the current object
        :param id_: current object id
        :param add_if_not_exist: default to False, if set to True, create the path if doens't exist
        """
        def _search_object(id_: int, name: str):
            contents = self._query_folder_contents(id_)
            folders = []
            current_id = -1
            for c in contents:
                if c['isFolder']:
                    if c["name"] == name:
                        current_id = c["id"]
                        break
                    else:
                        folders.append(c["name"])
                else:
                    if c["name"] == name:
                        # successfully matched the file
                        current_id = c["id"]
                        break

            return current_id, folders
        
        def _get_initial_id(id_: int, path: list) -> int:
            if id_ == -1:
                if path[0] == "/":
                    current_id = self._query_root_id()
                    path = path[1:]
                else:
                    raise ValueError(f"Please specify absolute path")
            else:
                current_id = id_
            
            return current_id, path
        
        current_id, path = _get_initial_id(id_, path)
        
        for object_name in path:
            next_id, folders = _search_object(current_id, object_name)
            
            if next_id == -1:
                if add_if_not_exist:
                    next_id = self._create_folder(object_name, current_id)
                else:
                    raise ValueError(f"Could not find {'/'.join(path)} in {', '.join(folders)}")

            current_id = next_id
    
        return current_id
        
    def delete(self) -> bool:
        """
        Delete Shared Data object        
        """
        object_base_url = self.folders_base_url if type(self).__name__ == "Folder" else self.files_base_url
        r = self.session.delete(f"{object_base_url}/{self.id}")
        if r.status_code != requests.codes.no_content:
            raise ValueError(f"Failed to delete: {r.text}")
        print(f"Delete {self.id}")

        return True
    
    def _query_folder_contents(self, id_: int):
        try:
            r = self.session.get(self.folders_base_url + "/" + str(id_))
            contents = r.json()['data']['contents']
        except Exception as e:
            raise ValueError(f"Failed to get contents for folder {id_}: {str(e)}")
        
        return contents

    def _query_root_id(self) -> int:
        
        print(self.folders_base_url + "/root")
        r = self.session.get(self.folders_base_url + "/root")
        if r.status_code == requests.codes.forbidden:
            raise ValueError(f"Access defined. Please check the right personal access token is provided for {self.base_url}")
        if r.status_code != requests.codes.ok:
            raise ValueError(f"Failed to get the root directory: {r.status_code}, {str(r.text)}")
        return r.json()['data']['id']


class File(SharedDataObject):
    def __init__(self, session, base_url: str, name: str, id_: int=-1):
        super(File, self).__init__(session, base_url, name, id_)

    def download(self, local_path: str) -> str:
        """
        Download and store file
        
        :param local_path: location to store the downloaded file
        """
        content = self.downloadobj()
        local_path = f"{local_path}/{Path(self.name).name}"
        with open(local_path, "wb") as ostr:
            ostr.write(content)

        return os.path.abspath(local_path)

    def downloadobj(self) -> bytes:
        """
        Download file as bytes
        """
        r = self.session.get(self.files_base_url + "/" + str(self.id) + "/contents")
        return r.content


class Folder(SharedDataObject):
    def __init__(self, session, base_url: str, name: str="/", id_: int=-1):
        super(Folder, self).__init__(session, base_url, name, id_)
        self.subfolders_ = None
        self.files_ = None
        
    def _initialize_objects(self):
        self.subfolders_ = []
        self.files_ = []
        for c in self._query_folder_contents(self.id):
            if c["isFolder"]:
                self.subfolders_.append(Folder(self.session, self.base_url, c["name"], c["id"]))
            else:
                self.files_.append(File(self.session, self.base_url, c["name"], c["id"]))

    @property
    def files(self):
        # lazy load the folder objects
        if self.files_ is None:
            self._initialize_objects()
        return self.files_

    @property
    def subfolders(self):
        # lazy load the folder objects
        if self.subfolders_ is None:
            self._initialize_objects()
        return self.subfolders_

    def list(self) -> list:
        """
        return list of objects in the current folder
        """
        return self.files + self.subfolders

    def create(self, path: str) -> "Folder":
        """
        Create folder under the current folder.
        Nested folder will be created if specified, e.g. folder1/folder2
        
        :param path: folder path that is relative to the current folder
        """
        # remove the heading slashs
        while path.startswith("/"): 
            path = path[1:]
        path = Path(path).parts
        new_id = self.get_id(path, self.id, True)
        new_folder = Folder(self.session, self.base_url, path[-1], new_id)
 
        return new_folder

    def upload_file(self, local_path: str) -> int:
        """
        Upload file to the current folder
        
        :param local_path: local path of the file to be uploaded
        """
        # with open(local_path, 'rb') as istr:
        return self.put_object(open(local_path, 'rb'), Path(local_path).name)

    def put_object(self, obj: bytes, file_name: str) -> int:
        """
        Write file object to the current folder
        
        :param obj: binary file object to be written
        :param file_name: the file name for the written object
        """
        try:
            field = {"field": (file_name, obj)}
            r = post_with_progress(self.session, f"{self.folders_base_url}/{self.id}/files", field)
            file_id = r.json()["data"]["id"]
            return file_id
        except Exception as e:
            raise ValueError(f"Failed to upload file: {file_name}: {str(e)}")
        
    def _create_folder(self, name: str, id_: str) -> int:
        try:
            r = self.session.post(
                    f"{self.folders_base_url}/{id_}/folders",
                    json={"name": name}
                )
            new_id = r.json()['data']['folder']['id']
        except Exception as e:
            raise ValueError(f"Failed to create folder {name}, under {id_}: {str(e)}")
        
        return new_id


class SharedDataClient:
    """
    A client to assist in managing data in Daisi Shared Data
    """
    def __init__(self, access_token: str="", base_url: str=daisi_base_url):
        """
        Shared Data client constructor method.
        session will be shared with the folder/file objects
        
        :param access_token: access token for authorizing to the platform
        :param base_url: The default URL to use for connecting to the daisi
        """
        self.session = requests.Session()
        access_token = access_token or os.getenv("DAISI_ACCESS_TOKEN", "")
        if access_token:
            self.session.headers.update({"Authorization": f"token {access_token}"})
        self.base_url = base_url + shared_data_base_route

    def Folder(self, name: str) -> Folder:
        """
        Create Folder object
        
        :param name: folder path in Shared Data
        """
        return Folder(self.session, self.base_url, name)

    def File(self, name: str) -> File:
        """
        Create File object
        
        :param name: absolute file path in Shared Data
        """
        return File(self.session, self.base_url, name)
    
    def upload_file(self, folder_name: str, local_path: str) -> int:
        """
        Upload file
        
        :param folder_name: absolute folder path in Shared Data
        :param local_path: file local path
        """
        folder = Folder(self.session, self.base_url, folder_name)
        return folder.upload_file(local_path)

    def put_object(self, folder_name: str, obj: bytes, file_name: str) -> int:
        """
        Upload file object
        
        :param folder_name: absolute folder path in Shared Data
        :param obj: binary object to be written
        :param file_name: the file name for the written object
        """
        folder = Folder(self.session, self.base_url, folder_name)
        return folder.put_object(obj, file_name)
    
    def download_file(self, file_name: str, local_path: str=".") -> str:
        """
        Download and store file
        
        :param file_name: absolute file path in Shared Data
        :param local_path: location to store the downloaded file
        """
        file = File(self.session, self.base_url, file_name)
        return file.download(local_path)
    
    def download_fileobj(self, file_name: str) -> bytes:
        """
        Download file as bytes
        
        :param file_name: absolute file path in Shared Data
        """
        file = File(self.session, self.base_url, file_name)
        return file.downloadobj()


