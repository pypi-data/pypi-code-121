import os
import ipynbname
from ml_sdk.ml.model.notebook import WatchmenNotebook
from ml_sdk.ml.sdk.watchmen.sdk import load_dataset_by_name


def get_notebook():
    note_name = ipynbname.name()
    path = ipynbname.path()
    notebook = WatchmenNotebook(name=note_name,storageLocation= path)
    return notebook


class WatchmenClient(object):
    def __init__(self,token):
        if token:
            self.token = token
        else:
            self.token = os.environ.get('TOKEN')

    def load_dataset(self, name):
        return load_dataset_by_name(self.token,name)


    def register_notebook(self):
        notebook = get_notebook()
        return notebook


    def save_topic_dataset(self,topic_name:str, dataset):
        pass


    def register_model(self):
        pass


#
# client  = WatchmenClient(token="0Z6ag50cdIPamBIgf8KfoQ")
# df = client.load_dataset("DEMO")
# print(df)









