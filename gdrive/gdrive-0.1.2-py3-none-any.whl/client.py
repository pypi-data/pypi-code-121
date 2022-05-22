import fnmatch
import logging
import os
import posixpath
import re
from typing import List, Any, Dict
from urllib.parse import urlparse

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from gdrive.auth import GoogleAuth
from gdrive.exception import GDriveNoSuchFileMetaException
from gdrive.utils import query_string_to_dict

log = logging.getLogger(__name__)


class GDriveClient:
    def __init__(self, gauth: GoogleAuth):
        self.service = build('drive', 'v3', credentials=gauth.credentials, cache_discovery=False)

    def get(self, path_qs: str):
        """
        :param path_qs: gdrive://a/b/c/file?mime_type=text/plain
        :param mime_type:
        :return:
        """
        log.debug(f"finding file: {path_qs}")
        query_parsed, query_dict = query_string_to_dict(path_qs)
        mime_type = query_dict.get("mime_type", None)
        file_meta = self.get_file_meta(query_parsed.path)
        contents = self.get_file(file_meta, mime_type)
        if mime_type == "text/plain":
            return contents.decode("utf-8")
        else:
            return contents

    def export(self, file_id: str, mime_type: str = None):
        '''
        Exports Google Doc to mime_type
        :param file_id: Google Drive's file ID
        :param mime_type: user-picked mime type
        :return: File contents in requested mime type
        '''
        exported = self.service.files().export(fileId=file_id, mimeType=mime_type).execute()
        return exported.decode("utf-8")

    def download(self, file_id: str):
        '''
        Download file as-is
        :param file_id: the Google file ID
        :return: file contents without any conversion
        '''
        exported = self.service.files().get_media(fileId=file_id).execute()
        return exported

    def get_file(self, file_meta: Dict[str, Any], mime_type=None):
        if file_meta['mimeType'] == 'application/vnd.google-apps.document':
            log.debug(f"Exporting file: {file_meta}")
            return self.export(file_meta['id'], mime_type if mime_type else file_meta['mimeType'])
        else:
            log.debug(f"Downloading file: {file_meta}")
            return self.download(file_meta['id'])

    def walk(self, path_qs: str, include_pat=None, exclude_pat=None) -> List[Dict[str, Any]]:
        """
        Traverse given directory
        :param path_qs: query string with path to walk to
        :param start_path: the path that can be in the form of scheme://path/
        :param include_pat:
        :param exclude_pat:
        :return:
        """
        query_parsed, query_dict = query_string_to_dict(path_qs)
        start_path = query_parsed.path
        log.debug(f"walk: {path_qs}, start_path: {start_path}")
        dir_file_meta = self.get_file_meta(path_qs)

        def merge(indict, cpath):
            indict.update({'content': loop(indict, os.path.join(cpath, indict['name']))})
            return indict

        def loop(current_file_meta, cpath) -> List[Dict[str, Any]]:
            def f(file_meta):
                relpath = posixpath.relpath(os.path.join(cpath, file_meta['name']), start_path)
                return self._check_include_exclude(relpath, include_pat, exclude_pat)

            return [(merge(e, cpath) if e['mimeType'] == 'application/vnd.google-apps.folder' else e) for e
                    in filter(f, self._list_children(current_file_meta, query_dict))]

        return loop(dir_file_meta, start_path)

    def get_file_meta(self, path_qs: str) -> Dict[str, Any]:
        '''
        Asserts that path exists on the google drive

        :return: full file_meta of file/folder traversed to (the last one)
        '''

        log.debug(f"gdrive segment list: {path_qs}")

        def no_file(next_names: List[str], parent_meta: Dict[str, Any], requested_path: str):
            raise GDriveNoSuchFileMetaException(
                f'Unable to lookup elements: {next_names}, under directory with meta: {parent_meta}, requested path: {requested_path}'
            )

        if not path_qs:
            return {'id': 'root', 'mimeType': ''}
        else:
            return self._traverse(path_qs, no_file)

    def get_file_meta_by_id(self, file_id: str, fields: str) -> Dict[str, Any]:
        return self.service.files().get(
            fileId=file_id,
            fields=fields,
        ).execute()

    def upload(self, dest_qs: str, file_to_upload: str, file_meta: Dict[str, Any] = {}):
        query_parsed, query_dict = query_string_to_dict(dest_qs)
        filename = os.path.basename(dest_qs)
        if filename == '':
            filename = os.path.basename(file_to_upload)
            dest = os.path.join(query_parsed.netloc, query_parsed.path, filename)
        else:
            dest = os.path.join(query_parsed.netloc, query_parsed.path)

        log.debug(f"uploading file: {file_to_upload} to: {dest}")

        if file_meta and 'mimeType' in file_meta:
            media = MediaFileUpload(file_to_upload, mimetype=file_meta['mimeType'])
        else:
            media = MediaFileUpload(file_to_upload)

        def if_not_exists(next_names: List[str], parent_meta: Dict[str, Any], requested_path: str):
            log.debug(f"Cannot find: {next_names}")
            p = parent_meta['id']
            ret = parent_meta
            for e in next_names[:-1]:
                ret = self.service.files().create(
                    body={'name': e, 'mimeType': 'application/vnd.google-apps.folder', 'parents': [p]},
                    fields="id"
                ).execute()
                p = ret['id']
            return ret

        uploaded_file_meta = self._traverse(dest, if_not_exists)

        if 'name' in uploaded_file_meta and uploaded_file_meta['name'] == filename:
            log.info(f"Updating: {filename}")
            self.service.files().update(
                fileId=uploaded_file_meta['id'],
                body=file_meta,
                media_body=media,
                fields="id"
            ).execute()
        else:
            log.info(f"Creating: {filename}")
            file_meta.update(
                {
                    'parents': [uploaded_file_meta['id']],
                    'name': filename
                }
            )
            self.service.files().create(
                body=file_meta,
                media_body=media,
                fields="id"
            ).execute()

    def trash(self, file_id: str):
        return self.service.files().update(
            fileId=file_id,
            body={'trashed': True},
            fields="id"
        ).execute()

    def _list_children(self, parent_meta: Dict[str, Any], query_dict: Dict[str, Any] = {}) -> List[Any]:
        def query(extra_params={}):
            r = self.service.files().list(
                q="'{}' in parents and trashed = false".format(parent_meta['id']),
                **extra_params
            ).execute()
            self._assert_incomplete_search(r)
            return r

        extra = query_dict.copy()
        json_response = query(extra)
        ret_list = json_response['files']
        while 'nextPageToken' in json_response:
            log.debug(f"Fetching next page of files under: {parent_meta}")
            {'pageToken': json_response['nextPageToken']}
            extra.update({'pageToken': json_response['nextPageToken']})
            json_response = query(extra)
            ret_list.extend(json_response['files'])
        return ret_list

    def _path_to_list(self, parsed_path) -> List[str]:
        p = parsed_path.netloc + parsed_path.path
        return p.strip(os.sep).split(os.sep)

    def _assert_incomplete_search(self, json_response):
        if json_response['incompleteSearch']:
            raise GDriveException('google drive query ended due to incompleteSearch')

    def _traverse(self, path_qs: str, on_empty=None):
        query_parsed, query_dict = query_string_to_dict(path_qs)
        path_segment_list = self._path_to_list(query_parsed)

        def go(parent_meta, idx) -> Dict[str, Any]:
            if idx >= len(path_segment_list):
                return parent_meta
            next_name = path_segment_list[idx]
            file_list = self._list_children(parent_meta, query_dict)
            r = [e for e in file_list if e['name'] == next_name]
            if len(r) > 0:
                # don't care if name occurred in other pages or already multiple times
                return go(r[0], idx + 1)
            else:
                return on_empty(path_segment_list[idx:], parent_meta, path_qs)

        return go({'id': 'root'}, 0)

    @staticmethod
    def _check_include_exclude(path_str, include_pat=None, exclude_pat=None) -> bool:
        """
        Check for glob or regexp patterns for include_pat and exclude_pat in the
        'path_str' string and return True/False conditions as follows.
          - Default: return 'True' if no include_pat or exclude_pat patterns are
            supplied
          - If only include_pat or exclude_pat is supplied: return 'True' if string
            passes the include_pat test or fails exclude_pat test respectively
          - If both include_pat and exclude_pat are supplied: return 'True' if
            include_pat matches AND exclude_pat does not match
        """

        def _pat_check(path_str, check_pat):
            if re.match("E@", check_pat):
                return True if re.search(check_pat[2:], path_str) else False
            else:
                return True if fnmatch.fnmatch(path_str, check_pat) else False

        ret = True  # -- default true
        # Before pattern match, check if it is regexp (E@'') or glob(default)
        if include_pat:
            if isinstance(include_pat, list):
                for include_line in include_pat:
                    retchk_include = _pat_check(path_str, include_line)
                    if retchk_include:
                        break
            else:
                retchk_include = _pat_check(path_str, include_pat)

        if exclude_pat:
            if isinstance(exclude_pat, list):
                for exclude_line in exclude_pat:
                    retchk_exclude = not _pat_check(path_str, exclude_line)
                    if not retchk_exclude:
                        break
            else:
                retchk_exclude = not _pat_check(path_str, exclude_pat)

        # Now apply include/exclude conditions
        if include_pat and not exclude_pat:
            ret = retchk_include
        elif exclude_pat and not include_pat:
            ret = retchk_exclude
        elif include_pat and exclude_pat:
            ret = retchk_include and retchk_exclude
        else:
            ret = True

        return ret
