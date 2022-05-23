from typing import Any, Dict, List, Optional
from enum import Enum
from deeplabel.exceptions import InvalidIdError
from deeplabel.basemodel import DeeplabelBase
import deeplabel.label.videos
import deeplabel.label.gallery
import deeplabel.label.folders
import deeplabel.client
import deeplabel


class FolderType(Enum):
    VIDEO = "VIDEO"
    GALLERY = "GALLERY"


class RootFolder(DeeplabelBase):
    type:FolderType
    project_id: str

    @property
    def folders(self):
        search_params = {
                'projectId':self.project_id,
                'type':self.type.value
            }
        if hasattr(self, 'folder_id'):
            search_params['parentFolderId'] = self.folder_id
        return deeplabel.label.folders.Folder._from_search_params(
            search_params,
            self.client
        )

    @property
    def videos(self) -> List["deeplabel.label.videos.Video"]:
        search_params = {
                "projectId": self.project_id,
                "limit": "-1",
            }
        if hasattr(self, 'folder_id'):
            search_params['parentFolderId'] = self.folder_id
        return deeplabel.label.videos.Video._from_search_params(
            search_params,
            client=self.client,
        )

    @property
    def galleries(self) -> List["deeplabel.label.gallery.Gallery"]:
        search_params = {
                "projectId": self.project_id,
                "limit": "-1",
            }
        if hasattr(self, 'folder_id'):
            search_params['parentFolderId'] = self.folder_id
        return deeplabel.label.gallery.Gallery._from_search_params(
            search_params,
            client=self.client,
        )

class Folder(RootFolder):
    description: str
    name: str
    folder_id: str
    parent_folder_id: Optional[str]

    @classmethod
    def _from_search_params(
        cls, params: Dict[str, Any], client: "deeplabel.client.BaseClient"
    ) -> List["Folder"]:
        resp = client.get("/projects/folders", params)
        folders = resp.json()["data"]["folders"]
        folders = [cls(**folder, client=client) for folder in folders]
        return folders

    @classmethod
    def from_project_id(
        cls, project_id: str, client: "deeplabel.client.BaseClient"
    ) -> List["Folder"]:
        folders = cls._from_search_params({"projectId": project_id}, client)
        return folders

    @classmethod
    def from_folder_id(
        cls, folder_id: str, client: "deeplabel.client.BaseClient"
    ) -> "Folder":
        folders = cls._from_search_params({"folderId": folder_id}, client)
        if not folders:
            raise InvalidIdError(f"No Folder found with folderId: {folder_id}")
        return folders[0]

