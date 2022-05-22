from projectal.entity import Entity
from projectal.linkers import *
from projectal import api


class Folder(Entity, FolderLinker, FileLinker):
    """
    Implementation of the [Folder](https://projectal.com/docs/latest/#tag/Folder) API.
    """
    _path = 'folder'
    _name = 'STORAGE_FOLDER'

    @classmethod
    def create(cls, entity):
        payload = entity
        endpoint = '/api/folder/add'
        response = api.post(endpoint, payload)
        entity['uuId'] = response['jobClue']['uuId'];
        return cls(entity)

    @classmethod
    def get(cls, uuId):
        return cls(api.get('/api/folder/get?uuId={}'.format(uuId)))

    @classmethod
    def update(cls, entity):
        payload = entity
        api.put('/api/folder/update', payload)
        return True

    @classmethod
    def delete(cls, uuId):
        api.delete('/api/folder/delete/{}'.format(uuId))
        return True

    # TODO: reimplemented here due to differences in list name vs other file linkers.
    # Remove in future if/when api is fixed
    def link_file(self, file):
        self._add_link(self, 'file', [file], list_name='files')

    def unlink_file(self,  file):
        self._delete_link(self, 'file', [file], list_name='files')

    @classmethod
    def list(cls, expand=True):
        """Return all folders as a list"""
        folders = api.get('/api/folder/list')
        return [cls(f) for f in folders]
