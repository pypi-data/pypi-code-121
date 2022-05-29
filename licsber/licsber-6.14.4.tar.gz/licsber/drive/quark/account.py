import json
from pathlib import Path


class QuarkAccount:
    save_json_path = Path.home() / '.licsber' / 'quark.json'
    upload_folder_id: str
    cookie: str

    def __init__(self, load: bool = True):
        if load:
            self.load()

    def require_force_login(self):
        print('请登录账号 并输入upload_folder_id和cookie.')
        upload_folder_id = input('upload_folder_id: ').strip(' ')
        if upload_folder_id != '':
            self.upload_folder_id = upload_folder_id

        cookie = input('cookie: ').strip(' ')
        if cookie != '':
            self.cookie = cookie

        self.save()

    def load(self):
        data = json.load(self.save_json_path.open('r'))
        self.upload_folder_id = data['upload_folder_id']
        self.cookie = data['cookie']

    @staticmethod
    def new(root_folder_id: str, cookie: str):
        qa = QuarkAccount(load=False)
        qa.root_folder_id = root_folder_id
        qa.cookie = cookie
        qa.save()
        return qa

    def to_dict(self):
        return {
            'upload_folder_id': self.upload_folder_id,
            'cookie': self.cookie,
        }

    def save(self):
        json.dump(self.to_dict(), self.save_json_path.open('w'))


if __name__ == '__main__':
    qa = QuarkAccount()
    qa.require_force_login()
    print(qa.to_dict())
