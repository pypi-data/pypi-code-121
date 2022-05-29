import json
import mimetypes

from licsber.drive.quark.account import QuarkAccount
from licsber.spider import get_session
from licsber.utils.utime import gmt_time_http_format, timestamp_mil


class QuarkDriver:
    def update_hash(self, task_id, md5, sha1):
        data = {
            'task_id': task_id,
            'md5': md5.lower(),
            'sha1': sha1.lower(),
        }
        return self.post('/file/update/hash', data=data)

    def upload_auth(self, pre_data, part_number=1):
        task_id = pre_data['task_id']
        data = {
            'auth_info': pre_data['auth_info'],
            'auth_meta': self.auth_meta(
                mine_type=pre_data['callback']['format_type'],
                bucket=pre_data['bucket'],
                obj_key=pre_data['obj_key'],
                part_number=part_number,
                upload_id=pre_data['upload_id'],
            ),
            'task_id': task_id,
        }
        return self.post('/file/upload/auth', data=data)

    def upload_pre(self, pdir_fid, file_name, file_size, mime_type=None):
        if not mime_type:
            mime_type = mimetypes.guess_type(file_name)[0]

        ts_mil = timestamp_mil()
        data = {
            'ccp_hash_update': True,
            'dir_name': '',
            'pdir_fid': pdir_fid,
            'size': file_size,
            'file_name': file_name,
            'format_type': mime_type,
            'l_created_at': ts_mil,
            'l_updated_at': ts_mil,
        }
        return self.post('/file/upload/pre', data=data)

    def __init__(self, account: QuarkAccount):
        self.account = account
        self.base_url = 'https://drive.quark.cn/1/clouddrive'
        self.s = get_session()
        self.params = {
            'pr': 'ucpro',
            'fr': 'pc',
        }
        self.build_session()

    def build_session(self):
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Referer': 'https://pan.quark.cn/',
            'Content-Type': 'application/json',
            'Cookie': self.account.cookie,
        }
        self.s.headers.update(headers)

    def post(self, path: str, data: dict):
        url = self.base_url + path
        data = json.dumps(data)
        return self.s.post(url, params=self.params, data=data)

    def auth_meta(self, mine_type, bucket, obj_key, part_number, upload_id):
        return f"""PUT

{mine_type}
{gmt_time_http_format()}
x-oss-date:{gmt_time_http_format()}
x-oss-user-agent:aliyun-sdk-js/6.6.1 Chrome 98.0.4758.80 on Windows 10 64-bit
/{bucket}/{obj_key}?partNumber={part_number}&uploadId={upload_id}"""
