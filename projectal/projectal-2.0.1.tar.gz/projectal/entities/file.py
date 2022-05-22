from projectal.entity import Entity
from projectal.linkers import FileLinker
from projectal import api


class File(Entity, FileLinker):
    """
    Implementation of the [File](https://projectal.com/docs/latest/#tag/File) API.
    """
    _path = 'file'
    _name = 'STORAGE_FILE'

    @classmethod
    def create(cls, file_data, entity):
        """
        Create a File entity with file data.

        `file_data` is the raw file data in bytes

        `entity` is the File entity and its fields.
        """
        payload = entity
        url = '/api/file/upload'
        file = {'file': file_data}
        response = api.post(url, payload, file=file)
        entity['uuId'] = response['jobClue']['uuId']
        return cls(entity)

    @classmethod
    def get(cls, uuId):
        """Get the File entity. No file data is included."""
        return cls(api.get('/api/file/get?uuId={}'.format(uuId)))

    @classmethod
    def update(cls, entity, file_data=None):
        """
        Update the File entity. Optionally, also update the
        file data that this File holds.
        """
        payload = entity
        url = '/api/file/update'
        if file_data:
            file = {'file': file_data}
            api.put(url, payload, file=file)
        else:
            api.put(url, payload, form=True)

    @classmethod
    def get_file_data(cls, uuId):
        """
        Get the file data that is held by the file with `uuId`.
        Returns the raw content of the response.
        """
        url = '/api/file/{}'.format(uuId)
        response = api.get(url, is_json=False)
        return response.content

    @classmethod
    def download_to_browser(cls, uuId):
        """
        Get the file data that is held by the file with `uuId`.
        Returns the response object which will have headers suitable
        to initiate a download by the user agent.
        """
        url = '/api/file/download'
        payload = {'uuId': uuId}
        response = api.post(url, payload, is_json=False)
        return response

    @classmethod
    def delete(cls, uuId):
        """
        Delete the File entity and its file data.
        """
        url = '/api/file/delete/{}'.format(uuId)
        api.delete(url)
        return True

    @classmethod
    def download_multiple(cls, list):
        """
        Given a list of File entities, return the file data held by
        each as a `.zip` file.
        """
        url = '/api/file/multidownload'
        response = api.post(url, list, is_json=False)
        return response.content

    @classmethod
    def list(cls, expand=True):
        """Return all files as a list"""
        files = api.get('/api/file/list')
        return [cls(f) for f in files]
