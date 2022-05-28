import os

from ml_sdk.ml.model.notebook import WatchmenNotebook
from ml_sdk.ml.sdk.watchmen.sdk import load_dataset_by_name


class WatchmenClient(object):
    def __init__(self,token):
        if token:
            self.token = token
        else:
            self.token = os.environ.get('TOKEN')

    def load_dataset(self, name):
        return load_dataset_by_name(self.token,name)


    def register_notebook(self,notebook:WatchmenNotebook):
        print(notebook)
        pass

    def save_topic_dataset(self,topic_name:str, dataset):
        pass


    def register_model(self):
        pass


#
# client  = WatchmenClient(token="0Z6ag50cdIPamBIgf8KfoQ")
# df = client.load_dataset("DEMO")
# print(df)









