"""
Module to get videos data
"""
from typing import Any, Dict, List, Optional
import deeplabel.client
import deeplabel
from deeplabel.exceptions import InvalidIdError
import deeplabel.infer.gallery.gallery_tasks
import deeplabel.infer.gallery.images
from deeplabel.basemodel import DeeplabelBase


class Gallery(DeeplabelBase):
    gallery_id: str
    project_id:str
    title: str
    parent_folder_id:Optional[str]

    @classmethod
    def _from_search_params(cls, params:Dict[str, Any], client: "deeplabel.client.BaseClient") -> List["Gallery"]:
        resp = client.get("/gallery", params=params)
        galleries = resp.json()["data"]["gallery"]
        galleries = [cls(**gallery, client=client) for gallery in galleries]
        return galleries
    
    @classmethod
    def from_gallery_id(cls, gallery_id:str, client: "deeplabel.client.BaseClient")->"Gallery":
        gallery = cls._from_search_params({"galleryId":gallery_id}, client=client)
        if not len(gallery):
            raise InvalidIdError(f"Failed to fetch video with videoId: {gallery_id}")
        return gallery[0]
    
    @classmethod
    def from_folder_id(cls, folder_id:str, client: "deeplabel.client.BaseClient")-> List["Gallery"]:
        return cls._from_search_params({"parentFolderId":folder_id}, client)
    
    @property
    def images(self)->List['deeplabel.infer.gallery.images.Image']:
        return deeplabel.infer.gallery.images.Image.from_gallery_and_project_id(self.gallery_id, self.project_id, self.client)

    @property
    def gallery_tasks(self):
        return deeplabel.infer.gallery.gallery_tasks.GalleryTask.from_gallery_id(self.gallery_id, self.client)