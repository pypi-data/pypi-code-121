import dropbox
import pandas as pd
import io
import json
import numpy as np

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)


class HunDropbox:
    def __init__(self, token):
        self.dbx = dropbox.Dropbox(token)

    def get_file_list(self, path):
        contents = self.dbx.files_list_folder(path)
        files_name = [content.name for content in contents.entries]
        self.dbx.close()
        return files_name

    def read_csv_without_index(self, path, csv_name):
        downfile, f = self.dbx.files_download(path+csv_name)
        df = pd.read_csv(f.raw)
        self.dbx.close()
        return df

    def read_csv(self, path, csv_name, index_col=None):
        try:
            downfile, f = self.dbx.files_download(path+csv_name)
            if index_col:
                df = pd.read_csv(f.raw, index_col=[index_col])
                df.index = pd.to_datetime(df.index)
            else:
                df = pd.read_csv(f.raw, index_col=[0])
        except dropbox.exceptions.ApiError:
            df = pd.DataFrame()

        self.dbx.close()
        return df

    def save_csv(self, path, csv_name, df):
        df_string = df.to_csv()
        db_bytes = bytes(df_string, 'utf8')
        self.dbx.files_upload(
            f=db_bytes,
            path=path + csv_name,
            mode=dropbox.files.WriteMode.overwrite
        )
        self.dbx.close()

    def save_json(self, path, name, data):
        # https://villoro.com/post/dropbox_python 참고
        with io.StringIO() as stream:
            json.dump(data, stream, cls=NpEncoder)
            stream.seek(0)
            self.dbx.files_upload(
                f    = stream.read().encode(),
                path = path+name,
                mode =dropbox.files.WriteMode.overwrite
            )
        self.dbx.close()

    def read_json(self, path, file_name):
        # https://villoro.com/post/dropbox_python 참고
        _, res = self.dbx.files_download(path+file_name)
        with io.BytesIO(res.content) as stream:
            data = json.load(stream)
        self.dbx.close()
        return data
