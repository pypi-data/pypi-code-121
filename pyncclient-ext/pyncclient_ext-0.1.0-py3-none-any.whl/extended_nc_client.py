#!/usr/bin/env python3

import os
import sys
import time
from typing import Final, Mapping, MutableMapping, Optional, Sequence
import urllib.parse
import uuid
import xml.etree.ElementTree as ET

from nextcloud_client import nextcloud_client   # type: ignore[import]
import six

class ExtendedNextcloudClient(nextcloud_client.Client):
    """
    Nextcloud client with additional tag management capabilities
    """
    # See https://doc.owncloud.com/server/10.10/developer_manual/webdav_api/tags.html#create-tags
    OWNCLOUD_NS: Final[str] = 'http://owncloud.org/ns'
    
    DAV_V1_REL: Final[str] = '../../'
    DAV_OTHER_REL: Final[str] = '../dav/'
    
    SYSTEMTAGS_BASE_URL: Final[str] = 'systemtags/'
    SYSTEMTAG_NAME = 'display-name'
    SYSTEMTAG_ID = 'id'
    SYSTEMTAGS_PROP_NAMES: Final[Sequence[str]] = [
        SYSTEMTAG_ID,
        SYSTEMTAG_NAME,
        'user-visible',
        'can-assign',
        'user-assignable'
    ]
    SYSTEMTAGS_PROP_MAPPING: Final[Mapping[str, str]] = {
        '{http://owncloud.org/ns}' + tag_prop: tag_prop  for tag_prop in SYSTEMTAGS_PROP_NAMES
    }
    
    SYSTEMTAGS_RELATIONS_BASE_URL: Final[str] = 'systemtags-relations/files/'
    
    # See https://docs.nextcloud.com/server/latest/developer_manual/client_apis/WebDAV/basic.html#requesting-properties
    PATH_FILEID = 'fileid'
    PATH_PROP_NAMES: Final[Sequence[str]] = [
        PATH_FILEID
    ]
    PATH_PROP_MAPPING_REVERSE: Final[Mapping[str, str]] = {
        tag_prop: '{http://owncloud.org/ns}' + tag_prop  for tag_prop in PATH_PROP_NAMES
    }
    PATH_PROPS = [
        '{DAV:}getlastmodified',
        '{DAV:}resourcetype',
        '{DAV:}getcontentlength',
        '{DAV:}quota-used-bytes',
        '{DAV:}quota-available-bytes',
        '{DAV:}getetag',
        *PATH_PROP_MAPPING_REVERSE.values()
    ]
    
    UPLOADS_BASE_URL_T: Final[str] = 'uploads/{0}/'
    FILES_BASE_URL_T: Final[str] = 'files/{0}/'
    
    def __init__(self, url: str, **kwargs):
        """Instantiates a client
            
        :param url: URL of the target nextCloud instance
        :param verify_certs: True (default) to verify SSL certificates, False otherwise
        :param dav_endpoint_version: None (default) to force using a specific endpoint version
        instead of relying on capabilities
        :param debug: set to True to print debugging messages to stdout, defaults to False
        """
        super().__init__(url, **kwargs)
        
        if not isinstance(self._dav_endpoint_version, bool) and self._dav_endpoint_version == 1:
            self._dav_prefix = self.DAV_V1_REL
        else:
            self._dav_prefix = self.DAV_OTHER_REL
        self._upload_files_dav_prefix = ''
        
        self.systemtags_base_url = self._dav_prefix + self.SYSTEMTAGS_BASE_URL 
        self.systemtags_relations_base_url = self._dav_prefix + self.SYSTEMTAGS_RELATIONS_BASE_URL
        
        # A way to cache the tags
        self._systemtags : MutableMapping[str, Mapping[str, Optional[str]]] = {}
    
    def login(self, user_id: str, password: str):
        """
        As the user id is not stored, it has to be intercepted here in
        order to create the uploads_base_url
        """
        super().login(user_id, password)
        quoted_user_id = urllib.parse.quote(user_id)
        if not isinstance(self._dav_endpoint_version, bool) and self._dav_endpoint_version == 1:
            self._dav_prefix = self.DAV_V1_REL
            self._upload_files_dav_prefix = ''
        else:
            self._dav_prefix = self.DAV_OTHER_REL
            self._upload_files_dav_prefix = self._dav_prefix + self.FILES_BASE_URL_T.format(quoted_user_id)
        
        self.systemtags_base_url = self._dav_prefix + self.SYSTEMTAGS_BASE_URL 
        self.systemtags_relations_base_url = self._dav_prefix + self.SYSTEMTAGS_RELATIONS_BASE_URL
        self.uploads_base_url = self._dav_prefix + self.UPLOADS_BASE_URL_T.format(quoted_user_id)
        
        res = self._make_ocs_request(
                'GET',
                self.OCS_SERVICE_CLOUD,
                'capabilities'
                )
    
    def get_systemtags(self, force_search: bool = False) -> Mapping[str, Mapping[str, Optional[str]]]:
        """
        It returns all the defined system tags
        """
        if len(self._systemtags) == 0 or force_search:
            self._systemtags = {}
            for tag in self.list(self.systemtags_base_url, properties=list(self.SYSTEMTAGS_PROP_MAPPING.keys())):
                props = {
                    self.SYSTEMTAGS_PROP_MAPPING[prop_name]: prop_val  for prop_name, prop_val in tag.attributes.items()
                }
                self._systemtags[props[self.SYSTEMTAG_NAME]] = props
        
        return self._systemtags
    
    def get_systemtag(self, tag_name: str, force_search: bool = False) -> Optional[str]:
        """
        It searches for the tag
        """
        props = self.get_systemtags(force_search=force_search).get(tag_name)
        return None  if props is None  else  props[self.SYSTEMTAG_ID]
    
    def create_systemtag(self, tag_name: str, user_visible: bool = True, user_assignable: bool = True, can_assign: bool = True) -> Optional[str]:
        """
        It creates a new system tag
        """
        # Create the tag
        if self._make_dav_request('POST', self.systemtags_base_url, json={
                'userVisible': user_visible,
                'userAssignable': user_assignable,
                'canAssign': can_assign,
                'name': tag_name
            }):
            
            # Invalidate the cache and repopulate
            return self.get_systemtag(tag_name, force_search=True)
        else:
            return None
    
    def file_info(self, path, properties: Optional[Sequence[str]] = None) -> nextcloud_client.FileInfo:
        """
        This version assures the needed properties to learn about
        systemtags are queried
        """
        if properties is None:
            augmented_properties = self.PATH_PROPS
        else:
            augmented_properties = self.PATH_PROPS.copy()
            augmented_properties.extend(properties)
        return super().file_info(path, augmented_properties)
    
    def ensure_tree_exists(self, encoded_path: str) -> Optional[nextcloud_client.FileInfo]:
        """
        It returns the status about the Nextcloud directory, creating
        it in case it does not exist yet. If it already exists, and it
        is not a directory, then return None
        """
        try:
            file_info = self.file_info(encoded_path)
            return file_info  if file_info.file_type == 'dir'  else  None
        except nextcloud_client.HTTPResponseError as e:
            if e.status_code == 404:
                return self._ensure_tree_exists(encoded_path)
            else:
                raise e
    
    def _ensure_tree_exists(self, encoded_path: str) -> Optional[nextcloud_client.FileInfo]:
        """
        It recursively creates the directory, creating the intermediate
        ancestors. If some ancestor already exists, and it is not a
        directory, then return None
        """
        
        slash : Optional[int] = None
        file_info : Optional[nextcloud_client.FileInfo] = None
        while (slash is None) or slash >= 0:
            slash = encoded_path.find('/', slash)
            if slash >= 0:
                slash += 1
                prepath = encoded_path[0:slash]
            else:
                prepath = encoded_path
            
            if prepath:
                try:
                    # Does it exist?
                    file_info = self.file_info(prepath)
                    
                    # Is a directory?
                    if file_info.file_type != 'dir':
                        file_info = None
                        break
                except nextcloud_client.HTTPResponseError as e:
                    if e.status_code == 404:
                        # Please, create it
                        self.mkdir(prepath)
                        file_info = self.file_info(prepath)
                    else:
                        raise e
        
        return file_info
    
    def add_tag(self, file_info: nextcloud_client.FileInfo, tag_name: str) -> Optional[bool]:
        """
        This method associates a system tag to a path which exists,
        so the input is a FileInfo named tuple 
        """
        # Add tag to path
        tag_id = self.get_systemtag(tag_name)
        if tag_id is None:
            return None
        file_id = file_info.attributes.get(self.PATH_PROP_MAPPING_REVERSE[self.PATH_FILEID])
        if file_id is None:
            return None
        return self._make_dav_request('PUT', self.systemtags_relations_base_url + file_id + '/' + tag_id)
    
    def put_file(self, remote_path, local_source_file, **kwargs) -> bool:
        """Uploads a file, optionally using chunks. If the file is smaller than
        ``chunk_size`` it will be uploaded directly.

        :param remote_path: path to the target file. A target directory can
            also be specified instead by appending a "/"
        :param local_source_file: path to the local file to upload
        :param chunked: (optional) use file chunking (defaults to True)
        :param chunk_size: (optional) chunk size in bytes, defaults to 10 MB
        :param keep_mtime: (optional) also update the remote file to the same
            mtime as the local one, defaults to True
        :returns: True if the operation succeeded, False otherwise
        :raises: HTTPResponseError in case an HTTP error status was returned
        """
        timestamp = int(os.path.getmtime(local_source_file))
        with open(local_source_file, mode='rb') as uH:
            return self.put_stream(uH, remote_path, **kwargs, remote_timestamp=timestamp)
    
    DEFAULT_CHUCK_SIZE: Final[int] = 10 * 1024 * 1024
    
    def put_stream(self, local_stream , remote_path: str, remote_timestamp: Optional[int] = None, **kwargs) -> bool:
        """Uploads a stream, optionally using chunks. If the file is smaller than
        ``chunk_size`` it will be uploaded directly.

        :param remote_path: path to the target file.
        :param local_source_file: path to the local file to upload
        :param \*\*kwargs: optional arguments that ``put_file`` accepts
        :returns: True if the operation succeeded, False otherwise
        :raises: HTTPResponseError in case an HTTP error status was returned
        """
        chunk_size = kwargs.get('chunk_size', self.DEFAULT_CHUCK_SIZE)
        transfer_id = int(time.time())
        
        headers = {}
        if kwargs.get('keep_mtime', True) or (remote_timestamp is not None):
            if remote_timestamp is None:
                remote_timestamp = transfer_id
            headers['X-OC-Mtime'] = str(remote_timestamp)

        remote_path = self._normalize_path(remote_path)
        if remote_path.endswith('/'):
            raise ValueError(f'{remote_path} is a directory')
        
        # Unchunked case
        if not kwargs.get('chunked', True):
            return self._make_dav_request(
                'PUT',
                remote_path,
                data=local_stream,
                headers=headers
            )
        
        chunk_folder = None
        the_size = None
        try:
            # This range should be interrupted when the end of the file
            # has been reached. Should we use a more explicit EOF detection?
            for chunk_offset in range(0, sys.maxsize, chunk_size):
                chunk_name = None
                data = local_stream.read(chunk_size)
                if chunk_offset == 0:
                    if len(data) < chunk_size:
                        # It is not worth chunking
                        return self._make_dav_request(
                            'PUT',
                            remote_path,
                            data=data,
                            headers=headers
                        )
                    else:
                        # Let's create the chunk uploading folder
                        chunk_folder = self.uploads_base_url + str(uuid.uuid4()) + '/'
                        self.mkdir(chunk_folder)
                
                if len(data) > 0:
                    the_size = chunk_offset + len(data)
                    
                    chunk_name = chunk_folder + '{0:015d}-{1:015d}'.format(chunk_offset, the_size -1)
                    
                    if not self._make_dav_request(
                            'PUT',
                            chunk_name,
                            data=data
                    ):
                        raise StopIteration('PUT chunk failed')
                
                if len(data) < chunk_size:
                    break
            
            # Last, assembly time!!!!
            headers['Destination'] = urllib.parse.urljoin(self._webdav_url + '/', self._normalize_path(self._upload_files_dav_prefix + remote_path)[1:])
            assert the_size is not None
            assert chunk_folder is not None
            headers['OC-Total-Length'] = str(the_size)
            if not self._make_dav_request(
                'MOVE',
                chunk_folder + '.file',
                headers=headers
            ):
                raise StopIteration('MOVE assembly failed')
        
        except Exception as e:
            # Removing the assembling directory
            if chunk_folder is not None:
                try:
                    self.delete(chunk_folder)
                except:
                    pass
            
            # Only interested in return for this specific case
            if isinstance(e, StopIteration):
                return False
            
            raise e
        
        return True
    
    OCS_SHARE_TYPE_EMAIL: Final[int] = 4
        
    def share_file(self, path, share_type, share_dest = None, **kwargs):
        """Shares a remote file with link

        :param path: path to the remote file to share
        :param perms (optional): permission of the shared object
        defaults to read only (1)
        :param public_upload (optional): allows users to upload files or folders
        :param password (optional): sets a password
        https://docs.nextcloud.com/server/latest/developer_manual/client_apis/OCS/ocs-share-api.html
        :param name (optional): display name for the link
        :param expire_date (optional): expiration date of the link in ISO8601 / rfc3339 date format
        :returns: instance of :class:`ShareInfo` with the share info
            or False if the operation failed
        :raises: HTTPResponseError in case an HTTP error status was returned
        """
        perms = kwargs.get('perms', None  if share_type==self.OCS_SHARE_TYPE_EMAIL  else  self.OCS_PERMISSION_READ)
        remote_user = kwargs.get('remote_user', share_type == self.OCS_SHARE_TYPE_REMOTE)
        if share_type in (self.OCS_SHARE_TYPE_USER, self.OCS_SHARE_TYPE_GROUP, self.OCS_SHARE_TYPE_REMOTE):
            if (((not isinstance(perms, int)) or (perms > self.OCS_PERMISSION_ALL))
                    or ((not isinstance(share_dest, six.string_types)) or (share_dest == ''))):
                return False

            if (share_type == self.OCS_SHARE_TYPE_REMOTE) and remote_user and (not share_dest.endswith('/')):
                share_dest += '/'
        
        path = self._normalize_path(path)
        post_data = {
            'shareType': share_type,
            'path': self._encode_string(path),
        }
        if share_type in (self.OCS_SHARE_TYPE_USER, self.OCS_SHARE_TYPE_REMOTE, self.OCS_SHARE_TYPE_GROUP, self.OCS_SHARE_TYPE_EMAIL):
            if not share_dest:
                return False
            post_data["shareWith"] = share_dest
        if perms:
            post_data['permissions'] = perms
        
        if share_type in (self.OCS_SHARE_TYPE_LINK, self.OCS_SHARE_TYPE_EMAIL):
            public_upload = kwargs.get('public_upload', 'false')
            if (public_upload is not None) and (isinstance(public_upload, bool)):
                post_data['publicUpload'] = str(public_upload).lower()
            
            password = kwargs.get('password', None)
            if isinstance(password, six.string_types):
                post_data['password'] = password
            
            name = kwargs.get('name', None)
            if name is not None:
                post_data['name'] = self._encode_string(name)
            
            expire_date = kwargs.get('expire_date', None)
            if expire_date is not None:
                post_data['expireDate'] = expire_date
        
        res = self._make_ocs_request(
            'POST',
            self.OCS_SERVICE_SHARE,
            'shares',
            data=post_data
        )
        
        if res.status_code != 200:
            raise nextcloud_client.HTTPResponseError(res)
        
        tree = ET.fromstring(res.content)
        self._check_ocs_status(tree)
        data_el = tree.find('data')
        if share_type in (self.OCS_SHARE_TYPE_LINK, self.OCS_SHARE_TYPE_EMAIL):
             share_info = {
                'id': data_el.find('id').text,
                'share_type': share_type,
                'path': path,
                'url': data_el.find('url').text,
                'token': data_el.find('token').text,
            }
        else:
            share_info = {
                'id': data_el.find('id').text,
                'share_type': share_type,
                'path': path,
                'permissions': perms
            }
        
        if share_type != self.OCS_SHARE_TYPE_LINK:
            share_info['share_with'] = share_dest
        
        return nextcloud_client.ShareInfo(share_info)
        
