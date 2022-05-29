import json
import mimetypes

from licsber.drive.quark.account import QuarkAccount
from licsber.drive.quark.driver import QuarkDriver


class Quark:
    def __init__(self, account: QuarkAccount = None, debug: bool = False):
        self.debug = debug
        if account is None:
            account = QuarkAccount()

        self.driver = QuarkDriver(account)

    def quick_upload_licsber_json(self, json_path, pdir_fid: str = None) -> bool:
        if pdir_fid is None:
            pdir_fid = self.driver.account.upload_folder_id

        file_meta = json.load(open(json_path, 'r'))
        file_name = file_meta['basename']
        file_size = file_meta['size']
        mime_type = mimetypes.guess_type(file_name)[0]
        if 'mime_type' in file_meta and file_meta['mime_type'] is not None:
            mime_type = file_meta['mime_type']

        if mime_type is None:
            mime_type = 'application/octet-stream'

        res = self.driver.upload_pre(pdir_fid, file_name, file_size, mime_type)
        if res.status_code != 200:
            print('upload pre fail.')
            print(res.headers)
            print(res.text)
            return False

        if self.debug:
            print(f"pre: {res.text}")

        task_id = res.json()['data']['task_id']

        file_md5 = file_meta['md5'].lower()
        file_sha1 = file_meta['sha1'].lower()
        res = self.driver.update_hash(task_id, file_md5, file_sha1)
        if res.status_code != 200:
            print('update hash fail.')
            print(res.headers)
            print(res.text)
            return False

        if self.debug:
            print(f"hash: {res.text}")

        return res.json()['data']['finish']


if __name__ == '__main__':
    test_json_path = 'ila.pdf.json'

    quark = Quark()
    suc = quark.quick_upload_licsber_json(test_json_path)
    print(suc)
