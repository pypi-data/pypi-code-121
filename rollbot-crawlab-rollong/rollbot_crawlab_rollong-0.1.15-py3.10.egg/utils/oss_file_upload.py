import datetime
import hashlib
import mimetypes
import os
import oss2
from scrapy.utils.python import to_bytes


class OssFileUpload:
    def __init__(self, key_id, access_key, endpoint_url, bucket_name):
        self._auth = oss2.Auth(key_id, access_key)
        self._bucket = oss2.Bucket(self._auth, endpoint_url, bucket_name)

    def exist(self, path):
        res = False
        try:
            res = self._bucket.object_exists(path)
        except:
            pass
        return res

    def upload_object(self, path, buf):
        self._bucket.put_object(key=path, data=buf.getvalue())

    def upload_from_file(self, path, file):
        self._bucket.put_object_from_file(key=path, filename=file)

    def get_url_md5(self, url):
        return hashlib.sha1(to_bytes(url)).hexdigest()

    def get_file_path(self, url, item, default_ext, folder):
        media_guid = self.get_url_md5(url)
        media_ext = os.path.splitext(url)[1]
        if media_ext not in mimetypes.types_map:
            media_ext = ''
            media_type = mimetypes.guess_type(url)[0]
            if media_type:
                media_ext = mimetypes.guess_extension(media_type)
        if '' == media_ext:
            media_ext = default_ext
        prefix = ''
        if item is not None:
            prefix = item.get("domain_id", '') + '/' + self.get_url_md5(item.get("source_url", "")) + "/"
        now = datetime.datetime.now().strftime('%Y%m')
        if folder and '' != folder:
            folder += "/"
        return prefix + folder + now + '/' + '%s%s' % (media_guid, media_ext)